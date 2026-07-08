"""
Any entity that moves around the map, defined by their location on it.
"""

from __future__ import annotations

from map import Coord, Direction, Map

class Entity:

    def __init__(self, init_coord: Coord, map: Map) -> None:
        self.coord = init_coord
        self.map = map
        
        if not map.can_move(self.coord):
            raise ValueError("Initial coordinate of the entity must be free in the corresponding map.")
    
    def set_map(self, map: Map) -> None:
        self.map = map
    
    def get_map(self, map: Map) -> Map:
        return self.map

    def move(self, coord: Coord) -> bool:
        if not self.map.can_move(coord):
            return False
        
        self.coord = coord
        return True

    def move(self, dir: Direction) -> bool:
        target = self.map.move(start=self.coord, dir=dir)
        if self.coord != target:
            self.coord = target
            return True
        else:
            return False