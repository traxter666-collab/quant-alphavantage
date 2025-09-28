import os
import requests

# Get API key
api_key = os.getenv('ALPHAVANTAGE_API_KEY', 'ZFL38ZY98GSN7E1S')
print(f"Using API Key: {api_key[:4]}...{api_key[-4:]}")

# SPY Price Update
url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=SPY&entitlement=realtime&apikey={api_key}"
response = requests.get(url)
data = response.json()

print("\nSPY/SPX PRICE UPDATE:")
print("=" * 25)

if "Global Quote" in data:
    quote = data["Global Quote"]
    price = quote.get("05. price", "N/A")
    change = quote.get("09. change", "N/A")
    change_pct = quote.get("10. change percent", "N/A")

    print(f"SPY Current: ${price}")
    print(f"Change: {change} ({change_pct})")

    if price != "N/A":
        spy_price = float(price)
        spx_estimate = spy_price * 10

        print(f"\nSPY/SPX CONVERSION:")
        print(f"SPY: ${spy_price:.2f}")
        print(f"SPX Estimate: ${spx_estimate:.2f}")

        print(f"\nActive Positions:")
        print(f"GOOGL 247.5P @ 1.75 (expires 9/26)")
        print(f"SPXW 6650P @ 7.50")

        # Key SPX levels
        print(f"\nKey SPX Levels:")
        print(f"Current: ${spx_estimate:.2f}")
        print(f"6650P Strike: $6650.00")
        print(f"Distance to 6650P: ${spx_estimate - 6650:+.2f}")

        if spx_estimate > 6650:
            print(f"6650P Status: OTM")
            print(f"Needs ${spx_estimate - 6650:.2f} drop to ITM")
        else:
            intrinsic = 6650 - spx_estimate
            print(f"6650P Status: ITM")
            print(f"Intrinsic: ${intrinsic:.2f}")
            pnl = intrinsic - 7.50
            print(f"P&L: ${pnl:+.2f}")
else:
    print("SPY quote not available")
    print("ERROR:", data)