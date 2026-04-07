from typing import TypedDict

class TypedDictStats(TypedDict):
    query: str
    answer: str


from langgraph.graph import StateGraph

builder = StateGraph(TypedDictStats)

    