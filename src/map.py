"""
Grid for Pacman.

From plan.md:

Initial grid:
- 2D matrix for step-able: false for walls. Size of the map, limits are treated as walls.
- Can check for movability into adjacent position, for a given entity with given position.
can_move(x, y)
"""

from __future__ import annotations

from typing import Tuple

Coord = Tuple[int, int]


class Map:
    
    def __init__(
        self, size_x: int=5, size_y: int=5,
        walls: list[Coord]=None,
        ) -> None:
        self.size_x, self.size_y = size_x, size_y
        
        # size_x by size_y grid for where is a wall
        self.wall_locs: list[list[bool]] = [ [[False] * size_y] * size_x ]
        
        if walls:
            self.add_walls(walls)
        
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
    
    def can_move(self, coord: Coord) -> bool:
        x, y = coord
        return self._in_bounds(coord) and not self.wall_locs[x][y]
