import os
from typing import List
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_core.vectorstores import VectorStore
from src.constants import VECTOR_DB_KNOWLEDGE_DIR
from src.llm import get_gemini_embedding

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

