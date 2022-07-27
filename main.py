import os
from itertools import chain

import cv2

from model.board import Board
import numpy as np
import util.screen as sc


# GAME SETTING
BOARD_SIZE_W, BOARD_SIZE_H = BOARD_SIZE = (8, 8)

# SCREEN SETTING
BLOCK_SIZE_W, BLOCK_SIZE_H = BLOCK_SIZE = (48, 48)
PADDING_X, PADDING_Y = PADDING = (24, 24)
WINDOW_SIZE_W, WINDOW_SIZE_H = WINDOW_SIZE = (PADDING_X * 2 + BOARD_SIZE_W * BLOCK_SIZE_W, PADDING_Y * 2 + BOARD_SIZE_H * BLOCK_SIZE_H)

board = Board(WINDOW_SIZE, PADDING, BOARD_SIZE, BLOCK_SIZE)
player = 1


def mouse_callback(event, px, py, flags, param):
    global player

    if event == cv2.EVENT_LBUTTONDOWN:
        # Convert ot board coordinate
        x, y = (px - PADDING_X) // BLOCK_SIZE_W, (py - PADDING_Y) // BLOCK_SIZE_H
        print(f'Mouse clicked at: {(px, py)}')
        print(f'Board coordinate: {(x, y)}')

        possible_moves = board.get_possible_moves(player)
        possible_moves
        if True in list(chain.from_iterable(possible_moves[y][x])):
            print('Move: ', possible_moves[y][x])
            board.put_player(player, (x, y), possible_moves[y][x])
            player = -player
            show_window()


def show_window():
    img = board.draw_board(player)
    cv2.imshow('Reversi', img)


def main():
    sc.clear_screen()

    WINDOW_TITLE = 'Reversi'
    cv2.namedWindow(WINDOW_TITLE)
    cv2.setMouseCallback(WINDOW_TITLE, mouse_callback)
    while True:
        show_window()
        key = cv2.waitKey(0)
        if key == ord('q'):
            break

    print('Game Over')


if __name__ == '__main__':
    main()