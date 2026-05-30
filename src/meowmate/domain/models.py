from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Tuple


Color = Tuple[int, int, int]


class CatAction(str, Enum):
    IDLE = "idle"
    WALK = "walk"
    SLEEP = "sleep"
    CLICKED = "clicked"
    DRAGGED = "dragged"
    HAPPY = "happy"
    ANNOYED = "annoyed"
    SPECIAL = "special"


@dataclass(frozen=True)
class CatAppearance:
    body: Color
    belly: Color
    accent: Color
    stripe: Color
    eye: Color
    pattern: str


@dataclass(frozen=True)
class CatBreed:
    id: str
    display_name: str
    appearance: CatAppearance
    personality: str
    behavior_style: str
    special_action: str
    behavior_weights: Dict[CatAction, int]
    speed_bias: float = 1.0
    affection_bias: float = 1.0
    annoyance_bias: float = 1.0


@dataclass
class CatStats:
    energy: int = 76
    mood: int = 80
    affection: int = 12
    xp: int = 0
    clicks_in_window: int = 0
    last_click_at: float = 0.0

    @property
    def level(self) -> int:
        return 1 + self.xp // 100

    def clamp(self) -> None:
        self.energy = max(0, min(100, self.energy))
        self.mood = max(0, min(100, self.mood))
        self.affection = max(0, min(100, self.affection))
        self.xp = max(0, self.xp)


@dataclass
class AppSettings:
    breed_id: str = "american_shorthair"
    always_on_top: bool = True
    muted: bool = True
    scale: float = 1.0
    move_speed: float = 1.0
    interaction_intensity: float = 1.0
    x: int | None = None
    y: int | None = None
    stats: CatStats = field(default_factory=CatStats)

    def clamp(self) -> None:
        self.scale = max(0.7, min(1.8, self.scale))
        self.move_speed = max(0.4, min(2.0, self.move_speed))
        self.interaction_intensity = max(0.3, min(2.0, self.interaction_intensity))
        self.stats.clamp()
