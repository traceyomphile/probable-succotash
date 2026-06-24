# Probable Succotash

Probable Succotash is a simple chess simulation project that combines a graphical chess board with two autonomous agents:

- a random chess agent
- a Monte Carlo Tree Search (MCTS) agent

The project is implemented in Python and uses Tkinter for the GUI.

## Overview

This assignment-style project demonstrates a basic chess environment where one agent plays randomly and the other uses Monte Carlo Tree Search to evaluate possible moves. The game starts automatically and displays the board as pieces move across the screen.

## Features

- Graphical chess board rendered with Tkinter
- Piece movement and basic chess rules
- Random agent for baseline play
- MCTS-based agent for move selection
- Checkmate detection and game termination logic
- Simple visual board with piece images from the assets folder

## Project Structure

- main.py: Starts the game and manages the match loop
- agent.py: Contains the random agent, the MCTS agent, and move-generation logic
- board.py: Defines the chess board model, move rules, and GUI rendering
- assets/: Image files for the chess pieces

## Requirements

- Python 3.8 or newer
- Tkinter (usually included with Python on Windows and most Linux distributions)

## How to Run

1. Open a terminal in the project folder.
2. Run:

```bash
python main.py
```

3. The game window will open and the match will begin after a short delay.

## Notes

- The current setup makes the white player use the random agent and the black player use the Monte Carlo agent.
- The game loop is intentionally simple and is meant for demonstrating agent behavior rather than full chess engine accuracy.
- You can modify the agents or game settings in main.py and agent.py to experiment with different strategies.

## Author

This project was developed as part of an assignment and is intended as a learning exercise in artificial intelligence and game-playing agents.
*Additional author*: Tracey Letlape