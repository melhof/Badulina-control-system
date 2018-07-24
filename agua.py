#! /usr/bin/python3

from time import sleep

from drivers import KMTronic, Mod4KO


def tick(board):
    for idx in range(board.size):
        board.on(idx)
        sleep(1)
        board.off(idx)

def main():
    kmt = KMTronic()
    mod4 = Mod4KO()
    while True:
        tick(kmt)
        tick(mod4)

def alloff():
    kmt = KMTronic()
    mod4 = Mod4KO()
    for board in [kmt, mod4]:
        for idx in range(board.size):
            board.off(idx)


if __name__ == '__main__':
    main()
