"""
ZeroSecondChess.py

Simulates a premove-only match between Stockfish (White) and LCZero (Black).
If a premove is illegal after the opponent's move, engine plays a depth=1 fallback.

Outputs:
  - PGN file of the game (uploadable to Chess.com for analysis)
"""

import chess
import chess.engine
import chess.pgn
from pathlib import Path
import time

# === Engine paths ===
STOCKFISH_PATH = r"C:\Users\Hatch\Downloads\stockfish-windows-x86-64-avx2\stockfish\stockfish-windows-x86-64-avx2.exe"
LC0_PATH = r"C:\Users\Hatch\Downloads\lc0-v0.31.2-windows-gpu-nvidia-cuda\lc0.exe"

# === Parameters ===
PREMOVE_DEPTH = 6
FALLBACK_DEPTH = 1
MAX_MOVES = 200
PGN_FILE = "premove_sf_vs_lc0.pgn"

def choose_premove(engine, board, depth):
    """Ask engine to pick a move from `board` with given depth."""
    try:
        limit = chess.engine.Limit(depth=depth)
        result = engine.play(board, limit)
        return result.move.uci() if result and result.move else None
    except Exception as e:
        print(f"[warn] engine failed to pick premove: {e}")
        return None

def safe_push(board, move_uci):
    """Try to push a move in UCI format. Return True if legal and pushed."""
    if not move_uci:
        return False
    move = chess.Move.from_uci(move_uci)
    if move in board.legal_moves:
        board.push(move)
        return True
    return False

def premove_match(sf_path, lc0_path):
    board = chess.Board()
    game = chess.pgn.Game()
    node = game
    moves_played = 0

    with chess.engine.SimpleEngine.popen_uci(sf_path) as sf, \
         chess.engine.SimpleEngine.popen_uci(lc0_path) as lc0:

        white_engine = sf
        black_engine = lc0

        while not board.is_game_over(claim_draw=True) and moves_played < MAX_MOVES:
            # Both choose premoves from the same position
            premove_white = choose_premove(white_engine, board, PREMOVE_DEPTH)
            premove_black = choose_premove(black_engine, board, PREMOVE_DEPTH)

            # --- White plays ---
            if not safe_push(board, premove_white):
                fb = choose_premove(white_engine, board, FALLBACK_DEPTH)
                if not safe_push(board, fb):
                    print("[error] White cannot move. Resigns.")
                    game.headers["Result"] = "0-1"
                    return game

            node = node.add_variation(board.peek())
            moves_played += 1
            if board.is_game_over(claim_draw=True):
                break

            # --- Black plays ---
            if premove_black and chess.Move.from_uci(premove_black) in board.legal_moves:
                board.push(chess.Move.from_uci(premove_black))
            else:
                fb = choose_premove(black_engine, board, FALLBACK_DEPTH)
                if not safe_push(board, fb):
                    print("[error] Black cannot move. Resigns.")
                    game.headers["Result"] = "1-0"
                    return game

            node = node.add_variation(board.peek())
            moves_played += 1

        game.headers["Result"] = board.result(claim_draw=True)
        return game

if __name__ == "__main__":
    print("Starting premove match: Stockfish (White) vs LCZero (Black)")
    start = time.time()
    game = premove_match(STOCKFISH_PATH, LC0_PATH)
    elapsed = time.time() - start

    # Save PGN
    with open(PGN_FILE, "w", encoding="utf-8") as f:
        print(game, file=f)

    print(f"Game finished in {elapsed:.1f}s. PGN saved to {Path(PGN_FILE).absolute()}")
    print("Result:", game.headers.get("Result", "?"))
