from langgraph.graph import StateGraph, START, END

from node import *
from event import *
from state_types import GameState
from graph_route import route_from_combat, route_from_map

builder = StateGraph(GameState)

# 1. 노드 등록 (이름표 달아주기)
builder.add_node("prologue", prologue_node)
builder.add_node("map_move", map_move_node)
builder.add_node("combat", combat_node)
builder.add_node("event", event_node)
builder.add_node("rest", rest_node)          # 팀원 합류 예정
builder.add_node("ending", ending_node)

# 2. 일반 엣지 연결 (무조건 다음으로 넘어가는 선)
builder.add_edge(START, "prologue")
builder.add_edge("prologue", "map_move")
# 이벤트나 휴식이 끝나면 다시 맵 탐색으로 돌아감
builder.add_edge("event", "map_move")
builder.add_edge("rest", "map_move")
builder.add_edge("ending", END)

# 3. 조건부 엣지 연결 (상황에 따라 갈림길이 생기는 선)
# (출발 노드, 판단 함수, {함수결과: "도착할_노드명"})
builder.add_conditional_edges(
    "map_move", 
    route_from_map,
    {
        "combat": "combat",
        "event": "event",
        "rest": "rest"
    }
)

builder.add_conditional_edges(
    "combat",
    route_from_combat,
    {
        "ending": "ending",
        "map_move": "map_move",
        "combat": "combat" # 루프 (계속 싸움)
    }
)

# ==========================================
# [ 그래프 컴파일 및 실행부 ]
# ==========================================
graph = builder.compile()

# 실행 테스트
if __name__ == "__main__":
    initial_state = {}
    final_state = graph.invoke(initial_state, config={"recursion_limit": 50})

