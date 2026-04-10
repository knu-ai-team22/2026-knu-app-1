from state_types import GameState

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