"""
Game logic for Intergalactic Tic-Tac-Toe (27x27 version)

Three-level hierarchy:
- Play in one 9x9 block at a time (selected from 3x3 grid of 9x9 blocks)
- Within a 9x9 block, play in 3x3 blocks (3x3 grid of blocks)
- Within a 3x3 block, place marks on cells (3x3 grid of cells)

Rules:
1. Place mark at [r,c] in a 3x3 block -> opponent must play in 3x3 block [r,c] in same 9x9
2. Win a 3x3 block at [r,c] -> next 9x9 block is [r,c] in the 3x3 grid of 9x9 blocks
3. If next 9x9 is already won, can play in any 9x9 block
4. Win game by winning three 9x9 blocks in a row
"""


class GameLogic:
    def __init__(self):
        """Initialize the game state."""
        # 27x27 board where each cell contains 'X', 'O', or ''
        self.board = [["" for _ in range(27)] for _ in range(27)]

        # 9x9 grid tracking which 3x3 blocks have been won: 'X', 'O', or ''
        self.blocks_3x3 = [["" for _ in range(9)] for _ in range(9)]

        # 3x3 grid tracking which 9x9 blocks have been won: 'X', 'O', or ''
        self.blocks_9x9 = [["" for _ in range(3)] for _ in range(3)]

        # Track which cells in each 3x3 block have been filled
        # blocks_state_3x3[i][j] is a 3x3 grid showing filled cells
        self.blocks_state_3x3 = [
            [[["" for _ in range(3)] for _ in range(3)] for _ in range(9)]
            for _ in range(9)
        ]

        # Track which 3x3 blocks in each 9x9 block have been won
        # blocks_state_9x9[i][j] is a 3x3 grid showing won 3x3 blocks
        self.blocks_state_9x9 = [
            [[["" for _ in range(3)] for _ in range(3)] for _ in range(3)]
            for _ in range(3)
        ]

        # Current player: 'X' or 'O'
        self.current_player = "X"

        # The 9x9 block the current player must play in (row, col in 3x3 grid)
        # None means they can play any 9x9 block
        self.active_9x9_block = None

        # The 3x3 block within the 9x9 block the current player must play in
        # None means they can play any 3x3 block within the active 9x9
        self.active_3x3_block = None

        # Game status: 'playing', 'x_wins', 'o_wins', 'draw'
        self.status = "playing"

    def get_valid_moves(self):
        """
        Get list of valid moves for current player.
        Returns list of (row, col) tuples on the 27x27 board.
        """
        valid_moves = []

        if self.status != "playing":
            return valid_moves

        # Determine which 9x9 block to play in
        if self.active_9x9_block is None:
            # Can play in any 9x9 block that isn't fully won
            active_blocks_9x9 = []
            for b9x9_row in range(3):
                for b9x9_col in range(3):
                    if self.blocks_9x9[b9x9_row][b9x9_col] == "":
                        active_blocks_9x9.append((b9x9_row, b9x9_col))
        else:
            # Restricted to specific 9x9 block
            active_blocks_9x9 = [self.active_9x9_block]

        # For each active 9x9 block, find valid 3x3 blocks and cells
        for b9x9_row, b9x9_col in active_blocks_9x9:
            # Determine which 3x3 blocks to play in
            if (
                self.active_9x9_block == (b9x9_row, b9x9_col)
                and self.active_3x3_block is not None
            ):
                # Restricted to specific 3x3 block
                active_blocks_3x3 = [self.active_3x3_block]
            else:
                # Can play in any non-won 3x3 block within this 9x9
                active_blocks_3x3 = []
                for b3x3_row in range(3):
                    for b3x3_col in range(3):
                        block_3x3_row_global = b9x9_row * 3 + b3x3_row
                        block_3x3_col_global = b9x9_col * 3 + b3x3_col
                        if (
                            self.blocks_3x3[block_3x3_row_global][block_3x3_col_global]
                            == ""
                        ):
                            active_blocks_3x3.append((b3x3_row, b3x3_col))

            # Add all empty cells in valid 3x3 blocks
            for b3x3_row, b3x3_col in active_blocks_3x3:
                block_3x3_row_global = b9x9_row * 3 + b3x3_row
                block_3x3_col_global = b9x9_col * 3 + b3x3_col

                start_row = block_3x3_row_global * 3
                start_col = block_3x3_col_global * 3

                for row in range(start_row, start_row + 3):
                    for col in range(start_col, start_col + 3):
                        if self.board[row][col] == "":
                            valid_moves.append((row, col))

        return valid_moves

    def make_move(self, row, col):
        """
        Make a move at the specified position on the 27x27 board.
        Returns True if move was valid, False otherwise.
        """
        if self.status != "playing":
            return False

        if row < 0 or row >= 27 or col < 0 or col >= 27:
            return False

        if self.board[row][col] != "":
            return False

        # Determine which 9x9 block this move is in
        block_9x9_row = row // 9
        block_9x9_col = col // 9

        # Determine which 3x3 block this move is in (globally)
        block_3x3_row_global = row // 3
        block_3x3_col_global = col // 3

        # Determine which 3x3 block this is within the 9x9 block
        block_3x3_row_local = (row // 3) % 3
        block_3x3_col_local = (col // 3) % 3

        # Validate 9x9 block constraint
        if self.active_9x9_block is not None:
            required_9x9_row, required_9x9_col = self.active_9x9_block
            if block_9x9_row != required_9x9_row or block_9x9_col != required_9x9_col:
                return False

        # Validate 3x3 block constraint (only if current 9x9 not won)
        if block_9x9_row < 3 and block_9x9_col < 3:
            if self.blocks_9x9[block_9x9_row][block_9x9_col] == "":
                # 9x9 block not won, check 3x3 constraint
                if self.active_3x3_block is not None:
                    required_3x3_row, required_3x3_col = self.active_3x3_block
                    if (
                        block_3x3_row_local != required_3x3_row
                        or block_3x3_col_local != required_3x3_col
                    ):
                        return False

        # Check if the 3x3 block is already won
        if self.blocks_3x3[block_3x3_row_global][block_3x3_col_global] != "":
            return False

        # Make the move
        self.board[row][col] = self.current_player
        local_row = row % 3
        local_col = col % 3
        self.blocks_state_3x3[block_3x3_row_global][block_3x3_col_global][local_row][
            local_col
        ] = self.current_player

        # Check if this move wins a 3x3 block
        block_won = self._check_block_3x3_win(
            block_3x3_row_global, block_3x3_col_global
        )
        if block_won:
            self.blocks_3x3[block_3x3_row_global][
                block_3x3_col_global
            ] = self.current_player

            # Update the 9x9 block's state
            self.blocks_state_9x9[block_9x9_row][block_9x9_col][block_3x3_row_local][
                block_3x3_col_local
            ] = self.current_player

            # Check if this move wins the 9x9 block
            if self._check_block_9x9_win(block_9x9_row, block_9x9_col):
                self.blocks_9x9[block_9x9_row][block_9x9_col] = self.current_player

                # Check if this wins the game (3 connected 9x9 blocks)
                if self._check_game_win():
                    self.status = f"{self.current_player}_wins"
                    return True

            # A 3x3 block was won, so set next 9x9 block based on local coordinates
            # A 3x3 block was won. Determine the next 9x9 and next 3x3
            next_9x9_row = block_3x3_row_local
            next_9x9_col = block_3x3_col_local

            # The cell within the just-won 3x3 that completed the win
            target_3x3_row = local_row
            target_3x3_col = local_col

            # If the next 9x9 block is already won, player may play anywhere
            if self.blocks_9x9[next_9x9_row][next_9x9_col] != "":
                self.active_9x9_block = None
                self.active_3x3_block = None
            else:
                # Restrict to that 9x9 block
                self.active_9x9_block = (next_9x9_row, next_9x9_col)

                # Compute global indices for the target 3x3 inside that 9x9
                global_target_3x3_row = next_9x9_row * 3 + target_3x3_row
                global_target_3x3_col = next_9x9_col * 3 + target_3x3_col

                # If the target 3x3 is already won, allow any 3x3 inside that 9x9
                if self.blocks_3x3[global_target_3x3_row][global_target_3x3_col] != "":
                    self.active_3x3_block = None
                else:
                    # Otherwise restrict to that specific 3x3 block
                    self.active_3x3_block = (target_3x3_row, target_3x3_col)
        else:
            # No 3x3 block was won, set constraint for opponent based on cell position
            target_3x3_row = local_row
            target_3x3_col = local_col

            # Set the 9x9 block (stays the same)
            self.active_9x9_block = (block_9x9_row, block_9x9_col)

            # Compute global indices for the target 3x3 inside this same 9x9
            global_target_3x3_row = block_9x9_row * 3 + target_3x3_row
            global_target_3x3_col = block_9x9_col * 3 + target_3x3_col

            # If the target 3x3 is already won, allow any 3x3 inside this 9x9
            if self.blocks_3x3[global_target_3x3_row][global_target_3x3_col] != "":
                self.active_3x3_block = None
            else:
                self.active_3x3_block = (target_3x3_row, target_3x3_col)

        # Switch player
        self.current_player = "O" if self.current_player == "X" else "X"

        return True

    def _check_block_3x3_win(self, block_row, block_col):
        """Check if a 3x3 block is won."""
        block = self.blocks_state_3x3[block_row][block_col]
        player = self.current_player

        # Check rows
        for row in block:
            if all(cell == player for cell in row):
                return True

        # Check columns
        for col in range(3):
            if all(block[row][col] == player for row in range(3)):
                return True

        # Check diagonals
        if all(block[i][i] == player for i in range(3)):
            return True
        if all(block[i][2 - i] == player for i in range(3)):
            return True

        return False

    def _check_block_9x9_win(self, block_row, block_col):
        """Check if a 9x9 block is won (3 in a row of 3x3 blocks)."""
        block = self.blocks_state_9x9[block_row][block_col]
        player = self.current_player

        # Check rows
        for row in block:
            if all(cell == player for cell in row):
                return True

        # Check columns
        for col in range(3):
            if all(block[row][col] == player for row in range(3)):
                return True

        # Check diagonals
        if all(block[i][i] == player for i in range(3)):
            return True
        if all(block[i][2 - i] == player for i in range(3)):
            return True

        return False

    def _check_game_win(self):
        """Check if the game is won (3 connected 9x9 blocks)."""
        player = self.current_player

        # Check rows
        for row in self.blocks_9x9:
            if all(cell == player for cell in row):
                return True

        # Check columns
        for col in range(3):
            if all(self.blocks_9x9[row][col] == player for row in range(3)):
                return True

        # Check diagonals
        if all(self.blocks_9x9[i][i] == player for i in range(3)):
            return True
        if all(self.blocks_9x9[i][2 - i] == player for i in range(3)):
            return True

        return False

    def undo_move(self):
        """
        Undo the last move (not implemented for simplicity).
        """
        pass

    def reset_game(self):
        """Reset the game to initial state."""
        self.__init__()
