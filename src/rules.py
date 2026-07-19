# check if the pakman will hit the wall, if yes, change to another random direction
# direction with pellet nearby are preferred

import random
from src.game import Observation
from src.map import Direction

RUSH_MODE_NAME = "rush"
IN_DANGER_MODE_NAME = "in_danger"
BIG_PACMAN_MODE_NAME = "big_pacman"
from src.game import Observation
from src.map import Direction

RUSH_MODE_NAME = "rush"
IN_DANGER_MODE_NAME = "in_danger"
BIG_PACMAN_MODE_NAME = "big_pacman"

# Takes in an observation, and outputs a Direction object (random)
# See the ```game.py``` file for the definition & details of Observation (a bit complicated).`
# A Direction object is one of: 
# - Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT
# - Direction.NEUTRAL for no input / motion
# Takes in an observation, and outputs a Direction object (random)
# See the ```game.py``` file for the definition & details of Observation (a bit complicated).`
# A Direction object is one of: 
# - Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT
# - Direction.NEUTRAL for no input / motion
def request_action(observation: Observation) -> Direction:
    player = observation.player

    player_mode = player.get_mode()
    
    # initial state: unset, left as empty. Then, set to default which is rush
    if player_mode == "":
        player.set_mode(RUSH_MODE_NAME)
        player_mode = player.get_mode()

    # Switch between "modes" based on triggers!
    

    # we run the logic under the different states
    if player_mode == RUSH_MODE_NAME:
        action = rush_state_logic(observation)
    elif player_mode == IN_DANGER_MODE_NAME:
        action = in_danger_state_logic(observation)
    elif player_mode == BIG_PACMAN_MODE_NAME:
        action = super_pacman_state_logic(observation)
    else:
        raise Exception(f"Player mode {player_mode} isn't implemented.")
    
    return action


def rush_state_logic(observation: Observation) -> Direction:
    player = observation.player

    player_mode = player.get_mode()
    
    # initial state: unset, left as empty. Then, set to default which is rush
    if player_mode == "":
        player.set_mode(RUSH_MODE_NAME)
        player_mode = player.get_mode()

    # Switch between "modes" based on triggers!
    

    # we run the logic under the different states
    if player_mode == RUSH_MODE_NAME:
        action = rush_state_logic(observation)
    elif player_mode == IN_DANGER_MODE_NAME:
        action = in_danger_state_logic(observation)
    elif player_mode == BIG_PACMAN_MODE_NAME:
        action = super_pacman_state_logic(observation)
    else:
        raise Exception(f"Player mode {player_mode} isn't implemented.")
    
    return action


def rush_state_logic(observation: Observation) -> Direction:
    player = observation.player
    dir = player.dir
    target = dir.move_towards(player.coord)

    if observation.map.can_move(target):
        return dir
    else:
        valid_dirs = []
        pellet_dirs = []

        for d in Direction:
            if d == Direction.NEUTRAL: continue
            if d == Direction.NEUTRAL: continue
            target = d.move_towards(player.coord)
            if observation.map.can_move(target):
                valid_dirs.append(d)
                if observation.map.have_pellets([target])[0]:
                    pellet_dirs.append(d)

        if not pellet_dirs:
            return random.choice(valid_dirs)
        else:
            return random.choice(pellet_dirs)


def in_danger_state_logic(observation: Observation) -> Direction:
    player = observation.player
    enemies = observation.enemies
    player_pos = player.coord
    valid_dirs = []

    max_ghost_dist = float('inf')
    best_dir = Direction.NEUTRAL

    for d in Direction:
        if d == Direction.NEUTRAL: continue
        target = d.move_towards(player_pos)
        if observation.map.can_move(target):
            valid_dirs.append(d)
            for enemy in enemies:
                if not enemy.is_dead():
                    dist = get_distance(target, enemy.coord)
                    if dist > max_ghost_dist:
                        max_ghost_dist = dist
                        best_dir = d

            
    if not valid_dirs:
        return Direction.NEUTRAL
    else:
        return best_dir

def get_distance(x, y):
    return abs(x[0] - y[0]) + abs(x[1] - y[1])

def is_ghost_nearby(observation:Observation, danger_dist: int = 3) -> bool:
    player_pos = observation.player.coord
    enemies = observation.enemies

    for enemy in enemies:
        if not enemy.is_dead():
            ghost_pos = enemy.coord
            dist = get_distance(player_pos, ghost_pos)
            if dist < danger_dist:
                return True
    
    return False


def super_pacman_state_logic(observation: Observation) -> Direction:
    return None