"""
Test real-time SPX last quote endpoint
"""
import requests
from datetime import datetime

POLYGON_KEY = "_u0zA0CH5ZspOHecb2G8uBxd2DUo4r9D"

print(f"Testing real-time SPX endpoints at {datetime.now()}")
print("=" * 70)

# Test 1: Last quote for I:SPX
print("\n1. Testing I:SPX last quote...")
url = f"https://api.polygon.io/v2/last/nbbo/I:SPX?apiKey={POLYGON_KEY}"
try:
    r = requests.get(url, timeout=5)
    print(f"   Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        print(f"   Response: {data}")
except Exception as e:
    print(f"   Error: {e}")

# Test 2: Try different format
print("\n2. Testing SPX (no I: prefix)...")
url = f"https://api.polygon.io/v2/last/nbbo/SPX?apiKey={POLYGON_KEY}"
try:
    r = requests.get(url, timeout=5)
    print(f"   Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        print(f"   Response: {data}")
except Exception as e:
    print(f"   Error: {e}")

# Test 3: Try $SPX
print("\n3. Testing $SPX format...")
url = f"https://api.polygon.io/v2/last/nbbo/$SPX?apiKey={POLYGON_KEY}"
try:
    r = requests.get(url, timeout=5)
    print(f"   Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        print(f"   Response: {data}")
except Exception as e:
    print(f"   Error: {e}")

# Test 4: Check what SPY shows currently
print("\n4. SPY for reference...")
url = f"https://api.polygon.io/v2/last/trade/SPY?apiKey={POLYGON_KEY}"
try:
    r = requests.get(url, timeout=5)
    if r.status_code == 200:
        data = r.json()
        spy_price = data['results']['p']
        print(f"   SPY: ${spy_price:.2f} → SPX equiv: ${spy_price * 10:.2f}")
except Exception as e:
    print(f"   Error: {e}")

print("\n" + "=" * 70)
