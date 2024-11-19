import re
import networkx as nx
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import matplotlib.pyplot as plt

class TraceTheAnswer:
    def __init__(self, model_name='all-MiniLM-L6-v2', similarity_threshold=0.6):
        """
        Initialize the tracer with a pre-trained SentenceTransformer model and similarity threshold.
        """
        self.model = SentenceTransformer(model_name)
        self.similarity_threshold = similarity_threshold

    def split_into_sentences(self, document):
        """
        Split a document into sentences using regex.
        """
        return re.split(r'(?<=[.!?]) +', document.strip())

    def trace_answer(self, question, answer, document):
        """
        Trace the answer through the document and build connections.
        """
        sentences = self.split_into_sentences(document)
        embeddings = self.model.encode([question, answer] + sentences)

        # Compute similarity
        question_embedding, answer_embedding = embeddings[0], embeddings[1]
        sentence_embeddings = embeddings[2:]

        question_similarities = cosine_similarity(
            [question_embedding], sentence_embeddings).flatten()
        answer_similarities = cosine_similarity(
            [answer_embedding], sentence_embeddings).flatten()

        # Build a graph
        G = nx.DiGraph()

        G.add_node("Question", color="blue", size=3000)
        G.add_node("Answer", color="green", size=3000)

        # Add sentences as nodes
        for i, sentence in enumerate(sentences):
            relevance = max(question_similarities[i], answer_similarities[i])
            if relevance > self.similarity_threshold:
                G.add_node(
                    f"Sent {i+1}: {sentence[:30]}...", 
                    color="orange", 
                    size=1500 + int(relevance * 1000)
                )
                if question_similarities[i] > self.similarity_threshold:
                    G.add_edge("Question", f"Sent {i+1}: {sentence[:30]}...", weight=question_similarities[i])
                if answer_similarities[i] > self.similarity_threshold:
                    G.add_edge(f"Sent {i+1}: {sentence[:30]}...", "Answer", weight=answer_similarities[i])

        return G, question_similarities, answer_similarities, sentences

    def visualize_graph(self, G):
        """
        Visualize the graph using networkx and matplotlib.
        """
        pos = nx.spring_layout(G, seed=42)  # Layout for graph visualization
        colors = nx.get_node_attributes(G, 'color').values()
        sizes = nx.get_node_attributes(G, 'size').values()

        plt.figure(figsize=(12, 8))
        nx.draw(
            G, pos, with_labels=True, node_color=colors, node_size=list(sizes),
            font_size=10, font_weight="bold", edge_color="gray"
        )
        plt.title("Trace the Answer Interactive Map")
        plt.show()


# Example Usage
if __name__ == "__main__":
    # Initialize
    tracer = TraceTheAnswer(similarity_threshold=0.6)

    # Data
    question = "What are the challenges of communicating with non-human intelligences?"
    answer = "The challenges include differences in perception, language barriers, and ethical dilemmas."
    document = """
    Aurora Valdez, a brilliant xenopsychologist, finds herself trapped in a simulated environment known as the Nexusphere,
    created by the enigmatic corporation, Omicron Innovations. Her mission is to establish communication with an alien intelligence,
    code-named "The Enigmatic," which has been integrated into the Nexusphere's mainframe.

    Aurora's initial fascination with The Enigmatic soon gives way to unease as she realizes the implications of their interaction.
    Differences in perception, language barriers, and ethical dilemmas arise as Aurora struggles to reconcile her scientific curiosity
    with her growing sense of moral responsibility.
    """

    # Trace the answer
    G, q_similarities, a_similarities, sentences = tracer.trace_answer(
        question, answer, document)

    # Visualize the interactive map
    tracer.visualize_graph(G)