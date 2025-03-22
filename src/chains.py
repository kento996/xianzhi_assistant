import os
from dotenv import load_dotenv
import logging

from langchain_core.prompts import PromptTemplate

from src.constants import XIANZHI_DOCUMENT_DIR
from src.llm import get_llm
from src.utils import get_pdf_text, get_text_chunks

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('chains')

# 加载环境变量
load_dotenv()
logger.info("加载环境变量配置")

# 从环境变量获取默认模型配置
DEFAULT_MODEL_PROVIDER = os.getenv("DEFAULT_MODEL_PROVIDER", "gemini")
DEFAULT_MODEL_NAME = os.getenv("DEFAULT_MODEL_NAME")

logger.info(f"Chains默认模型提供商: {DEFAULT_MODEL_PROVIDER}")
logger.info(f"Chains默认模型名称: {DEFAULT_MODEL_NAME or '未指定，将使用提供商默认模型'}")

class Chains:
    """
    用于创建和执行LLM链的基类
    """
    
    def __init__(self, model_provider=None, model_name=None):
        """
        初始化Chains对象
        
        Args:
            model_provider: 模型提供商，支持"gemini", "openai", "ollama"，默认使用环境变量中的配置
            model_name: 模型名称，默认使用环境变量中的配置
        """
        # 使用环境变量中的默认配置（如果参数未指定）
        self.model_provider = model_provider or DEFAULT_MODEL_PROVIDER
        self.model_name = model_name or DEFAULT_MODEL_NAME
        
        logger.info(f"初始化Chains，模型提供商: {self.model_provider}，模型名称: {self.model_name or '未指定'}")
        
        try:
            self.llm = get_llm(self.model_provider, self.model_name)
            logger.info("成功初始化LLM模型")
        except Exception as e:
            logger.error(f"初始化LLM模型失败: {str(e)}")
            raise
        
        self._init_prompts()
        
    def _init_prompts(self):
        """初始化提示模板"""
        logger.info("初始化提示模板")
        
        self.contentAbstractPrompt = """请对分析如下文档并完成以下任务：
                                    1. 分析文档的主题和内容
                                    2. 用一段话概括文档
                                    ## 文档
                                    ```
                                    {content_by_question}
                                    ```
                                    ## 注意
                                    你的输出结果是包含文档主题和内容的一段话"""
        self.contentAbstract_PromptTemplate = PromptTemplate(template=self.contentAbstractPrompt,
                                    input_variables=["content_by_question"])

        self.signalAnswerPrompt="""你是一位网络安全专家，请你完成如下任务：
        1. 分析如下安全问题
        2. 根据如下的相关文档知识回答问题
        ##问题
        {question}
        ##相关文档
        {contents}
        ##注意
        如果你觉得相关文档没用时，请你根据你自己的知识回答问题"""
        self.signalAnswer_PromptTemplate = PromptTemplate(template=self.signalAnswerPrompt,
                                    input_variables=["question","contents"])

        self.analyzeResultPrompt="""你是一位网络安全专家，请你完成如下任务：
        1. 分析如下安全问题
        2. 对如下的参考答案进行分析
        3. 根据有用的参考答案回答问题
        ##问题
        {question}
        ##参考内容
        {contents}"""
        self.analyzeResult_PromptTemplate = PromptTemplate(template=self.analyzeResultPrompt,
                                                 input_variables=["question", "contents"])

    def ContentAbstract_chain(self, content_by_question):
        """执行内容摘要链"""
        logger.info("执行内容摘要链")
        try:
            chain=self.contentAbstract_PromptTemplate | self.llm
            return chain.invoke({"content_by_question":content_by_question}).content
        except Exception as e:
            logger.error(f"执行内容摘要链失败: {str(e)}")
            raise

    def get_document_description_chain(self, filename, question):
        """执行文档描述链"""
        logger.info(f"执行文档描述链，文件名: {filename}")
        
        chain = self.signalAnswer_PromptTemplate | self.llm
        ctf_folder = XIANZHI_DOCUMENT_DIR
        pdf_path = os.path.join(ctf_folder, filename)
        
        if not os.path.exists(pdf_path):
            logger.error(f"文件不存在: {pdf_path}")
            raise FileNotFoundError(f"文件不存在: {pdf_path}")
        
        try:
            logger.info(f"读取PDF文件: {pdf_path}")
            raw_text = get_pdf_text(pdf_path)
            text_chunks = get_text_chunks(raw_text)
            
            contents = ""
            for index, text in enumerate(text_chunks):
                contents += str(index + 1) + "." + text.replace("\n", " ") + "\n"
            
            logger.info("执行文档描述链")
            return chain.invoke({"question":question, "contents":contents}).content
        except Exception as e:
            logger.error(f"处理文档时出错: {str(e)}")
            raise

    def analyze_chain(self, question, contents):
        """执行分析链"""
        logger.info("执行分析链")
        try:
            chain=self.analyzeResult_PromptTemplate | self.llm
            return chain.invoke({"question":question, "contents":contents}).content
        except Exception as e:
            logger.error(f"执行分析链失败: {str(e)}")
            raise

# 保持向后兼容性
class Chains_Gemini(Chains):
    """保持向后兼容的Gemini模型链类"""
    
    def __init__(self):
        logger.info("初始化Chains_Gemini (兼容模式)")
        super().__init__(model_provider="gemini")




