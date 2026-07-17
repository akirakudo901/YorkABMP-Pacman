from src.action_requester.ai import CoordMatchGhostAI, PhoebePlayerAI
from src.entity import Enemy, Player
from src.game import GameMap
from src.map import Map
from src.terminal_visualizer import TerminalGameVisualizer

def test_SITUATION_NAME_SUCH_AS_move_towards_the_current_direction():
    initial_map_ascii = \
"""
.....
.WWW.
.WWW.
.WWW.
.....
"""
    # x increases to the right, y downwards
    #  so (0,0) is the top left corner
    PLAYER_INIT_COORD = (0,0)
    ENEMY_INIT_COORDS = [
        # (4,0), # don't need an enemey for this test case
        ]
    
    # create the initial map situation containing the trigger we want to explore
    init_map = Map.map_from_ascii(ascii_repr=initial_map_ascii)

    # create player with appropriate action requester AI of choice
    player = Player(init_coord=PLAYER_INIT_COORD, action_requester=PhoebePlayerAI())
        
    # create enemy with appropriate action requester AI of choice
    enemies = [
        Enemy(init_coord=coord, action_requester=CoordMatchGhostAI(), enemy_id=i)
        for i, coord in enumerate(ENEMY_INIT_COORDS)
    ]

    # create game map
    game_map = GameMap(init_map, player, enemies)
    # optionally attach a terminal visualizer to see the current state in the terminal
    tgv = TerminalGameVisualizer(game_map, delay_ms=0)
    # strictly optional visualization of result, useful for human intuition
    print("Initial map state:")
    tgv.render() # see what's current

    # take a step
    observation = game_map.get_observation()
    
    player_action = game_map.request_player_action(observation)
    enemy_actions = game_map.request_enemy_actions(observation)
    
    # step function gives you the new observation
    new_obs, _done, _won = game_map.step(player_action, enemy_actions)

    # then you wanna check what's happening in the new observation - is it as expected?

    
    # strictly optional visualization of result, useful for human intuition
    print("Obtained map state:")
    tgv.render()

if __name__ == "__main__":
    test_SITUATION_NAME_SUCH_AS_move_towards_the_current_direction()