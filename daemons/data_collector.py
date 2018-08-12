#! bin/python
'''
this script continuously feeds sensor readings into the DB
'''

# allow import parent dir:
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time

from app import app
from domain import record_flow_rate

def main():
    with app.app_context():
        while True:
            record_flow_rate() # ~10s
            time.sleep(50)

if __name__ == '__main__':
    main()
