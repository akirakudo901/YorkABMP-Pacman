# check if the pakman will hit the wall, if yes, change to another random direction
# direction with pellet nearby are preferred

import random
from typing import Any

from src.game import Observation
from src.map import Coord, Direction

RUSH_MODE_NAME = "rush"
IN_DANGER_MODE_NAME = "in_danger"
GREEDY_MODE_NAME = "greedy"
BIG_PACMAN_MODE_NAME = "big_pacman"

# "within the 3 units" -> radius of the pellet search perimeter around Pacman.
PELLET_SEARCH_RADIUS = 3

# The four real moves (NEUTRAL is not a travel direction).
MOVE_DIRS = [Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT]

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
    if is_ghost_nearby(observation, danger_dist=3):
        player.set_mode(IN_DANGER_MODE_NAME)

    # we run the logic under the different states
    if player_mode == RUSH_MODE_NAME:
        action = rush_state_logic(observation)
    elif player_mode == IN_DANGER_MODE_NAME:
        action = in_danger_state_logic(observation)
    elif player_mode == GREEDY_MODE_NAME:
        action = greedy_state_logic(observation)
    elif player_mode == BIG_PACMAN_MODE_NAME:
        action = super_pacman_state_logic(observation)
    else:
        raise Exception(f"Player mode {player_mode} isn't implemented.")
    
    return action


# --------------------------------------------------------------------------- #
# Rush state -- "Free Move": eat as many pellets as possible.
#
# State variables (see slide "State Variable: Rush"):
# - distance(a, b)           : units between two objects on the map
# - hit_the_wall(coord, dir) : True if the cell one step in `dir` is a wall
# - pellet_in_distance(dir)  : pellets along the path in `dir`, up to 3 units
#
# Trigger conditions:
# 1. choose the path with the largest value of pellet_in_distance
# 2. if hit_the_wall == True, turn around
# --------------------------------------------------------------------------- #

def rush_state_logic(observation: Observation) -> Direction:
    player = observation.player
    coord = player.coord
    current_dir = player.dir

    # Valid directions are the ones that do NOT hit a wall (hit_the_wall == False).
    valid_dirs = [d for d in MOVE_DIRS if not hit_the_wall(observation, coord, d)]
    if not valid_dirs:
        return Direction.NEUTRAL  # fully boxed in (should not happen on a real map)

    # Score every valid direction by how many pellets its path holds within 3 units.
    scores = {d: pellet_in_distance(observation, coord, d) for d in valid_dirs}
    best_score = max(scores.values())

    # Trigger condition 2: if going straight would hit a wall, we MUST turn.
    must_turn = hit_the_wall(observation, coord, current_dir)

    # Keep momentum: if we can keep going straight and no other path is strictly
    # richer in pellets, don't turn. This avoids jittering on empty corridors.
    if not must_turn and scores[current_dir] >= best_score:
        return current_dir

    # Trigger condition 1: choose the path with the largest pellet_in_distance.
    best_dirs = [d for d in valid_dirs if scores[d] == best_score]

    # Prefer not to reverse into where we just came from when a real choice exists.
    back = opposite(current_dir)
    non_reverse = [d for d in best_dirs if d != back]
    choices = non_reverse if non_reverse else best_dirs

    return random.choice(choices)


def distance(a: Coord, b: Coord) -> int:
    """State variable `distance`: number of grid (Manhattan) units between
    two objects, matching how `distance` is drawn on the slides.
    """
    (ax, ay), (bx, by) = a, b
    return abs(ax - bx) + abs(ay - by)


def hit_the_wall(observation: Observation, coord: Coord, dir: Direction) -> bool:
    """State variable `hit_the_wall`: True if the cell one step in `dir` is not
    walkable -- the distance to that obstacle is 0 and moving is impossible.
    """
    return not observation.map.can_move(dir.move_towards(coord))


def pellet_in_distance(
    observation: Observation,
    coord: Coord,
    dir: Direction,
    radius: int = PELLET_SEARCH_RADIUS,
    normal_pellet_score: int=1,
    power_pellet_score: int=1,
) -> int:
    """State variable `pellet_in_distance`: number of pellets in the straight
    path along `dir`, looking up to `radius` units ahead. The scan stops at a
    wall, because a wall ends the path.

    Can optionally weight normal vs. power pellets differently, e.g. to prioritize
    paths with power pellets.
    """
    count = 0
    cur = coord
    for _ in range(radius):
        cur = dir.move_towards(cur)
        if not observation.map.can_move(cur):
            break  # wall ends this corridor
        if observation.map.have_normal_pellets([cur])[0]:
            count += normal_pellet_score
        elif observation.map.have_power_pellets([cur])[0]:
            count += power_pellet_score
    return count


def opposite(dir: Direction) -> Direction:
    """The reverse of a travel direction (used to avoid pointless back-tracking)."""
    dx, dy = dir.delta()
    return Direction.delta_to_dir((-dx, -dy))


# --------------------------------------------------------------------------- #
# In danger state
# --------------------------------------------------------------------------- #

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


# --------------------------------------------------------------------------- #
# Greedy state
# 
#  Triggered when there is a power pellet within 3 units of distance
#     - Moves to eat the power pellet
#     - Otherwise, prioritize pellets
#     - Otherwise, keep going the same direction if possible
#     - Otherwise, turn to the sides if possible
#     - Otherwise, turn around
# --------------------------------------------------------------------------- #

def greedy_state_logic(observation: Observation) -> Direction:
    # Currently, only a slight change from the "rush" logic
    player = observation.player
    coord = player.coord
    current_dir = player.dir

    # Valid directions are the ones that do NOT hit a wall
    valid_dirs = [d for d in MOVE_DIRS if not hit_the_wall(observation, coord, d)]
    if not valid_dirs:
        return Direction.NEUTRAL  # fully boxed in (should not happen on a real map)

    # Score every valid direction by how many pellets its path holds within 3 units.
    # Weight power pellets as much higher so that we prioritize them
    scores = {
        d: pellet_in_distance(observation, coord, d, normal_pellet_score=1, power_pellet_score=5) 
        for d in valid_dirs
        }
    best_score = max(scores.values())

    # If going straight would hit a wall, we MUST turn.
    must_turn = hit_the_wall(observation, coord, current_dir)

    # Keep momentum: if we can keep going straight and no other path is strictly
    # richer in pellets, don't turn. This avoids jittering on empty corridors.
    if not must_turn and scores[current_dir] >= best_score:
        return current_dir

    # Otherwise choose the path with the largest score.
    best_dirs = [d for d in valid_dirs if scores[d] == best_score]

    # Prefer not to reverse into where we just came from when a real choice exists.
    back = opposite(current_dir)
    non_reverse = [d for d in best_dirs if d != back]
    choices = non_reverse if non_reverse else best_dirs

    return random.choice(choices)


# --------------------------------------------------------------------------- #
# Super pacman state
# 
# Pacman is here while in "super pacman" mode: 30 frames after eating a power pellet
#     - If a ghost is within 3 units of distance, chase it
# --------------------------------------------------------------------------- #
def super_pacman_state_logic(observation: Observation) -> Direction:
    player = observation.player
    enemies = observation.enemies
    player_pos = player.coord

    # we wanna pick the direction that minimizes the distance to the closest ghost
    best_dir = Direction.NEUTRAL
    min_ghost_dist = float('inf')

    for d in Direction:
        if d == Direction.NEUTRAL: continue
        target = d.move_towards(player_pos)
        if observation.map.can_move(target):
            # for this direction, check: what is the direction to the closest ghost?
            dist_to_enemies = [
                get_distance(target, enemy.coord) 
                for enemy in enemies if not enemy.is_dead()
            ]
            min_dist = min(dist_to_enemies)
            
            # we keep the direction that minimizes the minimum distance to a ghost
            if min_ghost_dist > min_dist:
                best_dir = d
                min_ghost_dist = min_dist
            
    return best_dir

