from typing import TypedDict, List
from langgraph.graph import StateGraph


class Statement(TypedDict):
    messages: List[str]

builder = StateGraph(Statement)


def say_hello():
    pass