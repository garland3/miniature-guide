class BattleshipUI {
    constructor() {
        this.gameId = null;
        this.gameState = null;
        this.isPlayerTurn = false;
        
        this.initializeEventListeners();
    }

    initializeEventListeners() {
        document.getElementById('new-game-btn').addEventListener('click', () => this.startNewGame());
        document.getElementById('play-again-btn').addEventListener('click', () => this.startNewGame());
    }

    async startNewGame() {
        try {
            const response = await fetch('/api/new-game', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error('Failed to start new game');
            }

            const data = await response.json();
            this.gameId = data.game_id;
            this.gameState = data.game_state;
            
            this.hideModal();
            this.showGameArea();
            this.updateUI();
            this.addLogEntry('🎮 New game started! Click on enemy waters to attack!');
            
        } catch (error) {
            console.error('Error starting new game:', error);
            this.addLogEntry('❌ Error starting new game. Please try again.');
        }
    }

    showGameArea() {
        document.getElementById('game-area').style.display = 'block';
    }

    hideModal() {
        document.getElementById('game-over-modal').style.display = 'none';
    }

    showGameOverModal(winner) {
        const modal = document.getElementById('game-over-modal');
        const title = document.getElementById('game-over-title');
        const message = document.getElementById('game-over-message');

        if (winner === 'player') {
            title.textContent = '🎉 Victory!';
            message.textContent = 'Congratulations! You sunk all enemy ships!';
        } else {
            title.textContent = '💥 Defeat!';
            message.textContent = 'The enemy has sunk all your ships. Better luck next time!';
        }

        modal.style.display = 'flex';
    }

    updateUI() {
        if (!this.gameState) return;

        this.updateTurnIndicator();
        this.updateBoards();
        this.updateShipsStatus();
    }

    updateTurnIndicator() {
        const indicator = document.getElementById('turn-indicator');
        const status = document.getElementById('game-status');

        if (this.gameState.game_over) {
            indicator.textContent = 'Game Over';
            status.textContent = `Winner: ${this.gameState.winner === 'player' ? 'You' : 'Computer'}`;
        } else {
            indicator.textContent = this.gameState.current_turn === 'player' ? 'Your Turn' : 'Computer\'s Turn';
            status.textContent = '';
        }

        this.isPlayerTurn = this.gameState.current_turn === 'player' && !this.gameState.game_over;
    }

    updateBoards() {
        this.renderBoard('player-board', this.gameState.player_board, false);
        this.renderBoard('computer-board', this.gameState.computer_board, true);
    }

    renderBoard(boardId, boardData, isComputer) {
        const boardElement = document.getElementById(boardId);
        boardElement.innerHTML = '';

        for (let row = 0; row < 10; row++) {
            for (let col = 0; col < 10; col++) {
                const cell = document.createElement('div');
                cell.className = 'cell';
                cell.dataset.row = row;
                cell.dataset.col = col;

                const cellValue = boardData[row][col];
                
                // Set cell content and class based on value
                switch (cellValue) {
                    case '~':
                        cell.textContent = '';
                        cell.classList.add('water');
                        break;
                    case 'S':
                        cell.textContent = '🚢';
                        cell.classList.add('ship');
                        break;
                    case 'X':
                        cell.textContent = '🎯';
                        cell.classList.add('hit');
                        break;
                    case 'O':
                        cell.textContent = '⭕';
                        cell.classList.add('miss');
                        break;
                }

                // Add click handler for computer board
                if (isComputer) {
                    cell.classList.add('computer-cell');
                    if (cellValue === '~') {  // Only allow clicking on unshot cells
                        cell.addEventListener('click', () => this.playerShoot(row, col));
                    }
                }

                boardElement.appendChild(cell);
            }
        }
    }

    async playerShoot(row, col) {
        if (!this.isPlayerTurn) {
            this.addLogEntry('⚠️ Not your turn!');
            return;
        }

        try {
            const response = await fetch(`/api/game/${this.gameId}/shoot`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ row, col })
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Shot failed');
            }

            const data = await response.json();
            this.gameState = data.game_state;
            
            // Handle player shot result
            const playerShot = data.player_shot;
            this.animateShot(row, col, 'computer-board', playerShot.hit);
            
            if (playerShot.hit) {
                if (playerShot.sunk) {
                    this.addLogEntry(`🎯 ${playerShot.message}`, 'sunk');
                } else {
                    this.addLogEntry('🎯 Direct hit!', 'hit');
                }
            } else {
                this.addLogEntry('💦 Miss!', 'miss');
            }

            // Handle computer shot if it happened
            if (data.computer_shot) {
                const computerShot = data.computer_shot;
                const [compRow, compCol] = computerShot.position;
                
                setTimeout(() => {
                    this.animateShot(compRow, compCol, 'player-board', computerShot.hit);
                    
                    if (computerShot.hit) {
                        if (computerShot.sunk) {
                            this.addLogEntry(`💥 Computer sunk your ${computerShot.ship_type}!`, 'sunk');
                        } else {
                            this.addLogEntry('💥 Computer hit your ship!', 'hit');
                        }
                    } else {
                        this.addLogEntry('🌊 Computer missed!', 'miss');
                    }
                }, 1000);
            }

            // Update UI after a short delay to show animations
            setTimeout(() => {
                this.updateUI();
                
                // Check for game over
                if (this.gameState.game_over) {
                    setTimeout(() => {
                        this.showGameOverModal(this.gameState.winner);
                    }, 1000);
                }
            }, 1500);

        } catch (error) {
            console.error('Error making shot:', error);
            this.addLogEntry(`❌ Error: ${error.message}`);
        }
    }

    animateShot(row, col, boardId, isHit) {
        const boardElement = document.getElementById(boardId);
        const cellIndex = row * 10 + col;
        const cell = boardElement.children[cellIndex];
        
        if (cell) {
            cell.classList.add(isHit ? 'animate-hit' : 'animate-miss');
            setTimeout(() => {
                cell.classList.remove('animate-hit', 'animate-miss');
            }, 500);
        }
    }

    updateShipsStatus() {
        const playerStatus = document.getElementById('player-ships-status');
        const computerStatus = document.getElementById('computer-ships-status');

        playerStatus.innerHTML = `Ships Remaining: ${this.gameState.player_ships_remaining}/5`;
        computerStatus.innerHTML = `Ships Remaining: ${this.gameState.computer_ships_remaining}/5`;
    }

    addLogEntry(message, type = '') {
        const logContent = document.getElementById('log-content');
        const entry = document.createElement('div');
        entry.className = `log-entry ${type}`;
        entry.textContent = `${new Date().toLocaleTimeString()}: ${message}`;
        
        logContent.appendChild(entry);
        logContent.scrollTop = logContent.scrollHeight;
    }
}

// Initialize the game when the page loads
document.addEventListener('DOMContentLoaded', () => {
    new BattleshipUI();
});
