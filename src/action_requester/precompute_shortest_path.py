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

from collections import deque
import json

from src.map import Coord, Direction, Map

class SingleShortestPathMap:

    def __init__(self, map: Map, source_coord: Coord) -> None:
        """Initializes a shortest-path map from ``source_coord``, precomputed at initialization."""
        if not map.can_move(source_coord):
            raise ValueError(f"source_coord {source_coord} is not a valid/walkable map location.")
       
        self.source_coord = source_coord
        
        x, y = map.size_x, map.size_y
        self.distance_query = [[-1 for _ in range(y)] for _ in range(x)]
        self.direction_query = [[None for _ in range(y)] for _ in range(x)]

        self.precompute_shortest_path(map)
    

    def precompute_shortest_path(self, map: Map) -> None:
        """
        Apply breadth-first search to the map to fill the shortest-path info for
        each position relative to source_coord:
        - The minimum number of steps for source_coord <-> target
        - Which way to go to get to source_coord with the minimum number of steps
        """
        # each entry is a three-tuple: [current-coord, parent-direction, path-length-to-here]
        init_entry = (self.source_coord, Direction.NEUTRAL, 0)
        frontier = deque([init_entry])
        x, y = map.size_x, map.size_y
        visited = [[False for _ in range(y)] for _ in range(x)]

        while len(frontier) > 0:
            # pop from the right end
            coord, parent_dir, path_len = frontier.pop()
            c_x, c_y = coord
            # if visited, ignore
            if visited[c_x][c_y]:
                continue
            # if not visited, mark the shortest path + parent dir + visited
            self.distance_query[c_x][c_y] = path_len
            self.direction_query[c_x][c_y] = parent_dir
            visited[c_x][c_y] = True
            # add its neighbors to the queue
            for d in Direction:
                if d == Direction.NEUTRAL: continue
                n_x, n_y = d.move_towards(coord)
                # skip if it is unreachable in the map
                if not map.can_move((n_x, n_y)): continue
                # skip if visited
                if visited[n_x][n_y]: continue
                # append the new entry
                new_entry = ((n_x, n_y), d.opposite(), path_len + 1)
                frontier.appendleft(new_entry)
    

    def query_distance(self, coord: Coord) -> int:
        x, y = coord
        return self.distance_query[x][y]
    

    def query_direction(self, coord: Coord) -> Direction:
        x, y = coord
        return self.direction_query[x][y]


    def to_json(self) -> str:
        """Serialize this shortest-path map to a JSON string."""
        return json.dumps({
            "source_coord": list(self.source_coord),
            "distance_query": self.distance_query,
            "direction_query": [
                [None if d is None else d.value for d in row]
                for row in self.direction_query
            ],
        })


    @classmethod
    def from_json(cls, data: str) -> "SingleShortestPathMap":
        """Reconstruct a SingleShortestPathMap from a JSON string produced by ``to_json``."""
        parsed = json.loads(data)
        obj = cls.__new__(cls)
        obj.source_coord = tuple(parsed["source_coord"])
        obj.distance_query = parsed["distance_query"]
        obj.direction_query = [
            [None if d is None else Direction(d) for d in row]
            for row in parsed["direction_query"]
        ]
        return obj



class GroupedShortestPathMap:

    def __init__(self, map: Map) -> None:
        """Creates a SingleShortestPathMap for each reachable position in the map."""
        self.pathmaps: dict[Coord, SingleShortestPathMap] = {}

        for y in range(map.size_y):
            for x in range(map.size_x):
                coord = (x, y)
                # if not reachable, ignore
                if not map.can_move(coord): continue
                # else, create a page for it
                self.pathmaps[coord] = SingleShortestPathMap(map, coord)
    

    def query_distance(self, source_coord: Coord, target_coord: Coord) -> int:
        pathmap = self.pathmaps[source_coord]
        return pathmap.query_distance(target_coord)
    

    def query_direction(self, source_coord: Coord, target_coord: Coord) -> Direction:
        pathmap = self.pathmaps[source_coord]
        return pathmap.query_direction(target_coord)


    def to_json(self) -> str:
        """Serialize all per-source shortest-path maps to a JSON string."""
        return json.dumps({
            f"{x},{y}": json.loads(pathmap.to_json())
            for (x, y), pathmap in self.pathmaps.items()
        })


    @classmethod
    def from_json(cls, data: str) -> "GroupedShortestPathMap":
        """Reconstruct a GroupedShortestPathMap from a JSON string produced by ``to_json``."""
        parsed = json.loads(data)
        obj = cls.__new__(cls)
        obj.pathmaps = {}
        for key, pathmap_data in parsed.items():
            x_str, y_str = key.split(",")
            coord = (int(x_str), int(y_str))
            obj.pathmaps[coord] = SingleShortestPathMap.from_json(json.dumps(pathmap_data))
        return obj