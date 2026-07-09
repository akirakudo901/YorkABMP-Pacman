"""
Shared keyboard controller logic for Pacman.
"""

from typing import TYPE_CHECKING, Optional

from map import Direction

if TYPE_CHECKING:
    from game import Observation, Action


class KeyboardControllerBase:
    """
    Gathers user directional input for Pacman using WASD or arrow keys.
    Platform-specific subclasses implement get_key().
    """

    KEY_DIRECTION_MAP = {
        'w': Direction.UP,
        'a': Direction.LEFT,
        's': Direction.DOWN,
        'd': Direction.RIGHT,
        ' ': Direction.NEUTRAL,
        None: Direction.NEUTRAL,
    }

    ARROW_DIRECTION_MAP = {
        'A': Direction.UP,
        'B': Direction.DOWN,
        'C': Direction.RIGHT,
        'D': Direction.LEFT,
    }

    def __init__(self):
        pass

    def request_action(self, observation: "Observation", context: dict) -> "Action":
        return self.get_direction()

    def get_key(self) -> Optional[str]:
        raise NotImplementedError

    def get_direction(self) -> Direction:
        """
        Blocks for a keypress and returns one of 'UP', 'DOWN', 'LEFT', 'RIGHT', or 'NEUTRAL'.
        Accepts both WASD and arrow keys.
        """
        key = self.get_key()
        if key is None:
            return Direction.NEUTRAL
        if key.startswith('ARROW_'):
            code = key[-1]
            return self.ARROW_DIRECTION_MAP.get(code, Direction.NEUTRAL)
        key = key.lower()
        return self.KEY_DIRECTION_MAP.get(key, Direction.NEUTRAL)
