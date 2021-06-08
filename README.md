# Battlestar Generator
A Battlestar (region-less Star Battle) puzzle generator. It samples a uniform random legal star configuration, then repeatedly places blocks on an empty board until the star configuration is the unique solution to the board. Blocks are sampled according to a Boltzmann distribution over the star frequencies of all alternative solutions to the current board.

## Dependencies
* NumPy
* PIL (for generating images)

## Arguments
1. **S**: Board side-length
2. **N**: Stars per row and column
3. **temperature**: Boltzmann distribution (inverse) temperature- higher temperatures produce boards with fewer, but more structured clues, and vice-versa.
4. **n_puzzles**: Number of puzzles to generate

## Usage
```bash
# Generate 2 8x8 1★ boards with temperature 20
python3 battlestar_generator.py 8 1 20 2
```
```
> loading star configs...
> processing star configs...
> generating...
board:
░░░░░░░░░░░░░░░░
░░▓▓▓▓▓▓▓▓▓▓░░░░
░░░░░░░░░░░░░░░░
░░░░░░░░░░▓▓░░░░
░░░░▓▓░░▓▓▓▓▓▓▓▓
░░░░░░▓▓▓▓▓▓▓▓░░
░░░░▓▓░░▓▓▓▓▓▓▓▓
░░░░░░░░░░▓▓▓▓░░
solution:
. . . . . * . .
* . . . . . . .
. . * . . . . .
. . . . . . * .
. . . * . . . .
. . . . . . . *
. * . . . . . .
. . . . * . . .
> saved battlestar_8_1_20_1.png
board:
░░░░░░░░░░░░░░░░
░░▓▓▓▓▓▓░░░░░░░░
░░▓▓░░▓▓░░░░▓▓░░
░░░░░░░░░░▓▓▓▓▓▓
░░▓▓░░░░░░▓▓▓▓▓▓
░░▓▓░░░░░░▓▓▓▓▓▓
░░░░░░░░░░░░▓▓▓▓
░░▓▓▓▓░░░░▓▓▓▓▓▓
solution:
. . . . . . * .
* . . . . . . .
. . . . . . . *
. * . . . . . .
. . . . * . . .
. . * . . . . .
. . . . . * . .
. . . * . . . .
> saved battlestar_8_1_20_2.png
```
