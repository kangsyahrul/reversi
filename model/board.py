from itertools import chain

import cv2
import numpy as np


class Board:

    def __init__(self, window_size, padding, board_size, block_size):
        self.window_w, self.window_h = window_size
        self.padding_w, self.padding_h = padding
        self.board_w, self.board_h = board_size
        self.block_w, self.block_h = block_size

        self.background = self.create_background()
        self.value = self.create_board()
        self.shape = self.value.shape

    def create_board(self):
        value = np.zeros((self.board_h, self.board_w), dtype=np.int8)
        h, w = value.shape
        x, y = (w // 2) - 1, (h // 2) - 1

        value[y + 0][x + 0], value[y + 0][x + 1] = +1, -1
        value[y + 1][x + 0], value[y + 1][x + 1] = -1, +1

        return value

    def create_background(self):
        img = np.zeros((self.window_h, self.window_w, 3), dtype=np.int8)

        x1, y1 = self.padding_w, self.padding_h
        x2, y2 = self.window_w - self.padding_w, self.window_h - self.padding_h

        # img = cv2.rectangle(img, (x1, y1), (x2, y2), (145, 249, 130), -1)
        img = cv2.rectangle(img, (x1, y1), (x2, y2), (0, 249, 0), -1)

        for x in range(self.padding_w, self.window_w - self.padding_w, self.block_w):
            img = cv2.line(img, (x, y1), (x, y2), (0, 0, 0), 1, cv2.LINE_AA)

        for y in range(self.padding_h, self.window_h - self.padding_w, self.block_h):
            img = cv2.line(img, (x1, y), (x2, y), (0, 0, 0), 1, cv2.LINE_AA)

        return img

    def draw_pions(self, img):
        for y, row in enumerate(self.value):
            for x, val in enumerate(row):
                if val != 0:
                    xc, yc = self.padding_w + x * self.block_w + self.block_w // 2, self.padding_h + y * self.block_h + self.block_h // 2
                    if val == 1:
                        color = (200, 200, 200)
                    else:
                        color = (0, 0, 0)
                    img = cv2.circle(img, (xc, yc), self.block_w // 3, color, -1)
        return img

    def draw_possible_moves(self, img, player):
        possible_moves = self.get_possible_moves(player)
        h, w = possible_moves.shape[:2]
        for x in range(w):
            for y in range(h):
                val = possible_moves[y][x]
                if True in list(chain.from_iterable(val)):
                    xc = self.padding_w + x * self.block_w + self.block_w // 2
                    yc = self.padding_h + y * self.block_h + self.block_h // 2
                    if player == 1:
                        color = (200, 200, 200)
                    else:
                        color = (0, 0, 0)
                    img = cv2.circle(img, (xc, yc), self.block_w // 3, color, 2)

                    for y_, _ in enumerate(val):
                        for x_, __ in enumerate(_):
                            if __:
                                dx = (1 - x_) * self.block_w // 4
                                dy = (1 - y_) * self.block_w // 4
                                img = cv2.circle(img, (xc + dx, yc + dy), self.block_w // 8, color, -1)

        return img

    def draw_board(self, player):
        img = self.background.copy()

        # Draw pions
        img = self.draw_pions(img)

        # Draw possible moves
        img = self.draw_possible_moves(img, player)

        return img

    def get_possible_moves(self, player):
        moves = np.zeros((self.board_h, self.board_w, 3, 3), dtype=bool)

        for y in range(self.board_h):
            for x in range(self.board_w):
                val = self.value[y][x]
                if val == player:
                    # Vertical
                    moves = self.get_diagonal_possibility(x, y, player, moves, directions=[(0, -1), (0, 1)])

                    # Horizontal
                    moves = self.get_diagonal_possibility(x, y, player, moves, directions=[(-1, 0), (1, 0)])

                    # Diagonal
                    moves = self.get_diagonal_possibility(x, y, player, moves)

        return moves

    def put_player(self, player, coordinate, mode):
        x, y = coordinate
        self.value[y][x] = player
        print(f'coordinate: {coordinate}')

        # Vertical move
        for direction, (start, end, inc) in [(mode[0][1], [y + 1, self.board_h, 1]), (mode[2][1], [y - 1, -1, -1])]:
            if not direction:
                continue
            for y1 in range(start, end, inc):
                if self.value[y1][x] == -player:
                    self.value[y1][x] = player
                else:
                    break

        # Horizontal move
        for direction, (start, end, inc) in [(mode[1][0], [x + 1, self.board_w, +1]), (mode[1][2], [x - 1, -1, -1])]:
            print(f'(direction, (start, end, inc)): {direction, (start, end, inc)}')
            if not direction:
                continue
            for x1 in range(start, end, inc):
                if self.value[y][x1] == -player:
                    self.value[y][x1] = player
                else:
                    break

        # Diagonal move
        for direction, (dx, dy) in [(mode[0][0], (+1, +1)), (mode[0][2], (-1, +1)), (mode[2][0], (1, -1)), (mode[2][2], (-1, -1))]:
            if not direction:
                continue
            print(f'DIAGONAL: {(dx, dy)}')
            i = 1
            while True:
                x1, y1 = x + dx * (i + 0), y + dy * (i + 0)

                if (x1 < 0 or self.board_w <= x1) or (y1 < 0 or self.board_h <= y1):
                    break

                if self.value[y1][x1] == -player:
                    self.value[y1][x1] = player
                else:
                    break

                i += 1

    def get_vertical_possibility(self, x, y, player, moves, mode='up'):
        if mode == 'up':
            c, d = 1, 0
            y_start, y_end, y_inc = (y - 1, -1, -1)
        else:
            c, d = 1, 2
            y_start, y_end, y_inc = (y + 1, self.board_h, 1)

        coordinate = (None, None)
        for y1 in range(y_start, y_end, y_inc):
            val1 = self.value[y1][x]
            val2 = self.value[y1 - y_inc][x]
            if val1 == 0:
                if val2 == -player:
                    coordinate = (x, y1)
                elif val2 == player:
                    coordinate = (None, None)
            else:
                coordinate = (None, None)

        if coordinate != (None, None):
            a, b = coordinate
            moves[b][a][d][c] = True

        return moves

    def get_horizontal_possibility(self, x, y, player, moves, mode='left'):
        if mode == 'left':
            c, d = 0, 1
            x_start, x_end, x_inc = (x - 1, -1, -1)
        else:
            c, d = 2, 1
            x_start, x_end, x_inc = (x + 1, self.board_w, 1)

        coordinate = (None, None)
        for x1 in range(x_start, x_end, x_inc):
            val2 = self.value[y][x1]
            val3 = self.value[y][x1 - x_inc]
            if val2 == 0:
                if val3 == -player:
                    coordinate = (x1, y)
                elif val3 == player:
                    coordinate = (None, None)
            else:
                coordinate = (None, None)

        if coordinate != (None, None):
            a, b = coordinate
            moves[b][a][d][c] = True

        return moves

    def get_diagonal_possibility(self, x, y, player, moves, directions=None):
        if directions is None:
            directions = [(-1, -1), (1, -1), (-1, 1), (1, 1)]

        print(f'player: {player}')
        print(f'(x, y): {(x, y)}')
        print(f'directions: {directions}')
        for (dx, dy) in directions:
            c, d = 1 + dx, 1 + dy
            print(f'(dx, dy): {(dx, dy)}')
            i = 2
            coordinate = (None, None)
            while True:
                x1, y1 = x + dx * (i + 0), y + dy * (i + 0)
                x2, y2 = x + dx * (i - 1), y + dy * (i - 1)

                print(f'\t(x1, y1): {(x1, y1)}')
                print(f'\t(x2, y2): {(x2, y2)}')

                if ((x1 < 0 or self.board_w <= x1)
                        or (x2 < 0 or self.board_w <= x2)
                        or (y1 < 0 or self.board_h <= y1)
                        or (y2 < 0 or self.board_h <= y2)):
                    break

                val1, val2 = None, None

                if (0 <= x1 < self.board_w) and (0 <= y1 < self.board_h):
                    val1 = self.value[y1][x1]
                print(f'\tval1: {val1}')

                if (0 <= x2 < self.board_w) and (0 <= y2 < self.board_h):
                    val2 = self.value[y2][x2]
                print(f'\tval2: {val2}')

                if val1 is None:
                    val1 = 0

                if val2 is None:
                    continue

                if (val1 is None) and (val2 is None):
                    break

                if val1 == 0:
                    if val2 == -player:
                        coordinate = (x1, y1)
                        print(f'\t\tcoordinate: {coordinate}')
                    elif val2 == player:
                        coordinate = (None, None)
                else:
                    if coordinate != (None, None):
                        coordinate = (None, None)
                        break

                i += 1

            print(f'  RESULT: {coordinate}')
            a, b = coordinate
            if a is not None and b is not None:
                moves[b][a][d][c] = True
                print(f'  UPDATE: {coordinate}')

        return moves
