"""
Any entity that moves around the map, defined by their location on it.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from src.action_requester.action_requester import ActionRequester
from src.map import Coord, Direction, Map

if TYPE_CHECKING:
    from src.game import Observation, Action

DEFAULT_SUPER_PACMAN_LEN = 30
DEFAULT_ENEMY_DEATH_LEN = 30

class Entity:

    def __init__(
        self, 
        init_coord: Coord,
        action_requester: ActionRequester,
        direction: Direction=Direction.DOWN,
        ) -> None:
        self.coord = init_coord
        self.dir = direction

        self.action_requester = action_requester
    
    def move(self, coord: Coord, map: Map) -> bool:
        if not map.can_move(coord):
            return False
        
        self.coord = coord
        return True

    def move(self, dir: Direction, map: Map) -> bool:
        self.dir = dir
        target = map.move(start=self.coord, dir=dir)
        if self.coord != target:
            self.coord = target
            return True
        else:
            return False
    
    def request_action(self, observation: "Observation", context: dict) -> "Action":
        return self.action_requester.request_action(observation, context)


class Player(Entity):

    def __init__(
        self, 
        *args, 
        super_pacman_len: int=DEFAULT_SUPER_PACMAN_LEN,
        **kwargs
        ) -> None:
        super().__init__(*args, **kwargs)

        self.super_pacman_len = super_pacman_len
        self.super_pacman_countdown = 0
        self.mode = "" # mode to use for finite state machine-style mode switching
        # Elapsed time in the current greedy/super state, read by the mode switch's
        # counter-hunting rules. Wiring its per-tick lifecycle is behavior/teammate work.
        self.state_timer = 0

        self._validate_super_pacman_length()
    
    def set_mode(self, mode_name: str) -> None:
        self.mode = mode_name
    
    def get_mode(self) -> str:
        return self.mode
    
    def _validate_super_pacman_length(self):
        if type(self.super_pacman_len) != int:
            raise ValueError(f"self.super_pacman_len should be of type int, got {type(self.super_pacman_len)}")
        if self.super_pacman_len < 0:
            raise ValueError(f"self.super_pacman_len should be at least 0, got {self.super_pacman_len}")
    
    def set_super_pacman_length(self, length: int) -> None:
        self.super_pacman_len = length
        self._validate_super_pacman_length()

    def start_super_pacman_mode(self) -> None:
        self.super_pacman_countdown = self.super_pacman_len
    
    def is_super_pacman_mode(self) -> bool:
        # check if self.super_pacman_countdown is greater than 0
        return self.super_pacman_countdown > 0
    
    def get_super_pacman_countdown(self) -> int:
        return self.super_pacman_countdown
    
    def tick(self) -> None:
        """Function for 'ticking' any time-based functionality."""
        self.super_pacman_countdown = max(self.super_pacman_countdown - 1, 0)


class Enemy(Entity):

    def __init__(
        self, 
        *args,
        enemy_id: int,
        lookahead_size: int=0,
        death_len: int=DEFAULT_ENEMY_DEATH_LEN,
        **kwargs
        ) -> None:
        super().__init__(*args, **kwargs)

        self.enemy_id = enemy_id
        self.lookahead_size = lookahead_size
        
        self.death_len = death_len
        self.revive_countdown = 0

        self._validate_death_length()
    
    def _validate_death_length(self):
        if type(self.death_len) != int:
            raise ValueError(f"self.death_len should be of type int, got {type(self.death_len)}")
        if self.death_len < 0:
            raise ValueError(f"self.death_len should be at least 0, got {self.death_len}")
    
    def set_death_length(self, length: int) -> None:
        self.death_len = length
        self._validate_death_length()

    def kill(self) -> None:
        self.revive_countdown = self.death_len
    
    def is_dead(self) -> bool:
        return self.revive_countdown > 0
    
    def get_revive_countdown(self) -> int:
        return self.revive_countdown
    
    def tick(self) -> None:
        """Function for 'ticking' any time-based functionality."""
        self.revive_countdown = max(self.revive_countdown - 1, 0)
    
    def request_action(self, observation: "Observation", context: dict) -> "Action":
        full_context = dict(**context)
        full_context["enemy_id"] = self.enemy_id
        full_context["lookahead_size"] = self.lookahead_size
        
        return super().request_action(observation, full_context)