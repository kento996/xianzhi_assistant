from google.generativeai.types import HarmCategory, HarmBlockThreshold
from langchain_core.language_models import BaseChatModel
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.llms import Ollama
from langchain_community.embeddings import OllamaEmbeddings
from dotenv import load_dotenv
import os
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('llm')

# 从.env文件加载环境变量
load_dotenv()
logger.info("加载环境变量配置")

# 从.env文件获取默认模型配置
DEFAULT_MODEL_PROVIDER = os.getenv("DEFAULT_MODEL_PROVIDER", "gemini")
DEFAULT_MODEL_NAME = os.getenv("DEFAULT_MODEL_NAME", None)
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# 特定模型提供商的默认模型配置
DEFAULT_GEMINI_MODEL = os.getenv("DEFAULT_GEMINI_MODEL", "gemini-pro")
DEFAULT_OPENAI_MODEL = os.getenv("DEFAULT_OPENAI_MODEL", "gpt-3.5-turbo")
DEFAULT_OLLAMA_MODEL = os.getenv("DEFAULT_OLLAMA_MODEL", "llama2")

# 嵌入模型配置
DEFAULT_GEMINI_EMBEDDING_MODEL = os.getenv("DEFAULT_GEMINI_EMBEDDING_MODEL", "models/embedding-001")
DEFAULT_OPENAI_EMBEDDING_MODEL = os.getenv("DEFAULT_OPENAI_EMBEDDING_MODEL", "text-embedding-ada-002")

logger.info(f"默认模型提供商: {DEFAULT_MODEL_PROVIDER}")
logger.info(f"使用的模型: {DEFAULT_MODEL_NAME or '未指定，将使用提供商默认模型'}")

def get_llm(model_provider=None, model_name=None) -> BaseChatModel:
    """
    获取LLM模型实例
    
    Args:
        model_provider: 模型提供商，支持"gemini", "openai", "ollama"
        model_name: 模型名称，为None时使用默认模型
        
    Returns:
        BaseChatModel: LLM模型实例
    """
    # 如果未指定，使用环境变量中的默认值
    model_provider = model_provider or DEFAULT_MODEL_PROVIDER
    logger.info(f"使用模型提供商: {model_provider}")
    
    try:
        if model_provider == "gemini":
            # 如果没有指定model_name，使用DEFAULT_MODEL_NAME，如果仍为None则使用DEFAULT_GEMINI_MODEL
            specific_model = model_name or DEFAULT_MODEL_NAME or DEFAULT_GEMINI_MODEL
            logger.info(f"使用Gemini模型: {specific_model}")
            if not GOOGLE_API_KEY:
                raise ValueError("未设置GOOGLE_API_KEY环境变量，无法使用Gemini模型")
            return get_gemini(specific_model)
        elif model_provider == "openai":
            specific_model = model_name or DEFAULT_MODEL_NAME or DEFAULT_OPENAI_MODEL
            logger.info(f"使用OpenAI模型: {specific_model}")
            if not OPENAI_API_KEY:
                raise ValueError("未设置OPENAI_API_KEY环境变量，无法使用OpenAI模型")
            return get_openai(specific_model)
        elif model_provider == "ollama":
            specific_model = model_name or DEFAULT_MODEL_NAME or DEFAULT_OLLAMA_MODEL
            logger.info(f"使用Ollama模型: {specific_model}")
            return get_ollama(specific_model)
        else:
            raise ValueError(f"不支持的模型提供商: {model_provider}")
    except Exception as e:
        logger.error(f"获取LLM模型失败: {str(e)}")
        raise

def get_embedding(model_provider=None, model_name=None):
    """
    获取嵌入模型实例
    
    Args:
        model_provider: 模型提供商，支持"gemini", "openai", "ollama"
        model_name: 模型名称，为None时使用默认模型
        
    Returns:
        嵌入模型实例
    """
    # 如果未指定，使用环境变量中的默认值
    model_provider = model_provider or DEFAULT_MODEL_PROVIDER
    logger.info(f"使用嵌入模型提供商: {model_provider}")
    
    try:
        if model_provider == "gemini":
            specific_model = model_name or DEFAULT_MODEL_NAME or DEFAULT_GEMINI_EMBEDDING_MODEL
            logger.info(f"使用Gemini嵌入模型: {specific_model}")
            if not GOOGLE_API_KEY:
                raise ValueError("未设置GOOGLE_API_KEY环境变量，无法使用Gemini嵌入模型")
            return get_gemini_embedding(specific_model)
        elif model_provider == "openai":
            specific_model = model_name or DEFAULT_MODEL_NAME or DEFAULT_OPENAI_EMBEDDING_MODEL
            logger.info(f"使用OpenAI嵌入模型: {specific_model}")
            if not OPENAI_API_KEY:
                raise ValueError("未设置OPENAI_API_KEY环境变量，无法使用OpenAI嵌入模型")
            return get_openai_embedding(specific_model)
        elif model_provider == "ollama":
            specific_model = model_name or DEFAULT_MODEL_NAME or DEFAULT_OLLAMA_MODEL
            logger.info(f"使用Ollama嵌入模型: {specific_model}")
            return get_ollama_embedding(specific_model)
        else:
            raise ValueError(f"不支持的模型提供商: {model_provider}")
    except Exception as e:
        logger.error(f"获取嵌入模型失败: {str(e)}")
        raise

def get_gemini(model_name=DEFAULT_GEMINI_MODEL) -> BaseChatModel:
    """获取Gemini模型实例"""
    try:
        return ChatGoogleGenerativeAI(
            model=model_name,
            temperature=0,
            convert_system_message_to_human=True,
            transport="rest",
            google_api_key=GOOGLE_API_KEY,
            safety_settings={
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
            }
        )
    except Exception as e:
        logger.error(f"初始化Gemini模型失败: {str(e)}")
        raise

# 保留向后兼容性的函数
def get_gemini_pro_15() -> BaseChatModel:
    return get_gemini("gemini-1.5-pro-latest")

# 保留向后兼容性的函数
def get_gemini_pro() -> BaseChatModel:
    return get_gemini("gemini-pro")

def get_gemini_embedding(model_name=DEFAULT_GEMINI_EMBEDDING_MODEL):
    """获取Gemini嵌入模型实例"""
    try:
        return GoogleGenerativeAIEmbeddings(
            model=model_name,
            transport="rest",
            google_api_key=GOOGLE_API_KEY
        )
    except Exception as e:
        logger.error(f"初始化Gemini嵌入模型失败: {str(e)}")
        raise

def get_openai(model_name=DEFAULT_OPENAI_MODEL) -> BaseChatModel:
    """获取OpenAI模型实例"""
    try:
        return ChatOpenAI(
            model=model_name,
            temperature=0,
            api_key=OPENAI_API_KEY,
        )
    except Exception as e:
        logger.error(f"初始化OpenAI模型失败: {str(e)}")
        raise

def get_openai_embedding(model_name=DEFAULT_OPENAI_EMBEDDING_MODEL):
    """获取OpenAI嵌入模型实例"""
    try:
        return OpenAIEmbeddings(
            model=model_name,
            api_key=OPENAI_API_KEY,
        )
    except Exception as e:
        logger.error(f"初始化OpenAI嵌入模型失败: {str(e)}")
        raise

def get_ollama(model_name=DEFAULT_OLLAMA_MODEL) -> BaseChatModel:
    """获取Ollama模型实例"""
    try:
        return Ollama(
            model=model_name,
            temperature=0,
            base_url=OLLAMA_BASE_URL,
        )
    except Exception as e:
        logger.error(f"初始化Ollama模型失败: {str(e)}, 请确保Ollama服务正在运行且地址正确")
        raise

def get_ollama_embedding(model_name=DEFAULT_OLLAMA_MODEL):
    """获取Ollama嵌入模型实例"""
    try:
        return OllamaEmbeddings(
            model=model_name,
            base_url=OLLAMA_BASE_URL,
        )
    except Exception as e:
        logger.error(f"初始化Ollama嵌入模型失败: {str(e)}, 请确保Ollama服务正在运行且地址正确")
        raise


