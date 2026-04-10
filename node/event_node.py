import random
from state_types import GameState
from llm import get_llm

from typing import Literal
from langchain_core.messages import SystemMessage

# ==========================================
# [ 이벤트 시스템: 데코레이터 및 함수 정의 ]
# ==========================================

def check_success(dice_num:int) -> Literal['대실패','실패','성공','크리티컬']:
    if 1 <= dice_num <= 5: return '대실패'
    if 6 <= dice_num <= 10: return '실패'
    if 11 <= dice_num <= 15: return '성공'
    if 16 <= dice_num <= 20: return '크리티컬'

_event_map = {}
def event_name(event_situation:str):
    def wrapper(func):
        func._situation = event_situation 
        _event_map[func.__name__] = func
        return func
    return wrapper

# ==========================================
# [ 핵심 탐험 노드 (수정본: 층수 증가 및 한국어 고정) ]
# ==========================================
def event_node(state: GameState):
    print("\n[ 미지의 방에 들어왔습니다. ]")
    
    # 랜덤이 아니라 현재 층에 맞춰 이벤트 지정 (수정된 로직)
    if state.get("event_type") == "fountain":
        event_func = _event_map['fountain_event_func']
    else:
        event_func = _event_map['trap_event_func']
        
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
    llm = get_llm()
    res1 = llm.invoke([SystemMessage(content=prompt)])
    print(f"\n🎙️ GM: {res1.content}\n")

    human_action = input('당신의 행동: ')
        
    dice = random.randint(state.get('min_dice_num', 1), state.get('max_dice_num', 20))
    dice_word = check_success(dice)
    print(f"\n🎲 주사위 굴림: {dice} / 20 ➔ [{dice_word}]")

    change_str, update_dict = event_func(state, dice_word)

    # 2차 LLM 호출 (결과 서술) - [수정] 한국어 강제 옵션 추가!
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