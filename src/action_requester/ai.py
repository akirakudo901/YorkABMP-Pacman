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
        enemy_id = context["enemy_id"]
        myself = observation.enemies[enemy_id]
        player = observation.player

        m_x, m_y = myself.coord
        p_x, p_y = player.coord
        # check general direction of player relative to current position
        d_x, d_y = (p_x - m_x), (p_y - m_y)
        x_dir = Direction.delta_to_dir((d_x, 0))
        y_dir = Direction.delta_to_dir((0, d_y))
        # move in first direction if possible
        move_candidate_x = x_dir.move_towards(myself.coord)
        if observation.map.can_move(move_candidate_x):
            return x_dir
        # otherwise move in second direction
        return y_dir