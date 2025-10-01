"""
Test various SPX endpoints for real-time data
"""
import requests
from datetime import datetime

POLYGON_KEY = "_u0zA0CH5ZspOHecb2G8uBxd2DUo4r9D"

print(f"Current Time: {datetime.now()}")
print("=" * 70)

# Test 1: Aggregates (previous day close)
print("\n1. Testing I:SPX aggregates (prev day close)...")
url = f"https://api.polygon.io/v2/aggs/ticker/I:SPX/prev?adjusted=true&apiKey={POLYGON_KEY}"
try:
    r = requests.get(url, timeout=5)
    if r.status_code == 200:
        data = r.json()
        if 'results' in data and len(data['results']) > 0:
            print(f"   SPX Close (prev): ${data['results'][0]['c']:.2f}")
except Exception as e:
    print(f"   Error: {e}")

# Test 2: Try SPY real-time and convert
print("\n2. Testing SPY snapshot × 10 conversion...")
url = f"https://api.polygon.io/v2/snapshot/locale/us/markets/stocks/tickers/SPY?apiKey={POLYGON_KEY}"
try:
    r = requests.get(url, timeout=5)
    if r.status_code == 200:
        data = r.json()
        if 'ticker' in data and 'day' in data['ticker']:
            spy_price = data['ticker']['day'].get('c')
            if spy_price:
                spx_equiv = spy_price * 10
                print(f"   SPY: ${spy_price:.2f} → SPX equiv: ${spx_equiv:.2f}")
except Exception as e:
    print(f"   Error: {e}")

# Test 3: Try last trade for SPY
print("\n3. Testing SPY last trade...")
url = f"https://api.polygon.io/v2/last/trade/SPY?apiKey={POLYGON_KEY}"
try:
    r = requests.get(url, timeout=5)
    if r.status_code == 200:
        data = r.json()
        if 'results' in data:
            spy_price = data['results']['p']
            spx_equiv = spy_price * 10
            print(f"   SPY Last: ${spy_price:.2f} → SPX equiv: ${spx_equiv:.2f}")
except Exception as e:
    print(f"   Error: {e}")

print("\n" + "=" * 70)
