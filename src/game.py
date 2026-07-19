"""
Sets up the logic of the game.

- Step player if there is keyboard input
- If move player, check for pellet to consume
- Step enemy based on AI input
- If enemy on player, lose
"""

from dataclasses import dataclass
from copy import deepcopy

from src.entity import Entity, Player, Enemy
from src.map import Direction, Map

from src.terminal_visualizer import TerminalGameVisualizer
from src.visualizer import GameVisualizer

# Mere alias for easier reading
Action = Direction

@dataclass
class Observation:
    map: Map
    player: Player
    enemies: list[Enemy]

PELLET_SCORE = 1

class GameMap:

    def __init__(self, map: Map, player: Player, enemies: list[Enemy]) -> None:
        self.map = map
        self.player = player
        self.enemies = enemies
        
        # check the map allows these starting positions
        self._validate_coord_on_map(self.player)
        for enemy in self.enemies:
            self._validate_coord_on_map(enemy)

        self._set_initial_player_enemy_states(self.player, self.enemies)
        
        self.reset()
    
    def _set_initial_player_enemy_states(self, player: Player, enemies: list[Enemy]) -> None:
        # Cloning and storing initial state for later recreation
        self.init_player_state = deepcopy(player)
        self.init_enemy_states = [deepcopy(e) for e in enemies]
    
    def _validate_coord_on_map(self, entity: Entity) -> None:
        if not self.map.can_move(entity.coord):
            raise ValueError("Coordinate of the entity must be free in the corresponding map.")
    
    def reset(self) -> None:
        self.score = 0
        self.done = False
        self.won = False

        self.player = deepcopy(self.init_player_state)
        self.enemies = [deepcopy(e) for e in self.init_enemy_states]
    
    def step(self, player_action: Action, enemy_actions: list[Action]) -> tuple[Observation, bool, bool]:
        def _lose():
            self.done, self.won = True, False
        
        def _win():
            self.done, self.won = True, True
        
        prev_player_coord = tuple(self.player.coord)
        prev_enemy_coords = [tuple(e.coord) for e in self.enemies]
        
        # move player
        self.player.move(player_action, self.map)
        # if pellet is at the new location, consume it
        has_pellet = self.map.have_pellets([self.player.coord])[0]
        if has_pellet:
            self.map.consume_pellets([self.player.coord])
            self.score += PELLET_SCORE
        
        # move enemies
        for enemy, e_action in zip(self.enemies, enemy_actions):
            enemy.move(e_action, self.map)
        
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
            player=deepcopy(self.player), 
            enemies=[deepcopy(e) for e in self.enemies]
        )
    
    def request_player_action(self, observation: Observation) -> Action:
        context = {} # empty context for now
        return self.player.request_action(observation, context)

    def request_enemy_actions(self, observation: Observation) -> list[Action]:
        # add context for lookahead steps
        lookahead_sizes = [-3, 3, 1, -1]
        lookahead_sizes = lookahead_sizes[:len(self.enemies)]
        return [e.request_action(observation, {"lookahead_size": lasz}) 
                for e, lasz in zip(self.enemies, lookahead_sizes)]


def _create_visualizer(kind: str, game_map: GameMap, delay_ms: int):
    if kind == "tk":
        return GameVisualizer(game_map, delay_ms=delay_ms)
    if kind == "terminal":
        return TerminalGameVisualizer(game_map, delay_ms=delay_ms)
    return None


def game_loop(
    map: Map,
    player: Player,
    enemies: list[Enemy],
    delay_ms: int = 50,
    visualizer: str | bool = "tk",
) -> None:
    if visualizer is True:
        visualizer = "tk"
    elif visualizer is False:
        visualizer = "none"

    game_map = GameMap(map, player, enemies)

    observation = game_map.get_observation()
    done, won = False, False
    viz = _create_visualizer(visualizer, game_map, delay_ms)

    print("="*20)
    print("Starting a game!")
    print("="*20)

    if viz and not viz.render(observation):
        viz.close()
        return

    while not done:
        # request actions based on the current observation
        player_action = game_map.request_player_action(observation)
        enemy_actions = game_map.request_enemy_actions(observation)
        # take a step
        new_obs, done, won = game_map.step(player_action, enemy_actions)

        observation = new_obs

        if viz and not viz.render(observation, done=done, won=won):
            break

        # if delay_ms > 0:
        #     time.sleep(delay_ms / 1000)
    
    print("="*20)
    print(f"Player {'won!' if won else 'lost...'}")
    print(f"- Score: {game_map.score}")
    print("="*20)

    if viz:
        viz.render(observation, done=True, won=won)
        viz.wait_before_close()
        viz.close()