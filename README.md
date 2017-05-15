# Words with Friends Solver
Finds optimal words to play in Words with Friends (Scrabble) given board
 and letters in hand.

Uses the dictionary word list for scrabble found [here](https://github.com/jonbcard/scrabble-bot/blob/master/src/dictionary.txt).

### Usage

`python solver.py` for a new board.

`python solver.py [saved board filename]` if using a previously saved board state.

Words are input manually, with each word given a position and direction.
The grid is zero-indexed with `(0,0)` in the top-left corner.

It's possible to save the current board state as a `csv` file.
This can be loaded later, via the command-line argument.
*Note: the CSV when viewed directly is transposed.*

### Algorithm
The algorithm is fairly naive and just brute-forces by checking every
word in the dictionary in every possible position.
Blatantly invalid positions (doesn't fit, overwrites current words) are
quickly discarded.

If a word passes some basic validation tests, the board
(with new word added) is checked to ensure every word on the board is
still a valid word. In this way, any 'extra' words generated on the side
 are validated simultaneously.

If a word is deemed valid, its score is calculated, taking into account
the multipliers on the board.
It also considers if a word already on the board is changed by the
addition of the new word, and assigns points accordingly.

Given the naivety of the algorithm, it takes a minute or two to find
every valid move given the current board state and letters in the
player's hand.

