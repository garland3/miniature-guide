# FastAPI Battleship Game 🚢

A modern web-based implementation of the classic Battleship game built with FastAPI, featuring a beautiful UI and real-time gameplay.

## Features

- **Classic Battleship Gameplay**: Traditional rules with 5 ships of different sizes
- **Beautiful Modern UI**: Responsive design with animations and visual effects
- **Real-time Game State**: Interactive web interface with live updates
- **Smart AI Opponent**: Computer player that provides challenging gameplay
- **Game Management**: Multiple games can be played simultaneously
- **REST API**: Full API for game management and interaction

## Ships

- **Carrier**: 5 cells
- **Battleship**: 4 cells  
- **Cruiser**: 3 cells
- **Submarine**: 3 cells
- **Destroyer**: 2 cells

## Quick Start

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Server**:
   ```bash
   python main.py
   ```

3. **Open Your Browser**:
   Navigate to `http://localhost:8000` to start playing!

## How to Play

1. Click **"New Game"** to start a fresh battle
2. Your ships and the computer's ships are automatically placed
3. Click on cells in the **Enemy Waters** (right board) to attack
4. **🎯 X** = Hit, **⭕ O** = Miss, **🚢 S** = Your ships
5. Sink all enemy ships to win!
6. The computer will automatically take its turn after yours

## Game Controls

- **Left Board**: Your fleet - defend these ships!
- **Right Board**: Enemy waters - click to attack!
- **Battle Log**: Track all moves and results
- **Ships Status**: See remaining ships for both players

## API Endpoints

### Game Management
- `POST /api/new-game` - Start a new game
- `GET /api/game/{game_id}` - Get game state
- `DELETE /api/game/{game_id}` - Delete a game
- `GET /api/games` - List all active games

### Gameplay
- `POST /api/game/{game_id}/shoot` - Take a shot at coordinates

### Example API Usage

```python
import requests

# Start a new game
response = requests.post("http://localhost:8000/api/new-game")
game_data = response.json()
game_id = game_data["game_id"]

# Take a shot
shot_data = {"row": 0, "col": 0}
response = requests.post(f"http://localhost:8000/api/game/{game_id}/shoot", json=shot_data)
result = response.json()
```

## Project Structure

```
├── main.py              # FastAPI application and API endpoints
├── game_logic.py        # Core battleship game logic and classes
├── requirements.txt     # Python dependencies
├── templates/
│   └── index.html      # Main game interface
├── static/
│   ├── style.css       # Game styling and animations  
│   └── script.js       # Frontend JavaScript logic
└── README.md           # This file
```

## Technical Details

- **Backend**: FastAPI with Python 3.12+
- **Frontend**: Vanilla JavaScript with modern CSS
- **Game Logic**: Object-oriented design with proper separation of concerns
- **AI**: Random shot selection with collision detection
- **State Management**: In-memory storage (easily extensible to database)

## Development

To extend the game:

1. **Enhanced AI**: Implement smarter targeting algorithms in `game_logic.py`
2. **Multiplayer**: Add WebSocket support for real-time multiplayer games
3. **Persistence**: Replace in-memory storage with database integration
4. **Statistics**: Track player statistics and game history
5. **Custom Ships**: Allow players to manually place their ships

## License

This project is open source and available under the MIT License.