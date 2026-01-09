"""Game persistence utilities for saving and loading games."""

import json
import os
from datetime import datetime


class GamePersistence:
    """Handles saving and loading game state to/from JSON."""

    SAVES_DIR = "game_saves"

    @staticmethod
    def ensure_saves_dir():
        """Ensure the saves directory exists."""
        if not os.path.exists(GamePersistence.SAVES_DIR):
            os.makedirs(GamePersistence.SAVES_DIR)

    @staticmethod
    def save_game(
        game_logic, player_x_name: str, player_o_name: str, filename: str = None
    ) -> str:
        """Save game state to JSON file.

        Args:
            game_logic: GameLogic instance with current game state
            player_x_name: Name of player X
            player_o_name: Name of player O
            filename: Optional filename (without path). If None, auto-generates from timestamp.

        Returns:
            Path to saved file
        """
        GamePersistence.ensure_saves_dir()

        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"game_{timestamp}.json"

        filepath = os.path.join(GamePersistence.SAVES_DIR, filename)

        game_data = {
            "player_x_name": player_x_name,
            "player_o_name": player_o_name,
            "current_player": game_logic.current_player,
            "status": game_logic.status,
            "board": game_logic.board,
            "blocks_3x3": game_logic.blocks_3x3,
            "blocks_9x9": game_logic.blocks_9x9,
            "blocks_state_3x3": game_logic.blocks_state_3x3,
            "blocks_state_9x9": game_logic.blocks_state_9x9,
            "active_9x9_block": game_logic.active_9x9_block,
            "active_3x3_block": game_logic.active_3x3_block,
            "saved_at": datetime.now().isoformat(),
        }

        with open(filepath, "w") as f:
            json.dump(game_data, f, indent=2)

        return filepath

    @staticmethod
    def load_game(filepath: str) -> tuple:
        """Load game state from JSON file.

        Args:
            filepath: Path to game save file

        Returns:
            Tuple of (game_logic, player_x_name, player_o_name)
        """
        from game_logic import GameLogic

        with open(filepath, "r") as f:
            game_data = json.load(f)

        # Create game logic instance
        game = GameLogic()

        # Restore game state
        game.current_player = game_data["current_player"]
        game.status = game_data["status"]
        game.board = game_data["board"]
        game.blocks_3x3 = game_data["blocks_3x3"]
        game.blocks_9x9 = game_data["blocks_9x9"]
        game.blocks_state_3x3 = game_data["blocks_state_3x3"]
        game.blocks_state_9x9 = game_data["blocks_state_9x9"]
        game.active_9x9_block = game_data["active_9x9_block"]
        game.active_3x3_block = game_data["active_3x3_block"]

        player_x_name = game_data["player_x_name"]
        player_o_name = game_data["player_o_name"]

        return game, player_x_name, player_o_name

    @staticmethod
    def list_saves() -> list:
        """List all saved game files.

        Returns:
            List of (filename, filepath, saved_at) tuples sorted by date
        """
        GamePersistence.ensure_saves_dir()

        saves = []
        for filename in os.listdir(GamePersistence.SAVES_DIR):
            if filename.endswith(".json"):
                filepath = os.path.join(GamePersistence.SAVES_DIR, filename)
                with open(filepath, "r") as f:
                    game_data = json.load(f)
                saved_at = game_data.get("saved_at", "")
                saves.append((filename, filepath, saved_at))

        # Sort by saved_at timestamp (newest first)
        saves.sort(key=lambda x: x[2], reverse=True)
        return saves
