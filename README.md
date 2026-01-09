# International Tic-Tac-Toe (27x27)

The project is fully generated with AI!
A Python PyQt5 implementation of a three-level Intergalactic Tic-Tac-Toe variant played on a 27x27 grid.

## Game Rules

The game features three levels of nested tic-tac-toe:

**Board Structure:**
- 27x27 grid of individual cells
- Divided into 9 blocks of 9x9 cells (3x3 grid of 9x9 blocks)
- Each 9x9 block contains 9 blocks of 3x3 cells (3x3 grid of 3x3 blocks)

**Gameplay:**
1. Players alternate turns placing X and O
2. Game starts: player can choose any 9x9 block to play in
3. Within a 9x9 block, players must play in 3x3 blocks
4. Win a 3x3 block by getting three in a row (horizontally, vertically, or diagonally)
5. Win a 9x9 block by winning three 3x3 blocks in a row within it
6. Win the game by winning three 9x9 blocks in a row

### Turn Constraint Rules

**After placing a mark at cell position [r, c] within a 3x3 block:**
- Opponent must play in the 3x3 block at coordinates [r, c] within the **same 9x9 block**
- **Exception:** If that 3x3 block is already won, opponent can play any non-won 3x3 block

**After winning a 3x3 block at coordinates [r, c]:**
- Next player must switch to the 9x9 block at coordinates [r, c] in the 3x3 grid of 9x9 blocks
- Within that 9x9 block, opponent can initially play any non-won 3x3 block
- **Exception:** If that 9x9 block is already won, player can choose any 9x9 block

### Examples

**Example 1:** You place at [1, 1] (center) in a 3x3 block of 9x9 block [0, 0]
→ Opponent must play in 3x3 block [1, 1] of the same 9x9 block [0, 0]

**Example 2:** You win 3x3 block [2, 1] in some 9x9 block
→ Next 9x9 block is [2, 1] in the 3x3 grid of 9x9 blocks
→ Opponent can play any non-won 3x3 block within 9x9 block [2, 1]

## Installation

```bash
pip install -r requirements.txt
```

## Running the Game

```bash
python main.py
```

## Project Structure

- `main.py` - Entry point for the application
- `game_logic.py` - Core game logic and state management
- `ui.py` - PyQt5 GUI components and rendering
- `requirements.txt` - Project dependencies
