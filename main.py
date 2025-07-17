from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Dict
import os

from game_logic import BattleshipGame

app = FastAPI(title="Battleship Game", description="A FastAPI implementation of the classic Battleship game")

# Create static and templates directories if they don't exist
os.makedirs("static", exist_ok=True)
os.makedirs("templates", exist_ok=True)

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# In-memory game storage (in production, use a database)
games: Dict[str, BattleshipGame] = {}

class ShotRequest(BaseModel):
    row: int
    col: int

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Serve the main game page"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/api/new-game")
async def new_game():
    """Start a new battleship game"""
    game = BattleshipGame()
    games[game.game_id] = game
    return {
        "game_id": game.game_id,
        "message": "New game started!",
        "game_state": game.get_game_state()
    }

@app.get("/api/game/{game_id}")
async def get_game_state(game_id: str):
    """Get the current state of a game"""
    if game_id not in games:
        raise HTTPException(status_code=404, detail="Game not found")
    
    game = games[game_id]
    return game.get_game_state()

@app.post("/api/game/{game_id}/shoot")
async def player_shoot(game_id: str, shot: ShotRequest):
    """Player takes a shot at the computer's board"""
    if game_id not in games:
        raise HTTPException(status_code=404, detail="Game not found")
    
    game = games[game_id]
    
    # Player shoots
    player_result = game.player_shoot(shot.row, shot.col)
    
    if not player_result["valid"]:
        raise HTTPException(status_code=400, detail=player_result["message"])
    
    response = {
        "player_shot": player_result,
        "game_state": game.get_game_state()
    }
    
    # If game is not over and it's computer's turn, computer shoots
    if not game.game_over and game.current_turn == "computer":
        computer_result = game.computer_shoot()
        response["computer_shot"] = computer_result
        response["game_state"] = game.get_game_state()
    
    return response

@app.delete("/api/game/{game_id}")
async def delete_game(game_id: str):
    """Delete a game"""
    if game_id not in games:
        raise HTTPException(status_code=404, detail="Game not found")
    
    del games[game_id]
    return {"message": "Game deleted successfully"}

@app.get("/api/games")
async def list_games():
    """List all active games"""
    return {
        "games": [
            {
                "game_id": game_id,
                "current_turn": game.current_turn,
                "game_over": game.game_over,
                "winner": game.winner
            }
            for game_id, game in games.items()
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
