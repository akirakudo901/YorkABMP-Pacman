"""
Terminal-based visualizer for the Pacman game.

Clears the screen (like Ctrl+L) before each frame, then redraws the map.
"""

from __future__ import annotations

import sys
import time
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from game import GameMap, Observation

PLAYER_CHARS = {
    "RIGHT": ">",
    "LEFT": "<",
    "UP": "^",
    "DOWN": "v",
    "NEUTRAL": "C",
}


def clear_terminal() -> None:
    """Clear the terminal and move the cursor to the top-left."""
    sys.stdout.write("\033[2J\033[H")
    sys.stdout.flush()


class TerminalGameVisualizer:
    """Renders a GameMap state in the terminal."""

    def __init__(self, game_map: GameMap, delay_ms: int = 120) -> None:
        self.game_map = game_map
        self.delay_ms = delay_ms

    def render(
        self,
        observation: Observation | None = None,
        *,
        done: bool = False,
        won: bool = False,
    ) -> bool:
        """Clear the terminal and draw the current game state."""
        if observation is None:
            observation = self.game_map.get_observation()

        clear_terminal()
        self._print_hud(self.game_map.score, done=done, won=won)
        self._print_map(observation)

        if done:
            message = "You won!" if won else "Game over"
            print()
            print(message)

        if self.delay_ms > 0:
            time.sleep(self.delay_ms / 1000)

        return True

    def wait_before_close(self, delay_ms: int = 2000) -> None:
        """Keep the final frame visible before the game loop exits."""
        if delay_ms > 0:
            time.sleep(delay_ms / 1000)

    def close(self) -> None:
        pass

    def _print_hud(self, score: int, *, done: bool, won: bool) -> None:
        status = ""
        if done:
            status = " — You won!" if won else " — Game over"
        print(f"Score: {score}{status}")
        print()

    def _print_map(self, observation: Observation) -> None:
        game_map = observation.map
        grid = self._build_grid(observation)

        for y in range(game_map.size_y):
            row = []
            for x in range(game_map.size_x):
                row.append(grid[x][y])
            print("".join(row))

    def _build_grid(self, observation: Observation) -> list[list[str]]:
        game_map = observation.map
        grid = [[" " for _ in range(game_map.size_y)] for _ in range(game_map.size_x)]

        for x in range(game_map.size_x):
            for y in range(game_map.size_y):
                if game_map.wall_locs[x][y]:
                    grid[x][y] = "W"
                elif game_map.pellet_locs[x][y]:
                    grid[x][y] = "."

        player_x, player_y = observation.player.coord
        grid[player_x][player_y] = PLAYER_CHARS.get(
            observation.player.dir.name,
            "C",
        )

        for enemy in observation.enemies:
            enemy_x, enemy_y = enemy.coord
            grid[enemy_x][enemy_y] = str(enemy.enemy_id)

        return grid


def visualize(game_map: GameMap, delay_ms: int = 120) -> TerminalGameVisualizer:
    """Create a terminal visualizer bound to a GameMap instance."""
    return TerminalGameVisualizer(game_map, delay_ms=delay_ms)
