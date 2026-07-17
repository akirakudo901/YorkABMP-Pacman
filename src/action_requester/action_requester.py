"""
An action requester which requests an immediate action given the current state.
"""

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from src.game import Observation, Action

class ActionRequester(Protocol):
    def request_action(self, observation: "Observation", context: dict) -> "Action":
        """
        Given the current observation and additional context, decide and return an Action.
        """
        ...