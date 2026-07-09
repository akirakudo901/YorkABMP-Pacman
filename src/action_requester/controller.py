"""
Keyboard based controller for the user. Written using Cursor!

Selects the platform-specific implementation at import time.
"""

import sys

if sys.platform == 'win32':
    from action_requester.controller.controller_windows import KeyboardController
else:
    from action_requester.controller.controller_macos import KeyboardController

__all__ = ['KeyboardController']
