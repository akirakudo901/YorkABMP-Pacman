import unittest
from src.map import Map
from src.entity import Player, Enemy
from src.game import Observation
from src.rules import request_action, IN_DANGER_MODE_NAME, RUSH_MODE_NAME

class TestInDangerTransition(unittest.TestCase):

    def setUp(self):
        # Initialize a simple 5x5 map without loading from a file to keep the test lightweight and isolated.
        self.map = Map(size_x=5, size_y=5)

    def test_stay_in_rush_mode_at_safe_distance(self):
        """
        [Boundary Test: Distance = 4]
        Test that Pacman remains in 'rush' mode when the closest active ghost 
        is at a Manhattan distance of exactly 4 (just outside the danger zone).
        """
        player = Player(init_coord=(0, 0), action_requester=None)
        
        # Ghost at (4, 0) -> Manhattan distance: |0-4| + |0-0| = 4
        enemy = Enemy(init_coord=(4, 0), action_requester=None, enemy_id=0)
        
        obs = Observation(map=self.map, player=player, enemies=[enemy])
        request_action(obs)
        
        # Assert: Pacman should still feel safe and stay in rush mode
        self.assertEqual(player.get_mode(), RUSH_MODE_NAME)

    def test_switch_to_in_danger_at_critical_threshold(self):
        """
        [Boundary Test: Distance = 3]
        Test that Pacman immediately triggers 'in_danger' mode when the closest
        active ghost steps onto the exact threshold boundary of 3.
        """
        player = Player(init_coord=(0, 0), action_requester=None)
        
        # Ghost at (3, 0) -> Manhattan distance: |0-3| + |0-0| = 3
        enemy = Enemy(init_coord=(3, 0), action_requester=None, enemy_id=0)
        
        obs = Observation(map=self.map, player=player, enemies=[enemy])
        request_action(obs)
        
        # Assert: Pacman must trigger defensive state instantly at 3 steps
        self.assertEqual(player.get_mode(), IN_DANGER_MODE_NAME)

    def test_switch_to_in_danger_when_very_close(self):
        """
        [General Test: Distance = 2]
        Test that Pacman switches to 'in_danger' mode when a ghost is well within 
        the danger threshold (distance <= 3).
        """
        player = Player(init_coord=(0, 0), action_requester=None)
        
        # Ghost at (2, 0) -> Manhattan distance: |0-2| + |0-0| = 2
        enemy = Enemy(init_coord=(2, 0), action_requester=None, enemy_id=0)
        
        obs = Observation(map=self.map, player=player, enemies=[enemy])
        request_action(obs)
        
        self.assertEqual(player.get_mode(), IN_DANGER_MODE_NAME)

if __name__ == '__main__':
    unittest.main()