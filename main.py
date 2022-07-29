import os
import sys
import time
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

USER, COMPUTER = +1, -1

board = Board(WINDOW_SIZE, PADDING, BOARD_SIZE, BLOCK_SIZE)
player = USER

is_game_over = False
# winner = None


def mouse_callback(event, px, py, flags, param):
    global player, is_game_over

    if event == cv2.EVENT_LBUTTONDOWN:
        # Convert to board coordinate
        x, y = (px - PADDING_X) // BLOCK_SIZE_W, (py - PADDING_Y) // BLOCK_SIZE_H
        # print(f'Mouse clicked at: {(px, py)}')
        # print(f'Board coordinate: {(x, y)}')

        # User turn
        move_possibilities, move_scores = board.get_possible_moves(player)
        is_move_able = board.can_move(player)
        if not is_move_able:
            is_game_over = True
            show_window()

        else:
            if player == USER:
                move_possibilities_list = list(chain.from_iterable(move_possibilities[y][x]))
                if True in move_possibilities_list:
                    # print('Move: ', move_possibilities[y][x])
                    # print('Count: ', move_possibilities_list.count(True))
                    board.put_player(player, (x, y), move_possibilities[y][x])
                    player = -player
                    show_window()

                # Computer turn
                (x, y), score = board.next_move(player)
                move_possibilities, move_scores = board.get_possible_moves(player)
                # print(f'Computer choice: {(x, y)}')

                if None in [x, y]:
                    is_game_over = True
                    show_window()

                else:
                    board.put_player(player, (x, y), move_possibilities[y][x])
                    player = -player
                    show_window()

                    # User turn
                    move_possibilities, move_scores = board.get_possible_moves(player)
                    is_move_able = board.can_move(player)
                    if not is_move_able:
                        is_game_over = True
                        show_window()


def show_window(wait=True):
    global is_game_over

    img = board.draw_board(player)
    cv2.imshow('Reversi', img)
    if wait:
        cv2.waitKey(1)
        time.sleep(1)

    sc.clear_screen()
    value_user = board.value[board.value == USER]
    score_user = abs(np.sum(value_user))

    value_computer = board.value[board.value == COMPUTER]
    score_computer = abs(np.sum(value_computer))

    print('Reversi Game')
    print(f'Score User: {score_user:03d}')
    print(f'Score Computer: {score_computer:03d}')

    if is_game_over:
        sc.clear_screen()
        print('GAME OVER')

        # Calculate the score
        winner = None
        if score_user > score_computer:
            print('YOU WIN')

        elif score_user < score_computer:
            print('YOU LOSE')

        else:
            print('DRAW')

    print('Press "Q" to quit')
    print('Press "R" to rematch or restart')

    # else:
        # key = cv2.waitKey(0)
        # if key == ord('q') and key == ord('Q'):
        #     print('Exit the game')
        #     sys.exit(0)
        #
        # if key == ord('r') or key == ord('R'):
        #     is_game_over = False
        #     winner = False
        #
        #     board.rematch()
        #
        # show_window()


def main():
    global is_game_over, player


    WINDOW_TITLE = 'Reversi'
    cv2.namedWindow(WINDOW_TITLE)
    cv2.setMouseCallback(WINDOW_TITLE, mouse_callback)
    show_window()

    while True:
        key = cv2.waitKey(0)
        print('Key pressed')
        if key == ord('q') or key == ord('Q'):
            print('Exit the game')
            is_game_over = True
            break

        if key == ord('r') or key == ord('R'):
            is_game_over = False
            player = USER

            board.rematch()
            show_window(wait=False)

    sys.exit(0)


if __name__ == '__main__':
    main()
