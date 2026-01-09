"""
PyQt5 UI for Intergalactic Tic-Tac-Toe (27x27 version with three-level hierarchy)
"""

from PyQt5.QtWidgets import (
    QMainWindow,
    QWidget,
    QGridLayout,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QMessageBox,
    QFrame,
    QScrollArea,
    QLineEdit,
    QStackedWidget,
    QFileDialog,
)
from PyQt5.QtCore import Qt, pyqtSignal, QObject
from PyQt5.QtGui import QColor, QFont, QPalette, QBrush
from game_logic import GameLogic
from game_persistence import GamePersistence
import json
import os


class CellButton(QPushButton):
    """Custom button for each cell in the tic-tac-toe board."""

    clicked_position = pyqtSignal(int, int)  # row, col

    def __init__(self, row, col):
        super().__init__()
        self.row = row
        self.col = col
        self.player = ""

        self.setMinimumSize(25, 25)
        self.setMaximumSize(25, 25)
        self.setFont(QFont("Arial", 7, QFont.Bold))
        self.setFocusPolicy(Qt.NoFocus)  # Remove focus rectangle cursor
        self.clicked.connect(self._on_click)

    def _on_click(self):
        self.clicked_position.emit(self.row, self.col)

    def set_player(self, player):
        """Set the player mark ('X', 'O', or '')."""
        self.player = player
        self.setText(player)

        if player == "X":
            self.setStyleSheet(
                """
                QPushButton {
                    background-color: #0066cc;
                    color: white;
                    border: 1px solid #004499;
                    border-radius: 2px;
                    font-weight: bold;
                    font-size: 8px;
                }
            """
            )
        elif player == "O":
            self.setStyleSheet(
                """
                QPushButton {
                    background-color: #cc0000;
                    color: white;
                    border: 1px solid #990000;
                    border-radius: 2px;
                    font-weight: bold;
                    font-size: 8px;
                }
            """
            )
        else:
            self.setStyleSheet(
                """
                QPushButton {
                    background-color: white;
                    border: 1px solid #e0e0e0;
                    border-radius: 2px;
                    font-size: 8px;
                }
            """
            )

        self.setEnabled(player == "")

    def highlight_active(self, player="X"):
        """Highlight this cell as part of the active block using player's color."""
        if player == "X":
            # Very light blue for X (available moves)
            self.setStyleSheet(
                """
                QPushButton {
                    background-color: #f5faff;
                    border: 0.5px solid #0066cc;
                    border-radius: 2px;
                }
            """
            )
        else:  # player == 'O'
            # Very light red for O (available moves)
            self.setStyleSheet(
                """
                QPushButton {
                    background-color: #fffaf9;
                    border: 0.5px solid #cc0000;
                    border-radius: 2px;
                }
            """
            )
        self.setEnabled(True)

    def clear_highlight(self):
        """Clear any highlighting from this cell."""
        if self.player == "":
            self.setStyleSheet(
                """
                QPushButton {
                    background-color: white;
                    border: 1px solid #e0e0e0;
                    border-radius: 2px;
                    font-size: 8px;
                }
            """
            )

    def reset(self):
        """Reset the cell."""
        self.player = ""
        self.setText("")
        self.setStyleSheet(
            """
            QPushButton {
                background-color: white;
                border: 1px solid #e0e0e0;
                border-radius: 2px;
            }
        """
        )
        self.setEnabled(True)


class Block3x3Frame(QFrame):
    """Frame representing a 3x3 block (level 0)."""

    def __init__(self, block_row, block_col):
        super().__init__()
        self.block_row = block_row
        self.block_col = block_col

        self.setFrameStyle(QFrame.Box | QFrame.Raised)
        self.setLineWidth(1)

        layout = QGridLayout()
        layout.setSpacing(1)
        layout.setContentsMargins(1, 1, 1, 1)

        self.buttons = []
        for local_row in range(3):
            row_buttons = []
            for local_col in range(3):
                global_row = block_row * 3 + local_row
                global_col = block_col * 3 + local_col
                btn = CellButton(global_row, global_col)
                layout.addWidget(btn, local_row, local_col)
                row_buttons.append(btn)
            self.buttons.append(row_buttons)

        self.setLayout(layout)

    def get_button(self, row, col):
        """Get button at local position within this block."""
        return self.buttons[row][col]

    def highlight_won(self, player):
        """Highlight the entire block as won."""
        if not player:
            self.setStyleSheet("QFrame { border: 1px solid #cccccc; }")
            return

        color_map = {"X": "#d9f0ff", "O": "#ffd9d9"}
        color = color_map.get(player, "white")
        border_color = "#0066cc" if player == "X" else "#cc0000"

        self.setStyleSheet(
            f"""
            QFrame {{
                background-color: {color};
                border: 2px solid {border_color};
            }}
        """
        )


class Block9x9Frame(QFrame):
    """Frame representing a 9x9 block (level 1) - contains nine 3x3 blocks."""

    def __init__(self, block_row, block_col):
        super().__init__()
        self.block_row = block_row
        self.block_col = block_col

        self.setFrameStyle(QFrame.Box | QFrame.Raised)
        self.setLineWidth(2)

        layout = QGridLayout()
        layout.setSpacing(2)
        layout.setContentsMargins(2, 2, 2, 2)

        self.blocks_3x3 = []
        for block_3x3_row in range(3):
            row_frames = []
            for block_3x3_col in range(3):
                global_block_row = block_row * 3 + block_3x3_row
                global_block_col = block_col * 3 + block_3x3_col
                frame = Block3x3Frame(global_block_row, global_block_col)
                layout.addWidget(frame, block_3x3_row, block_3x3_col)
                row_frames.append(frame)
            self.blocks_3x3.append(row_frames)

        self.setLayout(layout)

    def get_cell_button(self, row, col):
        """Get the button at global position within this 9x9 block."""
        block_3x3_row = (row // 3) % 3
        block_3x3_col = (col // 3) % 3
        local_row = row % 3
        local_col = col % 3
        return self.blocks_3x3[block_3x3_row][block_3x3_col].get_button(
            local_row, local_col
        )

    def highlight_won(self, player):
        """Highlight the entire block as won."""
        if not player:
            self.setStyleSheet("QFrame { border: 2px solid #999999; }")
            return

        color_map = {"X": "#c8e6f5", "O": "#ffc8c8"}
        color = color_map.get(player, "white")
        border_color = "#0066cc" if player == "X" else "#cc0000"

        self.setStyleSheet(
            f"""
            QFrame {{
                background-color: {color};
                border: 3px solid {border_color};
            }}
        """
        )


class WelcomePanel(QWidget):
    """Welcome panel with rules and player name inputs."""

    # Signal emitted when Start is clicked with player names
    game_started = pyqtSignal(str, str)  # (name_x, name_o)

    # Signal emitted when a game is loaded
    game_loaded = pyqtSignal(object, str, str)  # (game_logic, name_x, name_o)

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(40, 40, 40, 40)

        # Title
        title = QLabel("Intergalactic Tic-Tac-Toe")
        title.setFont(QFont("Arial", 32, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Rules
        rules_title = QLabel("Rules:")
        rules_title.setFont(QFont("Arial", 16, QFont.Bold))
        rules_title.setAlignment(Qt.AlignCenter)
        layout.addWidget(rules_title)

        layout.addSpacing(10)

        rules_text = QLabel(
            "• The board is 27×27 divided into a 3×3 grid of 9×9 blocks.\n\n"
            "• Each 9×9 block is divided into a 3×3 grid of 3×3 blocks.\n\n"
            "• Place your mark in a cell → your opponent must play in the 3×3 block at that cell's local position.\n\n"
            "• Win a 3×3 block → your opponent plays in the 9×9 block at that block's local position.\n\n"
            "• If the target 3×3 or 9×9 block is already won, you can play anywhere in the next level.\n\n"
            "• Win a 9×9 block → your opponent plays in the 3×3 grid of the 9×9 block at that block's position.\n\n"
            "• First player to win 3 connected 9×9 blocks wins the game!"
        )
        rules_text.setFont(QFont("Arial", 13))
        rules_text.setAlignment(Qt.AlignCenter)
        rules_text.setWordWrap(True)
        layout.addWidget(rules_text)

        layout.addSpacing(40)

        # Player names
        names_title = QLabel("Players:")
        names_title.setFont(QFont("Arial", 16, QFont.Bold))
        names_title.setAlignment(Qt.AlignCenter)
        layout.addWidget(names_title)

        name_layout = QHBoxLayout()
        name_layout.setSpacing(15)
        name_layout.addStretch()

        x_label = QLabel("Player X:")
        x_label.setFont(QFont("Arial", 13, QFont.Bold))
        name_layout.addWidget(x_label)
        self.player_x_input = QLineEdit()
        self.player_x_input.setPlaceholderText("Enter name")
        self.player_x_input.setFont(QFont("Arial", 12))
        self.player_x_input.setFixedWidth(150)
        self.player_x_input.setFixedHeight(35)
        name_layout.addWidget(self.player_x_input)

        o_label = QLabel("Player O:")
        o_label.setFont(QFont("Arial", 13, QFont.Bold))
        name_layout.addWidget(o_label)
        self.player_o_input = QLineEdit()
        self.player_o_input.setPlaceholderText("Enter name")
        self.player_o_input.setFont(QFont("Arial", 12))
        self.player_o_input.setFixedWidth(150)
        self.player_o_input.setFixedHeight(35)
        name_layout.addWidget(self.player_o_input)

        name_layout.addStretch()
        layout.addLayout(name_layout)

        layout.addStretch()

        # Start and Load buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        button_layout.addStretch()

        start_button = QPushButton("Start New Game")
        start_button.setFont(QFont("Arial", 12, QFont.Bold))
        start_button.setFixedHeight(40)
        start_button.setFixedWidth(150)
        start_button.setStyleSheet(
            """
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """
        )
        start_button.clicked.connect(self._on_start_clicked)
        button_layout.addWidget(start_button)

        load_button = QPushButton("Load Game")
        load_button.setFont(QFont("Arial", 12, QFont.Bold))
        load_button.setFixedHeight(40)
        load_button.setFixedWidth(150)
        load_button.setStyleSheet(
            """
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """
        )
        load_button.clicked.connect(self._on_load_clicked)
        button_layout.addWidget(load_button)

        button_layout.addStretch()
        layout.addLayout(button_layout)

        self.setLayout(layout)
        self.setStyleSheet(
            """
            QWidget {
                background-color: white;
            }
            QLabel {
                color: black;
            }
            QLineEdit {
                padding: 8px 12px;
                border: 2px solid #cccccc;
                border-radius: 4px;
                background-color: white;
                font-size: 12px;
            }
            QLineEdit:focus {
                border: 2px solid #4CAF50;
                background-color: white;
            }
        """
        )

    def _on_start_clicked(self):
        """Emit game_started signal with player names."""
        name_x = self.player_x_input.text().strip() or "X"
        name_o = self.player_o_input.text().strip() or "O"
        self.game_started.emit(name_x, name_o)

    def _on_load_clicked(self):
        """Load a saved game."""
        saves = GamePersistence.list_saves()

        if not saves:
            QMessageBox.information(self, "No Saves", "No saved games found.")
            return

        # Create dialog to select save file
        dialog = QFileDialog(self)
        dialog.setFileMode(QFileDialog.ExistingFile)
        dialog.setNameFilter("Game Saves (*.json)")
        dialog.setDirectory(GamePersistence.SAVES_DIR)

        if dialog.exec_():
            filepath = dialog.selectedFiles()[0]
            try:
                game, name_x, name_o = GamePersistence.load_game(filepath)
                self.set_names(name_x, name_o)
                self.game_loaded.emit(game, name_x, name_o)
            except Exception as e:
                QMessageBox.critical(
                    self, "Load Failed", f"Could not load game: {str(e)}"
                )

    def set_names(self, name_x: str, name_o: str):
        """Pre-fill player names (for restart)."""
        self.player_x_input.setText(name_x)
        self.player_o_input.setText(name_o)


class WelcomeWindow(QMainWindow):
    """Welcome screen with rules and player name inputs."""

    # Signal emitted when Start is clicked with player names
    game_started = pyqtSignal(str, str)  # (name_x, name_o)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Intergalactic Tic-Tac-Toe (27x27)")
        self.setGeometry(50, 50, 800, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Title
        title = QLabel("Intergalactic Tic-Tac-Toe")
        title.setFont(QFont("Arial", 24, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Rules
        rules_title = QLabel("Rules:")
        rules_title.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(rules_title)

        rules_text = QLabel(
            "• The board is 27×27 divided into a 3×3 grid of 9×9 blocks.\n"
            "• Each 9×9 block is divided into a 3×3 grid of 3×3 blocks.\n"
            "• Place your mark in a cell → your opponent must play in the 3×3 block at that cell's local position.\n"
            "• Win a 3×3 block → your opponent plays in the 9×9 block at that block's local position.\n"
            "• If the target 3×3 or 9×9 block is already won, you can play anywhere in the next level.\n"
            "• Win a 9×9 block → your opponent plays in the 3×3 grid of the 9×9 block at that block's position.\n"
            "• First player to win 3 connected 9×9 blocks wins the game!"
        )
        rules_text.setFont(QFont("Arial", 10))
        rules_text.setWordWrap(True)
        layout.addWidget(rules_text)

        layout.addSpacing(20)

        # Player names
        names_title = QLabel("Players:")
        names_title.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(names_title)

        name_layout = QHBoxLayout()
        name_layout.setSpacing(10)

        name_layout.addWidget(QLabel("Player X:"))
        self.player_x_input = QLineEdit()
        self.player_x_input.setPlaceholderText("Enter name")
        name_layout.addWidget(self.player_x_input)

        name_layout.addWidget(QLabel("Player O:"))
        self.player_o_input = QLineEdit()
        self.player_o_input.setPlaceholderText("Enter name")
        name_layout.addWidget(self.player_o_input)

        layout.addLayout(name_layout)

        layout.addStretch()

        # Start button
        start_button = QPushButton("Start")
        start_button.setFont(QFont("Arial", 12, QFont.Bold))
        start_button.setFixedHeight(40)
        start_button.clicked.connect(self._on_start_clicked)
        layout.addWidget(start_button)

        central_widget.setLayout(layout)
        self.setStyleSheet(
            """
            QMainWindow {
                background-color: #f5f5f5;
            }
            QPushButton {
                padding: 8px 16px;
                border-radius: 4px;
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QLineEdit {
                padding: 6px;
                border: 1px solid #ccc;
                border-radius: 4px;
            }
        """
        )

    def _on_start_clicked(self):
        """Emit game_started signal with player names."""
        name_x = self.player_x_input.text().strip() or "X"
        name_o = self.player_o_input.text().strip() or "O"
        self.game_started.emit(name_x, name_o)

    def set_names(self, name_x: str, name_o: str):
        """Pre-fill player names (for restart)."""
        self.player_x_input.setText(name_x)
        self.player_o_input.setText(name_o)


class GameBoard(QWidget):
    """Main game board widget containing the full 27x27 board."""

    def __init__(self, game_logic):
        super().__init__()
        self.game = game_logic
        self.blocks_9x9 = []

        layout = QGridLayout()
        layout.setSpacing(3)
        layout.setContentsMargins(5, 5, 5, 5)

        for block_9x9_row in range(3):
            row_frames = []
            for block_9x9_col in range(3):
                frame = Block9x9Frame(block_9x9_row, block_9x9_col)
                layout.addWidget(frame, block_9x9_row, block_9x9_col)
                row_frames.append(frame)
            self.blocks_9x9.append(row_frames)

        self.setLayout(layout)

    def get_cell_button(self, row, col):
        """Get the button at global position (27x27 board)."""
        block_9x9_row = row // 9
        block_9x9_col = col // 9
        local_row = row % 9
        local_col = col % 9
        return self.blocks_9x9[block_9x9_row][block_9x9_col].get_cell_button(
            local_row, local_col
        )

    def update_board(self):
        """Update the board display based on game state."""
        # Update all cells and clear previous highlighting
        for row in range(27):
            for col in range(27):
                btn = self.get_cell_button(row, col)
                btn.set_player(self.game.board[row][col])
                btn.clear_highlight()

        # Highlight active 3x3 block within active 9x9 block
        if (
            self.game.active_3x3_block is not None
            and self.game.active_9x9_block is not None
        ):
            block_9x9_row, block_9x9_col = self.game.active_9x9_block
            block_3x3_row, block_3x3_col = self.game.active_3x3_block
            block_3x3_row_global = block_9x9_row * 3 + block_3x3_row
            block_3x3_col_global = block_9x9_col * 3 + block_3x3_col

            for local_row in range(3):
                for local_col in range(3):
                    global_row = block_3x3_row_global * 3 + local_row
                    global_col = block_3x3_col_global * 3 + local_col
                    btn = self.get_cell_button(global_row, global_col)
                    if btn.player == "":
                        btn.highlight_active(self.game.current_player)
        elif self.game.active_9x9_block is not None:
            # Can play anywhere in active 9x9 block (in non-won 3x3 blocks)
            block_9x9_row, block_9x9_col = self.game.active_9x9_block
            for local_row in range(9):
                for local_col in range(9):
                    global_row = block_9x9_row * 9 + local_row
                    global_col = block_9x9_col * 9 + local_col
                    btn = self.get_cell_button(global_row, global_col)
                    if btn.player == "":
                        # Check if in won 3x3 block
                        block_3x3_row = global_row // 3
                        block_3x3_col = global_col // 3
                        if self.game.blocks_3x3[block_3x3_row][block_3x3_col] == "":
                            btn.highlight_active(self.game.current_player)
        elif self.game.active_9x9_block is None:
            # Can play in any 9x9 block, highlight all non-won 3x3 blocks
            for row in range(27):
                for col in range(27):
                    block_3x3_row = row // 3
                    block_3x3_col = col // 3
                    block_9x9_row = row // 9
                    block_9x9_col = col // 9

                    btn = self.get_cell_button(row, col)
                    if btn.player == "":
                        # Highlight if in non-won 3x3 and non-won 9x9
                        if (
                            self.game.blocks_3x3[block_3x3_row][block_3x3_col] == ""
                            and self.game.blocks_9x9[block_9x9_row][block_9x9_col] == ""
                        ):
                            btn.highlight_active(self.game.current_player)

        # Highlight won 3x3 blocks
        for block_row in range(9):
            for block_col in range(9):
                winner = self.game.blocks_3x3[block_row][block_col]
                if winner:
                    block_9x9_row = block_row // 3
                    block_9x9_col = block_col // 3
                    block_3x3_row = block_row % 3
                    block_3x3_col = block_col % 3
                    self.blocks_9x9[block_9x9_row][block_9x9_col].blocks_3x3[
                        block_3x3_row
                    ][block_3x3_col].highlight_won(winner)

        # Highlight won 9x9 blocks
        for block_row in range(3):
            for block_col in range(3):
                winner = self.game.blocks_9x9[block_row][block_col]
                if winner:
                    self.blocks_9x9[block_row][block_col].highlight_won(winner)

    def reset_board(self):
        """Reset all buttons."""
        for block_9x9_row in range(3):
            for block_9x9_col in range(3):
                self.blocks_9x9[block_9x9_row][block_9x9_col].highlight_won("")
                for block_3x3_row in range(3):
                    for block_3x3_col in range(3):
                        self.blocks_9x9[block_9x9_row][block_9x9_col].blocks_3x3[
                            block_3x3_row
                        ][block_3x3_col].highlight_won("")

        for row in range(27):
            for col in range(27):
                self.get_cell_button(row, col).reset()


class GamePanel(QWidget):
    """Game panel showing the board and game state."""

    # Signal emitted when game ends (winner_mark)
    game_ended = pyqtSignal(str)  # 'X' or 'O'

    # Signal emitted when restart is requested
    restart_requested = pyqtSignal()

    def __init__(self, player_x_name: str, player_o_name: str):
        super().__init__()
        self.game = GameLogic()
        self.player_names = {"X": player_x_name, "O": player_o_name}
        self.game_over_shown = False

        # Create layout
        layout = QVBoxLayout()

        # Status label
        self.status_label = QLabel(
            f"Game Started - {player_x_name} (X) plays first (can play anywhere)"
        )
        self.status_label.setFont(QFont("Arial", 11, QFont.Bold))
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)

        # Create game board
        self.board = GameBoard(self.game)

        # Center board vertically and horizontally
        board_layout = QHBoxLayout()
        board_layout.addStretch()
        board_layout.addWidget(self.board)
        board_layout.addStretch()

        center_layout = QVBoxLayout()
        center_layout.addStretch()
        center_layout.addLayout(board_layout)
        center_layout.addStretch()
        layout.addLayout(center_layout)

        # Connect cell signals
        for block_9x9_row in range(3):
            for block_9x9_col in range(3):
                for block_3x3_row in range(3):
                    for block_3x3_col in range(3):
                        global_block_row = block_9x9_row * 3 + block_3x3_row
                        global_block_col = block_9x9_col * 3 + block_3x3_col
                        for local_row in range(3):
                            for local_col in range(3):
                                btn = (
                                    self.board.blocks_9x9[block_9x9_row][block_9x9_col]
                                    .blocks_3x3[block_3x3_row][block_3x3_col]
                                    .get_button(local_row, local_col)
                                )
                                btn.clicked_position.connect(self._on_cell_clicked)

        # Control buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        button_layout.addStretch()

        save_button = QPushButton("Save Game")
        save_button.setFont(QFont("Arial", 11, QFont.Bold))
        save_button.setFixedHeight(40)
        save_button.setFixedWidth(120)
        save_button.setStyleSheet(
            """
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """
        )
        save_button.clicked.connect(self._on_save_game)
        button_layout.addWidget(save_button)

        load_button = QPushButton("Load Game")
        load_button.setFont(QFont("Arial", 11, QFont.Bold))
        load_button.setFixedHeight(40)
        load_button.setFixedWidth(120)
        load_button.setStyleSheet(
            """
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """
        )
        load_button.clicked.connect(self._on_load_game)
        button_layout.addWidget(load_button)

        restart_button = QPushButton("Restart")
        restart_button.setFont(QFont("Arial", 11, QFont.Bold))
        restart_button.setFixedHeight(40)
        restart_button.setFixedWidth(120)
        restart_button.setStyleSheet(
            """
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """
        )
        restart_button.clicked.connect(self._on_restart)
        button_layout.addWidget(restart_button)

        button_layout.addStretch()
        layout.addLayout(button_layout)

        self.setLayout(layout)
        self.setStyleSheet(
            """
            QWidget {
                background-color: #f5f5f5;
            }
            QLabel {
                padding: 10px;
            }
            QPushButton {
                padding: 8px 16px;
                border-radius: 4px;
            }
        """
        )

        self.update_display()

    def _on_cell_clicked(self, row, col):
        """Handle cell click."""
        if self.game_over_shown:
            return

        if self.game.make_move(row, col):
            self.update_display()

            if self.game.status != "playing":
                self._on_game_over()
        else:
            QMessageBox.warning(self, "Invalid Move", "Cannot place mark here!")

    def update_display(self):
        """Update the display."""
        self.board.update_board()

        if self.game.status == "playing":
            player_label = self.player_names.get(
                self.game.current_player, self.game.current_player
            )
            status_text = f"Current Player: {player_label} ({self.game.current_player})"

            if self.game.active_9x9_block is not None:
                br, bc = self.game.active_9x9_block
                status_text += f" | Playing in 9x9 Block [{br},{bc}]"

                if self.game.active_3x3_block is not None:
                    r, c = self.game.active_3x3_block
                    status_text += f" | Must use 3x3 Block [{r},{c}]"
                else:
                    status_text += " | (Can use any 3x3 block)"
            else:
                status_text += " | (Can play any 9x9 block)"

            self.status_label.setText(status_text)
        else:
            winner = self.game.status.split("_")[0]
            winner_name = self.player_names.get(winner, winner)
            self.status_label.setText(f"Game Over - {winner_name} ({winner}) Wins! 🎉")

    def _on_game_over(self):
        """Handle end of game: show result message."""
        self.game_over_shown = True
        winner = self.game.status.split("_")[0]
        winner_name = self.player_names.get(winner, winner)
        QMessageBox.information(
            self,
            "Game Over",
            f"{winner_name} ({winner}) Wins!\n\nClick Restart to play again.",
            QMessageBox.Ok,
        )
        self.game_ended.emit(winner)

    def _on_restart(self):
        """Emit restart signal to return to welcome screen."""
        self.restart_requested.emit()

    def _on_save_game(self):
        """Save the current game state."""
        try:
            filepath = GamePersistence.save_game(
                self.game, self.player_names["X"], self.player_names["O"]
            )
            filename = os.path.basename(filepath)
            QMessageBox.information(
                self, "Save Successful", f"Game saved as: {filename}"
            )
        except Exception as e:
            QMessageBox.critical(self, "Save Failed", f"Could not save game: {str(e)}")

    def _on_load_game(self):
        """Load a saved game state."""
        saves = GamePersistence.list_saves()

        if not saves:
            QMessageBox.information(self, "No Saves", "No saved games found.")
            return

        # Create dialog to select save file
        dialog = QFileDialog(self)
        dialog.setFileMode(QFileDialog.ExistingFile)
        dialog.setNameFilter("Game Saves (*.json)")
        dialog.setDirectory(GamePersistence.SAVES_DIR)

        if dialog.exec_():
            filepath = dialog.selectedFiles()[0]
            try:
                game, name_x, name_o = GamePersistence.load_game(filepath)
                self.game = game
                self.player_names = {"X": name_x, "O": name_o}
                self.game_over_shown = False
                self.board.game = game
                self.update_display()
                QMessageBox.information(
                    self,
                    "Load Successful",
                    f"Game loaded: {os.path.basename(filepath)}",
                )
            except Exception as e:
                QMessageBox.critical(
                    self, "Load Failed", f"Could not load game: {str(e)}"
                )

    def reset_game(self):
        """Reset the game."""
        self.game.reset_game()
        self.board.reset_board()
        self.game_over_shown = False
        self.update_display()


class GameWindow(QMainWindow):
    """Main window with stacked views for welcome and game."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Intergalactic Tic-Tac-Toe (27x27)")
        self.setGeometry(50, 50, 1000, 700)
        self.showMaximized()  # Start window maximized

        # Create stacked widget to hold both views
        self.stacked = QStackedWidget()
        self.setCentralWidget(self.stacked)

        # Create welcome panel
        self.welcome_panel = WelcomePanel()
        self.welcome_panel.game_started.connect(self._on_game_started)
        self.welcome_panel.game_loaded.connect(self._on_game_loaded)
        self.stacked.addWidget(self.welcome_panel)

        # Placeholder for game panel (will be created on start)
        self.game_panel = None

        # Start with welcome view
        self.stacked.setCurrentIndex(0)

        self.setStyleSheet(
            """
            QMainWindow {
                background-color: #f5f5f5;
            }
        """
        )

    def _on_game_started(self, name_x: str, name_o: str):
        """Handle start from welcome panel."""
        # Create new game panel with player names
        if self.game_panel is not None:
            # Remove old game panel
            self.stacked.removeWidget(self.game_panel)

        self.game_panel = GamePanel(name_x, name_o)
        self.game_panel.restart_requested.connect(self._on_restart_requested)
        self.stacked.addWidget(self.game_panel)

        # Switch to game view
        self.stacked.setCurrentWidget(self.game_panel)
        self.welcome_panel.set_names(name_x, name_o)

    def _on_game_loaded(self, game_logic, name_x: str, name_o: str):
        """Handle game load from welcome panel."""
        # Create new game panel with loaded game
        if self.game_panel is not None:
            self.stacked.removeWidget(self.game_panel)

        self.game_panel = GamePanel(name_x, name_o)
        self.game_panel.game = game_logic  # Override with loaded game
        self.game_panel.board.game = game_logic
        self.game_panel.restart_requested.connect(self._on_restart_requested)
        self.stacked.addWidget(self.game_panel)

        # Switch to game view
        self.stacked.setCurrentWidget(self.game_panel)
        self.game_panel.update_display()
        self.welcome_panel.set_names(name_x, name_o)

    def _on_restart_requested(self):
        """Handle restart from game panel."""
        # Switch back to welcome view
        self.stacked.setCurrentWidget(self.welcome_panel)
