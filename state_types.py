from operator import add
from typing import TypedDict, Annotated, Literal
from pydantic import BaseModel, Field

# ==========================================
# 1. 상태 클래스 및 Pydantic 모델
# ==========================================
class GameState(TypedDict):
    player_name: str
    player_hp: int
    player_max_hp: int
    player_atk: int
    
    monster_name: str
    monster_hp: int
    monster_max_hp: int
    monster_atk: int

    stage_depth: int
    crossroads: int
    event_type: str  

    min_dice_num: int
    max_dice_num: int
    
    history: Annotated[list[str], add]

class CombatOutput(BaseModel):
    situation_category: Literal["critical_hit", "player_attack", "monster_attack", "player_defense"] = Field(description="전투 상황 카테고리")
    description: str = Field(description="주사위 결과에 따른 다이나믹한 전투 액션 묘사 (3-4문장)")

