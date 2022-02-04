import os

from transformers import pipeline

script_dir = os.path.dirname(__file__)  # <--- absolute dir the script is in
docs = os.path.join(script_dir, "./docs/")  # <--- documents directory


class DocumentStore:
    def __init__(self):
        """Initialize extractive question answering pipeline."""
        self.qa_pipeline = pipeline(
            "question-answering",
            model="deepset/gelectra-base-germanquad",
            tokenizer="deepset/gelectra-base-germanquad",
        )

    def get_answer(self, question, topic):
        """Main function to be called to extract an answer to question
        by only looking up the topic document.

        Args:
            question (str): question asked by user
            topic (str): most recent topic / service

        Returns:
            str: relevant paragraph with highlighted answer
        """
        context, raw_file = self.get_document(topic)
        qa_res = self.qa_pipeline({"context": context, "question": question})["answer"]
        paragraph = self.get_relevant_paragraph(raw_file, qa_res)
        response = self.highlight_relevant_span(qa_res, paragraph)
        return response

    def get_document(self, topic):
        """Finds and reads the to the topic relevant document.

        Args:
            topic (str): topic which also corresponds to document name

        Returns:
            (str, str): tuple containing the striped and raw document
        """
        doc_list = os.listdir(docs)
        # get relevant document based on current topic
        doc = next(obj for obj in doc_list if topic in obj)
        doc = os.path.join(script_dir, "./docs/" + doc)
        # open and read document
        file = open(doc, mode="r")
        raw_file = file.read()
        context = raw_file.replace("\n", " ")
        file.close()
        return context, raw_file

    def get_relevant_paragraph(self, raw_file, answer):
        """Given the answer, finds the relevant paragraph where the answer
        was extracted from.

        Args:
            raw_file (str): raw document file
            answer (str): extracted answer

        Returns:
            str: relevant paragraph
        """
        paragraphs = raw_file.split("\n\n")
        rel_para = next(
            paragraph
            for paragraph in paragraphs
            if answer in paragraph.replace("\n", " ")
        )
        return rel_para

    def highlight_relevant_span(self, answer, paragraph):
        """Inserts highliting markers into the relevant paragraph.

        Args:
            answer (str): answer to question
            paragraph (str): relevant paragraph

        Returns:
            str: paragraph where the answer is marked
        """
        html_start = '<span class="hl"><b>'
        html_end = "</b></span>"
        try:
            idx = paragraph.index(answer)
            end_idx = idx + len(answer)
        except ValueError:
            # substring not found error can occur if the answer contains a new line command
            idx = paragraph.replace("\n", " ").index(answer)
            end_idx = idx + len(answer) + 2
        response = (
            paragraph[:idx]
            + html_start
            + paragraph[idx:end_idx]
            + html_end
            + paragraph[end_idx:]
        )
        response = response.replace("\n", "<br>")
        return response


if __name__ == "__main__":
    ds = DocumentStore()
    while True:
        topic = "wohnung_anmelden"
        q = input("q: ")
        print(ds.get_answer(q, topic))
