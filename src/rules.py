# check if the pakman will hit the wall, if yes, change to another random direction
# direction with pellet nearby are preferred

import random
from src.game import Observation
from src.map import Direction

# Takes in an observation, and outputs a Direction object (random)
# See the ```game.py``` file for the definition & details of Observation (a bit complicated).`
# A Direction object is one of: 
# - Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT
# - Direction.NEUTRAL for no input / motion
def request_action(observation: Observation) -> Direction:

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