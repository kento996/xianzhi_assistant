# src/agent.py

from langchain.agents import initialize_agent, AgentType
from src.llm import get_llm
from src.AgentTools import TOOL_MAP

def create_agent(tool_name: str, model_provider="gemini", model_name=None):
    """
    创建只包含指定工具的 Agent。
    """
    if tool_name not in TOOL_MAP:
        raise ValueError(f"未知工具名: {tool_name}")

    llm = get_llm(model_provider, model_name)
    tools = [TOOL_MAP[tool_name]]

    agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
    )

    return agent
