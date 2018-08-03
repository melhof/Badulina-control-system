#! bin/python

import os, sys
# allow import parent dir
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time

from app import app
from agua import record_flow_rate

def main():
    with app.app_context():
        while True:
            time.sleep(1)
            record_flow_rate()

if __name__ == '__main__':
    main()
