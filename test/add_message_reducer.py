from typing import Annotated, TypedDict, List

from langgraph.graph import StateGraph, START, END

from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage, HumanMessage

from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()

model = ChatGroq(
    model="openai/gpt-oss-20b",
)

class MessageStatement(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]

def chat_node(state:MessageStatement) -> dict:

    conversation_history = state["messages"]
    response = model.invoke(conversation_history)

    return {
        "messages": response
    }

graph = StateGraph(MessageStatement)

graph.add_node(chat_node)

graph.add_edge(START, "chat_node")
graph.add_edge("chat_node", END)

agent = graph.compile()

message_1 = HumanMessage(content="안녕하세요! 제 이름은 큰웅이에요!")

result = agent.invoke({
    "messages": message_1
})

print("첫 번째 호출")
for msg in result["messages"]:
    print(f'[{msg.type}] {msg.content}')

print()

message_2 = HumanMessage(content="제 이름은 뭐일까요?")

result2 = agent.invoke({
    "messages": result["messages"] + [message_2]
})

print("두 번째 호출")
for msg in result2["messages"]:
    print(f'[{msg.type}] {msg.content}')