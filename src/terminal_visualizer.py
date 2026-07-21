"""
Terminal-based visualizer for the Pacman game.

Clears the screen (like Ctrl+L) before each frame, then redraws the map.
"""

from __future__ import annotations

import sys
import time
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.entity import Player
    from src.game import GameMap, Observation

PLAYER_CHARS = {
    "RIGHT": ">",
    "LEFT": "<",
    "UP": "^",
    "DOWN": "v",
    "NEUTRAL": "C",
}

WALL_CHAR = "▪"
PELLET_CHAR = "."
POWER_PELLET_CHAR = "O"
DEAD_ENEMY_CHAR = "X"

RESET = "\033[0m"
COLOR_WALL = "\033[92m"  # bright green
COLOR_WALL_SUPER = "\033[93m"  # bright yellow
COLOR_PLAYER = "\033[93m"  # bright yellow
COLOR_PLAYER_WARNING = "\033[38;5;208m"  # orange
COLOR_ENEMY_FRIGHTENED = "\033[35m"  # purple / magenta
COLOR_DEAD = "\033[90m"  # bright black / grey
ENEMY_COLORS = (
    "\033[91m",  # red
    "\033[96m",  # cyan
    "\033[93m",  # yellow
    "\033[95m",  # pink (bright magenta)
)

WARNING_FRAMES = 6
COUNTDOWN_SECONDS = 3
COLOR_COUNTDOWN = "\033[97m"  # bright white

# ~10 characters wide, 7 rows tall block digits.
COUNTDOWN_DIGITS: dict[int, tuple[str, ...]] = {
    1: (
        "   ████   ",
        " ██████   ",
        "   ████   ",
        "   ████   ",
        "   ████   ",
        "   ████   ",
        "██████████",
    ),
    2: (
        " ████████ ",
        "██      ██",
        "        ██",
        "   ██████ ",
        " ██       ",
        "██        ",
        "██████████",
    ),
    3: (
        " ████████ ",
        "██      ██",
        "        ██",
        "  ██████  ",
        "        ██",
        "██      ██",
        " ████████ ",
    ),
}


def _colored(text: str, color: str) -> str:
    return f"{color}{text}{RESET}"


def _oscillate(countdown: int, color_a: str, color_b: str) -> str:
    """Alternate between two colors each frame while a countdown is running."""
    return color_a if countdown % 2 == 0 else color_b


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

    def show_countdown(
        self,
        observation: Observation | None = None,
        seconds: int = COUNTDOWN_SECONDS,
    ) -> None:
        """Show a 3-2-1 countdown overlaid on the middle of the map."""
        if observation is None:
            observation = self.game_map.get_observation()

        for n in range(seconds, 0, -1):
            clear_terminal()
            self._print_hud(self.game_map.score, done=False, won=False)
            self._print_map(observation, overlay_digit=n)
            time.sleep(1.0)

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

    def _print_map(
        self,
        observation: Observation,
        *,
        overlay_digit: int | None = None,
    ) -> None:
        game_map = observation.map
        grid = self._build_grid(observation)
        if overlay_digit is not None:
            self._overlay_countdown_digit(grid, game_map.size_x, game_map.size_y, overlay_digit)

        for y in range(game_map.size_y):
            row = []
            for x in range(game_map.size_x):
                row.append(grid[x][y])
            print("".join(row))

    def _overlay_countdown_digit(
        self,
        grid: list[list[str]],
        size_x: int,
        size_y: int,
        digit: int,
    ) -> None:
        art = COUNTDOWN_DIGITS.get(digit)
        if art is None:
            return

        digit_h = len(art)
        digit_w = len(art[0])
        start_x = (size_x - digit_w) // 2
        start_y = (size_y - digit_h) // 2

        for dy, line in enumerate(art):
            y = start_y + dy
            if y < 0 or y >= size_y:
                continue
            for dx, ch in enumerate(line):
                x = start_x + dx
                if x < 0 or x >= size_x:
                    continue
                if ch != " ":
                    grid[x][y] = _colored(ch, COLOR_COUNTDOWN)

    def _player_color(self, player: Player) -> str:
        countdown = player.get_super_pacman_countdown()
        if player.is_super_pacman_mode() and countdown <= WARNING_FRAMES:
            return _oscillate(countdown, COLOR_PLAYER, COLOR_PLAYER_WARNING)
        return COLOR_PLAYER

    def _wall_color(self, *, super_pacman: bool, super_countdown: int) -> str:
        if not super_pacman:
            return COLOR_WALL
        if super_countdown <= WARNING_FRAMES:
            return _oscillate(super_countdown, COLOR_WALL_SUPER, COLOR_WALL)
        return COLOR_WALL_SUPER

    def _build_grid(self, observation: Observation) -> list[list[str]]:
        game_map = observation.map
        grid = [[" " for _ in range(game_map.size_y)] for _ in range(game_map.size_x)]
        super_pacman = observation.player.is_super_pacman_mode()
        super_countdown = observation.player.get_super_pacman_countdown()
        wall_color = self._wall_color(
            super_pacman=super_pacman, super_countdown=super_countdown
        )

        for x in range(game_map.size_x):
            for y in range(game_map.size_y):
                if game_map.wall_locs[x][y]:
                    grid[x][y] = _colored(WALL_CHAR, wall_color)
                elif game_map.power_pellet_locs[x][y]:
                    grid[x][y] = POWER_PELLET_CHAR
                elif game_map.pellet_locs[x][y]:
                    grid[x][y] = PELLET_CHAR

        player_x, player_y = observation.player.coord
        player_char = PLAYER_CHARS.get(observation.player.dir.name, "C")
        grid[player_x][player_y] = _colored(player_char, self._player_color(observation.player))

        for enemy in observation.enemies:
            enemy_x, enemy_y = enemy.coord
            original = ENEMY_COLORS[enemy.enemy_id % len(ENEMY_COLORS)]

            if enemy.is_dead():
                revive_countdown = enemy.get_revive_countdown()
                if revive_countdown <= WARNING_FRAMES:
                    color = _oscillate(revive_countdown, COLOR_DEAD, original)
                else:
                    color = COLOR_DEAD
                grid[enemy_x][enemy_y] = _colored(DEAD_ENEMY_CHAR, color)
                continue

            if super_pacman:
                if super_countdown <= WARNING_FRAMES:
                    color = _oscillate(super_countdown, COLOR_ENEMY_FRIGHTENED, original)
                else:
                    color = COLOR_ENEMY_FRIGHTENED
            else:
                color = original

            grid[enemy_x][enemy_y] = _colored(str(enemy.enemy_id), color)

        return grid


def visualize(game_map: GameMap, delay_ms: int = 120) -> TerminalGameVisualizer:
    """Create a terminal visualizer bound to a GameMap instance."""
    return TerminalGameVisualizer(game_map, delay_ms=delay_ms)
