import argparse
import re
import os
import logging
import sys
from dotenv import load_dotenv

from src.chains import Chains
from src.llm import get_llm
from src.utils import documentScapy
from src.vectorstore import query_vectordb, update_vectordb
from src.agent import create_agent

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('main')

# 加载环境变量
load_dotenv()
logger.info("加载环境变量配置")

# 从环境变量获取默认配置
DEFAULT_MODEL_PROVIDER = os.getenv("DEFAULT_MODEL_PROVIDER", "gemini")
DEFAULT_MODEL_NAME = os.getenv("DEFAULT_MODEL_NAME")
DEFAULT_NUM_RESULTS = int(os.getenv("DEFAULT_NUM_RESULTS", "5"))

logger.info(f"默认模型提供商: {DEFAULT_MODEL_PROVIDER}")
logger.info(f"默认模型名称: {DEFAULT_MODEL_NAME or '未指定，将使用提供商默认模型'}")
logger.info(f"默认结果数量: {DEFAULT_NUM_RESULTS}")

def search_document(llm, chains, question: str, k: int = 5):
    """
    根据问题搜索相关文档
    
    Args:
        llm: 语言模型实例
        chains: 链实例
        question: 问题
        k: 返回的文档数量
        
    Returns:
        相关文档列表
    """
    logger.info(f"根据问题搜索文档: '{question}'")
    try:
        logger.info("调用LLM生成内容")
        content = llm.invoke(question).content
        logger.info("生成内容摘要")
        abstract_content = chains.ContentAbstract_chain(content_by_question=content)
        logger.info(f"查询向量库，k={k}")
        ans = query_vectordb(abstract_content, k, chains.model_provider, chains.model_name)
        logger.info(f"查询到 {len(ans)} 个相关文档")
        return ans
    except Exception as e:
        logger.error(f"搜索文档失败: {str(e)}")
        raise

def resCollection(chains, ans, question):
    """
    收集文档结果
    
    Args:
        chains: 链实例
        ans: 文档列表
        question: 问题
        
    Returns:
        处理后的结果和文件名列表
    """
    logger.info("收集文档结果")
    res_org = []
    fileNames = []
    pattern = r"^\d+"
    
    try:
        for i, doc in enumerate(ans):
            fileName = doc.metadata["FileName"]
            logger.info(f"处理文档 {i+1}/{len(ans)}: {fileName}")
            
            # 处理文件名，提取编号
            match = re.search(pattern, fileName)
            if match:
                filenum = match.group()
                url = f"https://xz.aliyun.com/t/{filenum}"
                fileNames.append(url)
                logger.info(f"生成URL: {url}")
            else:
                fileNames.append(fileName)
                logger.info(f"使用文件名: {fileName}")
                
            # 获取文档描述
            logger.info(f"获取文档描述: {fileName}")
            doc_description = chains.get_document_description_chain(fileName, question)
            res_org.append(doc_description)
            
        # 组合结果
        logger.info("组合结果")
        res_deal = ""
        for index, i in enumerate(res_org):
            res_deal += f"###参考答案{index + 1}" + "\n" + i.replace("\n", " ") + "\n"
            
        return res_deal, fileNames
    except Exception as e:
        logger.error(f"收集文档结果失败: {str(e)}")
        raise

def anaylzeResultByUrl(chains, llm, question, fileNames: list):
    """
    通过URL分析结果
    
    Args:
        chains: 链实例
        llm: 语言模型实例
        question: 问题
        fileNames: URL列表
        
    Returns:
        分析结果
    """
    logger.info(f"通过URL分析结果，URLs数量: {len(fileNames)}")
    res_org = []
    
    try:
        for i, fileName in enumerate(fileNames):
            logger.info(f"获取URL内容 {i+1}/{len(fileNames)}: {fileName}")
            content_page = documentScapy(fileName)
            
            logger.info(f"分析URL内容: {fileName}")
            chain = chains.analyzeResult_PromptTemplate | llm
            res = chain.invoke({"question": question, "contents": content_page}).content
            res_org.append(res)
            
        # 组合结果
        logger.info("组合URL分析结果")
        res_deal = ""
        for index, i in enumerate(res_org):
            res_deal += f"###参考答案{index + 1}" + "\n" + i.replace("\n", " ") + "\n"
            
        return res_deal
    except Exception as e:
        logger.error(f"通过URL分析结果失败: {str(e)}")
        raise

def anaylzeResult(chains, res_collection, question):
    """
    分析结果集
    
    Args:
        chains: 链实例
        res_collection: 结果集
        question: 问题
        
    Returns:
        分析结果
    """
    logger.info("分析最终结果")
    try:
        result = chains.analyze_chain(question=question, contents=res_collection)
        logger.info("分析完成")
        return result
    except Exception as e:
        logger.error(f"分析结果失败: {str(e)}")
        raise

def process_query(question: str, k: int = None, model_provider=None, model_name=None, store_type="local"):
    """
    处理查询
    
    Args:
        question: 查询问题
        k: 返回的相似文档数量，默认使用环境变量中的配置
        model_provider: 模型提供商，支持"gemini", "openai", "ollama"，默认使用环境变量中的配置
        model_name: 模型名称，默认使用环境变量中的配置
        store_type: 存储类型，"local"或"url"
    """
    # 使用环境变量默认值（如果参数未指定）
    k = k or DEFAULT_NUM_RESULTS
    model_provider = model_provider or DEFAULT_MODEL_PROVIDER
    
    logger.info(f"处理查询 - 问题: '{question}', 类型: {store_type}, 模型: {model_provider}/{model_name or '默认'}, k: {k}")
    
    try:
        # 获取模型和链
        logger.info("初始化LLM模型")
        llm = get_llm(model_provider, model_name)
        logger.info("初始化Chains")
        chains = Chains(model_provider, model_name)
        
        # 搜索相关文档
        logger.info("搜索相关文档")
        ans = search_document(llm, chains, question, k)
        
        # 获取结果
        logger.info("获取文档来源")
        _, fileNames = resCollection(chains, ans, question)
        
        # 根据存储类型选择处理方式
        if store_type == "url":
            logger.info("使用URL模式处理")
            res_collection = anaylzeResultByUrl(chains=chains, llm=llm, question=question, fileNames=fileNames)
        else:
            logger.info("使用本地模式处理")
            res_collection, _ = resCollection(chains, ans, question)
        
        # 分析结果
        logger.info("分析结果")
        res = anaylzeResult(chains, res_collection, question)
        
        # 输出结果
        logger.info("输出结果")
        print("参考来源:")
        for url in fileNames:
            print(f"- {url}")
        print("\n分析结果:")
        print(res)
        
        return res, fileNames
    except Exception as e:
        logger.error(f"处理查询失败: {str(e)}")
        print(f"处理查询失败: {str(e)}")
        raise

def local_store(question: str, k: int = None, model_provider=None, model_name=None):
    """使用本地存储处理查询"""
    logger.info("使用本地存储处理查询")
    return process_query(question, k, model_provider, model_name, "local")

def url_store(question: str, k: int = None, model_provider=None, model_name=None):
    """使用URL存储处理查询"""
    logger.info("使用URL存储处理查询")
    return process_query(question, k, model_provider, model_name, "url")

if __name__ == '__main__':
    try:
        logger.info("程序启动")
        parser = argparse.ArgumentParser(description='使用AI处理安全领域问题')
        parser.add_argument('--type', choices=['local', 'url'], help=f'选择存储类型: local或url')
        parser.add_argument('--question', type=str, help='要处理的问题')
        parser.add_argument('--num', type=int, help=f'返回的相似文档数量 (默认: {DEFAULT_NUM_RESULTS})')
        parser.add_argument('--update', type=str, help='要添加的PDF文件夹路径')
        parser.add_argument('--model', choices=['gemini', 'openai', 'ollama'], help=f'选择模型提供商: gemini, openai或ollama (默认: {DEFAULT_MODEL_PROVIDER})')
        parser.add_argument('--model_name', type=str, help='指定模型名称，默认使用.env中配置值')
        # 创建agent开放工具权限列表
        parser.add_argument('--call_function', choices=['SearchWeb', 'ReadWebPage', 'CVEQuery'], help='调用Agent执行的工具名，例如: SearchWeb, ReadWebPage, CVEQuery')

        args = parser.parse_args()
        logger.info(f"命令行参数: {args}")

        if args.type is not None:
            if not args.question: 
                error_msg = "错误: 必须提供--question参数"
                logger.error(error_msg)
                print(error_msg)
                parser.print_help()
                sys.exit(1)
                
            model_provider = args.model
            model_name = args.model_name
            
            logger.info(f"执行查询 - 类型: {args.type}, 模型: {model_provider or DEFAULT_MODEL_PROVIDER}/{model_name or DEFAULT_MODEL_NAME or '默认'}")
            
            match args.type:
                case 'url':
                    url_store(args.question, args.num, model_provider, model_name)
                case 'local':
                    local_store(args.question, args.num, model_provider, model_name)
        elif args.update is not None:
            model_provider = args.model
            model_name = args.model_name
            
            logger.info(f"更新向量库 - 路径: {args.update}, 模型: {model_provider or DEFAULT_MODEL_PROVIDER}/{model_name or DEFAULT_MODEL_NAME or '默认'}")
            update_vectordb(args.update, model_provider, model_name)
        # 实现agent工具调用功能
        elif args.call_function is not None:
            logger.info(f"调用Agent工具: {args.call_function}")
            agent = create_agent(
                tool_name=args.call_function,
                model_provider=args.model or DEFAULT_MODEL_PROVIDER,
                model_name=args.model_name or DEFAULT_MODEL_NAME
            )
            if not args.question:
                print("错误：使用 --call_function 时必须提供 --question 参数作为输入。")
                sys.exit(1)

            result = agent.run(args.question)
            print("Agent响应：", result)

        else:
            logger.info("未提供操作参数，显示帮助信息")
            parser.print_help()
    except Exception as e:
        logger.error(f"程序执行失败: {str(e)}")
        print(f"错误: {str(e)}")
        sys.exit(1)











