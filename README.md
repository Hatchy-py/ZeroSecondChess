# Premove Chess Engine Match

This Python script simulates a chess match between two UCI engines under **premove-only rules**:

- Both engines select their next move **before** the opponent moves.
- If the chosen move is illegal after the opponent's move, the engine plays a **depth=1 fallback** move.

Example use: Stockfish vs LCZero, Stockfish vs Komodo, etc.

## Features
- Customizable engine paths and names.
- Adjustable premove depth and fallback depth.
- Saves a `.pgn` file you can upload to Chess.com or Lichess for analysis.
- Works with any UCI-compatible chess engine.

## Requirements
- Python 3.8+
- [python-chess](https://pypi.org/project/python-chess/)
- Two UCI chess engine executables (e.g., Stockfish, LCZero).

Install dependencies:
```bash
pip install python-chess
