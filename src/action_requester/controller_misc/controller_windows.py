"""
Windows keyboard input using msvcrt.
"""

import msvcrt
import time
from typing import Optional

from action_requester.controller_misc.controller_base import KeyboardControllerBase

# Scan codes for arrow keys (second byte after b'\x00' or b'\xe0').
_ARROW_SCAN_CODES = {
    b'H': 'ARROW_A',  # up
    b'P': 'ARROW_B',  # down
    b'M': 'ARROW_C',  # right
    b'K': 'ARROW_D',  # left
}


class KeyboardController(KeyboardControllerBase):
    def get_key(self) -> Optional[str]:
        """
        Reads a single keystroke from stdin. Returns the character pressed,
        or None if not recognized.
        """
        if self.timeout is not None:
            deadline = time.monotonic() + self.timeout
            while not msvcrt.kbhit():
                if time.monotonic() >= deadline:
                    return None
                time.sleep(0.01)

        ch = msvcrt.getch()
        if ch in (b'\x00', b'\xe0'):
            ch2 = msvcrt.getch()
            return _ARROW_SCAN_CODES.get(ch2)
        try:
            return ch.decode('utf-8')
        except UnicodeDecodeError:
            return None
