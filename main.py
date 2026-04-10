import random
from operator import add
from typing import TypedDict, Annotated, Literal
from pydantic import BaseModel, Field
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.graph import StateGraph, START, END

from dotenv import load_dotenv
load_dotenv()

# from langchain_openai import ChatOpenAI 
# llm = ChatOpenAI(model="gpt-5-mini") 

from langchain_groq import ChatGroq
llm = ChatGroq(model="openai/gpt-oss-20b")

# ==========================================
# 1. 상태 클래스 및 Pydantic 모델
# ==========================================
class GameState(TypedDict):
    player_name: str
    player_hp: int
    player_max_hp: int
    player_atk: int
    
    monster_name: str
    monster_hp: int
    monster_max_hp: int
    monster_atk: int

    stage_depth: int
    crossroads: int
    event_type: str  

    min_dice_num: int
    max_dice_num: int
    
    history: Annotated[list[str], add]

class CombatOutput(BaseModel):
    situation_category: Literal["critical_hit", "player_attack", "monster_attack", "player_defense"] = Field(description="전투 상황 카테고리")
    description: str = Field(description="주사위 결과에 따른 다이나믹한 전투 액션 묘사 (3-4문장)")


# ==========================================
# 2. 프롤로그 노드
# ==========================================
def prologue_node(state: GameState):
    start_message = """
======================================================
           🎲 M A S T E R   O F   D I C E 🎲           
======================================================
[상황 설정]
차갑고 축축한 지하 미궁의 입구. 
당신의 손에는 낡은 무기와 '20면체 주사위'뿐입니다.
5개의 층을 돌파하고 미궁의 주인을 쓰러뜨리십시오.
======================================================
"""
    print(start_message)
    player_name = input("용사님의 이름은 무엇인가요?: ")

    print(f"\n환영합니다, [{player_name}] 용사님. 전투 스테이지로 이동합니다.")
    print("행운을 빕니다.\n")
    
    return {
        "player_name": player_name,
        "player_hp": 50, "player_max_hp": 50, "player_atk": 10,
        "stage_depth": 0, 
        "min_dice_num": 1, "max_dice_num": 20,
        "history": [f"{player_name} 용사가 미궁에 입장했습니다."]
    }


# ==========================================
# 3. 맵 이동 (길잡이) 노드
# ==========================================
def map_move_node(state: GameState):

    depth = state.get('stage_depth', 1)
    if state.get('history'):
        depth += 1

    print(f"\n{'='*40}")
    print(f"      🏰 [ 지하 {depth}층 ]")
    print(f"{'='*40}")

    monster_list = ["고블린", "슬라임", "스켈레톤"]
    random_monster = random.choice(monster_list)

    # 기본 업데이트 세팅 
    updates = {
        "stage_depth": depth, # 계산된 층수 저장        
        "monster_name": random_monster,
        "monster_atk": 10, "monster_hp": 30, "monster_max_hp": 30
    }

    if depth == 1:
        print("미궁의 몬스터가 길을 막고 있습니다! (첫 전투)")
        updates["crossroads"] = 1 # 무조건 전투

    elif depth == 2:
        print("갈림길이 나왔습니다!")
        print("1. 전투 / 2. 수상한 우물 발견 (회복 이벤트)")
        select = int(input("1 또는 2 입력: "))
        updates["crossroads"] = select
        updates["event_type"] = "fountain" # 2층은 우물

    elif depth == 3:
        print("갈림길이 나왔습니다!")
        print("1. 전투 / 2. 화려한 보물상자 발견 (상자 이벤트)")
        select = int(input("1 또는 2 입력: "))
        updates["crossroads"] = select
        updates["event_type"] = "trap" # 3층은 상자

    elif depth == 4:
        print("최후의 전투에 앞서 안전한 휴식처를 발견했습니다!")
        updates["crossroads"] = 3 # 3: 휴식

    elif depth == 5:
        print("🔥 최후의 전투가 시작됩니다! 거대한 문이 열립니다...")
        updates["monster_name"] = "엘리트 " + random_monster # 보스는 엘리트 수식어
        updates["monster_atk"] = int(10 * 1.5) # 공격력 1.5배
        updates["monster_hp"] = int(30 * 1.5) # 체력 1.5배
        updates["monster_max_hp"] = int(30 * 1.5)
        updates["crossroads"] = 1 # 보스 전투

    return updates


# ==========================================
# 4. 전투 노드
# ==========================================
def combat_node(state: GameState):
    print(f"\n[{state['monster_name']} (HP: {state['monster_hp']}/{state['monster_max_hp']})] vs [{state['player_name']} (HP: {state['player_hp']}/{state['player_max_hp']})]")
    
    # 입력을 변수(player_action)에 저장합니다.
    player_action = input("어떤 행동을 하시겠습니까? (예: 칼로 힘껏 내리친다 / 엔터 시 기본 공격): ")
    
    # 엔터만 쳤을 경우를 대비한 기본값 설정
    if not player_action.strip():
        player_action = "무기를 꽉 쥐고 적을 향해 돌진한다."
        print(f"(기본 행동: {player_action})")
    
    dice = random.randint(state.get('min_dice_num', 1), state.get('max_dice_num', 20))
    
    # 파이썬 수학 판정 로직
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

    # 프롬프트에 '플레이어의 행동 선언'을 명확히 주입합니다.
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
    
    if current_monster_hp <= 0:
        print(f"\n🎉 해냈습니다! [{state['monster_name']}]을(를) 처치했습니다!")

    updates = {
        "player_hp": state['player_hp'] - p_dmg,
        "monster_hp": current_monster_hp,
        "history": [f"[{state['monster_name']} 전투] 행동: {player_action} (🎲{dice}) -> {res.description}"]
    }

    return updates

# ==========================================
# [ 이벤트 시스템: 데코레이터 및 함수 정의 ]
# ==========================================
C_dice = Literal['대실패','실패','성공','크리티컬']

def check_success(dice_num:int) -> C_dice:
    if 1 <= dice_num <= 5: return '대실패'
    if 6 <= dice_num <= 10: return '실패'
    if 11 <= dice_num <= 15: return '성공'
    if 16 <= dice_num <= 20: return '크리티컬'

def event_name(event_situation:str):
    def wrapper(func):
        func._situation = event_situation
        return func
    return wrapper

# 🪤 함정 이벤트
@event_name('화려한 보물상자에 장치된 함정 이벤트')
def trap_event_func(state: GameState, dice_word: str) -> tuple[str, dict]:
    event_result_map = {'대실패': -10, '실패': -5, '성공': 0, '크리티컬': 5}
    change_hp = event_result_map[dice_word]
    update = {'player_hp': state['player_hp'] + change_hp}

    if change_hp == 0: return '아무일도 없었다!', update
    elif change_hp > 0: return f'오히려 숨겨진 포션을 찾아 HP를 {change_hp} 회복했다.', update
    else: return f'함정에 당해 {change_hp} 피해를 입었다.', update

# ⛲ 우물 이벤트
@event_name('어두운 방 한가운데 있는 수상한 우물 이벤트')
def fountain_event_func(state: GameState, dice_word: str) -> tuple[str, dict]:
    event_result_map = {'대실패': -5, '실패': 0, '성공': 10, '크리티컬': 20}
    change_hp = event_result_map[dice_word]
    
    # 최대 체력 증가 로직 예시
    if dice_word == '크리티컬':
        return f'신성한 물입니다! 최대 HP가 10 증가하고 체력이 {change_hp} 회복되었습니다.', {'player_max_hp': state['player_max_hp'] + 10, 'player_hp': state['player_hp'] + change_hp}
    elif change_hp > 0:
        return f'상쾌한 물입니다. HP를 {change_hp} 회복했다.', {'player_hp': state['player_hp'] + change_hp}
    else:
        return f'썩은 물입니다. {change_hp} 피해를 입었다.', {'player_hp': state['player_hp'] + change_hp}


# ==========================================
# 5. 이벤트 노드
# ==========================================
def event_node(state: GameState):
    print("\n[ 미지의 방에 들어왔습니다. ]")
    
    # 현재 층에 맞춰 이벤트 지정 
    if state.get("event_type") == "fountain":
        event_func = fountain_event_func
    else:
        event_func = trap_event_func
        
    event_situation = getattr(event_func, '_situation', '알 수 없는 이벤트')

    recent_history = "\n".join(state['history'][-3:])

    # 1차 LLM 호출 (상황 생성)
    prompt = f'''당신은 TRPG 게임의 "탐험 이벤트 생성기"입니다.
    이전 상황 요약: {recent_history}
    
    ## 역할
    - 플레이어가 맞이하는 "{event_situation} 상황"만 생성합니다.
    - 결과, 판정, 피해, 성공 여부를 절대 포함하지 마세요.
    - 오직 "상황 묘사"까지만 수행하세요.
    - 반드시 한국어로 작성하며 3~6문장으로 구성하세요.
    - 플레이어의 선택을 유도하는 상황으로 끝내세요.
    '''

    res1 = llm.invoke([SystemMessage(content=prompt)])
    print(f"\n🎙️ GM: {res1.content}\n")

    human_action = input('당신의 행동: ')
        
    dice = random.randint(state.get('min_dice_num', 1), state.get('max_dice_num', 20))
    dice_word = check_success(dice)
    print(f"\n🎲 주사위 굴림: {dice} / 20 ➔ [{dice_word}]")

    change_str, update_dict = event_func(state, dice_word)

    # 2차 LLM 호출 (결과 서술)
    result_prompt = f'''
    당신은 TRPG 게임의 "탐험 이벤트 결과 처리 GM"입니다.
    
    ## 입력 정보
    - 직전 상황: {res1.content}
    - 플레이어 행동: {human_action}
    - 시스템 처리 결과: {change_str} (이 내용을 이야기에 자연스럽게 녹여서 서술하세요)
    - 주사위 판정: {dice_word}
    
    ## 출력 규칙
    - 4~8문장으로 사건 진행과 결과를 서술하세요.
    - 시스템 메시지("HP -3")를 그대로 출력하지 말고, 문장으로 풀어서 설명하세요.
    - 반드시 한국어로 작성하세요. (CRITICAL)
    '''

    res2 = llm.invoke([SystemMessage(content=result_prompt)])
    print(f"\n🎙️ GM: {res2.content}")
    print(f"(시스템 판정: {change_str})\n")

    return {
        **update_dict, 
        "history": [f"[탐험] {event_situation} -> {human_action} (🎲{dice}) -> {res2.content}"]
    }


# ==========================================
# 6. 휴식 노드
# ==========================================
def rest_node(state: GameState):
    print("\n" + "="*50)
    print("----- 4 stage ----- 평온한 휴식처에 도착했습니다.")
    print(f"[STAGE {state.get('stage_depth', 4)}] 화톳불의 안식처")
    print(f"현재 상태: {state.get('player_name', '용사')} (HP: {state.get('player_hp', 10)}/{state.get('player_max_hp', 20)})")
    print(f"현재 주사위 최소 눈금: {state.get('min_dice_num', 1)}")
    print("="*50)

    # 1. 올바른 입력을 받을 때까지 반복 (While 루프 적용)
    while True:
        print("\n당신의 선택을 기다립니다..")
        print("1. [휴식] 체력을 최대 체력의 절반만큼 회복합니다.")
        print("2. [주사위 강화] 10면체 주사위를 굴려 최소 눈금을 영구적으로 높입니다.")
        
        user_input = input("\n선택 (1 또는 2): ").strip()

        update_data = {}  
        narration = ""    

        # [휴식 선택]
        if user_input == "1" or "휴식" in user_input:
            recovery_amount = state.get('player_max_hp', 20) // 2
            current_hp = state.get('player_hp', 10)
            max_hp = state.get('player_max_hp', 20)
            
            update_hp = min(current_hp + recovery_amount, max_hp)
            actual_recovered = update_hp - current_hp

            update_data = {"player_hp": update_hp}
            narration = f"모닥불 옆에서 휴식을 취하여 체력을 {actual_recovered}만큼 회복했습니다."
            print(f"\n{narration}")
            break # 루프 탈출

        # [주사위 강화 선택]
        elif user_input == "2" or "강화" in user_input:
            update_roll = random.randint(1, 10)
            current_min_dice = state.get('min_dice_num', 1)
            
            print(f"\n당신의 운명을 시험하였습니다.... 결과: [🎲 {update_roll}]!")
            
            # 다운그레이드 방지 안전장치
            if update_roll > current_min_dice:
                update_min = update_roll
                narration = f"주사위에 신비한 힘이 깃듭니다! 이제 주사위의 최소 눈금이 {update_min}으로 강화되었습니다."
            else:
                update_min = current_min_dice
                narration = f"아쉽게도 눈금이 오르지 않았습니다. 주사위의 최소 눈금은 그대로 {update_min}입니다."

            update_data = {"min_dice_num": update_min}
            print(f"\n{narration}")
            break # 루프 탈출

        # [잘못된 입력]
        else:
            print("올바른 선택지를 입력해야 합니다. 다시 선택해 주세요.")


    # 2. LLM을 통한 네러티브 묘사 생성
    prompt = f"""
    당신은 판타지 TRPG의 게임 마스터입니다.
    현재 상황: {narration}
    플레이어 이름: {state.get('player_name', '용사')}

    위 상황을 플레이어의 성격이 느껴지도록 아주 생생하고 짧게 묘사해주세요.
    직접 플레이어에게 말을 거는 듯한 말투를 사용하세요.
    """
    
    response = llm.invoke(prompt).content
    print(f"\n🎙️ [GM]: {response}")

    # 3. 상태 업데이트 및 스테이지 매니저로 이동
    return {
            **update_data,
            "history": [f"[휴식처] {response}"],
        }

# ==========================================
# 7. 엔딩 노드
# ==========================================
def ending_node(state: GameState):
    print("\n" + "="*50)
    
    if state['player_hp'] < 1:
        # 배드 엔딩
        print("당신의 생명이 꺼져갑니다...\n"
              "당신은 자신의 운을 원망합니다.\n"
              "\"다시 태어난다면... 다음 기회가 있었다면...\"\n")

        print(f"💀 [{state['monster_name']}]에게 치명상을 입고 쓰러졌습니다!")
        print(f"지하 {state['stage_depth']}층에서 모험이 끝났습니다.")
        print("\n[ B A D   E N D I N G ]")

    else:
        # 해피 엔딩
        print("당신은 마지막 전투의 희열을 아직 만끽하고 있습니다.\n"
              "미궁의 주인이 쓰러지며, 굳게 닫혀있던 지상으로 향하는 문이 열립니다.\n"
              "따스한 빛이 당신을 감싸며 기나긴 악몽이 마침내 끝났음을 알립니다.\n")
        
        print(f"🎉 무사히 미궁의 끝(지하 {state['stage_depth']}층)을 돌파했습니다!")
        print(f"최종 남은 체력: {state['player_hp']} / {state['player_max_hp']}")
        print("\n[ H A P P Y   E N D I N G ]")
        
    print("="*50 + "\n")
    
    return state


# ==========================================
# 8. 라우터
# ==========================================
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
    


# ==========================================
# 9. 노드 및 엣지 설정
# ==========================================
builder = StateGraph(GameState)

# 1. 노드 등록 (이름표 달아주기)
builder.add_node("prologue", prologue_node)
builder.add_node("map_move", map_move_node)
builder.add_node("combat", combat_node)
builder.add_node("event", event_node)
builder.add_node("rest", rest_node)          
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

graph = builder.compile()

# 실행 테스트
if __name__ == "__main__":
    initial_state = {}
    final_state = graph.invoke(initial_state, config={"recursion_limit": 50})

