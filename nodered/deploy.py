#! ../bin/python
'''
run with:
    ./deploy.py push

'''

import sys
import os
import json

import requests
 

host = 'http://{}:1880'.format(os.environ['PI_IP'])

url = host + '/{}/'

def current_flow_rate():
    '''
    example of getting flow rate from python
    get flow rate from node-red:
    this should be in L/s
    '''
    response = requests.get(url.format('water_flow_rate'))
    payload = response.json()
    freq = payload['freq']
    return freq

def list_flows():
    resp = requests.get(url.format('flows'))
    data = resp.json()
    flows = []
    for datum in data:
        if datum['type'] == 'tab':
            tab = (datum['label'], datum['id'])
            flows.append(tab)

    return flows

def read_data(filename):
    with open(filename) as file_descriptor:
        return json.load(file_descriptor)

def write_data(filename, data):
    with open(filename, 'w') as file_descriptor:
        return json.dump(data, file_descriptor, indent=4)

def pull(flow_id):
    resp = requests.get(url.format('flow/' + flow_id))
    data = resp.json()
    return data

def push(flow_id, json):
    return requests.put(url.format('flow/' + flow_id), json=json)

def pull_relays():
    relays_id = '1dd2320a.7877fe'
    data = pull(relays_id)
    write_data('relays.json', data)

def push_relays():
    flow = read_data('relays.json')
    nodes = flow['nodes']

    with open('relays.html') as fd:
        page = fd.read()

    idx = [i for i,n in enumerate(nodes) if n['type'] == 'template'][0]

    flow['nodes'][idx]['template'] = page

    relays_id = '1dd2320a.7877fe'
    push(relays_id, flow)

def pull_all():
    pull_relays()

def push_all():
    push_relays()

def main():
    try:
        cmd = sys.argv[1]
        if cmd == 'pull':
            print('pulling...')
            pull_all()
        elif cmd == 'push':
            print('pushing...')
            push_all()
        else:
            raise Exception()
    except:
        print('Usage: ./deploy.py pull')

if __name__ == '__main__':
    main()
