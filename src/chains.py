import os

from langchain_core.prompts import PromptTemplate

from src.constants import XIANZHI_DOCUMENT_DIR
from src.llm import get_gemini_pro
from src.utils import get_pdf_text, get_text_chunks


class Chains_Gemini:
    llm=get_gemini_pro()
    contentAbstractPrompt = """请对分析如下文档并完成以下任务：
                                    1. 分析文档的主题和内容
                                    2. 用一段话概括文档
                                    ## 文档
                                    ```
                                    {content_by_question}
                                    ```
                                    ## 注意
                                    你的输出结果是包含文档主题和内容的一段话"""
    contentAbstract_PromptTemplate = PromptTemplate(template=contentAbstractPrompt,
                                    input_variables=["content_by_question"])

    signalAnswerPrompt="""你是一位网络安全专家，请你完成如下任务：
    1. 分析如下安全问题
    2. 根据如下的相关文档知识回答问题
    ##问题
    {question}
    ##相关文档
    {contents}
    ##注意
    如果你觉得相关文档没用时，请你根据你自己的知识回答问题"""
    signalAnswer_PromptTemplate = PromptTemplate(template=signalAnswerPrompt,
                                    input_variables=["question","contents"])

    analyzeResultPrompt="""你是一位网络安全专家，请你完成如下任务：
    1. 分析如下安全问题
    2. 对如下的参考答案进行分析
    3. 根据有用的参考答案回答问题
    ##问题
    {question}
    ##参考内容
    {contents}"""
    analyzeResult_PromptTemplate = PromptTemplate(template=analyzeResultPrompt,
                                                 input_variables=["question", "contents"])


    def ContentAbstract_chain(self,content_by_question):
        llm=self.llm
        chain=self.contentAbstract_PromptTemplate | llm
        return chain.invoke({"content_by_question":content_by_question}).content

    def get_document_description_chain(self,filename,question):
        llm = self.llm
        chain = self.signalAnswer_PromptTemplate | llm
        ctf_folder = XIANZHI_DOCUMENT_DIR
        pdf_path = os.path.join(ctf_folder, filename)
        try:
            raw_text = get_pdf_text(pdf_path)
            text_chunks = get_text_chunks(raw_text)
        except Exception as e:
            raise e
        contents = ""
        for index, text in enumerate(text_chunks):
            contents += str(index + 1) + "." + text.replace("\n", " ") + "\n"
        return chain.invoke({"question":question,
                             "contents":contents}).content

    def analyze_chain(self,question,contents):
        llm = self.llm
        chain=self.analyzeResult_PromptTemplate | llm
        return chain.invoke({"question":question,
                             "contents":contents}).content




