import argparse
import re

from src.chains import Chains_Gemini
from src.llm import get_gemini_pro
from src.utils import documentScapy
from src.vectorstore import query_vectordb, update_vectordb


def search_document(llm,chains,question:str,k:int=5):
    content = llm.invoke(question).content
    abstract_content = chains.ContentAbstract_chain(content_by_question=content)
    ans=query_vectordb(abstract_content,k)
    return ans

def resCollection(chains,ans,question):
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

def anaylzeResultByUrl(chains,llm,question,fileNames:list):
    res_org=[]
    for fileName in fileNames:
        content_page=documentScapy(fileName)
        chain=chains.analyzeResult_PromptTemplate | llm
        res=chain.invoke({"question":question,"contents":content_page}).content
        res_org.append(res)
    res_deal = ""
    for index, i in enumerate(res_org):
        res_deal += f"###参考答案{index + 1}" + "\n" + i.replace("\n", " ") + "\n"
    # print(res_deal)
    return res_deal

def anaylzeResult(chains,res_collection,question):
    return chains.analyze_chain(question=question,contents=res_collection)

def local_store(question:str,k:int=5):
    llm = get_gemini_pro()
    chains = Chains_Gemini()
    ans = search_document(llm, chains, question, k)
    res_collection, fileNames = resCollection(chains, ans,question)
    res = anaylzeResult(chains, res_collection, question)
    print(fileNames)
    print(res)

def url_store(question:str,k:int=5):
    llm = get_gemini_pro()
    chains = Chains_Gemini()
    ans = search_document(llm, chains, question, k)
    _, fileNames = resCollection(chains, ans,question)
    res_collection=anaylzeResultByUrl(chains=chains,llm=llm,question=question,fileNames=fileNames)
    res = anaylzeResult(chains, res_collection, question)
    print(fileNames)
    print(res)



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process questions and store them locally or via URL')
    parser.add_argument('--type', choices=['local', 'url'], help='Choose storage type: local or url')
    parser.add_argument('--question', type=str, help='Question to store')
    parser.add_argument('--num', type=int, default=5, help='Number (default: 5)')
    parser.add_argument('--update', type=str, help='Enter the pdf folder you want to add')

    args = parser.parse_args()

    if args.type !=None:
        match args.type:
            case 'url':
                url_store(args.question, args.num)
            case 'local':
                local_store(args.question, args.num)
    elif args.type == None:
        update_vectordb(args.update)











