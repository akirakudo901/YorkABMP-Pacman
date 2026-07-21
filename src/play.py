"""
File for playing a game!
"""

import json
from pathlib import Path

from src.action_requester.precompute_shortest_path import GroupedShortestPathMap
from src.entity import Enemy, Player
from src.game import game_loop
from src.map import Coord, Map
from src.action_requester.ai import CoordMatchGhostAI, PhoebePlayerAI, ShortestPathGhostAI
from src.action_requester.controller import KeyboardController

KEYBOARD_TIMEOUT_MS = 200
DELAY_MS = 200
VIS_FORMAT = "terminal"

DEFAULT_ENEMY_LOOKAHEAD_SIZES = [-3, 3, 1, -1]

PRECOMPUTED_DIR = r"precomputed_shortest_path"

def make_game(
    map_file_path: str, 
    player_init_coord: Coord,
    enemy_init_coords: list[Coord],
    enemy_lookahead_sizes: list[int]=DEFAULT_ENEMY_LOOKAHEAD_SIZES,
    control_player: bool=False,
    use_best_path_ghost_ai: bool=True
    ):
    with open(map_file_path, 'r') as f:
        map_ascii = f.read()
    map = Map.map_from_ascii(map_ascii)

    if use_best_path_ghost_ai:
        precomputed_path = Path(PRECOMPUTED_DIR) / f"{Path(map_file_path).stem}_precomputed.json"
        # if pre-existing, load
        if precomputed_path.is_file():
            with open(precomputed_path, 'r') as f:
                content = json.load(f)
            precomputed_map = GroupedShortestPathMap.from_json(content)
        else:
            precomputed_map = GroupedShortestPathMap(map)
            precomputed_json = precomputed_map.to_json()
            with open(precomputed_path, 'w') as f:
                json.dump(precomputed_json, f)
        
        ghost_ai_cls = lambda: ShortestPathGhostAI(precomputed_map)
   
    else:
        ghost_ai_cls = CoordMatchGhostAI

    if control_player:
        player = Player(
            init_coord=player_init_coord, 
            action_requester=KeyboardController(timeout=KEYBOARD_TIMEOUT_MS/1000)
        )
    else:
        player = Player(init_coord=player_init_coord, action_requester=PhoebePlayerAI())
    
    enemy_lookahead_sizes = enemy_lookahead_sizes + [0] * len(enemy_init_coords)
    enemy_lookahead_sizes = enemy_lookahead_sizes[:len(enemy_init_coords)]
    enemies = [
        Enemy(init_coord=coord, action_requester=ghost_ai_cls(), 
              enemy_id=i, lookahead_size=lsz)
        for i, (coord, lsz) in enumerate(zip(enemy_init_coords, enemy_lookahead_sizes))
    ]
    
    game_loop(map=map, player=player, enemies=enemies, delay_ms=200, visualizer=VIS_FORMAT)

def game_small_grid(control_player: bool=False):
    FILE = "maps/9x9grid.txt"
    PLAYER_INIT_COORD = (0,0)
    ENEMY_INIT_COORDS = [
        (8,0), 
        # (8,8)
    ]

    make_game(FILE, PLAYER_INIT_COORD, ENEMY_INIT_COORDS, control_player=control_player)

def game_original_pacman(control_player: bool=False):
    FILE = "maps/orig_pacman_with_power_pellet.txt"
    PLAYER_INIT_COORD = (0,0)
    ENEMY_INIT_COORDS = [(0,28), (25,28)]

    make_game(FILE, PLAYER_INIT_COORD, ENEMY_INIT_COORDS, control_player=control_player)


if __name__ == "__main__":
    # You can play the small grid version of the game!
    # game_small_grid(control_player=False)
    # Or the original pacman game (no warp or power pellets)
    game_original_pacman(control_player=False)