"""
Tkinter-based visualizer for the Pacman game.
"""

from __future__ import annotations

import time
import tkinter as tk
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.game import GameMap, Observation

# Classic-inspired palette
COLOR_BACKGROUND = "#000000"
COLOR_WALL = "#2121DE"
COLOR_PELLET = "#FFB897"
COLOR_PLAYER = "#FFFF00"
COLOR_HUD_TEXT = "#FFFFFF"
GHOST_COLORS = ("#FF0000", "#FFB8FF", "#00FFFF", "#FFB852")

HUD_HEIGHT = 32


class GameVisualizer:
  """Renders a GameMap state in a tkinter window."""

  def __init__(self, game_map: GameMap, cell_size: int = 48, delay_ms: int = 120) -> None:
    self.game_map = game_map
    self.cell_size = cell_size
    self.delay_ms = delay_ms

    game_map_obj = game_map.map
    grid_width = game_map_obj.size_x * cell_size
    grid_height = game_map_obj.size_y * cell_size

    self.root = tk.Tk()
    self.root.title("Pacman")
    self.root.resizable(False, False)
    self.root.configure(bg=COLOR_BACKGROUND)

    self.canvas = tk.Canvas(
      self.root,
      width=grid_width,
      height=grid_height + HUD_HEIGHT,
      bg=COLOR_BACKGROUND,
      highlightthickness=0,
    )
    self.canvas.pack()

    self._closed = False
    self.root.protocol("WM_DELETE_WINDOW", self._on_close)

  def _on_close(self) -> None:
    self._closed = True
    self.root.destroy()

  def render(
    self,
    observation: Observation | None = None,
    *,
    done: bool = False,
    won: bool = False,
  ) -> bool:
    """Draw the current game state. Returns False if the window was closed."""
    if self._closed:
      return False

    if observation is None:
      observation = self.game_map.get_observation()

    self.canvas.delete("all")
    self._draw_hud(self.game_map.score, done=done, won=won)
    self._draw_map(observation)
    self._draw_entities(observation)

    if done:
      self._draw_overlay(won)

    try:
      self.root.update()
    except tk.TclError:
      self._closed = True
      return False

    if self.delay_ms > 0:
      time.sleep(self.delay_ms / 1000)

    return not self._closed

  def wait_before_close(self, delay_ms: int = 2000) -> None:
    """Keep the final frame visible before closing the window."""
    if self._closed:
      return
    deadline = time.time() + delay_ms / 1000
    while time.time() < deadline and not self._closed:
      try:
        self.root.update()
        time.sleep(0.05)
      except tk.TclError:
        self._closed = True
        break

  def close(self) -> None:
    if not self._closed:
      self._closed = True
      try:
        self.root.destroy()
      except tk.TclError:
        pass

  def _draw_hud(self, score: int, *, done: bool, won: bool) -> None:
    status = ""
    if done:
      status = " — You won!" if won else " — Game over"
    self.canvas.create_text(
      8,
      HUD_HEIGHT // 2,
      text=f"Score: {score}{status}",
      fill=COLOR_HUD_TEXT,
      anchor="w",
      font=("Helvetica", 14, "bold"),
    )

  def _draw_map(self, observation: Observation) -> None:
    game_map = observation.map
    size = self.cell_size
    y_offset = HUD_HEIGHT

    for x in range(game_map.size_x):
      for y in range(game_map.size_y):
        left = x * size
        top = y * size + y_offset
        right = left + size
        bottom = top + size

        if game_map.wall_locs[x][y]:
          self.canvas.create_rectangle(
            left,
            top,
            right,
            bottom,
            fill=COLOR_WALL,
            outline=COLOR_WALL,
          )
        elif game_map.pellet_locs[x][y]:
          pellet_radius = max(2, size // 10)
          cx = left + size // 2
          cy = top + size // 2
          self.canvas.create_oval(
            cx - pellet_radius,
            cy - pellet_radius,
            cx + pellet_radius,
            cy + pellet_radius,
            fill=COLOR_PELLET,
            outline=COLOR_PELLET,
          )

  def _draw_entities(self, observation: Observation) -> None:
    size = self.cell_size
    y_offset = HUD_HEIGHT

    player_x, player_y = observation.player.coord
    self._draw_pacman(player_x, player_y, observation.player.dir.name, size, y_offset)

    for enemy in observation.enemies:
      color = GHOST_COLORS[enemy.enemy_id % len(GHOST_COLORS)]
      self._draw_ghost(enemy.coord[0], enemy.coord[1], color, size, y_offset)

  def _cell_center(self, x: int, y: int, size: int, y_offset: int) -> tuple[int, int]:
    return x * size + size // 2, y * size + size // 2 + y_offset

  def _draw_pacman(self, x: int, y: int, direction: str, size: int, y_offset: int) -> None:
    cx, cy = self._cell_center(x, y, size, y_offset)
    radius = size // 2 - 2
    mouth_angles = {
      "RIGHT": (35, 290),
      "LEFT": (215, 290),
      "UP": (125, 290),
      "DOWN": (305, 290),
      "NEUTRAL": (0, 359),
    }
    start, extent = mouth_angles.get(direction, (0, 359))
    self.canvas.create_arc(
      cx - radius,
      cy - radius,
      cx + radius,
      cy + radius,
      start=start,
      extent=extent,
      fill=COLOR_PLAYER,
      outline=COLOR_PLAYER,
    )

  def _draw_ghost(self, x: int, y: int, color: str, size: int, y_offset: int) -> None:
    cx, cy = self._cell_center(x, y, size, y_offset)
    radius = size // 2 - 2
    body_bottom = cy + radius // 2

    self.canvas.create_oval(
      cx - radius,
      cy - radius,
      cx + radius,
      cy + radius // 2,
      fill=color,
      outline=color,
    )
    self.canvas.create_rectangle(
      cx - radius,
      cy,
      cx + radius,
      body_bottom,
      fill=color,
      outline=color,
    )

    eye_offset = radius // 3
    eye_radius = max(2, radius // 5)
    for dx in (-eye_offset, eye_offset):
      ex = cx + dx
      ey = cy - radius // 4
      self.canvas.create_oval(
        ex - eye_radius,
        ey - eye_radius,
        ex + eye_radius,
        ey + eye_radius,
        fill="white",
        outline="white",
      )
      pupil_radius = max(1, eye_radius // 2)
      self.canvas.create_oval(
        ex - pupil_radius + 1,
        ey - pupil_radius,
        ex + pupil_radius + 1,
        ey + pupil_radius,
        fill="black",
        outline="black",
      )

  def _draw_overlay(self, won: bool) -> None:
    width = int(self.canvas["width"])
    height = int(self.canvas["height"])
    self.canvas.create_rectangle(0, 0, width, height, fill="#000000", stipple="gray50")
    message = "You won!" if won else "Game over"
    self.canvas.create_text(
      width // 2,
      height // 2,
      text=message,
      fill=COLOR_PLAYER if won else "#FF4444",
      font=("Helvetica", 28, "bold"),
    )


def visualize(game_map: GameMap, cell_size: int = 48, delay_ms: int = 120) -> GameVisualizer:
  """Create a visualizer bound to a GameMap instance."""
  return GameVisualizer(game_map, cell_size=cell_size, delay_ms=delay_ms)
