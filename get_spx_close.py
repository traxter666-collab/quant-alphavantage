#!/usr/bin/env python3
import requests

api_key = '_u0zA0CH5ZspOHecb2G8uBxd2DUo4r9D'
url = f'https://api.polygon.io/v2/aggs/ticker/I:SPX/prev?adjusted=true&apikey={api_key}'
response = requests.get(url, timeout=20)
data = response.json()

if data.get('status') == 'OK' and 'results' in data and len(data['results']) > 0:
    close_price = data['results'][0]['c']
    open_price = data['results'][0]['o']
    high_price = data['results'][0]['h']
    low_price = data['results'][0]['l']
    volume = data['results'][0]['v']

    print(f'SPX (I:SPX) OFFICIAL CLOSING DATA:')
    print(f'Close: ${close_price:.2f}')
    print(f'Open: ${open_price:.2f}')
    print(f'High: ${high_price:.2f}')
    print(f'Low: ${low_price:.2f}')
    print(f'Volume: {volume:,}')
else:
    print(f'Error: {data}')
