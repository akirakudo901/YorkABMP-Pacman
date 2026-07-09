# check if the pakman will hit the wall, if yes, change to another random direction
# direction with pellet nearby are preferred

import random
from game import Observation
from map import Direction

# takes in an observation, and outputs a Direction object (random)
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