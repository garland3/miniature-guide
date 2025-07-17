#!/usr/bin/env python3
"""
Unit tests for the computer player functionality in the Battleship game
"""

import unittest
from unittest.mock import patch
from game_logic import BattleshipGame, GameBoard, CellState, ShipType


class TestComputerPlayer(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.game = BattleshipGame()
    
    def test_computer_shoot_valid_turn(self):
        """Test that computer can shoot when it's their turn"""
        # Set up game state where it's computer's turn
        self.game.current_turn = "computer"
        self.game.game_over = False
        
        result = self.game.computer_shoot()
        
        self.assertTrue(result["valid"])
        self.assertIn("position", result)
        self.assertIsInstance(result["position"], tuple)
        self.assertEqual(len(result["position"]), 2)
    
    def test_computer_shoot_invalid_turn(self):
        """Test that computer cannot shoot when it's not their turn"""
        # Set up game state where it's player's turn
        self.game.current_turn = "player"
        self.game.game_over = False
        
        result = self.game.computer_shoot()
        
        self.assertFalse(result["valid"])
        self.assertEqual(result["message"], "Not computer's turn or game is over")
    
    def test_computer_shoot_game_over(self):
        """Test that computer cannot shoot when game is over"""
        self.game.current_turn = "computer"
        self.game.game_over = True
        
        result = self.game.computer_shoot()
        
        self.assertFalse(result["valid"])
        self.assertEqual(result["message"], "Not computer's turn or game is over")
    
    def test_computer_shoots_valid_position(self):
        """Test that computer always shoots at valid board positions"""
        self.game.current_turn = "computer"
        
        for _ in range(10):  # Test multiple shots
            result = self.game.computer_shoot()
            if result["valid"]:
                row, col = result["position"]
                self.assertTrue(0 <= row < self.game.player_board.size)
                self.assertTrue(0 <= col < self.game.player_board.size)
                # Reset turn for next iteration
                self.game.current_turn = "computer"
    
    def test_computer_avoids_duplicate_shots(self):
        """Test that computer doesn't shoot at the same position twice"""
        self.game.current_turn = "computer"
        shot_positions = set()
        
        # Take multiple shots and ensure no duplicates
        for _ in range(20):  # More than enough to test duplicate avoidance
            result = self.game.computer_shoot()
            if result["valid"]:
                position = result["position"]
                self.assertNotIn(position, shot_positions, 
                               f"Computer shot at position {position} twice")
                shot_positions.add(position)
                # Reset turn for next iteration
                self.game.current_turn = "computer"
    
    def test_computer_shot_affects_player_board(self):
        """Test that computer shots actually affect the player board"""
        self.game.current_turn = "computer"
        initial_shots_count = len(self.game.player_board.shots_taken)
        
        result = self.game.computer_shoot()
        
        if result["valid"]:
            final_shots_count = len(self.game.player_board.shots_taken)
            self.assertEqual(final_shots_count, initial_shots_count + 1)
            
            # Check that the shot position is recorded
            position = result["position"]
            self.assertIn(position, self.game.player_board.shots_taken)
    
    def test_computer_detects_hit(self):
        """Test that computer correctly detects hits"""
        # Manually place a ship at a known position
        self.game.player_board.grid[0][0] = CellState.SHIP
        
        # Mock random.choice to always select position (0, 0)
        with patch('random.choice', return_value=(0, 0)):
            self.game.current_turn = "computer"
            result = self.game.computer_shoot()
            
            self.assertTrue(result["valid"])
            self.assertTrue(result["hit"])
            self.assertEqual(result["position"], (0, 0))
    
    def test_computer_detects_miss(self):
        """Test that computer correctly detects misses"""
        # Ensure position (0, 0) is empty
        self.game.player_board.grid[0][0] = CellState.EMPTY
        
        # Mock random.choice to always select position (0, 0)
        with patch('random.choice', return_value=(0, 0)):
            self.game.current_turn = "computer"
            result = self.game.computer_shoot()
            
            self.assertTrue(result["valid"])
            self.assertFalse(result["hit"])
            self.assertEqual(result["position"], (0, 0))
    
    def test_computer_turn_switches_after_shot(self):
        """Test that turn switches to player after computer shot"""
        self.game.current_turn = "computer"
        self.game.game_over = False
        
        result = self.game.computer_shoot()
        
        if result["valid"] and not result.get("game_over", False):
            self.assertEqual(self.game.current_turn, "player")
    
    def test_computer_wins_when_all_player_ships_sunk(self):
        """Test that computer wins when all player ships are sunk"""
        # Sink all player ships except one position
        for ship in self.game.player_board.ships:
            for pos in ship.positions:
                ship.hits.add(pos)
                row, col = pos
                self.game.player_board.grid[row][col] = CellState.HIT
        
        # Leave one position unsunk and mock computer to hit it
        last_ship = self.game.player_board.ships[-1]
        last_position = list(last_ship.positions)[-1]
        last_ship.hits.remove(last_position)
        row, col = last_position
        self.game.player_board.grid[row][col] = CellState.SHIP
        
        # Mock random.choice to select the last position
        with patch('random.choice', return_value=last_position):
            self.game.current_turn = "computer"
            result = self.game.computer_shoot()
            
            self.assertTrue(result["valid"])
            self.assertTrue(result["hit"])
            self.assertTrue(result.get("game_over", False))
            self.assertEqual(result.get("winner"), "computer")
            self.assertTrue(self.game.game_over)
            self.assertEqual(self.game.winner, "computer")
    
    def test_computer_no_available_positions(self):
        """Test computer behavior when no positions are available"""
        # Fill all positions as already shot
        for r in range(self.game.player_board.size):
            for c in range(self.game.player_board.size):
                self.game.player_board.shots_taken.add((r, c))
        
        self.game.current_turn = "computer"
        result = self.game.computer_shoot()
        
        self.assertFalse(result["valid"])
        self.assertEqual(result["message"], "No positions available")
    
    @patch('random.choice')
    def test_computer_random_selection(self, mock_choice):
        """Test that computer uses random selection for shots"""
        mock_choice.return_value = (5, 5)
        self.game.current_turn = "computer"
        
        result = self.game.computer_shoot()
        
        # Verify random.choice was called
        mock_choice.assert_called_once()
        
        # Verify the mocked position was used
        if result["valid"]:
            self.assertEqual(result["position"], (5, 5))


class TestComputerPlayerIntegration(unittest.TestCase):
    """Integration tests for computer player with full game flow"""
    
    def test_full_game_computer_participation(self):
        """Test computer participation in a full game scenario"""
        game = BattleshipGame()
        
        # Simulate several rounds of player-computer turns
        for round_num in range(5):
            if game.game_over:
                break
                
            # Player turn
            if game.current_turn == "player":
                # Simulate player shot
                result = game.player_shoot(round_num, round_num)
                if result["valid"] and not game.game_over:
                    self.assertEqual(game.current_turn, "computer")
            
            # Computer turn
            if game.current_turn == "computer" and not game.game_over:
                result = game.computer_shoot()
                self.assertTrue(result["valid"])
                if not game.game_over:
                    self.assertEqual(game.current_turn, "player")
    
    def test_computer_ai_strategy_consistency(self):
        """Test that computer AI strategy remains consistent"""
        game = BattleshipGame()
        game.current_turn = "computer"
        
        shots_taken = []
        for _ in range(10):
            if game.game_over:
                break
            result = game.computer_shoot()
            if result["valid"]:
                shots_taken.append(result["position"])
                game.current_turn = "computer"  # Reset for next iteration
        
        # Verify all shots are unique (no duplicates)
        self.assertEqual(len(shots_taken), len(set(shots_taken)))
        
        # Verify all shots are within board bounds
        for row, col in shots_taken:
            self.assertTrue(0 <= row < game.player_board.size)
            self.assertTrue(0 <= col < game.player_board.size)


if __name__ == '__main__':
    unittest.main()