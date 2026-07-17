"""
macOS / POSIX keyboard input using termios.
"""

import select
import sys
import termios
import tty
from typing import Optional

from src.action_requester.controller_misc.controller_base import KeyboardControllerBase


class KeyboardController(KeyboardControllerBase):
    def get_key(self) -> Optional[str]:
        """
        Reads a single keystroke from stdin. Returns the character pressed,
        or None if not recognized.
        """
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            if self.timeout is not None:
                ready, _, _ = select.select([sys.stdin], [], [], self.timeout)
                if not ready:
                    return None
            ch = sys.stdin.read(1)
            if ch == '\x1b':
                ch2 = sys.stdin.read(1)
                if ch2 == '[':
                    ch3 = sys.stdin.read(1)
                    return f"ARROW_{ch3}"
                return None
            return ch
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
