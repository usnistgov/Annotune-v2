import glob
import json
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


class TextGrouper:
    def __init__(self, model_name='all-MiniLM-L6-v2', threshold=0.8, min_document_length=50):
        """
        Initialize the grouper with a pre-trained SentenceTransformer model, similarity threshold, and minimum document length.
        """
        self.model = SentenceTransformer(model_name)
        self.threshold = threshold
        self.data = []  # Store the loaded data with questions, answers, and documents
        self.min_document_length = min_document_length

    def load_data(self, folder, starts):
        """
        Load question-answer data and associated documents from files matching a specific pattern.
        """
        for start in starts:  # Loop through each prefix in the starts list
            files = glob.glob(folder + start + "*")
            for file in files:
                with open(file, "r") as f:
                    self.data.extend(json.load(f))

    def filter_and_deduplicate_documents(self, documents):
        """
        Filter out short documents and deduplicate them, keeping only the longest versions.
        """
        unique_documents = {}
        for doc in documents:
            stripped_doc = doc.strip()
            if len(stripped_doc) >= self.min_document_length:  # Exclude shorter documents
                if stripped_doc not in unique_documents or len(doc) > len(unique_documents[stripped_doc]):
                    unique_documents[stripped_doc] = doc
        return list(unique_documents.values())

    def group_texts(self, texts):
        """
        Group texts (questions, answers, or documents) based on cosine similarity.
        """
        if not texts:
            return []

        # Encode the texts into embeddings
        embeddings = self.model.encode(texts)

        # Calculate pairwise cosine similarity
        similarity_matrix = cosine_similarity(embeddings)

        # Group texts based on the similarity threshold
        groups = []
        visited = set()

        for i, text in enumerate(texts):
            if i in visited:
                continue
            group = [text]
            visited.add(i)
            for j in range(len(texts)):
                if j != i and similarity_matrix[i, j] > self.threshold:
                    group.append(texts[j])
                    visited.add(j)
            groups.append(group)

        return groups

    def group_questions_answers_documents(self):
        """
        Group questions, answers, and relevant documents together.
        """
        grouped_data = []

        # Group questions and answers
        questions = [item["question"] for item in self.data]
        answers = [item["answer"] for item in self.data]

        grouped_questions = self.group_texts(questions)
        grouped_answers = self.group_texts(answers)

        # Map questions and answers back to their relevant documents
        for q_group, a_group in zip(grouped_questions, grouped_answers):
            relevant_docs = set()

            for item in self.data:
                if item["question"] in q_group or item["answer"] in a_group:
                    relevant_docs.update(item["documents"].values())

            # Filter and deduplicate relevant documents
            filtered_docs = self.filter_and_deduplicate_documents(relevant_docs)

            grouped_data.append({
                "questions": q_group,
                "answers": a_group,
                "documents": filtered_docs
            })

        return grouped_data

    def save_grouped_data(self, grouped_data, output_path):
        """
        Save grouped questions, answers, and documents to a JSON file.
        """
        with open(output_path, "w") as file:
            json.dump(grouped_data, file, indent=4)


if __name__ == "__main__":
    folder = "/Users/danielstephens/Desktop/Annotune-v2/annotune/total_saved/"
    starts = ['Communica', 'Cultural', 'Ethics an', 'Humanity', 'The Other', 'The impac', 'The unkno']  # List of prefixes

    grouper = TextGrouper(min_document_length=430)  # Set minimum document length to 100 characters

    # Load data
    grouper.load_data(folder, starts)

    # Group questions, answers, and documents together
    grouped_data = grouper.group_questions_answers_documents()

    # Save grouped data to a JSON file
    grouper.save_grouped_data(grouped_data, "/Users/danielstephens/Desktop/Annotune-v2/annotune/grouped/grouped_questions_answers_documentsss.json")
