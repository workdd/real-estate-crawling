import json
import requests

with open('config.json', 'r') as f:
    config = json.load(f)
api_address = config['DEFAULT']['API_ADDRESS']  # 'secret-key-of-myapp'
authorization = config['DEFAULT']['AUTHORIZATION']  # 'web-hooking-url-from-ci-service'


def getLatLng(query):
    res = requests.get(api_address,
                       params={'query': query.strip()},
                       headers={'Authorization': authorization})
    x = json.loads(res.text).get('documents')[0]['x']
    y = json.loads(res.text).get('documents')[0]['y']
    return float(y), float(x), json.loads(res.text).get('documents')[0]['address']['region_3depth_name']
