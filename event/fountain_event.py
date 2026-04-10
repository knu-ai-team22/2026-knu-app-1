from node import event_name
from state_types import GameState

# ⛲ (보너스) 우물 이벤트 추가! 데코레이터의 강력함 증명
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
