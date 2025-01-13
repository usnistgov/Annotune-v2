import json
import glob


class JsonProcessor:
    def __init__(self, input_dir, output_dir, full_data):
        """
        Initialize the JsonProcessor class.
        
        :param input_dir: Directory containing the input JSON files.
        :param output_dir: Directory where the processed JSON files will be saved.
        :param full_data: List of dictionaries containing full summary data.
        """
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.full_data = full_data

    @staticmethod
    def standardize_json(data):
        """
        Standardize JSON data to a common format.

        :param data: JSON data to be standardized.
        :return: Standardized data as a list of dictionaries.
        """
        standardized = []

        if isinstance(data, list):
            for entry in data:
                standardized.append({
                    "question": entry["question"],
                    "answer": entry["answer"],
                    "documents": entry["documents"]
                })

        elif isinstance(data, dict) and "questions" in data:
            for entry in data["questions"]:
                standardized.append({
                    "question": entry["question"],
                    "answer": entry["answer"],
                    "documents": entry["documents"]
                })

        return standardized

    def replace_documents_with_full_summary(self, questions_data):
        """
        Replace document text in questions_data with corresponding full summaries from full_data.

        :param questions_data: List of questions and associated document texts.
        :return: Updated questions data with replaced summaries.
        """
        for question in questions_data:
            for doc_key, doc_text in question["documents"].items():
                phrases = [phrase.strip().replace(" ", "").replace(".", "") for phrase in doc_text.split(",")]
                match_found = False

                for full_doc in self.full_data:
                    summary_text = full_doc["summary"].replace(" ", "").replace(".", "")

                    for start_index in range(len(phrases)):
                        if all(phrase in summary_text for phrase in phrases[start_index:]):
                            question["documents"][doc_key] = full_doc["summary"]
                            match_found = True
                            break

                    if match_found:
                        break

                if not match_found:
                    combined_text = "".join(phrases)
                    midpoint = len(combined_text) // 2
                    part1 = combined_text[:midpoint].strip()
                    part2 = combined_text[midpoint:].strip()

                    for full_doc in self.full_data:
                        summary_text = full_doc["summary"].replace(" ", "").replace(".", "")
                        if part1 in summary_text or part2 in summary_text:
                            question["documents"][doc_key] = full_doc["summary"]
                            break
        return questions_data

    @staticmethod
    def read_jsonl(file_path):
        """
        Read a .jsonl file and parse its content.

        :param file_path: Path to the .jsonl file.
        :return: List of JSON objects.
        """
        data = []
        with open(file_path, 'r') as f:
            for line in f:
                data.append(json.loads(line))
        return data

    def process_files(self):
        """
        Process all JSON files in the input directory, standardize and replace document texts,
        then save the updated data to the output directory.
        """
        files = glob.glob(f"{self.input_dir}/*")
        for file in files:
            with open(file, "r") as f:
                data = json.load(f)
            
            standard_data = self.standardize_json(data)
            updated_questions_data = self.replace_documents_with_full_summary(standard_data)
            
            output_file = f"{self.output_dir}/{file.split('/')[-1]}"
            with open(output_file, "w") as out_file:
                json.dump(updated_questions_data, out_file, indent=4)


# Example usage:
if __name__ == "__main__":
    
    input_directory = "/Users/danielstephens/Desktop/Annotune-v2/annotune/savedFiles"
    output_directory = "/Users/danielstephens/Desktop/Annotune-v2/annotune/newSaved"
    full_data = JsonProcessor.read_jsonl("/Users/danielstephens/Desktop/Annotune-v2/synthetic-first-contact-plot-summaries-20241030-182950.jsonl")
    processor = JsonProcessor(input_directory, output_directory, full_data)
    processor.process_files()
