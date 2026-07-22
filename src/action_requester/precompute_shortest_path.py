"""
We can pre-compute a breadth-first search-based distance grid for a given map that we can query for!
- Given a map with N reachable spots, the database will consist of N copies of the same map, where:
  - The ith copy encodes the shortest path from the ith position in the map to any position in the map
    - This is encoded as a grid: each position is annotated with the shortest path size to the origin, and which direction to move to reach the origin

Then, at query time, a ghost can:
- query for the entry using the position of the player
- look up its own position in the map to identify the number of steps to the player
- follow the pointer in the map as the shortest path to the player
"""

from __future__ import annotations

from collections import deque
from pathlib import Path

import numpy as np

from src.map import Coord, Direction, Map

# Unreachable / non-walkable cells use the max uint8 distance (never queried).
UNREACHABLE_DISTANCE = np.iinfo(np.uint8).max  # 255

_DIR_TO_CODE: dict[Direction, int] = {
    Direction.NEUTRAL: 0,
    Direction.UP: 1,
    Direction.DOWN: 2,
    Direction.LEFT: 3,
    Direction.RIGHT: 4,
}
_CODE_TO_DIR: dict[int, Direction] = {code: d for d, code in _DIR_TO_CODE.items()}


class SingleShortestPathMap:

    def __init__(self, map: Map, source_coord: Coord) -> None:
        """Initializes a shortest-path map from ``source_coord``, precomputed at initialization."""
        if not map.can_move(source_coord):
            raise ValueError(f"source_coord {source_coord} is not a valid/walkable map location.")

        self.source_coord = source_coord
        size_x, size_y = map.size_x, map.size_y
        self.distance_query = np.full((size_x, size_y), UNREACHABLE_DISTANCE, dtype=np.uint8)
        self.direction_query = np.zeros((size_x, size_y), dtype=np.uint8)

        self.precompute_shortest_path(map)

    def precompute_shortest_path(self, map: Map) -> None:
        """
        Apply breadth-first search to the map to fill the shortest-path info for
        each position relative to source_coord:
        - The minimum number of steps for source_coord <-> target
        - Which way to go to get to source_coord with the minimum number of steps
        """
        # each entry is a three-tuple: [current-coord, parent-direction-code, path-length-to-here]
        init_entry = (self.source_coord, _DIR_TO_CODE[Direction.NEUTRAL], 0)
        frontier: deque[tuple[Coord, int, int]] = deque([init_entry])
        visited = np.zeros(self.distance_query.shape, dtype=bool)

        while frontier:
            coord, parent_dir_code, path_len = frontier.pop()
            c_x, c_y = coord
            if visited[c_x, c_y]:
                continue
            self.distance_query[c_x, c_y] = path_len
            self.direction_query[c_x, c_y] = parent_dir_code
            visited[c_x, c_y] = True
            for d in Direction:
                if d == Direction.NEUTRAL:
                    continue
                n_x, n_y = d.move_towards(coord)
                if not map.can_move((n_x, n_y)):
                    continue
                if visited[n_x, n_y]:
                    continue
                frontier.appendleft(((n_x, n_y), _DIR_TO_CODE[d.opposite()], path_len + 1))

    def query_distance(self, coord: Coord) -> int:
        x, y = coord
        return int(self.distance_query[x, y])

    def query_direction(self, coord: Coord) -> Direction:
        x, y = coord
        return _CODE_TO_DIR[int(self.direction_query[x, y])]

    def save(self, path: str | Path) -> None:
        """Serialize this shortest-path map to a numpy ``.npz`` file."""
        np.savez(
            path,
            source_coord=np.asarray(self.source_coord, dtype=np.int16),
            distance_query=self.distance_query,
            direction_query=self.direction_query,
        )

    @classmethod
    def load(cls, path: str | Path) -> SingleShortestPathMap:
        """Reconstruct a SingleShortestPathMap from a ``.npz`` file produced by ``save``."""
        with np.load(path) as data:
            src = np.array(data["source_coord"])
            distance_query = np.array(data["distance_query"], dtype=np.uint8)
            direction_query = np.array(data["direction_query"], dtype=np.uint8)
        obj = cls.__new__(cls)
        obj.source_coord = (int(src[0]), int(src[1]))
        obj.distance_query = distance_query
        obj.direction_query = direction_query
        return obj


class GroupedShortestPathMap:

    def __init__(self, map: Map) -> None:
        """Creates a SingleShortestPathMap for each reachable position in the map."""
        self.pathmaps: dict[Coord, SingleShortestPathMap] = {}

        for y in range(map.size_y):
            for x in range(map.size_x):
                coord = (x, y)
                if not map.can_move(coord):
                    continue
                self.pathmaps[coord] = SingleShortestPathMap(map, coord)

    def query_distance(self, source_coord: Coord, target_coord: Coord) -> int:
        return self.pathmaps[source_coord].query_distance(target_coord)

    def query_direction(self, source_coord: Coord, target_coord: Coord) -> Direction:
        return self.pathmaps[source_coord].query_direction(target_coord)

    def save(self, path: str | Path) -> None:
        """Serialize all per-source shortest-path maps to a single numpy ``.npz`` file."""
        if not self.pathmaps:
            raise ValueError("Cannot save an empty GroupedShortestPathMap.")

        items = list(self.pathmaps.items())
        sources = np.asarray([coord for coord, _ in items], dtype=np.int16)
        distances = np.stack([pathmap.distance_query for _, pathmap in items], axis=0)
        directions = np.stack([pathmap.direction_query for _, pathmap in items], axis=0)
        np.savez(path, sources=sources, distances=distances, directions=directions)

    @classmethod
    def load(cls, path: str | Path) -> GroupedShortestPathMap:
        """Reconstruct a GroupedShortestPathMap from a ``.npz`` file produced by ``save``."""
        with np.load(path) as data:
            sources = np.array(data["sources"])
            distances = np.array(data["distances"], dtype=np.uint8)
            directions = np.array(data["directions"], dtype=np.uint8)

        obj = cls.__new__(cls)
        obj.pathmaps = {}
        for i, (x, y) in enumerate(sources):
            coord = (int(x), int(y))
            pathmap = SingleShortestPathMap.__new__(SingleShortestPathMap)
            pathmap.source_coord = coord
            pathmap.distance_query = distances[i]
            pathmap.direction_query = directions[i]
            obj.pathmaps[coord] = pathmap
        return obj
