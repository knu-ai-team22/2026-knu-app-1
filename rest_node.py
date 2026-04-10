from operator import add

from langgraph.graph import StateGraph, START, END
from typing import Annotated, TypedDict, Literal
from langchain_google_genai import ChatGoogleGenerativeAI

from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from langchain_groq import ChatGroq
from dotenv import load_dotenv


import random
from langgraph.types import Command

load_dotenv()



model = ChatOpenAI(
    model="gpt-5-mini", 
    temperature=0.7      
)

class GameState(TypedDict):
    player_atk: int
    player_hp: int
    player_max_hp: int
    player_name: str
    
    monster_atk: int
    monster_hp: int
    monster_max_hp: int
    monster_name: str

    stage_depth: int
    min_dice_num: int
    history: Annotated[list[str], add]

def rest_node(state: GameState):
    print("-----4stage------ 평온한 휴식처에 도착했습니다.")
    print(f"[STAGE {state['stage_depth']}]화톳불의 안식처")
    print(f"현재 상태: {state['player_name']} (HP: {state['player_hp']}/{state['player_max_hp']})")
    print(f"현재 주사위 최소 눈금: {state['min_dice_num']}")
    print("="*50)



    print("\n 당신의 선택을 기다립니다..")
    print("1. [휴식] 체력을 최대 체력의 절반만큼 회복합니다.")
    print("2. [주사위 강화] 10면체 주사위를 굴려 최소 눈금을 영구적으로 높입니다.")
    
    user_input = input("\n선택 (1 또는 2): ").strip()

    update_data = {}  #노드 안에서 일어난 변화 바구니.
    narration = ""    #어떤일 일어났는지 '설명'을 담는 바구니.

    if user_input == "1" or "휴식" in user_input:
        recovery_amount = state['player_max_hp'] // 2
        update_hp = min(state['player_hp'] + recovery_amount, state['player_max_hp'])
        actual_recovered = update_hp - state['player_hp']

        update_data = {"player_hp": update_hp}
        narration = f"모닥불 옆에서 휴식을 취하여 체력을 {actual_recovered}만큼 회복했습니다."
        print(f"\n {narration}")

    elif user_input == "2" or "강화" in user_input:
        update_roll = random.randint(1,10)
        update_min = update_roll
        print(f"\n 당신의 운명을 시험하였습니다....  결과: [{update_min}]!")
    

        update_data = {"min_dice_num": update_min}
        narration = f"주사위에 신비한 힘이 깃듭니다! 이제 주사위의 최소 눈금이 {update_min}으로 강화되었습니다."

        print({f"\n {narration}"})

    else:
         print("올바른 선택지를 입력해야합니다.")
         return Command(goto="rest_node")
    

    prompt = f"""
    당신은 판타지 TRPG의 게임 마스터입니다.
    현재 상황: {narration}
    플레이어 이름: {state['player_name']}

    위 상황을 플레이어의 성격이 느껴지도록 아주 생생하고 짧게 묘사해주세요.
    직접 플레이어에게 말을 거는 듯한 말투를 사용하세요.
    """

   
    response = model.invoke(prompt).content

    print(f"\n[GM]: {response}")


    return Command(
        update={
            **update_data,
            "history": [f"[휴식처] {response}"],
            "stage_depth": 5  
        },
        goto="Boss_node"
    )







# --- 테스트용 실행 코드 ---
if __name__ == "__main__":
    # 1. 초기 상태 설정 (테스트 데이터)1
    initial_state = {
        "player_name": "강준영",
        "player_hp": 10,
        "player_max_hp": 20,
        "min_dice_num": 1,
        "stage_depth": 4,
        "history": []
    }

    # 2. 함수 직접 실행
    print("게임 테스트를 시작합니다...")
    result = rest_node(initial_state)
    
    # 3. 결과 확인
    print("\n" + "="*50)
    print("노드 실행 결과 (반환된 Command):")
    print(result)





