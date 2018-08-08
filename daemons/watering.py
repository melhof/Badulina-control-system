#! bin/python
'''
This script runs the irrigation schedule
'''

# allow import parent dir:
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time

from app import app
from domain import apply_schedule

def main():
    with app.app_context():
        while True:
            apply_schedule()
            time.sleep(10)

if __name__ == '__main__':
    main()
