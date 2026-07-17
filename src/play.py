"""
File for playing a game!
"""

from src.entity import Enemy, Player
from src.game import game_loop
from src.map import Coord, Map
from src.action_requester.ai import CoordMatchGhostAI, PhoebePlayerAI
from src.action_requester.controller import KeyboardController

KEYBOARD_TIMEOUT_MS = 200
DELAY_MS = 200
VIS_FORMAT = "terminal"

def make_game(
    map_file_path: str, 
    player_init_coord: Coord,
    enemy_init_coords: list[Coord],
    control_player: bool=False
    ):
    with open(map_file_path, 'r') as f:
        map_ascii = f.read()
    map = Map.map_from_ascii(map_ascii)

    if control_player:
        player = Player(
            init_coord=player_init_coord, 
            action_requester=KeyboardController(timeout=KEYBOARD_TIMEOUT_MS/1000)
        )
    else:
        player = Player(init_coord=player_init_coord, action_requester=PhoebePlayerAI())
        
    enemies = [
        Enemy(init_coord=coord, action_requester=CoordMatchGhostAI(), enemy_id=i)
        for i, coord in enumerate(enemy_init_coords)
    ]
    
    game_loop(map=map, player=player, enemies=enemies, delay_ms=200, visualizer=VIS_FORMAT)

def game_small_grid(control_player: bool=False):
    FILE = "../maps/9x9grid.txt"
    PLAYER_INIT_COORD = (0,0)
    ENEMY_INIT_COORDS = [
        (8,0), 
        # (8,8)
    ]

    make_game(FILE, PLAYER_INIT_COORD, ENEMY_INIT_COORDS, control_player)

def game_original_pacman(control_player: bool=False):
    FILE = "../maps/orig_pacman_no_power_pellet.txt"
    PLAYER_INIT_COORD = (0,0)
    ENEMY_INIT_COORDS = [(0,28), (25,28)]

    make_game(FILE, PLAYER_INIT_COORD, ENEMY_INIT_COORDS, control_player)


if __name__ == "__main__":
    # You can play the small grid version of the game!
    # game_small_grid(control_player=False)
    # Or the original pacman game (no warp or power pellets)
    game_original_pacman(control_player=False)