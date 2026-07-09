"""
A simple rule-based AI for the ghosts and player.
"""

from typing import TYPE_CHECKING

from map import Direction

if TYPE_CHECKING:
    from game import Observation, Action

class CoordMatchGhostAI:

    def request_action(self, observation: "Observation", context: dict) -> "Action":
        if "enemy_id" not in context:
            raise Exception("Pass the enemy_id when requesting action to a ghost/enemy.")
        enemy_id: int = context["enemy_id"]
        lookahead_size = context.get("lookahead_size", 0)
        
        myself = observation.enemies[enemy_id]
        player = observation.player

        m_x, m_y = myself.coord
        p_x, p_y = player.coord
        # compute "goal" location based on player position and direction
        p_dir_x, p_dir_y = player.dir.delta()
        g_x, g_y = p_x + lookahead_size * p_dir_x, p_y + lookahead_size * p_dir_y
        # check general direction of player relative to current position
        d_x, d_y = (g_x - m_x), (g_y - m_y)
        x_dir = Direction.delta_to_dir((d_x, 0))
        y_dir = Direction.delta_to_dir((0, d_y))
        # move in first direction if possible
        move_candidate_x = x_dir.move_towards(myself.coord)
        if x_dir != Direction.NEUTRAL and observation.map.can_move(move_candidate_x):
            return x_dir
        # otherwise move in second direction
        return y_dir

from rules import request_action as request_action_phoebe

class PhoebePlayerAI:

    def request_action(self, observation: "Observation", context: dict) -> "Action":
        return request_action_phoebe(observation)
