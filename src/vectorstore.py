import os
from typing import List
from dotenv import load_dotenv
import logging
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_core.vectorstores import VectorStore

from src.chains import Chains
from src.constants import VECTOR_DB_KNOWLEDGE_DIR
from src.llm import get_embedding
from src.utils import get_pdf_text, get_text_chunks

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('vectorstore')

# 加载环境变量
load_dotenv()
logger.info("加载环境变量配置")

# 从环境变量获取默认模型配置
DEFAULT_MODEL_PROVIDER = os.getenv("DEFAULT_MODEL_PROVIDER", "gemini")
DEFAULT_MODEL_NAME = os.getenv("DEFAULT_MODEL_NAME")
DEFAULT_VECTOR_DB_DIR = os.getenv("DEFAULT_VECTOR_DB_DIR", VECTOR_DB_KNOWLEDGE_DIR)

logger.info(f"Vectorstore默认模型提供商: {DEFAULT_MODEL_PROVIDER}")
logger.info(f"Vectorstore默认模型名称: {DEFAULT_MODEL_NAME or '未指定，将使用提供商默认模型'}")
logger.info(f"向量库目录: {DEFAULT_VECTOR_DB_DIR}")

# 默认向量库路径
VECTOR_DB_KNOWLEDGE_PATH = os.path.join(DEFAULT_VECTOR_DB_DIR, "XianzhiVectorStore")

# 不同模型提供商的向量库路径
VECTOR_DB_PATHS = {
    "gemini": os.path.join(DEFAULT_VECTOR_DB_DIR, "XianzhiVectorStore_gemini"),
    "openai": os.path.join(DEFAULT_VECTOR_DB_DIR, "XianzhiVectorStore_openai"),
    "ollama": os.path.join(DEFAULT_VECTOR_DB_DIR, "XianzhiVectorStore_ollama")
}

# 向量库实例缓存
vector_dbs = {}

def get_vectordb(model_provider=None, model_name=None) -> VectorStore:
    """
    获取或创建向量库实例
    
    Args:
        model_provider: 模型提供商，支持"gemini", "openai", "ollama"，默认使用环境变量中的配置
        model_name: 模型名称，默认使用环境变量中的配置
        
    Returns:
        VectorStore: 向量库实例
    """
    # 使用环境变量默认值（如果参数未指定）
    model_provider = model_provider or DEFAULT_MODEL_PROVIDER
    model_name = model_name or DEFAULT_MODEL_NAME
    
    cache_key = f"{model_provider}_{model_name or 'default'}"
    logger.info(f"获取向量库，提供商: {model_provider}，模型: {model_name or '默认'}，缓存键: {cache_key}")
    
    if cache_key in vector_dbs:
        logger.info(f"使用缓存的向量库: {cache_key}")
        return vector_dbs[cache_key]
    
    vector_db_path = VECTOR_DB_PATHS.get(model_provider, VECTOR_DB_KNOWLEDGE_PATH)
    logger.info(f"向量库路径: {vector_db_path}")
    
    try:
        # 获取嵌入模型
        logger.info(f"获取嵌入模型，提供商: {model_provider}")
        embedding = get_embedding(model_provider, model_name)
        
        if os.path.exists(vector_db_path):
            logger.info(f"加载已存在的向量库: {vector_db_path}")
            db = FAISS.load_local(vector_db_path, embedding, allow_dangerous_deserialization=True)
            logger.info("向量库加载成功")
        else:
            logger.info(f"向量库不存在，创建新的向量库: {vector_db_path}")
            # 如果向量库不存在，创建一个空的向量库
            db = FAISS.from_texts(["初始化向量库"], embedding)
            # 确保目录存在
            os.makedirs(os.path.dirname(vector_db_path), exist_ok=True)
            db.save_local(vector_db_path)
            logger.info("新向量库创建并保存成功")
        
        # 存入缓存
        vector_dbs[cache_key] = db
        return db
    except Exception as e:
        logger.error(f"获取向量库失败: {str(e)}")
        raise

def query_vectordb(query: str, k: int = 20, model_provider=None, model_name=None) -> List[Document]:
    """
    查询向量库
    
    Args:
        query: 查询文本
        k: 返回的最相似文档数量
        model_provider: 模型提供商，默认使用环境变量中的配置
        model_name: 模型名称，默认使用环境变量中的配置
        
    Returns:
        List[Document]: 相似文档列表
    """
    # 使用环境变量默认值（如果参数未指定）
    model_provider = model_provider or DEFAULT_MODEL_PROVIDER
    model_name = model_name or DEFAULT_MODEL_NAME
    
    logger.info(f"查询向量库，提供商: {model_provider}，k: {k}")
    
    try:
        db = get_vectordb(model_provider, model_name)
        logger.info(f"执行相似度搜索，查询: '{query[:50]}...'")
        docs = db.similarity_search(query, k=k)
        logger.info(f"查询成功，返回 {len(docs)} 个结果")
        return docs
    except Exception as e:
        logger.error(f"查询向量库失败: {str(e)}")
        raise

def update_vectordb(pdf_documents_path: str, model_provider=None, model_name=None):
    """
    更新向量库
    
    Args:
        pdf_documents_path: PDF文档路径
        model_provider: 模型提供商，默认使用环境变量中的配置
        model_name: 模型名称，默认使用环境变量中的配置
    """
    # 使用环境变量默认值（如果参数未指定）
    model_provider = model_provider or DEFAULT_MODEL_PROVIDER
    model_name = model_name or DEFAULT_MODEL_NAME
    
    logger.info(f"更新向量库，文档路径: {pdf_documents_path}，提供商: {model_provider}")
    
    if not os.path.exists(pdf_documents_path):
        error_msg = f"指定的目录不存在: {pdf_documents_path}"
        logger.error(error_msg)
        print(error_msg)
        return
    
    try:
        db = get_vectordb(model_provider, model_name)
        vector_db_path = VECTOR_DB_PATHS.get(model_provider, VECTOR_DB_KNOWLEDGE_PATH)
        
        pdf_files = [f for f in os.listdir(pdf_documents_path) if f.lower().endswith('.pdf')]
        logger.info(f"找到 {len(pdf_files)} 个PDF文件")
        
        if not pdf_files:
            logger.warning(f"目录中没有PDF文件: {pdf_documents_path}")
            print(f"警告: 目录中没有PDF文件: {pdf_documents_path}")
            return
        
        for filename in pdf_files:
            try:
                filepath = os.path.join(pdf_documents_path, filename)
                logger.info(f"处理文件: {filepath}")
                
                # 读取并分割文本
                text_chunks = get_text_chunks(get_pdf_text(filepath))
                logger.info(f"文件 {filename} 分割为 {len(text_chunks)} 个文本块")
                
                contents = ""
                for index, text in enumerate(text_chunks):
                    contents += str(index + 1) + "." + text.replace("\n", " ") + "\n"
                
                # 创建摘要
                logger.info(f"为文件 {filename} 创建摘要")
                chain = Chains(model_provider, model_name)
                text_abstract = chain.ContentAbstract_chain(contents)
                
                # 创建文档对象
                documents = []
                documents.append(
                    Document(
                        page_content=text_abstract,
                        metadata={
                            "FileName": filename
                        }
                    )
                )
                
                # 添加到向量库
                logger.info(f"将文件 {filename} 添加到向量库")
                db.add_documents(documents)
                db.save_local(vector_db_path)
                logger.info(f"文件 {filename} 成功添加到向量库")
                print(f"已添加文档 {filename} 到向量库")
            except Exception as e:
                logger.error(f"处理文件 {filename} 时出错: {str(e)}")
                print(f"处理文件 {filename} 时出错: {str(e)}")
                continue
        
        logger.info(f"向量库更新完成，保存到: {vector_db_path}")
    except Exception as e:
        logger.error(f"更新向量库时出错: {str(e)}")
        raise

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        pdf_dir = sys.argv[1]
        model_provider = sys.argv[2] if len(sys.argv) > 2 else None
        model_name = sys.argv[3] if len(sys.argv) > 3 else None
        update_vectordb(pdf_dir, model_provider, model_name)




