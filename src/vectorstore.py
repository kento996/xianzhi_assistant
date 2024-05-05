import os
from typing import List
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_core.vectorstores import VectorStore

from src.chains import Chains_Gemini
from src.constants import VECTOR_DB_KNOWLEDGE_DIR
from src.llm import get_gemini_embedding
from src.utils import get_pdf_text, get_text_chunks

VECTOR_DB_KNOWLEDGE_PATH = os.path.join(VECTOR_DB_KNOWLEDGE_DIR,"XianzhiVectorStore")

db: VectorStore = None

if os.path.exists(VECTOR_DB_KNOWLEDGE_PATH):
    db = FAISS.load_local(VECTOR_DB_KNOWLEDGE_PATH,
                          get_gemini_embedding(),
                          allow_dangerous_deserialization=True)

def query_vectordb(query: str, k: int = 20) -> List[Document]:
    while True:
        try:
            docs = db.similarity_search(query, k=k)
            break
        except Exception as e:
            raise e

    return docs

def update_vectordb(pdf_documents_path:str):
    if not os.path.exists(pdf_documents_path):
        print("The specified directory does not exist.")
        return
    for filename in os.listdir(pdf_documents_path):
        filepath = os.path.join(pdf_documents_path, filename)
        text_chunks=get_text_chunks(get_pdf_text(filepath))
        contents=""
        for index, text in enumerate(text_chunks):
            contents += str(index + 1) + "." + text.replace("\n", " ") + "\n"
        chain=Chains_Gemini()
        text_abstract=chain.ContentAbstract_chain(contents)
        documents = []
        documents.append(
            Document(
                page_content=text_abstract,
                metadata={
                    "FileName": filename+"(2)"
                }
            )
        )
        db.add_documents(documents)
        db.save_local(VECTOR_DB_KNOWLEDGE_PATH)





if __name__ == '__main__':
    update_vectordb("/Users/kento/PycharmProjects/XianzhiAsistant/DocumentStore/test")




