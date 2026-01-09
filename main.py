"""
Main entry point for Intergalactic Tic-Tac-Toe
"""

import sys
from PyQt5.QtWidgets import QApplication
from ui import GameWindow


def main():
    """Run the application."""
    app = QApplication(sys.argv)
    window = GameWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
