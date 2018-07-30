#! /usr/bin/python3
'''Test program. running "./test_script.py" will tick through relays
'''

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

if __name__ == '__main__':
    main()
