import random
from state_types import GameState, CombatOutput
from llm import get_llm

# ==========================================
# 4. 전투 노드
# ==========================================
def combat_node(state: GameState):
    print(f"\n[{state['monster_name']} (HP: {state['monster_hp']}/{state['monster_max_hp']})] vs [{state['player_name']} (HP: {state['player_hp']}/{state['player_max_hp']})]")
    
    # [수정 포인트 1] 입력을 변수(player_action)에 저장합니다.
    player_action = input("어떤 행동을 하시겠습니까? (예: 칼로 힘껏 내리친다 / 엔터 시 기본 공격): ")
    
    # 엔터만 쳤을 경우를 대비한 기본값 설정
    if not player_action.strip():
        player_action = "무기를 꽉 쥐고 적을 향해 돌진한다."
        print(f"(기본 행동: {player_action})")
    
    dice = random.randint(state.get('min_dice_num', 1), state.get('max_dice_num', 20))
    
    # 파이썬 수학 판정 로직 (기존과 동일)
    p_dmg, m_dmg = 0, 0
    if dice <= 5:
        category = "monster_attack (대실패)"
        p_dmg = state['monster_atk']
    elif dice <= 10:
        category = "player_defense (실패/아쉬운 타격)"
        p_dmg = int(state['monster_atk'] * 0.5)
    elif dice <= 15:
        category = "player_attack (유효타)"
        m_dmg = state['player_atk']
    else:
        category = "critical_hit (크리티컬!)"
        m_dmg = int(state['player_atk'] * 1.5)

    # [수정 포인트 2] 프롬프트에 '플레이어의 행동 선언'을 명확히 주입합니다.
    llm = get_llm()
    structured_llm = llm.with_structured_output(CombatOutput)
    prompt = f"""
    당신은 TRPG GM입니다. 
    플레이어: {state['player_name']}
    몬스터: {state['monster_name']}
    
    [이번 턴의 정보]
    플레이어의 행동 선언: "{player_action}"
    시스템 주사위 판정: {dice} -> 결과: {category}
    
    위 정보를 바탕으로 두 캐릭터의 격동적인 전투 장면을 묘사하세요.
    반드시 플레이어가 선언한 행동("{player_action}")을 문맥에 녹여내고, 
    그 행동이 주사위 결과({category})에 따라 어떻게 빗나갔는지, 막혔는지, 혹은 치명상을 입혔는지 다이나믹하게 풀어내세요.
    """
    res = structured_llm.invoke(prompt)

    print(f"\n🎲 주사위: {dice} -> {category}")
    print(f"🎙️ GM: {res.description}")
    print(f"(적 체력 변화: -{m_dmg} / 내 체력 변화: -{p_dmg})")

    current_monster_hp = state['monster_hp'] - m_dmg
    
    updates = {
        "player_hp": state['player_hp'] - p_dmg,
        "monster_hp": current_monster_hp,
        "history": [f"[{state['monster_name']} 전투] 행동: {player_action} (🎲{dice}) -> {res.description}"]
    }

    return updates