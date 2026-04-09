from exploration_event_node import exploration_node, GameState
from langgraph.graph import StateGraph, START, END


builder = StateGraph(GameState)

builder.add_node('exploration', exploration_node)

builder.add_edge(START, 'exploration')
builder.add_edge('exploration', END)

graph = builder.compile()

state = GameState(
    player_hp=10,
    player_max_hp=10,
    monster_hp=0,
    monster_name=[],
    stage_depth=0,
    min_dice_num=0,
    history=[],
)

graph.invoke(state)