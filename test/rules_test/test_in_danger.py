import unittest
from src.map import Map
from src.entity import Player, Enemy
from src.game import Observation
from src.rules import request_action, IN_DANGER_MODE_NAME, RUSH_MODE_NAME

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
    def test_economic_at_28s_with_close_ghost_remains_economic(self):
        """
        [Counter-Hunting Boundary: T = 28s, Dist <= 2]
        Verifies the aggressive economic retention strategy. At 28 seconds, if a ghost 
        is within extreme close proximity (Distance <= 2), Pacman assumes a high probability 
        of consuming the threat/pellet and safely stays in ECONOMIC mode.
        """
        player = Player(init_coord=(0, 0), action_requester=None)
        player.set_mode(ECONOMIC_MODE_NAME)
        if hasattr(player, 'state_timer'):
            player.state_timer = 28
            
        # Ghost at Distance = 2 -> Should trigger aggressive retention
        enemy = Enemy(init_coord=(2, 0), action_requester=None, enemy_id=0)
        obs = Observation(map=self.map, player=player, enemies=[enemy])
        request_action(obs)
        
        self.assertEqual(player.get_mode(), ECONOMIC_MODE_NAME)

    def test_economic_at_28s_with_dist_3_switches_to_in_danger(self):
        """
        [Counter-Hunting Boundary: T = 28s, Dist = 3]
        Verifies the strategic retreat fallback. At 28 seconds, if a ghost is at an awkward 
        tactical distance (Distance = 3), Pacman flags it as an unviable counter-hunt opportunity 
        and preemptively switches to IN_DANGER mode.
        """
        player = Player(init_coord=(0, 0), action_requester=None)
        player.set_mode(ECONOMIC_MODE_NAME)
        if hasattr(player, 'state_timer'):
            player.state_timer = 28
            
        # Ghost at Distance = 3 -> Tactical ambiguity triggers safety retreat
        enemy = Enemy(init_coord=(3, 0), action_requester=None, enemy_id=0)
        obs = Observation(map=self.map, player=player, enemies=[enemy])
        request_action(obs)
        
        self.assertEqual(player.get_mode(), IN_DANGER_MODE_NAME)

    def test_economic_at_29s_with_dist_1_remains_economic(self):
        """
        [Counter-Hunting Boundary: T = 29s, Dist = 1]
        Verifies immediate close-quarters aggression. At 29 seconds, a ghost right next 
        to Pacman (Distance = 1) is targeted for an instant capture, maintaining the active 
        ECONOMIC state execution.
        """
        player = Player(init_coord=(0, 0), action_requester=None)
        player.set_mode(ECONOMIC_MODE_NAME)
        if hasattr(player, 'state_timer'):
            player.state_timer = 29
            
        # Ghost at Distance = 1 -> Direct contact option preserves economic farming
        enemy = Enemy(init_coord=(1, 0), action_requester=None, enemy_id=0)
        obs = Observation(map=self.map, player=player, enemies=[enemy])
        request_action(obs)
        
        self.assertEqual(player.get_mode(), ECONOMIC_MODE_NAME)

    def test_economic_at_29s_with_dist_2_or_3_switches_to_in_danger(self):
        """
        [Counter-Hunting Boundary: T = 29s, Dist = 2 and 3]
        Verifies perimeter defense activation right before final timeout. At 29 seconds, 
        ghost distances of 2 or 3 cannot guarantee an instant consume loop, forcing an 
        immediate switch to IN_DANGER mode for defense.
        """
        # Test Sub-case: Distance = 2
        player_d2 = Player(init_coord=(0, 0), action_requester=None)
        player_d2.set_mode(ECONOMIC_MODE_NAME)
        if hasattr(player_d2, 'state_timer'): player_d2.state_timer = 29
        enemy_d2 = Enemy(init_coord=(2, 0), action_requester=None, enemy_id=0)
        obs_d2 = Observation(map=self.map, player=player_d2, enemies=[enemy_d2])
        request_action(obs_d2)
        self.assertEqual(player_d2.get_mode(), IN_DANGER_MODE_NAME)

        # Test Sub-case: Distance = 3
        player_d3 = Player(init_coord=(0, 0), action_requester=None)
        player_d3.set_mode(ECONOMIC_MODE_NAME)
        if hasattr(player_d3, 'state_timer'): player_d3.state_timer = 29
        enemy_d3 = Enemy(init_coord=(3, 0), action_requester=None, enemy_id=0)
        obs_d3 = Observation(map=self.map, player=player_d3, enemies=[enemy_d3])
        request_action(obs_d3)
        self.assertEqual(player_d3.get_mode(), IN_DANGER_MODE_NAME)

    def test_economic_at_29s_with_safe_distance_remains_economic(self):
        """
        [Counter-Hunting Boundary: T = 29s, Dist > 3]
        Ensures that when ghosts are completely out of range (Distance > 3), Pacman naturally 
        keeps clearing resources in ECONOMIC mode without false defensive alerts.
        """
        player = Player(init_coord=(0, 0), action_requester=None)
        player.set_mode(ECONOMIC_MODE_NAME)
        if hasattr(player, 'state_timer'):
            player.state_timer = 29
            
        # Ghost far away at Distance = 4
        enemy = Enemy(init_coord=(4, 0), action_requester=None, enemy_id=0)
        obs = Observation(map=self.map, player=player, enemies=[enemy])
        request_action(obs)
        
        self.assertEqual(player.get_mode(), ECONOMIC_MODE_NAME)

    def test_economic_to_in_danger_at_and_past_30s_timeout(self):
        """
        [Standard Baseline Boundary: T >= 30s, Dist <= 3]
        Validates that once the temporal safety threshold is breached (T = 30s or 31s), 
        the aggressive retention logic expires. Any ghost within the standard radius 
        (Distance <= 3) universally triggers a transition to IN_DANGER mode.
        """
        # Test Sub-case: T = 30s, Distance = 3
        player_t30 = Player(init_coord=(0, 0), action_requester=None)
        player_t30.set_mode(ECONOMIC_MODE_NAME)
        if hasattr(player_t30, 'state_timer'): player_t30.state_timer = 30
        enemy_t30 = Enemy(init_coord=(3, 0), action_requester=None, enemy_id=0)
        obs_t30 = Observation(map=self.map, player=player_t30, enemies=[enemy_t30])
        request_action(obs_t30)
        self.assertEqual(player_t30.get_mode(), IN_DANGER_MODE_NAME)

        # Test Sub-case: T = 31s, Distance = 2
        player_t31 = Player(init_coord=(0, 0), action_requester=None)
        player_t31.set_mode(ECONOMIC_MODE_NAME)
        if hasattr(player_t31, 'state_timer'): player_t31.state_timer = 31
        enemy_t31 = Enemy(init_coord=(2, 0), action_requester=None, enemy_id=0)
        obs_t31 = Observation(map=self.map, player=player_t31, enemies=[enemy_t31])
        request_action(obs_t31)
        self.assertEqual(player_t31.get_mode(), IN_DANGER_MODE_NAME)

if __name__ == '__main__':
    unittest.main()