"""
Grid for Pacman.

From plan.md:

Initial grid:
- 2D matrix for step-able: false for walls. Size of the map, limits are treated as walls.
- Can check for movability into adjacent position, for a given entity with given position.
can_move(x, y)
"""

from __future__ import annotations

from enum import Enum
from typing import Tuple

Coord = Tuple[int, int]

class Direction(Enum):
    UP = 'U'
    DOWN = 'D'
    LEFT = 'L'
    RIGHT = 'R'
    NEUTRAL = 'N'

    def delta(self) -> Tuple[int, int]:
        """Return (dx, dy) for this direction."""
        if self == Direction.UP:
            return (0, -1)
        elif self == Direction.DOWN:
            return (0, 1)
        elif self == Direction.LEFT:
            return (-1, 0)
        elif self == Direction.RIGHT:
            return (1, 0)
        elif self == Direction.NEUTRAL:
            return (0, 0)
        else:
            raise ValueError("Unknown Direction")
    
    def move_towards(self, start: Coord) -> Coord:
        dx, dy = self.delta()
        sx, sy = start
        return (sx + dx, sy + dy)

class Map:
    
    def __init__(
        self, size_x: int=5, size_y: int=5,
        walls: list[Coord]=None,
        pellets: list[Coord]=None,
        ) -> None:
        self.size_x, self.size_y = size_x, size_y
        
        # size_x by size_y grid for where is a wall
        self.wall_locs: list[list[bool]] = [[False] * size_y] * size_x
        # similar matrix for location of pellets
        self.pellet_locs: list[list[bool]] = [[False] * size_y] * size_x
        
        if walls:
            self.add_walls(walls)
        
        if pellets:
            self.add_pellets(pellets)
    
    # Helpers related to wall setttings
    def add_walls(self, walls: list[Coord]) -> None:
        self._set_grid_state(walls, True, self.wall_locs)
    
    def remove_walls(self, walls: list[Coord]) -> None:
        self._set_grid_state(walls, False, self.wall_locs)
    
    def _set_grid_state(self, coords: list[Coord], val: bool, grid: list[list[bool]]) -> None:
        for coord in coords:
            if self._in_bounds(coord):
                x, y = coord
                grid[x][y] = val
    
    def _in_bounds(self, coord: Coord) -> bool:
        x, y = coord
        if x < 0 or (self.size_x - 1) < x:
            return False
        if y < 0 or (self.size_y - 1) < y:
            return False
        return True
    
    # Helpers related to movement
    def can_move(self, coord: Coord) -> bool:
        x, y = coord
        return self._in_bounds(coord) and not self.wall_locs[x][y]
    
    def move(self, start: Coord, dir: Direction) -> Coord:
        if not self.can_move(start):
            raise Exception("start must be a valid starting point.")
        
        target = dir.move_towards(start)
        return target if self.can_move(target) else start
    
    # Helpers related to pellets
    def add_pellets(self, coords: list[Coord]) -> None:
        self._set_grid_state(coords, True, self.pellet_locs)
    
    def remove_pellets(self, coords: list[Coord]) -> None:
        self._set_grid_state(coords, False, self.pellet_locs)
    
    def consume_pellets(self, coords: list[Coord]) -> None:
        self.remove_pellets(coords)
    
    def have_pellets(self, coords: list[Coord]) -> list[bool]:
        return [self._in_bounds((x, y)) and self.pellet_locs[x][y] for x, y in coords]