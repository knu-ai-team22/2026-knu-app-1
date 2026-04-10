import random
from state_types import GameState

# ==========================================
# 3. 맵 이동 (길잡이) 노드
# ==========================================
def map_move_node(state: GameState):
    # 히스토리가 있으면(이미 게임 진행 중이면) 층수 증가, 첫 진입이면 1층 유지
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
        print("미궁의 몬스터가 길을 막고 있습니다! (무조건 전투)")
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