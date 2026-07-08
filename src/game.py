"""
Sets up the logic of the game.

- Step player if there is keyboard input
- If move player, check for pellet to consume
- Step enemy based on AI input
- If enemy on player, lose
"""

from dataclasses import dataclass
from entity import Entity
from map import Coord, Direction, Map

# Mere alias for easier reading
Action = Direction

@dataclass
class Observation:
    map: Map
    player: Entity
    enemies: list[Entity]

PELLET_SCORE = 1

def _copy_entity(entity: Entity) -> Entity:
    """Copy an entity except the map which is a shallow copy, I think."""
    return Entity(
        init_coord=tuple(entity.coord),  
        map=entity.map, # points to the same still, but generally not an issue
        direction=entity.dir
    )

class GameMap:

    def __init__(self, map: Map, player: Entity, enemies: list[Entity]) -> None:
        self.map = map
        self.player = player
        self.enemies = enemies
        
        # set the map appropriately
        self.player.set_map(self.map)
        for enemy in self.enemies:
            enemy.set_map(self.map)

        self._set_initial_player_enemy_states(self.player, self.enemies)
        
        self.reset()
    
    def _set_initial_player_enemy_states(self, player: Entity, enemies: list[Entity]) -> None:
        # Cloning and storing initial state for later recreation
        self.init_player_state = _copy_entity(player)
        self.init_enemy_states = [_copy_entity(e) for e in enemies]
    
    def reset(self) -> None:
        self.score = 0
        self.done = False
        self.won = False

        self.player = _copy_entity(self.init_player_state)
        self.enemies = [_copy_entity(e) for e in self.init_enemy_states]
    
    def step(self, player_action: Action, enemy_actions: list[Action]) -> tuple[Observation, bool, bool]:
        def _lose():
            self.done, self.won = True, False
        
        def _win():
            self.done, self.won = True, True
        
        prev_player_coord = tuple(self.player.coord)
        prev_enemy_coords = [tuple(e.coord) for e in self.enemies]
        
        # move player
        self.player.move(player_action)
        # if pellet is at the new location, consume it
        has_pellet = self.map.have_pellets([self.player.coord])[0]
        if has_pellet:
            self.map.consume_pellets([self.player.coord])
            self.score += PELLET_SCORE
        
        # move enemies
        for enemy, e_action in zip(self.enemies, enemy_actions):
            enemy.move(e_action)
        
        # create the observation
        obs = self.get_observation()
        
        # if enemies are on top of the player, or they passed through each other, lose
        for enemy, prev_enemy_coord in zip(self.enemies, prev_enemy_coords):
            if (self.player.coord == enemy.coord or \
                self.player.coord == prev_enemy_coord and prev_player_coord == enemy.coord):
                _lose()
                return obs, self.done, self.won
        # if there's no more pellet otherwise, win
        if self.map.have_no_pellet():
            _win()
        return obs, self.done, self.won
    
    def get_observation(self) -> Observation:
        return Observation(
            map=self.map,
            player=_copy_entity(self.player), 
            enemies=[_copy_entity(e) for e in self.enemies]
        )
    
    def request_player_action(self, observation: Observation) -> Action:
        context = {} # empty context for now
        return self.player.request_action(observation, context)

    def request_enemy_actions(self, observation: Observation) -> list[Action]:
        context = {} # empty context for now
        return [e.request_action(observation, context) for e in self.enemies]
