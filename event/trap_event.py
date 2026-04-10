from node import event_name
from state_types import GameState

# 🪤 함정 이벤트
@event_name('화려한 보물상자에 장치된 함정 이벤트')
def trap_event_func(state: GameState, dice_word: str) -> tuple[str, dict]:
    event_result_map = {'대실패': -10, '실패': -5, '성공': 0, '크리티컬': 5}
    change_hp = event_result_map[dice_word]
    update = {'player_hp': state['player_hp'] + change_hp}

    if change_hp == 0: return '아무일도 없었다!', update
    elif change_hp > 0: return f'오히려 숨겨진 포션을 찾아 HP를 {change_hp} 회복했다.', update
    else: return f'함정에 당해 {change_hp} 피해를 입었다.', update

