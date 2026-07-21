import unittest
from src.map import Map
from src.entity import Player, Enemy
from src.game import Observation
from src.rules import request_action, IN_DANGER_MODE_NAME, RUSH_MODE_NAME
# The counter-hunting tests refer to the greedy/economic macro-state as ECONOMIC_MODE_NAME.
from src.rules import GREEDY_MODE_NAME as ECONOMIC_MODE_NAME

class TestInDangerTransition(unittest.TestCase):

    def setUp(self):
        # Initialize a simple 5x5 map without loading from a file to keep the test lightweight and isolated.
        self.map = Map(size_x=5, size_y=5)
    # =========================================================================
    # 1. Mode or State switch From Rush to Indanger(Defensive)
    # =========================================================================
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

    # =========================================================================
    # 2. Mode or State switch From Greedy to Indanger(Defensive)
    # =========================================================================

    # (Inverse Counter-Hunting Boundaries)
    def test_economic_with_2_frames_left_and_close_ghost_remains_economic(self):
        """
        [Counter-Hunting Boundary: remaining = 2, Dist <= 2]
        Verifies the aggressive economic retention strategy. With 2 super-pacman
        frames left, if a ghost is within extreme close proximity (Distance <= 2),
        Pacman assumes a high probability of consuming the threat/pellet and safely
        stays in ECONOMIC mode.
        """
        player = Player(init_coord=(0, 0), action_requester=None)
        player.set_mode(ECONOMIC_MODE_NAME)
        player.super_pacman_countdown = 2
            
        # Ghost at Distance = 2 -> Should trigger aggressive retention
        enemy = Enemy(init_coord=(2, 0), action_requester=None, enemy_id=0)
        obs = Observation(map=self.map, player=player, enemies=[enemy])
        request_action(obs)
        
        self.assertEqual(player.get_mode(), ECONOMIC_MODE_NAME)

    def test_economic_with_2_frames_left_and_dist_3_switches_to_in_danger(self):
        """
        [Counter-Hunting Boundary: remaining = 2, Dist = 3]
        Verifies the strategic retreat fallback. With 2 super-pacman frames left,
        if a ghost is at an awkward tactical distance (Distance = 3), Pacman flags
        it as an unviable counter-hunt opportunity and preemptively switches to
        IN_DANGER mode.
        """
        player = Player(init_coord=(0, 0), action_requester=None)
        player.set_mode(ECONOMIC_MODE_NAME)
        player.super_pacman_countdown = 2
            
        # Ghost at Distance = 3 -> Tactical ambiguity triggers safety retreat
        enemy = Enemy(init_coord=(3, 0), action_requester=None, enemy_id=0)
        obs = Observation(map=self.map, player=player, enemies=[enemy])
        request_action(obs)
        
        self.assertEqual(player.get_mode(), IN_DANGER_MODE_NAME)

    def test_economic_with_1_frame_left_and_dist_1_remains_economic(self):
        """
        [Counter-Hunting Boundary: remaining = 1, Dist = 1]
        Verifies immediate close-quarters aggression. With 1 super-pacman frame
        left, a ghost right next to Pacman (Distance = 1) is targeted for an
        instant capture, maintaining the active ECONOMIC state execution.
        """
        player = Player(init_coord=(0, 0), action_requester=None)
        player.set_mode(ECONOMIC_MODE_NAME)
        player.super_pacman_countdown = 1
            
        # Ghost at Distance = 1 -> Direct contact option preserves economic farming
        enemy = Enemy(init_coord=(1, 0), action_requester=None, enemy_id=0)
        obs = Observation(map=self.map, player=player, enemies=[enemy])
        request_action(obs)
        
        self.assertEqual(player.get_mode(), ECONOMIC_MODE_NAME)

    def test_economic_with_1_frame_left_and_dist_2_or_3_switches_to_in_danger(self):
        """
        [Counter-Hunting Boundary: remaining = 1, Dist = 2 and 3]
        Verifies perimeter defense activation right before final timeout. With 1
        super-pacman frame left, ghost distances of 2 or 3 cannot guarantee an
        instant consume loop, forcing an immediate switch to IN_DANGER mode for
        defense.
        """
        # Test Sub-case: Distance = 2
        player_d2 = Player(init_coord=(0, 0), action_requester=None)
        player_d2.set_mode(ECONOMIC_MODE_NAME)
        player_d2.super_pacman_countdown = 1
        enemy_d2 = Enemy(init_coord=(2, 0), action_requester=None, enemy_id=0)
        obs_d2 = Observation(map=self.map, player=player_d2, enemies=[enemy_d2])
        request_action(obs_d2)
        self.assertEqual(player_d2.get_mode(), IN_DANGER_MODE_NAME)

        # Test Sub-case: Distance = 3
        player_d3 = Player(init_coord=(0, 0), action_requester=None)
        player_d3.set_mode(ECONOMIC_MODE_NAME)
        player_d3.super_pacman_countdown = 1
        enemy_d3 = Enemy(init_coord=(3, 0), action_requester=None, enemy_id=0)
        obs_d3 = Observation(map=self.map, player=player_d3, enemies=[enemy_d3])
        request_action(obs_d3)
        self.assertEqual(player_d3.get_mode(), IN_DANGER_MODE_NAME)

    def test_economic_with_1_frame_left_and_safe_distance_remains_economic(self):
        """
        [Counter-Hunting Boundary: remaining = 1, Dist > 3]
        Ensures that when ghosts are completely out of range (Distance > 3), Pacman
        naturally keeps clearing resources in ECONOMIC mode without false defensive
        alerts.
        """
        player = Player(init_coord=(0, 0), action_requester=None)
        player.set_mode(ECONOMIC_MODE_NAME)
        player.super_pacman_countdown = 1
            
        # Ghost far away at Distance = 4
        enemy = Enemy(init_coord=(4, 0), action_requester=None, enemy_id=0)
        obs = Observation(map=self.map, player=player, enemies=[enemy])
        request_action(obs)
        
        self.assertEqual(player.get_mode(), ECONOMIC_MODE_NAME)

    def test_economic_to_in_danger_when_super_expired(self):
        """
        [Standard Baseline Boundary: remaining = 0, Dist <= 3]
        Validates that once super pacman has expired (countdown = 0), the aggressive
        retention logic expires. Any ghost within the standard radius
        (Distance <= 3) universally triggers a transition to IN_DANGER mode.
        """
        # Test Sub-case: remaining = 0, Distance = 3
        player_expired = Player(init_coord=(0, 0), action_requester=None)
        player_expired.set_mode(ECONOMIC_MODE_NAME)
        player_expired.super_pacman_countdown = 0
        enemy_expired = Enemy(init_coord=(3, 0), action_requester=None, enemy_id=0)
        obs_expired = Observation(map=self.map, player=player_expired, enemies=[enemy_expired])
        request_action(obs_expired)
        self.assertEqual(player_expired.get_mode(), IN_DANGER_MODE_NAME)

        # Test Sub-case: remaining = 0, Distance = 2
        player_expired2 = Player(init_coord=(0, 0), action_requester=None)
        player_expired2.set_mode(ECONOMIC_MODE_NAME)
        player_expired2.super_pacman_countdown = 0
        enemy_expired2 = Enemy(init_coord=(2, 0), action_requester=None, enemy_id=0)
        obs_expired2 = Observation(map=self.map, player=player_expired2, enemies=[enemy_expired2])
        request_action(obs_expired2)
        self.assertEqual(player_expired2.get_mode(), IN_DANGER_MODE_NAME)

if __name__ == '__main__':
    unittest.main()
