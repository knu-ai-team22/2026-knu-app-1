from pydantic import BaseModel, Field
from typing import TypedDict, List, Annotated, Literal, Union
from operator import add
from langchain_core.messages import BaseMessage, SystemMessage, AIMessage, HumanMessage
from langchain_core.tools import tool
from langgraph.graph import StateGraph, START, END
from langgraph.types import Command

from chat_model import get_llm
import random

class CharactorState(TypedDict):
    name:str
    desc:str
    hp:int
    max_hp:int
    stat:'StatState'

class StatState(TypedDict):
    strength:List[int]
    agility:List[int]
    dexterity:List[int]
    speech:List[int]

def charactor_info(char_state:CharactorState)->str:
    stat = char_state['stat']
    info = [
    f"이름: {char_state['name']}",
    f"배경설정: {char_state['desc']}",
    f"HP: {char_state['hp']}/{char_state['max_hp']}",
    "-능력치 주사위-",
    "근력:\t[%d~%d] + %d" % tuple(stat['strength']),
    "민첩:\t[%d~%d] + %d" % tuple(stat['agility']),
    "손재주:\t[%d~%d] + %d" % tuple(stat['dexterity']),
    "화술:\t[%d~%d] + %d" % tuple(stat['speech']),
    ]
    return '\n'.join(info)


class MainState(TypedDict):
    history:Annotated[List[BaseMessage], add]
    player:CharactorState
    enemies:List[CharactorState]
    event:Literal['start', 'explore', 'rest', 'combat']
    dice_category:str
    last_dice:int


def dice_roll(start:int, end:int)->int:
    '''
    주사위를 던져 입력된 범위 내(start <= x <= end)의 무작위 값을 얻습니다.
    
    Args:
        start (int): 무작위로 나올 수 있는 최소 주사위 값
        end (int): 무작위로 나올 수 있는 최대 주사위 값
    
    Returns:
        int: 무작위로 결정된 범위내 정수
    '''

    return random.randint(start, end)


def explanation_node(state:MainState)->Command:
    event = state['event']

    event_desc = {
        'combat': '전투 상황입니다. 긴장감과 위험을 강조하세요.',
        'rest': '휴식 상황입니다. 안정감과 회복 분위기를 강조하세요.',
        'explore': '탐험 상황입니다. 새로운 발견과 선택지를 강조하세요.'
    }

    enemies_info = [charactor_info(enemy) for enemy in state['enemies']]

    prompt = f'''
    당신은 TRPG를 위한 GM 중에서도 묘사 에이전트입니다.
    반드시 한국어로 대답하세요.
    반드시 아래 사항을 지켜 실감나게 상황을 묘사하세요.

    현재 상황:
    {event_desc[event]}

    플레이어 정보:
    {charactor_info(state['player'])}

    적 정보:
    {'\n\n'.join(enemies_info)}

     - 히스토리를 보고 자연스럽게 이어가세요.
     - 몰입감 있는 묘사를 하세요.
     - 위의 정보를 반영하되 수치를 언급하지 마세요.
     - 히스토리에 판정 결과가 있다면, 그 결과를 반영하여 상황의 성공/실패를 자연스럽게 묘사하세요.

    예시 (예시 이기 때문에 간략화 되어있다. 이것보다 풍부한 묘사를 할것):
    "도시의 관문지기가 혼자서 온 당신을 의심스러운 눈빛으로 보는군요."
    위와 같은 문장으로 끝맺어 플레이어가 대응으로 무엇을 할지 흥미를 끌어야 합니다.
    '''    

    llm = get_llm()

    messages = [
        SystemMessage(content=prompt),
        *state['history']
    ]

    response = llm.invoke(messages)

    print(response.content)
    
    state['last_dice'] = None
    if state.get('last_dice', None) is not None:
        return Command(update={
            'history': [response]
        }, goto=END)

    return Command(update={
            'history': [response]
    }, goto='dice_classify')


class ClassifyCategory(BaseModel):
    category:Literal['strength', 'agility', 'dexterity', 'speech']

def dice_classify_node(state:MainState)->MainState:
    
    player_message = HumanMessage(content=input())

    llm = get_llm().with_structured_output(ClassifyCategory)

    prompt = """
    당신은 TRPG 시스템의 판정 분류기입니다.
    
    역할:
    플레이어의 행동을 보고 어떤 능력치 판정이 필요한지 정확히 하나 선택하세요.
    
    가능한 능력치:
    - strength (근력: 힘, 밀기, 들기, 공격, 물리적 충돌)
    - agility (민첩: 회피, 균형, 빠른 움직임, 점프, 반사신경)
    - dexterity (손재주: 정밀한 손동작, 자물쇠 따기, 조작, 제작, 기술 작업)
    - speech (화술: 설득, 협박, 대화, 속임수, 협상)
    
    판단 규칙:
    - 플레이어의 "의도"를 기준으로 판단하세요
    - 결과가 아니라 행동의 방식에 집중하세요
    - 애매하면 가장 핵심적인 하나만 선택하세요
    - 반드시 하나만 선택해야 합니다
    
    상황 정보:
    이전 히스토리와 플레이어의 마지막 행동을 참고하세요
    """

    messages = [
        SystemMessage(content=prompt),
        *state["history"],
        player_message
    ]

    result:ClassifyCategory = llm.invoke(messages)

    print(f'판정 스텟: {result.category}')

    return {
        'history':[player_message],
        'dice_category':result.category,
    }

class DiceJudgeResult(BaseModel):
    dice_num:int

def dice_judge(state:MainState)->MainState:
    dice_category = state['dice_category']
    dice_range = state['player']['stat'][dice_category]

    # llm 이 히스토리를 통해 난이도를 설정 예시: 힘 굴림 5 이상시 성공 

    dice = dice_roll(dice_range[0], dice_range[1])
    result_num = dice + dice_range[2]
    
    # 나중에 LLM이 성공 실패 판단해서 tool 사용해서 state 수정할거임 일단 묘사만
    # 결과에 따라 성공 실패를 판단해서 알아서 tool 사용하게 할거임
    # 전투 상황에 실패하면 플레이어에게 불이익을 주고, 성공하면 적에게 불이익을 주는식
    # 그 수정 사항을 기록하여 히스토리에 넘겨 묘사 노드가 참고하게 할것
    # event 에 따라 판정시 결과가 달라지므로 보편적인 프롬프트를 쓰거나 아니면 케이스 마다 다른 프롬프트를 쓸것
    # 예: 휴식, 단련한다 -> 플레이어 능력치 수정

    print(f'{dice_category} 굴림: {dice} + {dice_range[2]} = {result_num}')

    

    return {
        "history": [
            AIMessage(content=f"[판정 결과] {dice_category} 판정 값: {result_num}")
        ],
        "last_dice": result_num  # 선택 (아래에서 설명)
    }

builder = StateGraph(MainState)

builder.add_node('explanation', explanation_node)
builder.add_node('dice_classify', dice_classify_node)
builder.add_node('dice_judge', dice_judge)

# 시작
builder.add_edge(START, 'explanation')
# 턴 진행)
builder.add_edge('dice_classify', 'dice_judge')
# 다시 묘사로 돌아감 (루프)
builder.add_edge('dice_judge', 'explanation')

graph = builder.compile()

player = CharactorState(
    name='아르시스',
    desc='막 모험을 시작한 신입 모험가, 낡은 장검과 가죽 갑옷으로 무장했다.',
    hp=10,
    max_hp=10,
    stat=StatState(
        strength=[1, 6, 1],
        agility=[1, 4, 3],
        dexterity=[1, 12, -2],
        speech=[1, 20, -10]
    )
)

enemy = CharactorState(
    name='고블린',
    desc='뭉둥이를 든 고블린 입니다.',
    hp=10,
    max_hp=10,
    stat=StatState(
        strength=[1, 4, 2],
        agility=[1, 4, 1],
        dexterity=[1, 6, -2],
        speech=[0, 0, 0]
    )
)

state = MainState(
    history=[
        SystemMessage(content='그런데 갑자기 고블린이 나타났다!')
    ],
    player=player,
    enemies=[enemy],
    event='combat'
)

result = graph.invoke(state)

#print(result)