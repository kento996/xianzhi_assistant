# src/tools/my_tools.py

from langchain.tools import Tool
import requests
from bs4 import BeautifulSoup


# 网络搜索工具函数
def search_web(query: str) -> str:
    """
    使用 DuckDuckGo 进行简单搜索。
    """
    try:
        url = f"https://duckduckgo.com/html/?q={query}"
        headers = {
            "User-Agent": "Mozilla/5.0"
        }
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code == 200:
            return f"已搜索: “{query}”，请访问 DuckDuckGo 查看结果。\n{url}"
        else:
            return f"搜索失败，状态码: {response.status_code}"
    except Exception as e:
        return f"搜索出错: {str(e)}"
    
# 网页抓取工具函数
def read_web_page(url: str) -> str:
    """
    读取网页内容，返回纯文本（用于分析）。
    """
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')

        # 提取正文文本
        text = soup.get_text(separator="\n")
        cleaned = '\n'.join(line.strip() for line in text.splitlines() if line.strip())

        return cleaned[:3000]  # 限制长度，避免太长（LangChain限制输入）
    except Exception as e:
        return f"抓取失败: {str(e)}"
    
# CVE 查询工具函数
def query_cve(cve_id: str) -> str:
    """
    查询 CVE 详情。
    使用 CIRCL CVE API: https://cve.circl.lu/api/cve/{CVE-ID}
    """
    try:
        api_url = f"https://cve.circl.lu/api/cve/{cve_id.upper()}"
        response = requests.get(api_url, timeout=10)
        
        if response.status_code != 200:
            return f"查询失败，状态码: {response.status_code}"

        data = response.json()
        if "summary" not in data:
            return "未找到该 CVE 的信息"

        summary = data.get("summary", "无描述")
        cvss = data.get("cvss", "无评分")
        references = data.get("references", [])
        ref_str = "\n".join(references[:5]) if references else "无参考链接"

        return (
            f"🛡️ CVE编号: {cve_id.upper()}\n"
            f"📄 简要描述: {summary}\n"
            f"📊 CVSS评分: {cvss}\n"
            f"🔗 参考链接:\n{ref_str}"
        )

    except Exception as e:
        return f"查询失败: {str(e)}"

# 工具字典，可扩展更多
TOOL_MAP = {
    "SearchWeb": Tool.from_function(
        func=search_web,
        name="SearchWeb",
        description="用于互联网搜索，比如查找最新漏洞资讯。输入应为自然语言问题。"
    ),
    "ReadWebPage": Tool.from_function(
        func=read_web_page,
        name="ReadWebPage",
        description="读取网页并提取正文，用于分析指定URL的内容。输入应为网页URL。"
    ),
    "CVEQuery": Tool.from_function(
        func=query_cve,
        name="CVEQuery",
        description="查询指定 CVE 编号的详细信息，包括描述、评分、参考链接。输入应为合法的 CVE ID。"
    )
}
