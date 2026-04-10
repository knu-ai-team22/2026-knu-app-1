from node import event_name
from state_types import GameState

@event_name('쓰러져 있는 npc 이벤트')
def meeting_fallen_stranger(state: GameState, dice_word: str) -> tuple[str, dict]:
    event_result_map = {'대실패': -10, '실패': 0, '성공': -5, '크리티컬': 0}
    change_hp = event_result_map[dice_word]
    
    if dice_word == '크리티컬':
        return f'모험가 : 도움을 주셔서 감사합니다. 신의 가호가 있기를 바라겠습니다.\n', {}
        
    elif dice_word == '성공':
        return f'모험가 : 도움을 주셔서 감사합니다. 하지만 많이 피곤해 보이시는군요.\n너무 피곤해서 {change_hp} 피해를 입었습니다.', {'player_hp': state['player_hp'] + change_hp}

    elif dice_word == '실패':
        return f'당신은 쓰러져 있는 사람을 보고도 그냥 지나쳤습니다.\n불길한 기운이 몰려옵니다.', {}

    elif dice_word == '대실패':
        return f'쓰러져 있던 모험가가 갑자기 이성을 잃은 채로 싸움을 걸어왔습니다.\n대처하지 못해 {change_hp} 피해를 입었습니다.', {'player_hp': state['player_hp'] + change_hp}