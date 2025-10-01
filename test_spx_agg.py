"""
Test SPX aggregate endpoint
"""
import requests
from datetime import datetime

POLYGON_KEY = "_u0zA0CH5ZspOHecb2G8uBxd2DUo4r9D"

print("Testing SPX aggregates endpoint...")

# Try previous day aggregates (should have latest close data)
url = f"https://api.polygon.io/v2/aggs/ticker/I:SPX/prev?adjusted=true&apiKey={POLYGON_KEY}"

try:
    response = requests.get(url, timeout=5)
    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"\nFull Response: {data}")

        if 'results' in data and len(data['results']) > 0:
            result = data['results'][0]
            spx_price = result['c']  # Close price
            print(f"\n✅ SPX Close: ${spx_price:.2f}")
        else:
            print(f"\n⚠️ No results in response")
    else:
        print(f"❌ API Error: {response.text}")

except Exception as e:
    print(f"❌ Exception: {e}")
