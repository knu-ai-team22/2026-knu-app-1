from typing import TypedDict, List, Annotated

from langgraph.graph import StateGraph, START, END

def append_step_count(curr: int, new: int) -> int:
    return curr + new

class TypedDictWithReducer(TypedDict):
    messages: List[str]
    step_count: Annotated[int, append_step_count]
    private_data: str | None

def node_a(state):
    print("Node A 시작!")
    return {
        "messages": ["첫 번째 노드 호출 완료"],
        "step_count": 1
    }


def node_b(state):
    print("Node B 시작!")

    if isinstance(state, dict):
        step_count = state["step_count"]
    else:
        step_count = state.step_count

    print(f"상태로부터 확인한 현재 스텝 카운트: {step_count}")

    return {
        "messages": ["두 번째 노드 호출 완료"],
        "step_count": 1
    }

graph = StateGraph(TypedDictWithReducer)

graph.add_node(node_a)
graph.add_node(node_b)

graph.add_edge(START, "node_a")
graph.add_edge("node_a", "node_b")
graph.add_edge("node_b", END)

agent = graph.compile()

final_state = agent.invoke({
    "messages": [],
    "step_count": 0,
    "private_data": ""
})