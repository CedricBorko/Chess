import string


def valid_target(coordinate):
    return 0 <= coordinate <= 63


def on_row(row_index, pos):
    return pos // 8 == row_index


def pos_to_letter_code(pos):
    letters = "abcdefgh"
    x = letters[pos % 8]
    y = 8 - (pos // 8)
    return f"{x}{y}"


def letter_code_to_number(letter, num):
    x = string.ascii_lowercase.index(letter)
    y = 8 - num
    return y * 8 + x
