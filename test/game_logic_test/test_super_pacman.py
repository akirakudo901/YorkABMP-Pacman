"""
Tests for super pacman mode.
"""

from src.entity import Enemy, Player
from src.game import GameMap
from src.map import Direction, Map

# Trigger

def test_consume_power_pellet_become_super_pacman():
    """Trigger: Consuming a power pellet turns the pacman into a super pacman"""

    map_ascii = \
"""
OO
..
"""
    map = Map.map_from_ascii(map_ascii)
    player = Player(init_coord=(0,0), action_requester=None, direction=Direction.RIGHT)
    
    assert not player.is_super_pacman_mode()

    gm = GameMap(map, player, enemies=[], super_pacman_len=30)
    obs, _, _ = gm.step(player_action=Direction.NEUTRAL, enemy_actions=[])

    assert obs.player.is_super_pacman_mode()
    assert obs.player.get_super_pacman_countdown() == 29 # first step consumes one countdown


def test_consume_another_power_pellet_refill():
    """Trigger: Consuming a new power pellet resets the countdown (not raw extension)"""
    map_ascii = \
"""
OO
..
"""
    map = Map.map_from_ascii(map_ascii)
    player = Player(init_coord=(0,0), action_requester=None, direction=Direction.RIGHT)

    gm = GameMap(map, player, enemies=[], super_pacman_len=30)
    obs, _, _ = gm.step(player_action=Direction.NEUTRAL, enemy_actions=[])

    assert obs.player.is_super_pacman_mode()
    assert obs.player.get_super_pacman_countdown() == 29 # first step consumes one countdown

    obs, _, _ = gm.step(player_action=Direction.NEUTRAL, enemy_actions=[])

    assert obs.player.get_super_pacman_countdown() == 28

    obs, _, _ = gm.step(player_action=Direction.RIGHT, enemy_actions=[])
    
    assert obs.player.is_super_pacman_mode()
    assert obs.player.get_super_pacman_countdown() == 29


# Expiry

def test_expiry_no_longer_super_pacman():
    """Expiry: After countdown is finished, we are no longer in super pacman mode"""
    map_ascii = \
"""
O.
..
"""
    map = Map.map_from_ascii(map_ascii)
    player = Player(init_coord=(0,0), action_requester=None, direction=Direction.RIGHT)

    gm = GameMap(map, player, enemies=[], super_pacman_len=3)
    obs, _, _ = gm.step(player_action=Direction.NEUTRAL, enemy_actions=[])

    assert obs.player.is_super_pacman_mode()
    assert obs.player.get_super_pacman_countdown() == 2 # first step consumes one countdown
    # one more tick, still super pacman
    obs, _, _ = gm.step(player_action=Direction.NEUTRAL, enemy_actions=[])

    assert obs.player.is_super_pacman_mode()
    assert obs.player.get_super_pacman_countdown() == 1
    # last tick, not super pacman anymore
    obs, _, _ = gm.step(player_action=Direction.NEUTRAL, enemy_actions=[])
    
    assert not obs.player.is_super_pacman_mode()
    assert obs.player.get_super_pacman_countdown() == 0


# Enemy

def test_collided_enemy_die_during_super_pacman():
    """Enemy: Enemy that overlaps / passes through the player are dead during super pacman mode"""
    map_ascii = \
"""
O.
..
"""
    map = Map.map_from_ascii(map_ascii)
    player = Player(init_coord=(0,0), action_requester=None, direction=Direction.RIGHT)
    enemies = [
        Enemy(init_coord=(1,0), action_requester=None, enemy_id=0, death_len=10),
        Enemy(init_coord=(1,1), action_requester=None, enemy_id=1, death_len=10),
        Enemy(init_coord=(0,1), action_requester=None, enemy_id=2, death_len=10)
    ]
    # activate super pacman
    gm = GameMap(map, player, enemies, super_pacman_len=30)
    obs, _, _ = gm.step(player_action=Direction.NEUTRAL, enemy_actions=[Direction.NEUTRAL]*3)

    assert obs.player.is_super_pacman_mode()
    # move: player to the right, enemy at (1,0) to the left, so they pass through each other
    #       enemy at (1,1) goes up, so it lands on the player
    #       enemy at (0,1) stays there
    obs, _, _ = gm.step(player_action=Direction.RIGHT, 
                        enemy_actions=[Direction.LEFT, Direction.UP, Direction.NEUTRAL])
    
    # still in super pacman mode
    assert obs.player.is_super_pacman_mode()
    # should be at the expected locations
    assert obs.player.coord == (1,0)
    assert obs.enemies[0].coord == (0,0)
    assert obs.enemies[1].coord == (1,0)
    assert obs.enemies[2].coord == (0,1)
    # expected status
    assert obs.enemies[0].is_dead()
    assert obs.enemies[1].is_dead()
    assert not obs.enemies[2].is_dead()


def test_dead_enemy_dont_move():
    """Enemy: When dead, enemies don't move"""
    map_ascii = \
"""
O.
..
"""
    map = Map.map_from_ascii(map_ascii)
    player = Player(init_coord=(0,0), action_requester=None, direction=Direction.RIGHT)
    enemies = [
        Enemy(init_coord=(1,0), action_requester=None, enemy_id=0, death_len=10),
        Enemy(init_coord=(0,1), action_requester=None, enemy_id=1, death_len=10)
    ]
    # activate super pacman
    gm = GameMap(map, player, enemies, super_pacman_len=30)
    obs, _, _ = gm.step(player_action=Direction.NEUTRAL, enemy_actions=[Direction.LEFT, Direction.NEUTRAL])

    assert obs.player.is_super_pacman_mode()
    # should be at the expected locations
    assert obs.player.coord == (0,0)
    assert obs.enemies[0].coord == (0,0)
    assert obs.enemies[1].coord == (0,1)
    # expected status
    assert obs.enemies[0].is_dead()
    assert not obs.enemies[1].is_dead()
    
    # then we ask them to move
    obs, _, _ = gm.step(player_action=Direction.NEUTRAL, 
                        enemy_actions=[Direction.RIGHT, Direction.RIGHT])
    
    # should be at the expected locations
    assert obs.player.coord == (0,0)
    assert obs.enemies[0].coord == (0,0) # didn't move
    assert obs.enemies[1].coord == (1,1) # did move


def test_revive_countdown_reduction_and_revive_at_end():
    """Enemy: Tick will deplete the revivew countdown; after countdown is finished, the enemy is revived"""
    map_ascii = \
"""
O.
..
"""
    map = Map.map_from_ascii(map_ascii)
    player = Player(init_coord=(0,0), action_requester=None, direction=Direction.RIGHT)
    enemies = [
        Enemy(init_coord=(1,0), action_requester=None, enemy_id=0, death_len=3),
        Enemy(init_coord=(0,1), action_requester=None, enemy_id=1, death_len=3)
    ]
    # activate super pacman
    gm = GameMap(map, player, enemies, super_pacman_len=30)
    obs, _, _ = gm.step(player_action=Direction.NEUTRAL, enemy_actions=[Direction.LEFT, Direction.NEUTRAL])

    assert obs.player.is_super_pacman_mode()
    # should be at the expected locations
    assert obs.player.coord == (0,0)
    assert obs.enemies[0].coord == (0,0)
    assert obs.enemies[1].coord == (0,1)
    # expected status
    assert obs.enemies[0].is_dead()
    assert obs.enemies[0].get_revive_countdown() == 2
    assert not obs.enemies[1].is_dead()

    obs, _, _ = gm.step(player_action=Direction.RIGHT, enemy_actions=[Direction.NEUTRAL]*2)

    # should be at the expected locations
    assert obs.player.coord == (1,0)
    assert obs.enemies[0].coord == (0,0)
    assert obs.enemies[1].coord == (0,1)
    # expected status
    assert obs.enemies[0].is_dead()
    assert obs.enemies[0].get_revive_countdown() == 1
    assert not obs.enemies[1].is_dead()

    obs, _, _ = gm.step(player_action=Direction.NEUTRAL, enemy_actions=[Direction.NEUTRAL]*2)

    # should be at the expected locations
    assert obs.player.coord == (1,0)
    assert obs.enemies[0].coord == (0,0)
    assert obs.enemies[1].coord == (0,1)
    # expected status: enemy 0 revived
    assert not obs.enemies[0].is_dead()
    assert not obs.enemies[1].is_dead()


if __name__ == "__main__":
    test_consume_power_pellet_become_super_pacman()
    test_consume_another_power_pellet_refill()
    
    test_expiry_no_longer_super_pacman()

    test_collided_enemy_die_during_super_pacman()
    test_dead_enemy_dont_move()
    test_revive_countdown_reduction_and_revive_at_end()