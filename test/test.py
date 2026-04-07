from typing import TypedDict

class TypedDictStats(TypedDict):
    query: str
    answer: str

from pydantic import BaseModel

class PydamticState(BaseModel):
    query: str
    answer: str

from dataclasses import dataclass

@dataclass
class DataClassState:
    query: str
    answer: str

    