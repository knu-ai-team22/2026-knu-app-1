
from typing import TypedDict, Annotated, Literal
from operator import add
import random

from pydantic import BaseModel, Field
from langchain.agents import create_agent
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.tools import tool
from chat_model import get_llm

class GameState(TypedDict):
    player_hp: int
    player_max_hp: int
    monster_hp: int
    monster_name: list[str]
    stage_depth: int
    min_dice_num: int
    history: Annotated[list[str], add]

C_dice = Literal['대실패','실패','성공','크리티컬']

def check_success(dice_num:int)->C_dice:
    if 1 <= dice_num <= 5:
        return '대실패'

    if 6 <= dice_num <= 10:
        return '실패'

    if 11 <= dice_num <= 15:
        return '성공'

    if 16 <= dice_num <= 20:
        return '크리티컬'


def event_name(event_situation:str):
    def wrapper(func):
        func._situation = event_situation
        return func
    return wrapper


@event_name('함정 이벤트')
def trap_event_func(state:GameState, dice_word:str)->tuple[str, GameState]:
    event_result_map = {
        '대실패':-3,
        '실패':-1,
        '성공':0,
        '크리티컬':2
    }
    change_hp = event_result_map[dice_word]
    update:GameState = {
        'player_hp':state['player_hp'] + change_hp
    }

    if change_hp == 0:
        return '아무일도 없었다!', update
    elif change_hp > 0:
        return f'HP를 {change_hp} 회복했다.', update
    else:
        return f'{change_hp} 피해를 입었다.', update


def exploration_node(state:GameState)->GameState:

    event_func = trap_event_func
    event_situation = getattr(event_func, '_situation', None)

    prompt = f'''당신은 TRPG 게임의 "탐험 이벤트 생성기"입니다.
    ## 역할
    - 플레이어가 맞이하는 "{event_situation} 상황"만 생성합니다.
    - 결과, 판정, 피해, 성공 여부를 절대 포함하지 마세요.
    - 오직 "상황 묘사"까지만 수행하세요.

    ## 출력 규칙
    - 반드시 한국어로 작성하세요.
    - 3~6문장으로 구성하세요.
    - 플레이어의 선택을 유도하는 상황으로 끝내세요.
    - 수치(HP 변화, 데미지 등)는 절대 언급하지 마세요.
    - GM처럼 분위기와 긴장감을 살려 묘사하세요.

    ## 금지 사항
    - "성공", "실패", "피해", "회복" 같은 결과 표현 금지
    - 주사위 결과를 추측하거나 암시 금지

    ## 목표
    - 플레이어가 행동을 입력하고 싶어지도록 만드는 것

    {event_situation}를 생성하세요.
    '''

    llm = get_llm()

    res1 = llm.invoke([
        *state['history'],
        SystemMessage(prompt),
    ])

    print(res1.content)

    human_message = HumanMessage(content=input('당신의 행동: '))

    dice = random.randint(1, 20)
    dice_word = check_success(dice)

    print(f'주사위 결과: {dice} / 20 | {dice_word}')

    change_str, update = event_func(state, dice_word)

    result_prompt = f'''
    당신은 TRPG 게임의 "탐험 이벤트 결과 처리 GM"입니다.

    ## 역할
    - 이전에 생성된 함정 상황과 플레이어의 행동을 바탕으로
      최종 결과를 서술합니다.

    ## 입력 정보
    - 변경사항: {change_str}
    - 주사위 결과: {dice} / 20 | {dice_word}

    ## 출력 규칙
    - 반드시 한국어로 작성하세요.
    - 4~8문장으로 서술하세요.
    - "플레이어의 행동 → 사건 진행 → 결과" 흐름을 따르세요.
    - 주사위 결과에 맞게 자연스럽게 서술하세요.
    - 변경사항을 반드시 이야기 속에 녹여서 표현하세요 (직접 문장으로 풀어서)

    ## 주사위 해석 가이드
    - 대실패: 상황이 크게 악화됨
    - 실패: 부분적으로 실패, 손해 발생
    - 성공: 의도한 행동이 무난히 성공
    - 크리티컬: 매우 유리하게 상황 해결

    ## 금지 사항
    - "HP -3" 같은 시스템 메시지 그대로 출력 금지
    - 메타 발언 금지 (예: "주사위 결과는...")
    - 설명체 금지 (항상 서술형)

    ## 목표
    - 플레이어가 실제 TRPG를 플레이하는 느낌을 받게 하는 것
    '''

    res2 = llm.invoke([
        *state['history'],
        res1,
        human_message,
        SystemMessage(result_prompt),
        SystemMessage(change_str)
    ])

    print(res2.content)
    print(change_str)

    return {
        **update,
        'history':list(map(lambda x: x.content,[res1, human_message, res2]))
    }

