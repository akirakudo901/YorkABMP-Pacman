"""
Keyboard based controller for the user. Written using Cursor!
"""

import sys
import termios
import tty
from typing import TYPE_CHECKING, Optional

from map import Direction

if TYPE_CHECKING:
    from game import Observation, Action

class KeyboardController:
    """
    Gathers user directional input for Pacman using WASD or arrow keys.
    """

    KEY_DIRECTION_MAP = {
        'w': Direction.UP,
        'a': Direction.LEFT,
        's': Direction.DOWN,
        'd': Direction.RIGHT,
        # Neutral (no movement) for space or extra keys
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
        pass  # No state

    def request_action(self, observation: "Observation", context: dict) -> "Action":
        return self.get_direction()

    def get_key(self) -> Optional[str]:
        """
        Reads a single keystroke from stdin. Returns the character pressed,
        or None if not recognized.
        """
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
            if ch == '\x1b':  # possible arrow key or escape sequence
                ch2 = sys.stdin.read(1)
                if ch2 == '[':
                    ch3 = sys.stdin.read(1)
                    # Arrow key pressed
                    return f"ARROW_{ch3}"
                else:
                    return None
            else:
                return ch
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

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