#! bin/python
'''Test program. running "./test_script.py" will tick through relays
'''

from agua import *

def main():
    while True:
        record_flow_rate()

if __name__ == '__main__':
    main()
