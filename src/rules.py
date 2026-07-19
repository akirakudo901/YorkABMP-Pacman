# check if the pakman will hit the wall, if yes, change to another random direction
# direction with pellet nearby are preferred

import random
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
    dir = player.dir
    target = dir.move_towards(player.coord)

    if observation.map.can_move(target):
        return dir
    else:
        valid_dirs = []
        pellet_dirs = []

        for d in Direction:
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
    return None


def super_pacman_state_logic(observation: Observation) -> Direction:
    return None