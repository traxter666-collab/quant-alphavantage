"""
Test AlphaVantage SPXW real-time options API
"""
import requests

ALPHA_VANTAGE_KEY = "ZFL38ZY98GSN7E1S"

print("Testing AlphaVantage SPXW Real-Time Options...")
print("=" * 70)

url = f"https://www.alphavantage.co/query?function=REALTIME_OPTIONS&symbol=SPXW&entitlement=realtime&apikey={ALPHA_VANTAGE_KEY}"

try:
    print(f"\nFetching: {url[:80]}...")
    response = requests.get(url, timeout=15)
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"\nResponse keys: {list(data.keys())}")

        if 'data' in data:
            print(f"Total options: {len(data['data'])}")

            # Find 2000 strike for put-call parity
            call_2000 = None
            put_2000 = None

            for option in data['data'][:50]:  # Check first 50
                strike = option.get('strike', '')
                if strike == '2000.00000':
                    if option.get('type') == 'call':
                        call_2000 = option
                        print(f"\n✅ Found 2000 CALL:")
                        print(f"   Mark: ${option.get('mark', 0)}")
                        print(f"   Bid: ${option.get('bid', 0)}")
                        print(f"   Ask: ${option.get('ask', 0)}")
                    elif option.get('type') == 'put':
                        put_2000 = option
                        print(f"\n✅ Found 2000 PUT:")
                        print(f"   Mark: ${option.get('mark', 0)}")
                        print(f"   Bid: ${option.get('bid', 0)}")
                        print(f"   Ask: ${option.get('ask', 0)}")

            # Calculate SPX using put-call parity
            if call_2000 and put_2000:
                call_mark = float(call_2000.get('mark', 0))
                put_mark = float(put_2000.get('mark', 0))

                spx_price = (call_mark - put_mark) + 2000
                print(f"\n📊 SPX from Put-Call Parity:")
                print(f"   Formula: (Call_Mark - Put_Mark) + Strike")
                print(f"   ({call_mark} - {put_mark}) + 2000")
                print(f"   SPX = ${spx_price:.2f}")
            else:
                print(f"\n❌ Could not find 2000 strike options")

            # Check underlying_price field
            if len(data['data']) > 0:
                first_option = data['data'][0]
                if 'underlying_price' in first_option:
                    print(f"\n📈 Underlying Price (direct): ${first_option['underlying_price']}")

                print(f"\nFirst option sample:")
                print(f"   Strike: {first_option.get('strike')}")
                print(f"   Type: {first_option.get('type')}")
                print(f"   Expiration: {first_option.get('expiration')}")
        else:
            print(f"\nNo 'data' key in response")
            print(f"Response: {data}")
    else:
        print(f"Error response: {response.text[:500]}")

except Exception as e:
    print(f"Exception: {e}")

print("\n" + "=" * 70)
