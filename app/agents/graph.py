from os import grantpt

from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage

from langgraph.graph import StateGraph, START, END, MessagesState

from langgraph.prebuilt import ToolNode, tools_condition

from app.agents.tools import tools

llm = ChatOllama(
    model= "gpt-oss:20b",
    temperature=0
)

llm_with_tools = llm.bind_tools(tools)

SYSTEM_PROMPT = """
You are a helpful customer support agent.

Use available tools when you need order information.
Never invent order details.
Always answer based on actual tool results.
"""

async def call_model(state: MessagesState):
    messages = [
    SystemMessage(content=SYSTEM_PROMPT),
    *state["messages"],
]

    response = await llm_with_tools.ainvoke(messages)

    return {"messages": [response]}




workflow = StateGraph(MessagesState)

workflow.add_node("agent", call_model)
workflow.add_node("tools", ToolNode(tools))

workflow.add_edge(START, "agent")
workflow.add_conditional_edges(
    "agent", 
    tools_condition,
    {
        "tools" : "tools",
        END: END
    }             
    )

workflow.add_edge("tools", "agent")

agent_gpaph = workflow.compile()

async def run_agent(user_message: str) -> str:
    result = await agent_gpaph.ainvoke(
        {
            "messages": [
                HumanMessage(content=user_message)
            ]
        }
    )

    return result["messages"][-1].content