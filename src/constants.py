from pathlib import Path

#项目root文件夹
ROOT_DIR=Path(__file__).parent.parent
#Prompts文件夹
PROMPTS_DIR=ROOT_DIR.joinpath("Prompts")
#向量知识库
VECTOR_DB_KNOWLEDGE_DIR=ROOT_DIR.joinpath("vectorStore")
#先知文章
XIANZHI_DOCUMENT_DIR=ROOT_DIR.joinpath("DocumentStore/xianzhi")


