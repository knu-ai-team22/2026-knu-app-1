from state_types import GameState

def route_from_map(state: GameState):
    crossroads = state.get("crossroads", 1)
    
    if crossroads == 1:
        return "combat"     # 전투 돌입
    elif crossroads == 2:
        return "event"      # 랜덤 이벤트 돌입 (상인 제외)
    elif crossroads == 3:
        return "rest"       # 휴식처 진입
    else:
        return "combat"
    

def route_from_combat(state: GameState):
    if state["player_hp"] <= 0:
        return "ending"
    
    elif state["monster_hp"] <= 0:
        # 현재 5층 보스를 잡았다면 엔딩으로
        if state.get("stage_depth") == 5:
            return "ending"
        else:
            return "map_move"
            
    else:
        return "combat"