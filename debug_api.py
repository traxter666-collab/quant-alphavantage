import os
import requests
from datetime import datetime

api_key = os.getenv('ALPHAVANTAGE_API_KEY', 'ZFL38ZY98GSN7E1S')
url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=SPY&entitlement=realtime&apikey={api_key}"

print("API Debug Test")
print("=" * 30)
print(f"Current time: {datetime.now()}")

response = requests.get(url)
data = response.json()

print("\nFull API Response:")
print(data)

if "Global Quote" in data:
    quote = data["Global Quote"]
    print(f"\nTimestamp from API: {quote.get('07. latest trading day', 'N/A')}")
    print(f"SPY Price: {quote.get('05. price', 'N/A')}")
    
print(f"\nIf SPX is actually 6543, then:")
print(f"SPY should be around: {6543/10:.2f}")
print(f"API showing SPY: {data.get('Global Quote', {}).get('05. price', 'N/A')}")
print(f"Data appears to be: STALE/DELAYED")