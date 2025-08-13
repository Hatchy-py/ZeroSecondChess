"""
premove_match.py

Simulates a premove-only chess match between two UCI engines.
If a premove is illegal after the opponent's move, the engine plays a depth=1 fallback move.

Outputs:
  - PGN file of the game (uploadable to Chess.com, Lichess, etc.)
"""

import chess
import chess.engine
import chess.pgn
from pathlib import Path
import time

# Engine paths and names (swap easily to change colors)
WHITE_ENGINE_PATH = r"C:\Path\To\Stockfish.exe"  # Update this
WHITE_ENGINE_NAME = "Stockfish"

BLACK_ENGINE_PATH = r"C:\Path\To\lc0.exe"  # Update this
BLACK_ENGINE_NAME = "LCZero"

# Parameters
PREMOVE_DEPTH = 6
FALLBACK_DEPTH = 1
MAX_MOVES = 200
PGN_FILE = "premove_match.pgn"

def choose_premove(engine, board, depth):
    """Ask engine to pick a move from `board` with given depth."""
    try:
        limit = chess.engine.Limit(depth=depth)
        result = engine.play(board, limit)
        return result.move.uci() if result and result.move else None
    except Exception as e:
        print(f"[warn] Engine failed to pick premove: {e}")
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

def premove_match(white_path, white_name, black_path, black_name):
    board = chess.Board()
    game = chess.pgn.Game()
    game.headers["White"] = white_name
    game.headers["Black"] = black_name
    node = game
    moves_played = 0

    with chess.engine.SimpleEngine.popen_uci(white_path) as white_eng, \
         chess.engine.SimpleEngine.popen_uci(black_path) as black_eng:

        while not board.is_game_over(claim_draw=True) and moves_played < MAX_MOVES:
            # Both choose premoves from the same position
            premove_white = choose_premove(white_eng, board, PREMOVE_DEPTH)
            premove_black = choose_premove(black_eng, board, PREMOVE_DEPTH)

            # --- White plays ---
            if not safe_push(board, premove_white):
                fb = choose_premove(white_eng, board, FALLBACK_DEPTH)
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
                fb = choose_premove(black_eng, board, FALLBACK_DEPTH)
                if not safe_push(board, fb):
                    print("[error] Black cannot move. Resigns.")
                    game.headers["Result"] = "1-0"
                    return game

            node = node.add_variation(board.peek())
            moves_played += 1

        game.headers["Result"] = board.result(claim_draw=True)
        return game

if __name__ == "__main__":
    print(f"Starting premove match: {WHITE_ENGINE_NAME} (White) vs {BLACK_ENGINE_NAME} (Black)")
    start = time.time()
    game = premove_match(
        WHITE_ENGINE_PATH, WHITE_ENGINE_NAME,
        BLACK_ENGINE_PATH, BLACK_ENGINE_NAME
    )
    elapsed = time.time() - start

    # Save PGN
    with open(PGN_FILE, "w", encoding="utf-8") as f:
        print(game, file=f)

    print(f"Game finished in {elapsed:.1f}s. PGN saved to {Path(PGN_FILE).absolute()}")
    print("Result:", game.headers.get("Result", "?"))
