from __future__ import annotations

import random
import time
from dataclasses import dataclass

from src.meowmate.domain.models import AppSettings, CatAction, CatBreed


@dataclass
class BehaviorState:
    action: CatAction = CatAction.IDLE
    previous_action: CatAction = CatAction.IDLE
    facing: int = -1
    frame: int = 0
    transition_frame: int = 0
    transition_frames: int = 10
    message: str = ""
    action_started_at: float = 0.0


class BehaviorEngine:
    def __init__(self, settings: AppSettings, breed: CatBreed) -> None:
        self.settings = settings
        self.breed = breed
        self.state = BehaviorState(action_started_at=time.time())

    def update_breed(self, breed: CatBreed) -> None:
        self.breed = breed
        self.set_action(CatAction.IDLE)

    def tick_animation(self) -> None:
        self.state.frame = (self.state.frame + 1) % 10_000
        self.state.transition_frame = min(
            self.state.transition_frames,
            self.state.transition_frame + 1,
        )
        if self.state.action == CatAction.SLEEP:
            self.settings.stats.energy += 1
        elif self.state.action == CatAction.WALK:
            self.settings.stats.energy -= 1
        self.settings.stats.clamp()

    def choose_next_action(self) -> CatAction:
        weights = dict(self.breed.behavior_weights)
        stats = self.settings.stats
        if stats.energy < 32:
            weights[CatAction.SLEEP] = weights.get(CatAction.SLEEP, 0) + 28
            weights[CatAction.WALK] = max(1, weights.get(CatAction.WALK, 1) - 12)
        if stats.mood < 35:
            weights[CatAction.ANNOYED] = weights.get(CatAction.ANNOYED, 0) + 24
        if stats.affection > 55:
            weights[CatAction.HAPPY] = weights.get(CatAction.HAPPY, 0) + 12
            weights[CatAction.SPECIAL] = weights.get(CatAction.SPECIAL, 0) + 8
        actions = list(weights)
        picked = random.choices(actions, weights=[weights[a] for a in actions], k=1)[0]
        self.set_action(picked)
        return picked

    def set_action(self, action: CatAction, message: str = "") -> None:
        if action == self.state.action and message == self.state.message:
            return
        self.state.previous_action = self.state.action
        self.state.action = action
        self.state.action_started_at = time.time()
        self.state.frame = 0
        self.state.transition_frame = 0
        self.state.message = message

    def click(self) -> None:
        now = time.time()
        stats = self.settings.stats
        if now - stats.last_click_at < 1.2:
            stats.clicks_in_window += 1
        else:
            stats.clicks_in_window = 1
        stats.last_click_at = now

        if stats.clicks_in_window >= max(3, int(5 / self.settings.interaction_intensity)):
            stats.mood -= int(6 * self.breed.annoyance_bias)
            self.set_action(CatAction.ANNOYED, "别戳啦")
        else:
            stats.affection += int(2 * self.breed.affection_bias)
            stats.mood += 1
            stats.xp += 1
            self.set_action(CatAction.CLICKED, "喵")
        stats.clamp()

    def tease(self) -> None:
        stats = self.settings.stats
        stats.mood += 4
        stats.energy -= 2
        stats.affection += 1
        stats.xp += 2
        stats.clamp()
        self.set_action(CatAction.HAPPY, "呼噜呼噜")

    def feed(self) -> None:
        stats = self.settings.stats
        stats.energy += 9
        stats.mood += 2
        stats.affection += 1
        stats.xp += 2
        stats.clamp()
        self.set_action(CatAction.HAPPY, "好吃")

    def sleep(self) -> None:
        self.set_action(CatAction.SLEEP, "晚安")

    def special(self) -> None:
        self.settings.stats.xp += 3
        self.settings.stats.clamp()
        self.set_action(CatAction.SPECIAL, self.breed.special_action)

    def drag_started(self) -> None:
        self.settings.stats.mood -= 1
        self.settings.stats.clamp()
        self.set_action(CatAction.DRAGGED, "")

    def drag_finished(self) -> None:
        self.set_action(CatAction.IDLE, "")
