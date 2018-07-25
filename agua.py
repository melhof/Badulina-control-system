#! /usr/bin/python3

from time import sleep

from drivers import kmt, mod4ko


def tick(board):
    for idx in range(board.size):
        board.turn_on(idx)
        sleep(1)
        board.turn_off(idx)

def main():
    while True:
        tick(kmt)
        tick(mod4ko)

def all_off():
    for board in [kmt, mod4ko]:
        board.reset()

if __name__ == '__main__':
    main()
