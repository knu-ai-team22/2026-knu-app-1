
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

class EventModel(BaseModel):
    change_hp:int = Field('')


def exploration_node(state:GameState)->GameState:
    prompt = f'''
    당신은 TRPG를 위한 GM중 탐험 이벤트 모듈입니다.
    반드시 한국어로 대답하세요.
    반드시 아래 사항을 지켜 실감나게 상황을 묘사하세요.


    '''

    llm = get_llm()

    res1 = llm.invoke([
        SystemMessage(prompt),
        SystemMessage('함정 이벤트를 생성하여 묘사하세요.')
    ])

    print(res1.content)

    human_message = HumanMessage(content=input('당신의 행동: '))

    dice = random.randint(1, 20)
    dice_word = check_success(dice)

    change_str = change_by_trap_event(state, dice_word)

    result_prompt = f'''
    당신은 TRPG를 위한 GM중 탐험 이벤트 모듈입니다.
    반드시 한국어로 대답하세요.
    반드시 아래 사항을 지켜 실감나게 상황을 묘사하세요.

    변경사항: {change_str}

    주사위 결과: {dice} / 20 | {dice_word}
    '''

    SystemMessage()


def change_by_trap_event(state:GameState, dice_word:str)->str:
    change_hp = 0
    if dice_word == '대실패':
        change_hp = -3
        return ''

    if dice_word == '실패':
        change_hp = -1
        return ''

    if dice_word == '성공':
        change_hp = 0

    if dice_word == '대성공':
        change_hp = 2

    if change_hp == 0:
        return '아무일도 없었다!'
    elif change_hp > 0:
        return f'HP를 {change_hp} 회복했다.'
    else:
        return f'{change_hp} 피해를 입었다.'





'''
예시:

함정 이벤트
"무슨 함정에 걸렸다 같은 상황을 생성" O

정보 이벤트
"어디에 뭐가 있더라 같은 정보를 말하는 NPC와의 만남" O

구출 이벤트
"상처입고 도망가는 NPC를 만나는 이벤트"

1~5: 대실패 (공격이 빗나가고 반격당함. 내 체력 -5)
6~10: 아쉬운 타격 (내 공격은 막히고, 적의 공격 허용. 내 체력 -3)
11~15: 유효타 (적에게 피해를 줌. 적 체력 -5)
16~20: 크리티컬 (약점 공격 성공! 적 체력 -10)

'''

