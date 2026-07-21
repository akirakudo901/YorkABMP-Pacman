"""
A simple rule-based AI for the ghosts and player.
"""

import random
from typing import TYPE_CHECKING

from src.action_requester.precompute_shortest_path import GroupedShortestPathMap
from src.map import Direction

if TYPE_CHECKING:
    from src.game import Observation, Action

class CoordMatchGhostAI:

    def request_action(self, observation: "Observation", context: dict) -> "Action":
        if "enemy_id" not in context:
            raise Exception("Pass the enemy_id when requesting action to a ghost/enemy.")
        enemy_id: int = context["enemy_id"]
        lookahead_size = context.get("lookahead_size", 0)
        
        myself = observation.enemies[enemy_id]
        player = observation.player

        # simple reeturn if dead or every odd frame for super countdown
        if myself.is_dead() or player.get_super_pacman_countdown() % 2 == 1:
            return Direction.NEUTRAL

        m_x, m_y = myself.coord
        p_x, p_y = player.coord
        # compute "goal" location based on player position and direction
        p_dir_x, p_dir_y = player.dir.delta()
        g_x, g_y = p_x + lookahead_size * p_dir_x, p_y + lookahead_size * p_dir_y
        # check general direction of player relative to current position
        d_x, d_y = (g_x - m_x), (g_y - m_y)
        # if the player is in super pacman mode, simply go the other way (flee)
        if player.is_super_pacman_mode():
            d_x, d_y = -d_x, -d_y
        x_dir = Direction.delta_to_dir((d_x, 0))
        y_dir = Direction.delta_to_dir((0, d_y))
        # move in first direction if possible
        move_candidate_x = x_dir.move_towards(myself.coord)
        if x_dir != Direction.NEUTRAL and observation.map.can_move(move_candidate_x):
            return x_dir
        # otherwise move in second direction
        return y_dir


class ShortestPathGhostAI:

    def __init__(self, shortest_path_map: GroupedShortestPathMap) -> None:
        self.shortest_path_map = shortest_path_map

    def request_action(self, observation: "Observation", context: dict) -> "Action":
        if "enemy_id" not in context:
            raise Exception("Pass the enemy_id when requesting action to a ghost/enemy.")
        enemy_id: int = context["enemy_id"]
        lookahead_size = context.get("lookahead_size", 0)
        
        myself = observation.enemies[enemy_id]
        player = observation.player

        # simple reeturn if dead or every odd frame for super countdown
        if myself.is_dead() or player.get_super_pacman_countdown() % 2 == 1:
            return Direction.NEUTRAL
        
        # compute "goal" location: furthest valid point from player.coord in (player.dir or -player.dir)
        current, direction = player.coord, player.dir
        if lookahead_size < 0:
            direction = direction.opposite()
        steps = abs(lookahead_size)

        # Step out up to 'steps', or until hit a wall
        furthest = current
        for _ in range(steps):
            next_coord = direction.move_towards(furthest)
            if not observation.map.can_move(next_coord):
                break
            furthest = next_coord
        goal_coord = furthest
        
        # query and return the best direction for fastest approach to the player
        best_dir_towards_player = self.shortest_path_map.query_direction(goal_coord, myself.coord)
        if player.is_super_pacman_mode():
            valid_dirs = [
                d for d in Direction 
                if d not in (best_dir_towards_player, Direction.NEUTRAL)
            ]
            if valid_dirs:
                return random.choice(valid_dirs)
            else:
                return Direction.NEUTRAL
        else:
            return best_dir_towards_player


from src.rules import request_action as request_action_phoebe

class PhoebePlayerAI:

    def request_action(self, observation: "Observation", context: dict) -> "Action":
        return request_action_phoebe(observation)
