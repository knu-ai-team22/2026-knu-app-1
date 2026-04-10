from state_types import GameState

def ending_node(state: GameState):
    print("\n" + "="*50)
    
    if state['player_hp'] < 1:
        # 배드 엔딩
        # 줄바꿈(\n)을 넣어서 터미널에서 읽기 좋게 다듬었습니다.
        print("당신의 생명이 꺼져갑니다...\n"
              "당신은 자신의 운을 원망합니다.\n"
              "\"다시 태어난다면... 다음 기회가 있었다면...\"\n")

        print(f"💀 [{state['monster_name']}]에게 치명상을 입고 쓰러졌습니다!")
        print(f"지하 {state['stage_depth']}층에서 모험이 끝났습니다.")
        print("\n[ B A D   E N D I N G ]")

    else:
        # 해피 엔딩 ("어쩌구 저쩌구" 보강!)
        print("당신은 마지막 전투의 희열을 아직 만끽하고 있습니다.\n"
              "미궁의 주인이 쓰러지며, 굳게 닫혀있던 지상으로 향하는 문이 열립니다.\n"
              "따스한 빛이 당신을 감싸며 기나긴 악몽이 마침내 끝났음을 알립니다.\n")
        
        print(f"🎉 무사히 미궁의 끝(지하 {state['stage_depth']}층)을 돌파했습니다!")
        print(f"최종 남은 체력: {state['player_hp']} / {state['player_max_hp']}")
        print("\n[ H A P P Y   E N D I N G ]")
        
    print("="*50 + "\n")
    
    # LangGraph 노드는 항상 state나 변경된 딕셔너리를 반환해야 합니다.
    # 엔딩은 바뀔 상태가 없으므로 그대로 반환합니다.
    return state