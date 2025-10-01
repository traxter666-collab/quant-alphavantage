"""
Test Yahoo Finance for real-time SPX
"""
import requests

print("Testing Yahoo Finance SPX...")

url = "https://query1.finance.yahoo.com/v8/finance/chart/%5EGSPC?interval=1m&range=1d"

try:
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers, timeout=10)

    if response.status_code == 200:
        data = response.json()

        # Get latest price from chart data
        if 'chart' in data and 'result' in data['chart']:
            result = data['chart']['result'][0]
            meta = result['meta']

            current_price = meta.get('regularMarketPrice')
            print(f"\n✅ Yahoo Finance SPX: ${current_price:.2f}")
            print(f"   Previous Close: ${meta.get('previousClose', 0):.2f}")
            print(f"   Day Range: ${meta.get('regularMarketDayLow', 0):.2f} - ${meta.get('regularMarketDayHigh', 0):.2f}")
        else:
            print(f"Unexpected structure: {data}")
    else:
        print(f"Error: Status {response.status_code}")

except Exception as e:
    print(f"Exception: {e}")
