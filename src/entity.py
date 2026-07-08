"""
Any entity that moves around the map, defined by their location on it.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from action_requester.action_requester import ActionRequester
from map import Coord, Direction, Map

if TYPE_CHECKING:
    from game import Observation, Action

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

# Nothing special yet
class Player(Entity):

    def __init__(
        self, 
        init_coord: Coord,
        action_requester: ActionRequester,
        direction: Direction=Direction.DOWN,
        ) -> None:
        super().__init__(init_coord, action_requester, direction)

class Enemy(Entity):

    def __init__(
        self, 
        init_coord: Coord,
        action_requester: ActionRequester,
        enemy_id: int,
        direction: Direction=Direction.DOWN,
        ) -> None:
        super().__init__(init_coord, action_requester, direction)
        self.enemy_id = enemy_id
    
    def request_action(self, observation: "Observation", context: dict) -> "Action":
        full_context = dict(**context)
        full_context["enemy_id"] = self.enemy_id
        return super().request_action(observation, full_context)