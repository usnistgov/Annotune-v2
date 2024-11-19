import glob
import json
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


class SemanticTextGrouper:
    def __init__(self, model_name='all-MiniLM-L6-v2', threshold=0.8, min_document_length=300):
        """
        Initialize the SemanticTextGrouper with a pre-trained SentenceTransformer model,
        similarity threshold, and minimum document length.
        """
        self.model = SentenceTransformer(model_name)
        self.threshold = threshold
        self.data = []  # Store the loaded data with questions, answers, and documents
        self.min_document_length = min_document_length

    def standardize_json(self, data):
        """
        Standardize the format of the input JSON data.
        """
        standardized = []
        if isinstance(data, list):
            for entry in data:
                if "question" in entry and "answer" in entry and "documents" in entry:
                    standardized.append({
                        "question": entry["question"],
                        "answer": entry["answer"],
                        "documents": entry["documents"]
                    })
        elif isinstance(data, dict) and "questions" in data:
            for entry in data["questions"]:
                if "question" in entry and "answer" in entry and "documents" in entry:
                    standardized.append({
                        "question": entry["question"],
                        "answer": entry["answer"],
                        "documents": entry["documents"]
                    })
        return standardized

    def load_data(self, folder, starts):
        """
        Load question-answer data and associated documents from files matching a specific pattern.
        """
        for start in starts:
            files = glob.glob(folder + start + "*")
            for file in files:
                try:
                    with open(file, "r") as f:
                        raw_data = json.load(f)
                        self.data.extend(self.standardize_json(raw_data))
                except Exception as e:
                    print(f"Error reading {file}: {e}")

    def filter_and_deduplicate_documents(self, documents):
        """
        Filter out short documents and deduplicate them, keeping only the longest versions.
        """
        unique_documents = {}
        for doc in documents:
            stripped_doc = doc.strip()
            if len(stripped_doc) >= self.min_document_length:
                if stripped_doc not in unique_documents or len(doc) > len(unique_documents[stripped_doc]):
                    unique_documents[stripped_doc] = doc
        return list(unique_documents.values())

    def group_texts(self, texts):
        """
        Group texts (questions, answers, or documents) based on cosine similarity.
        """
        if not texts:
            return []

        embeddings = self.model.encode(texts)
        similarity_matrix = cosine_similarity(embeddings)
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
        questions = [item["question"] for item in self.data]
        answers = [item["answer"] for item in self.data]

        grouped_questions = self.group_texts(questions)
        grouped_answers = self.group_texts(answers)

        for q_group, a_group in zip(grouped_questions, grouped_answers):
            relevant_docs = set()

            for item in self.data:
                if item["question"] in q_group or item["answer"] in a_group:
                    relevant_docs.update(item["documents"].values())

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
    folder = "/Users/danielstephens/Desktop/Annotune-v2/annotune/newSave/"
    starts = [
        'Communica', 'Cultural', 'Ethics an', 'Humanity', 'The Other', 
        'The impac', 'The unkno'
    ]

    grouper = SemanticTextGrouper(min_document_length=300)  # Set minimum document length to 300 characters

    # Load and process data
    print("Loading data...")
    grouper.load_data(folder, starts)
    print(f"Loaded {len(grouper.data)} entries.")

    # Group questions, answers, and documents
    print("Grouping data...")
    grouped_data = grouper.group_questions_answers_documents()
    print(f"Grouped data into {len(grouped_data)} groups.")

    # Save grouped data to a JSON file
    output_path = "/Users/danielstephens/Desktop/Annotune-v2/annotune/grouped/grouped_questions_answers_documentsss.json"
    print(f"Saving grouped data to {output_path}...")
    grouper.save_grouped_data(grouped_data, output_path)
    print("Grouped data saved successfully!")
