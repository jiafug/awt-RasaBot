import os

from transformers import pipeline

script_dir = os.path.dirname(__file__)  # <--- absolute dir the script is in
docs = os.path.join(script_dir, "./docs/")  # <--- documents directory


class DocumentStore:
    def init(self):
        self.qa_pipeline = pipeline(
            "question-answering",
            model="deepset/gelectra-base-germanquad",
            tokenizer="deepset/gelectra-base-germanquad")

    def get_answer(self, question, topic):
        context, raw_file = self.get_document(topic)
        qa_res = self.qa_pipeline({
            'context': context,
            'question': question
        })['answer']
        paragraph = self.get_relevant_paragraph(raw_file, qa_res)
        response = self.highlight_relevant_span(qa_res, paragraph)
        return response

    def get_document(self, topic):
        doc_list = os.listdir(docs)
        # get relevant document based on current topic
        doc = next(obj for obj in doc_list if topic in obj)
        doc = os.path.join(script_dir, './docs/' + doc)
        # open and read document
        file = open(doc, mode='r')
        raw_file = file.read()
        context = raw_file.replace('\n', ' ')
        file.close()
        return context, raw_file

    def get_relevant_paragraph(self, raw_file, answer):
        paragraphs = raw_file.split('\n\n')
        rel_para = next(paragraph for paragraph in paragraphs
                        if answer in paragraph.replace('\n', ' '))
        return rel_para

    def highlight_relevant_span(self, answer, paragraph):
        html_start = '<b>'
        html_end = '</b>'
        try:
            idx = paragraph.index(answer)
            end_idx = idx + len(answer)
        except ValueError:
            # substring not found error can occur if the answer contains a new line command
            idx = paragraph.replace('\n', ' ').index(answer)
            end_idx = idx + len(answer) + 2
        response = paragraph[:idx] + html_start + paragraph[
            idx:end_idx] + html_end + paragraph[end_idx:]
        return response


if __name__ == "__main__":
    ds = DocumentStore()
    ds.init()
    while True:
        topic = "wohnung_anmelden"
        q = input("q: ")
        print(ds.get_answer(q, topic))
