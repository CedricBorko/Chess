def valid_target(target):
    return 0 <= target < 64


def on_row(row, position):
    return position // 8 == row - 1

