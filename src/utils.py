from PyPDF2 import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter


def get_pdf_text(pdf):
    text = ""
    pdf_reader = PdfReader(pdf)
    for page in pdf_reader.pages:
        text += page.extract_text()

    return text

def get_text_chunks(
            text,
            chunk_size: int = 1000,
            chunk_overlap: int = 150
    ):
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len
        )
        return text_splitter.split_text(text)