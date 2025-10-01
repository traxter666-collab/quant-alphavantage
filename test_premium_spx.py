"""
Test Premium Polygon API for real-time SPX
"""
import requests

POLYGON_KEY = "_u0zA0CH5ZspOHecb2G8uBxd2DUo4r9D"

print("Testing Premium Polygon Endpoints for Real-Time SPX")
print("=" * 70)

# Test 1: Real-time quote (premium endpoint)
print("\n1. Testing real-time quote I:SPX...")
url = f"https://api.polygon.io/v3/quotes/I:SPX?apiKey={POLYGON_KEY}"
try:
    r = requests.get(url, timeout=5)
    print(f"   Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        print(f"   Response: {data}")
        if 'results' in data and len(data['results']) > 0:
            result = data['results'][0]
            bid = result.get('bid_price', 0)
            ask = result.get('ask_price', 0)
            mid = (bid + ask) / 2
            print(f"   ✅ SPX: Bid ${bid:.2f} / Ask ${ask:.2f} / Mid ${mid:.2f}")
except Exception as e:
    print(f"   Error: {e}")

# Test 2: Try last trade
print("\n2. Testing last trade I:SPX...")
url = f"https://api.polygon.io/v3/trades/I:SPX?limit=1&apiKey={POLYGON_KEY}"
try:
    r = requests.get(url, timeout=5)
    print(f"   Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        print(f"   Response: {data}")
        if 'results' in data and len(data['results']) > 0:
            price = data['results'][0].get('price')
            print(f"   ✅ SPX Last Trade: ${price:.2f}")
except Exception as e:
    print(f"   Error: {e}")

# Test 3: Snapshot
print("\n3. Testing snapshot indices/I:SPX...")
url = f"https://api.polygon.io/v3/snapshot/indices/I:SPX?apiKey={POLYGON_KEY}"
try:
    r = requests.get(url, timeout=5)
    print(f"   Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        print(f"   Response: {data}")
        if 'results' in data:
            result = data['results']
            value = result.get('value')
            if value:
                print(f"   ✅ SPX Value: ${value:.2f}")
except Exception as e:
    print(f"   Error: {e}")

print("\n" + "=" * 70)
