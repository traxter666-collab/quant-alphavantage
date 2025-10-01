"""
Test direct SPX API endpoint
"""
import requests

POLYGON_KEY = "_u0zA0CH5ZspOHecb2G8uBxd2DUo4r9D"

print("Testing direct SPX endpoint...")
url = f"https://api.polygon.io/v2/snapshot/locale/us/markets/stocks/tickers/I:SPX?apiKey={POLYGON_KEY}"

try:
    response = requests.get(url, timeout=5)
    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"\nFull Response: {data}")

        if 'ticker' in data and 'day' in data['ticker']:
            spx_price = data['ticker']['day'].get('c')
            print(f"\n✅ SUCCESS: SPX Price = ${spx_price:.2f}")
        else:
            print(f"\n⚠️ Unexpected data structure")
    else:
        print(f"❌ API Error: {response.text}")

except Exception as e:
    print(f"❌ Exception: {e}")
