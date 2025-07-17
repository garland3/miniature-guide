from typing import List, Dict, Optional, Tuple
from enum import Enum
import random
from uuid import uuid4

class CellState(Enum):
    EMPTY = "empty"
    SHIP = "ship"
    HIT = "hit"
    MISS = "miss"

class ShipType(Enum):
    CARRIER = {"name": "Carrier", "size": 5}
    BATTLESHIP = {"name": "Battleship", "size": 4}
    CRUISER = {"name": "Cruiser", "size": 3}
    SUBMARINE = {"name": "Submarine", "size": 3}
    DESTROYER = {"name": "Destroyer", "size": 2}

class Ship:
    def __init__(self, ship_type: ShipType, positions: List[Tuple[int, int]]):
        self.ship_type = ship_type
        self.positions = positions
        self.hits = set()
    
    @property
    def is_sunk(self) -> bool:
        return len(self.hits) == len(self.positions)
    
    def hit(self, position: Tuple[int, int]) -> bool:
        if position in self.positions:
            self.hits.add(position)
            return True
        return False

class GameBoard:
    def __init__(self, size: int = 10):
        self.size = size
        self.grid = [[CellState.EMPTY for _ in range(size)] for _ in range(size)]
        self.ships: List[Ship] = []
        self.shots_taken = set()
    
    def is_valid_position(self, row: int, col: int) -> bool:
        return 0 <= row < self.size and 0 <= col < self.size
    
    def can_place_ship(self, positions: List[Tuple[int, int]]) -> bool:
        for row, col in positions:
            if not self.is_valid_position(row, col):
                return False
            if self.grid[row][col] != CellState.EMPTY:
                return False
            # Check adjacent cells for other ships
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    new_row, new_col = row + dr, col + dc
                    if (self.is_valid_position(new_row, new_col) and 
                        self.grid[new_row][new_col] == CellState.SHIP and
                        (new_row, new_col) not in positions):
                        return False
        return True
    
    def place_ship(self, ship_type: ShipType, positions: List[Tuple[int, int]]) -> bool:
        if not self.can_place_ship(positions):
            return False
        
        ship = Ship(ship_type, positions)
        self.ships.append(ship)
        
        for row, col in positions:
            self.grid[row][col] = CellState.SHIP
        
        return True
    
    def auto_place_ships(self):
        """Automatically place ships randomly on the board"""
        ship_types = list(ShipType)
        
        for ship_type in ship_types:
            placed = False
            attempts = 0
            
            while not placed and attempts < 100:
                # Random direction (horizontal or vertical)
                horizontal = random.choice([True, False])
                size = ship_type.value["size"]
                
                if horizontal:
                    row = random.randint(0, self.size - 1)
                    col = random.randint(0, self.size - size)
                    positions = [(row, col + i) for i in range(size)]
                else:
                    row = random.randint(0, self.size - size)
                    col = random.randint(0, self.size - 1)
                    positions = [(row + i, col) for i in range(size)]
                
                if self.place_ship(ship_type, positions):
                    placed = True
                
                attempts += 1
    
    def shoot(self, row: int, col: int) -> Dict:
        if not self.is_valid_position(row, col):
            return {"valid": False, "message": "Invalid position"}
        
        if (row, col) in self.shots_taken:
            return {"valid": False, "message": "Already shot at this position"}
        
        self.shots_taken.add((row, col))
        
        if self.grid[row][col] == CellState.SHIP:
            self.grid[row][col] = CellState.HIT
            
            # Find which ship was hit
            hit_ship = None
            for ship in self.ships:
                if ship.hit((row, col)):
                    hit_ship = ship
                    break
            
            if hit_ship and hit_ship.is_sunk:
                return {
                    "valid": True,
                    "hit": True,
                    "sunk": True,
                    "ship_type": hit_ship.ship_type.value["name"],
                    "message": f"You sunk the {hit_ship.ship_type.value['name']}!"
                }
            else:
                return {
                    "valid": True,
                    "hit": True,
                    "sunk": False,
                    "message": "Hit!"
                }
        else:
            self.grid[row][col] = CellState.MISS
            return {
                "valid": True,
                "hit": False,
                "sunk": False,
                "message": "Miss!"
            }
    
    def all_ships_sunk(self) -> bool:
        return all(ship.is_sunk for ship in self.ships)
    
    def get_display_grid(self, hide_ships: bool = True) -> List[List[str]]:
        """Get grid for display, optionally hiding ships"""
        display_grid = []
        for row in self.grid:
            display_row = []
            for cell in row:
                if hide_ships and cell == CellState.SHIP:
                    display_row.append("~")
                elif cell == CellState.EMPTY:
                    display_row.append("~")
                elif cell == CellState.SHIP:
                    display_row.append("S")
                elif cell == CellState.HIT:
                    display_row.append("X")
                elif cell == CellState.MISS:
                    display_row.append("O")
                else:
                    display_row.append("~")
            display_grid.append(display_row)
        return display_grid

class BattleshipGame:
    def __init__(self):
        self.game_id = str(uuid4())
        self.player_board = GameBoard()
        self.computer_board = GameBoard()
        self.current_turn = "player"  # "player" or "computer"
        self.game_over = False
        self.winner = None
        self.computer_shots = set()
        
        # Auto-place ships for both boards
        self.player_board.auto_place_ships()
        self.computer_board.auto_place_ships()
    
    def player_shoot(self, row: int, col: int) -> Dict:
        if self.game_over or self.current_turn != "player":
            return {"valid": False, "message": "Not your turn or game is over"}
        
        result = self.computer_board.shoot(row, col)
        
        if result["valid"]:
            if self.computer_board.all_ships_sunk():
                self.game_over = True
                self.winner = "player"
                result["game_over"] = True
                result["winner"] = "player"
            else:
                self.current_turn = "computer"
        
        return result
    
    def computer_shoot(self) -> Dict:
        if self.game_over or self.current_turn != "computer":
            return {"valid": False, "message": "Not computer's turn or game is over"}
        
        # Simple AI: random shots avoiding already shot positions
        available_positions = [
            (r, c) for r in range(self.player_board.size) 
            for c in range(self.player_board.size)
            if (r, c) not in self.player_board.shots_taken
        ]
        
        if not available_positions:
            return {"valid": False, "message": "No positions available"}
        
        row, col = random.choice(available_positions)
        result = self.player_board.shoot(row, col)
        result["position"] = (row, col)
        
        if result["valid"]:
            if self.player_board.all_ships_sunk():
                self.game_over = True
                self.winner = "computer"
                result["game_over"] = True
                result["winner"] = "computer"
            else:
                self.current_turn = "player"
        
        return result
    
    def get_game_state(self) -> Dict:
        return {
            "game_id": self.game_id,
            "current_turn": self.current_turn,
            "game_over": self.game_over,
            "winner": self.winner,
            "player_board": self.player_board.get_display_grid(hide_ships=False),
            "computer_board": self.computer_board.get_display_grid(hide_ships=True),
            "player_ships_remaining": len([s for s in self.player_board.ships if not s.is_sunk]),
            "computer_ships_remaining": len([s for s in self.computer_board.ships if not s.is_sunk])
        }
