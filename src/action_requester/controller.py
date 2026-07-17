"""
Keyboard based controller for the user. Written using Cursor!

Selects the platform-specific implementation at import time.
"""

import sys

if sys.platform == 'win32':
    from src.action_requester.controller_misc.controller_windows import KeyboardController
else:
    from src.action_requester.controller_misc.controller_macos import KeyboardController

__all__ = ['KeyboardController']
