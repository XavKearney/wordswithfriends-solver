import csv
import sys
import threading

BOARD_WIDTH = 11
BOARD_HEIGHT = 11

LETTER_SCORES = {"A":1,"B":4,"C":4,"D":2,"E":1,"F":4,"G":3,"H":3,"I":1,"J":10,"K":5,"L":2,"M":4,"N":2,"O":1,"P":4,
                 "Q": 10,"R":1,"S":1,"T":1,"U":2,"V":5,"W":4,"X":8,"Y":3,"Z":10}


def print_board(board):
    for y in range(BOARD_HEIGHT):
        for x in range(BOARD_WIDTH):
            print(board[x][y], end=" ")
        print("\n", end="")


def add_word_to_board(board, word, position, horizontal=True):
    # horizontal is the default direction, goes vertical if false
    # position as tuple (x, y)
    start_x = position[0]
    start_y = position[1]
    if (horizontal and start_x + len(word) > BOARD_WIDTH)\
            or (not horizontal and start_y + len(word) > BOARD_HEIGHT):
        print("Word doesn't fit on the board!")
        return board
    if horizontal:
        for i in range(len(word)):
            board[start_x+i][start_y] = word[i]
    else:
        for i in range(len(word)):
            board[start_x][start_y+i] = word[i]
    return board


def get_new_word(board):
    new_word = input("New word (blank for end): ").upper()
    if new_word == "":
        return False
    position = tuple(int(x.strip()) for x in input("Enter position x,y: ").split(','))
    horizontal = input("Horizontal? (y/n): ")
    if horizontal == "y":
        horizontal = True
    else:
        horizontal = False
    return add_word_to_board(board, new_word, position,horizontal)


def load_dict(filename):
    with open(filename) as f:
        word_list = f.readlines()
    word_list = [x.strip() for x in word_list]
    return word_list


def save_board(filename,board):
    try:
        with open(filename, "w+", newline="") as f:
            writer = csv.writer(f)
            writer.writerows(board)
    except Exception as e:
        print(e)


def load_board(filename):
    board = [["-" for x in range(BOARD_WIDTH)] for y in range(BOARD_HEIGHT)]
    with open(filename, 'r') as f:
        reader = csv.reader(f)
        i = 0
        for row in reader:
            board[i] = row
            i += 1
    return board


def check_overwrite_word(board, word, position, horizontal):
    start_x = position[0]
    start_y = position[1]
    if horizontal:
        for i in range(len(word)):
            if board[start_x+i][start_y] != word[i] and board[start_x+i][start_y] != "-":
                return False
    else:
        for i in range(len(word)):
            if board[start_x][start_y+i] != word[i] and board[start_x][start_y+i] != "-":
                return False
    return True


def check_word_fits(word, position, horizontal):
    start_x = position[0]
    start_y = position[1]
    if (horizontal and start_x + len(word) > BOARD_WIDTH)\
            or (not horizontal and start_y + len(word) > BOARD_HEIGHT):
        return False
    else:
        return True


def check_word_joins(board, word, position, horizontal):
    start_x = position[0]
    start_y = position[1]
    attaches_to_word = False
    if horizontal:
        for i in range(len(word) + 2):
            if 0 < (start_x - 1) + i < BOARD_WIDTH and board[start_x - 1 + i][start_y] != "-":
                attaches_to_word = True
    else:
        for i in range(len(word) + 2):
            if 0 < (start_y - 1) + i < BOARD_HEIGHT and board[start_x][start_y - 1 + i] != "-":
                attaches_to_word = True
    return attaches_to_word


def check_placement_valid(board, word, position, horizontal, dict_words):
    # check if word fits on board
    if not check_word_fits(word, position, horizontal):
        return False
    # check if word overwrites any current words
    if not check_overwrite_word(board, word, position, horizontal):
        return False
    # check if word joins a current word
    if not check_word_joins(board, word, position, horizontal):
        return False
    # check if all words on board are valid
    test_board = [[board[x][y] for y in range(BOARD_HEIGHT)] for x in range(BOARD_WIDTH)]
    test_board = add_word_to_board(test_board, word, position, horizontal)
    new_board_words = get_board_words(test_board)
    return check_all_words_valid(new_board_words, dict_words)


def get_board_words(board):
    words = []
    # find all horizontal words
    for y in range(BOARD_HEIGHT):
        word = ""
        for x in range(BOARD_WIDTH):
            letter = board[x][y]
            if letter != "-":
                word = word + letter
            elif len(word) > 1:
                words.append(word)
                word = ""
            else:
                word = ""
        if len(word) > 1:
            words.append(word)
    # find all vertical words
    for x in range(BOARD_WIDTH):
        word = ""
        for y in range(BOARD_HEIGHT):
            letter = board[x][y]
            if letter != "-":
                word = word + letter
            elif len(word) > 1:
                words.append(word)
                word = ""
            else:
                word = ""
        if len(word) > 1:
            words.append(word)
    return words


def get_word_score(board, word, position, horizontal, multipliers):
    sum = 0
    start_x = position[0]
    start_y = position[1]
    triple_word = False
    double_word = False
    letter_mults = ["1","2","3"]
    word_mults = ["D","T"]
    if horizontal:
        for i in range(len(word)):
            mult = multipliers[start_x+i][start_y]
            if mult in letter_mults:
                sum += LETTER_SCORES[word[i]] * int(mult)
            elif mult in word_mults:
                if mult == "D":
                    double_word = True
                else:
                    triple_word = True
                sum += LETTER_SCORES[word[i]]
            else:
                sum += LETTER_SCORES[word[i]]
    else:
        for i in range(len(word)):
            mult = multipliers[start_x][start_y+i]
            if mult in letter_mults:
                sum += LETTER_SCORES[word[i]] * int(mult)
            elif mult in word_mults:
                if mult == "D":
                    double_word = True
                else:
                    triple_word = True
                sum += LETTER_SCORES[word[i]]
            else:
                sum += LETTER_SCORES[word[i]]
    if double_word:
        sum *= 2
    if triple_word:
        sum *= 3
    # check if added any new word
    current_board_words = get_board_words(board)
    test_board = [[board[x][y] for y in range(BOARD_HEIGHT)] for x in range(BOARD_WIDTH)]
    test_board = add_word_to_board(test_board, word, position, horizontal)
    new_board_words = get_board_words(test_board)
    for board_word in new_board_words:
        if board_word not in current_board_words and board_word != word:
            for letter in board_word:
                sum += LETTER_SCORES[letter]
    return sum


def check_letters_possible(board, word, position, horizontal, letters_have, unknowns):
    start_x = position[0]
    start_y = position[1]
    letters_available = letters_have[:]
    letters_used = 0
    unknowns_used = 0
    if horizontal:
        for i in range(len(word)):
            if board[start_x+i][start_y] == "-" and word[i] in letters_available:
                    letters_used += 1
                    letters_available.remove(word[i])
            elif board[start_x+i][start_y] == word[i]:
                continue
            else:
                unknowns_used += 1
    else:
        for i in range(len(word)):
            if board[start_x][start_y+i] == "-" and word[i] in letters_available:
                    letters_used += 1
                    letters_available.remove(word[i])
            elif board[start_x][start_y+i] == word[i]:
                continue
            else:
                unknowns_used += 1
    if letters_used > 0 and unknowns_used <= unknowns:
        return True
    else:
        return False


def check_all_words_valid(words, dict_list):
    for w in words:
        if w not in dict_list:
            return False
    return True


def load_multiplier_file(filename):
    multipliers = [["-" for x in range(BOARD_WIDTH)] for y in range(BOARD_HEIGHT)]
    with open(filename, 'r') as f:
        reader = csv.reader(f)
        i = 0
        for row in reader:
            multipliers[i] = row
            i += 1
    return multipliers


def search_words(word_list, game_board, horizontal, letts_avail, unknowns, valid_words):
    if horizontal:
        for word in word_list:
            for x in range(BOARD_WIDTH-len(word)):
                for y in range(BOARD_HEIGHT):
                    position = (x, y)
                    if check_letters_possible(game_board,word,position,horizontal,letts_avail,unknowns):
                        if check_placement_valid(game_board, word, position, horizontal, word_list):
                            score = get_word_score(game_board,word,position,horizontal,multipliers)
                            valid_words.append((word, position, score))
                            print(word + " at " + str(position) + " for " + str(score) + " points!")
    else:
        for word in word_list:
            for y in range(BOARD_HEIGHT-len(word)):
                for x in range(BOARD_WIDTH):
                    position = (x, y)
                    if check_letters_possible(game_board,word,position,horizontal,letts_avail,unknowns):
                        if check_placement_valid(game_board, word, position, horizontal, word_list):
                            score = get_word_score(game_board,word,position,horizontal,multipliers)
                            valid_words.append((word, position, score))
                            print(word + " at " + str(position) + " for " + str(score) + " points!")


if __name__ == "__main__":
    game_board = [["-" for y in range(BOARD_HEIGHT)] for x in range(BOARD_WIDTH)]
    multipliers = load_multiplier_file("multipliers.csv")
    word_list = load_dict("dictionary.txt")
    if len(sys.argv) > 1:
        try:
            game_board = load_board(sys.argv[1])
        except FileNotFoundError:
            print("Usage: python " + sys.argv[0] + " board_filename.csv")

    new_board = game_board
    while new_board:
        boards_words = get_board_words(game_board)
        if check_all_words_valid(boards_words,word_list):
            print(boards_words)
        else:
            print("Word on board not valid!")
        print_board(game_board)

        new_board = get_new_word(game_board)
        if new_board:
            game_board = new_board
    save_name = input("Save board? Enter file name, or blank for no: ")
    if save_name != "":
        save_board(save_name, game_board)

    letts_avail = input("Enter available letters as one string (? for blank):").upper()
    unknowns = letts_avail.count("?")
    letts_avail.replace("?", "")
    letts_avail = list(letts_avail)
    print("Checking for possible word additions...")

    horiz_possible_words = []
    horiz_thread = threading.Thread(target=search_words,
                                    args=(word_list, game_board, True, letts_avail, unknowns, horiz_possible_words))
    horiz_thread.start()
    vert_possible_words = []
    vert_thread = threading.Thread(target=search_words,
                                    args=(word_list, game_board, False, letts_avail, unknowns, vert_possible_words))
    vert_thread.start()
    horiz_thread.join()
    if vert_thread in threading.enumerate():
        vert_thread.join()

    horiz_possible_words = sorted(horiz_possible_words, key=lambda tup: tup[2],reverse=True)
    vert_possible_words = sorted(vert_possible_words, key=lambda tup: tup[2],reverse=True)
    print(horiz_possible_words[:10])
    print(vert_possible_words[:10])
    new_board = game_board
    while new_board:
        print_board(game_board)
        new_board = get_new_word(game_board)
        if new_board:
            game_board = new_board
    save_name = input("Save board? Enter file name, or blank for no: ")
    if save_name != "":
        save_board(save_name, game_board)
