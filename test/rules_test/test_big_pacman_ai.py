import unittest
from src.map import Map
from src.entity import Player, Enemy
from src.game import Observation
from src.rules import request_action, RUSH_MODE_NAME, BIG_PACMAN_MODE_NAME

class TestBigPacmanAI(unittest.TestCase):

    def setUp(self):
        """
        Set up an isolated 5x5 grid environment for each test case.
        This ensures tests run quickly without spinning up the full game engine runtime.
        """
        self.map = Map(size_x=5, size_y=5)

    # =========================================================================
    # 1. Mode Trigger Tests (State Transition Logic)
    # =========================================================================

    def test_switch_to_big_pacman_at_striking_distance(self):
        """
        [Mode Trigger] Distance = 3 with Super active.
        Verifies that when Pacman is in super mode, the AI state machine 
        successfully transitions from RUSH to BIG_PACMAN mode as soon as 
        an active ghost closes in within the critical Manhattan distance threshold (<= 3).
        """
        player = Player(init_coord=(0, 0), action_requester=None)
        # Mock the underlying game state to simulate that a super pellet was consumed
        player.is_super_pacman_mode = lambda: True 
        
        # Ghost at (3, 0) -> Manhattan distance = |0-3| + |0-0| = 3
        enemy = Enemy(init_coord=(3, 0), action_requester=None, enemy_id=0)
        
        obs = Observation(map=self.map, player=player, enemies=[enemy])
        request_action(obs)
        
        # Assert that the AI switches to the hunting state
        self.assertEqual(player.get_mode(), BIG_PACMAN_MODE_NAME)

    def test_stay_in_rush_even_if_super_when_ghost_is_far(self):
        """
        [Mode Trigger] Distance = 4 with Super active.
        Verifies that even if Pacman is in super mode, the AI stays in RUSH mode 
        to focus on clearing pellets efficiently if the ghost is still at a safe 
        distance (Manhattan distance > 3), preventing unnecessary chasing overhead.
        """
        player = Player(init_coord=(0, 0), action_requester=None)
        player.is_super_pacman_mode = lambda: True
        
        # Ghost at (4, 0) -> Manhattan distance = |0-4| + |0-0| = 4
        enemy = Enemy(init_coord=(4, 0), action_requester=None, enemy_id=0)
        
        obs = Observation(map=self.map, player=player, enemies=[enemy])
        request_action(obs)
        
        # Assert that the AI maintains the normal RUSH mode
        self.assertEqual(player.get_mode(), RUSH_MODE_NAME)

    # =========================================================================
    # 2. Within-mode Behavior Tests (Decision-Making Logic)
    # =========================================================================

    def test_big_pacman_chases_closer_ghost(self):
        """
        [Within-mode Behavior] Active Hunting Preference.
        Verifies the AI's steering decision when already in BIG_PACMAN mode.
        Given two available paths with ghosts at different distances, the AI 
        must actively choose the path leading to the closer ghost (distance 2) 
        rather than the farther one (distance 3) to optimize the super duration.
        """
        player = Player(init_coord=(0, 0), action_requester=None)
        player.is_super_pacman_mode = lambda: True
        player.set_mode(BIG_PACMAN_MODE_NAME)
        
        # far_enemy at (0, 3)  -> Manhattan distance = 3 (Path A)
        # close_enemy at (2, 0) -> Manhattan distance = 2 (Path B)
        far_enemy = Enemy(init_coord=(0, 3), action_requester=None, enemy_id=0)
        close_enemy = Enemy(init_coord=(2, 0), action_requester=None, enemy_id=1)
        
        obs = Observation(map=self.map, player=player, enemies=[far_enemy, close_enemy])
        action = request_action(obs)
        
        # Assert that the AI selects the optimal path towards the closer ghost.
        # Note: Replace "RIGHT" with your project's specific directional constant or enum (e.g., Direction.RIGHT)
        self.assertEqual(action, "RIGHT")

if __name__ == '__main__':
    unittest.main()