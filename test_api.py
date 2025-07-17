#!/usr/bin/env python3
"""
Simple test script to demonstrate the Battleship API
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_battleship_api():
    print("🚢 Testing Battleship Game API\n")
    
    # Start a new game
    print("1. Starting a new game...")
    response = requests.post(f"{BASE_URL}/api/new-game")
    
    if response.status_code != 200:
        print(f"❌ Failed to start game: {response.status_code}")
        return
    
    game_data = response.json()
    game_id = game_data["game_id"]
    print(f"✅ Game started! Game ID: {game_id}")
    print(f"   Initial state: Turn = {game_data['game_state']['current_turn']}")
    
    # Take some shots
    shots = [(0, 0), (0, 1), (5, 5), (9, 9), (2, 3)]
    
    for i, (row, col) in enumerate(shots):
        print(f"\n2.{i+1} Taking shot at ({row}, {col})...")
        
        shot_data = {"row": row, "col": col}
        response = requests.post(f"{BASE_URL}/api/game/{game_id}/shoot", json=shot_data)
        
        if response.status_code != 200:
            print(f"❌ Shot failed: {response.status_code}")
            error_data = response.json()
            print(f"   Error: {error_data.get('detail', 'Unknown error')}")
            continue
        
        result = response.json()
        player_shot = result["player_shot"]
        
        print(f"   Result: {player_shot['message']}")
        
        if "computer_shot" in result:
            comp_shot = result["computer_shot"]
            comp_pos = comp_shot["position"]
            print(f"   Computer shot at ({comp_pos[0]}, {comp_pos[1]}): {comp_shot['message']}")
        
        game_state = result["game_state"]
        print(f"   Ships remaining - You: {game_state['player_ships_remaining']}, Computer: {game_state['computer_ships_remaining']}")
        
        if game_state["game_over"]:
            print(f"\n🎉 Game Over! Winner: {game_state['winner']}")
            break
        
        time.sleep(1)  # Small delay between shots
    
    # Get final game state
    print(f"\n3. Getting final game state...")
    response = requests.get(f"{BASE_URL}/api/game/{game_id}")
    
    if response.status_code == 200:
        final_state = response.json()
        print(f"✅ Final state retrieved")
        print(f"   Game over: {final_state['game_over']}")
        print(f"   Winner: {final_state.get('winner', 'None')}")
    else:
        print(f"❌ Failed to get game state: {response.status_code}")
    
    # List all games
    print(f"\n4. Listing all games...")
    response = requests.get(f"{BASE_URL}/api/games")
    
    if response.status_code == 200:
        games_list = response.json()
        print(f"✅ Found {len(games_list['games'])} active games")
        for game in games_list['games']:
            print(f"   Game {game['game_id'][:8]}... - Turn: {game['current_turn']}, Over: {game['game_over']}")
    else:
        print(f"❌ Failed to list games: {response.status_code}")

if __name__ == "__main__":
    try:
        test_battleship_api()
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the server.")
        print("   Make sure the FastAPI server is running on http://localhost:8000")
        print("   Run: python main.py")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
