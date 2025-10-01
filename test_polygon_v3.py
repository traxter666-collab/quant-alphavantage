import requests

# Test with proper SSL verification (antivirus exception added)
url = 'https://api.polygon.io/v3/quotes/SPY?limit=1&apikey=_u0zA0CH5ZspOHecb2G8uBxd2DUo4r9D'
r = requests.get(url, timeout=5, verify=True)
data = r.json()

if 'results' in data and len(data['results']) > 0:
    q = data['results'][0]
    bid = q['bid_price']
    ask = q['ask_price']
    mid = (bid + ask) / 2
    spx = mid * 10
    print(f'SPX: ${spx:.2f} (SPY mid: ${mid:.2f})')
else:
    print('Error:', data)
