import unittest
from src.map import Map
from src.entity import Player, Enemy
from src.game import Observation
from src.rules import request_action, RUSH_MODE_NAME, IN_DANGER_MODE_NAME

# Constant for the refactored parent macro-state
GREEDY_MODE_NAME = "UNTHREATENED_GREEDY" 

class TestGreedyModeTransitions(unittest.TestCase):

    def setUp(self):
        # Initialize a lightweight 5x5 map for isolated boundary testing.
        self.map = Map(size_x=5, size_y=5)

    # =========================================================================
    # 1. Mode Switch From RUSH to UNTHREATENED GREEDY
    # =========================================================================

    def test_rush_to_greedy_boundary_distance_3(self):
        """
        [Boundary Test: Big Pellet Distance = 3, No Ghost]
        Verifies that when Pacman is in RUSH mode, if a big pellet is exactly at 
        the critical threshold of 3 units away, and there are no ghost threats 
        within 3 units, the agent successfully transitions into the GREEDY macro-state.
        """
        player = Player(init_coord=(0, 0), action_requester=None)
        player.set_mode(RUSH_MODE_NAME)
        
        # Place a big pellet at (3, 0) -> Manhattan distance: |0-3| + |0-0| = 3
        self.map.add_big_pellet(x=3, y=0) 
        
        # Place a ghost safely out of range
        enemy = Enemy(init_coord=(4, 4), action_requester=None, enemy_id=0)
        
        obs = Observation(map=self.map, player=player, enemies=[enemy])
        request_action(obs)
        
        # Assert: Pacman should successfully lock onto the greedy resource intent
        self.assertEqual(player.get_mode(), GREEDY_MODE_NAME)

    def test_remain_in_rush_when_big_pellet_at_distance_4(self):
        """
        [Boundary Test: Big Pellet Distance = 4, No Ghost]
        Verifies that when the big pellet is at a distance of 4 (just outside the 
        greedy activation threshold), Pacman does not prematurely switch states 
        and naturally maintains RUSH exploration mode.
        """
        player = Player(init_coord=(0, 0), action_requester=None)
        player.set_mode(RUSH_MODE_NAME)
        
        # Place a big pellet at (4, 0) -> Manhattan distance = 4
        self.map.add_big_pellet(x=4, y=0)
        enemy = Enemy(init_coord=(4, 4), action_requester=None, enemy_id=0)
        
        obs = Observation(map=self.map, player=player, enemies=[enemy])
        request_action(obs)
        
        self.assertEqual(player.get_mode(), RUSH_MODE_NAME)

    def test_rush_to_greedy_blocked_by_ghost_within_perimeter(self):
        """
        [Safety Constraint Test: Pellet <= 3 AND Ghost <= 3]
        Verifies the global safety interrupt override: even though a big pellet is 
        highly attractive within 3 units, if a ghost is also detected within the 
        3-unit perimeter, safety takes priority and the agent must not enter GREEDY mode.
        """
        player = Player(init_coord=(0, 0), action_requester=None)
        player.set_mode(RUSH_MODE_NAME)
        
        # Big pellet is close at (2, 0), but a ghost is threatening at (0, 2)
        self.map.add_big_pellet(x=2, y=0)
        enemy = Enemy(init_coord=(0, 2), action_requester=None, enemy_id=0)
        
        obs = Observation(map=self.map, player=player, enemies=[enemy])
        request_action(obs)
        
        # Assert: The safety-first priority must block the GREEDY transition
        self.assertNotEqual(player.get_mode(), GREEDY_MODE_NAME)
        self.assertEqual(player.get_mode(), IN_DANGER_MODE_NAME)

    # =========================================================================
    # 2. Mode Switch From IN_DANGER to UNTHREATENED GREEDY
    # =========================================================================

    def test_danger_to_greedy_when_threat_cleared(self):
        """
        [Recovery Transition Test: Ghost clears perimeter, Pellet exists]
        Verifies the recovery logic from IN_DANGER: once the active threat retreats 
        beyond the 3-unit boundary (e.g., distance = 4), and a big pellet remains 
        available within 3 units, the state machine successfully re-engages GREEDY mode.
        """
        player = Player(init_coord=(0, 0), action_requester=None)
        player.set_mode(IN_DANGER_MODE_NAME) # Start in a defensive state
        
        # Threat cleared: Ghost moves to (4, 0) -> Distance = 4
        enemy = Enemy(init_coord=(4, 0), action_requester=None, enemy_id=0)
        # Target still viable: Big pellet is at (0, 2) -> Distance = 2
        self.map.add_big_pellet(x=0, y=2)
        
        obs = Observation(map=self.map, player=player, enemies=[enemy])
        request_action(obs)
        
        # Assert: Threat is gone, immediately pivot back to the resource target
        self.assertEqual(player.get_mode(), GREEDY_MODE_NAME)

if __name__ == '__main__':
    unittest.main()