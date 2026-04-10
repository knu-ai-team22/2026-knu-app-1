import random
from state_types import GameState
from llm import get_llm

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
    llm = get_llm()
    response = llm.invoke(prompt).content
    print(f"\n🎙️ [GM]: {response}")

    # 3. 상태 업데이트 및 스테이지 매니저로 이동
    return {
            **update_data,
            "history": [f"[휴식처] {response}"],
        }