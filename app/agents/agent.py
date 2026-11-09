import json

from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage

from app.agents.tools import tools, tools_by_name

llm = ChatOllama(
    model= "gpt-oss:20b",
    temperature=0
)

llm_with_tools = llm.bind_tools(tools)

async def run_agent(user_message: str) -> str:
    messages = [
        SystemMessage(
            content=(
                "You are a helpful customer support agent. "
                "Use available tools when you need order information. "
                "Never invent order details. "
                "Answer based on actual tool results."
            )
        ),
        HumanMessage(content=user_message)
    ]

    for _ in range(5):
        response = await llm_with_tools.ainvoke(messages)

        # Add the LLM response to conversation history
        messages.append(response)

        # No tool calls means the agent has finished
        if not response.tool_calls:
            return response.content

        # Execute requested tools
        for tool_call in response.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            tool_call_id = tool_call["id"]

            selected_tool = tools_by_name.get(tool_name)

            if selected_tool is None:
                result = {"error": "Unknown tool"}
            else:
                try:
                    result = await selected_tool.ainvoke(tool_args)
                except Exception as exc:
                    result = {"error": str(exc)}
            messages.append(
                ToolMessage(
                    content=json.dumps(result, default=str),
                    tool_call_id = tool_call_id
                )
            )
    return "I couldn't complete your request. Please try again."