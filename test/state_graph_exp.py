# Typed Dict 기반 상태
from typing import TypedDict


class TypedDictState(TypedDict):
    query: str
    answer: str


# PydanticModel 기반 상태
from pydantic import BaseModel


class PydanticState(BaseModel):
    query: str
    answer: str = ""


# dataclass 기반 상태
from dataclasses import dataclass


@dataclass
class DataclassState:
    query: str
    answer: str = ""


from langgraph.graph import StateGraph

builder1 = StateGraph(TypedDictState)
builder2 = StateGraph(PydanticState)
builder3 = StateGraph(DataclassState)