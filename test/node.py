from langgraph.graph import StateGraph
from typing import TypedDict, List

class Statement(TypedDict):
    messages: List[str]

builder = StateGraph(Statement)


def say_hello(state: Statement):
    print("say_hello 노드 실행!")
    return {
        "messages": ["Hello!"]
    }


def say_world(state: Statement):
    print("say_world 노드 실행!")
    return {
        "messages": [" World!"]
    }

builder.add_node("hello_node", say_hello)

builder.add_node("world_node", say_world)