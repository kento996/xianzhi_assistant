import re

from src.chains import Chains_Gemini
from src.llm import get_gemini_pro
from src.vectorstore import query_vectordb

def search_document(llm,chains,question:str,k:int=5):
    content = llm.invoke(question).content
    abstract_content = chains.ContentAbstract_chain(content_by_question=content)
    ans=query_vectordb(abstract_content,k)
    return ans

def resCollection(chains,ans):
    res_org = []
    fileNames=[]
    pattern = r"^\d+"
    for i in ans:
        fileName = i.metadata["FileName"]
        filenum=re.match(pattern, fileName).group()
        fileNames.append(f"https://xz.aliyun.com/t/{filenum}")
        res_org.append(chains.get_document_description_chain(fileName, question))
    res_deal = ""
    for index, i in enumerate(res_org):
        res_deal += f"###参考答案{index + 1}" + "\n" + i.replace("\n", " ") + "\n"
    return res_deal,fileNames

def anaylzeResult(chains,res_collection,question):
    return chains.analyze_chain(question=question,contents=res_collection)

if __name__ == '__main__':
    question="k8s存在哪些漏洞"
    llm=get_gemini_pro()
    chains = Chains_Gemini()
    ans = search_document(llm,chains,question, k=5)
    res_collection,fileNames= resCollection(chains, ans)
    res=anaylzeResult(chains,res_collection,question)
    print(fileNames)
    print(res)





