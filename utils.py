#utils.py  This will have more things as I think of them, but these are utilities I need available to a bunch of the modules.
from docx import Document



def read_word_file(file_path):
    try:
        doc = Document(file_path)
        text = ""
        for para in doc.paragraphs:
            text += para.text + "\n"
        return text
    except Exception as e:
        print(f"An error occurred while reading the Word document: {e}")
        return None