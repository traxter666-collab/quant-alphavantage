"""
Test AlphaVantage SPXW real-time options - find ATM strikes
"""
import requests

ALPHA_VANTAGE_KEY = "ZFL38ZY98GSN7E1S"

print("Testing AlphaVantage SPXW Real-Time Options - ATM Strike Detection...")
print("=" * 70)

url = f"https://www.alphavantage.co/query?function=REALTIME_OPTIONS&symbol=SPXW&entitlement=realtime&apikey={ALPHA_VANTAGE_KEY}"

try:
    response = requests.get(url, timeout=15)

    if response.status_code == 200:
        data = response.json()

        if 'data' in data and len(data['data']) > 0:
            # Get underlying price if available
            first_option = data['data'][0]
            underlying = None
            if 'underlying_price' in first_option:
                underlying = float(first_option['underlying_price'])
                print(f"\n📊 Underlying SPX Price: ${underlying:.2f}")

            # Find strikes near current price
            print(f"\nSearching for ATM strikes near ${underlying:.2f}..." if underlying else "\nSearching for option strikes...")

            strikes = {}
            for option in data['data']:
                strike = float(option.get('strike', 0))
                exp = option.get('expiration', '')
                opt_type = option.get('type', '')

                # Focus on today's expiration (0DTE)
                if '2025-10-01' in exp:
                    if strike not in strikes:
                        strikes[strike] = {'call': None, 'put': None}

                    if opt_type == 'call':
                        strikes[strike]['call'] = option
                    elif opt_type == 'put':
                        strikes[strike]['put'] = option

            # Find strikes with both call and put
            print(f"\nFound {len(strikes)} strikes with 0DTE options")

            # Sort and show strikes near underlying
            sorted_strikes = sorted(strikes.keys())

            if underlying:
                # Find closest strikes to underlying
                atm_strikes = [s for s in sorted_strikes if abs(s - underlying) < 50]
                print(f"\nStrikes within 50 points of ${underlying:.2f}:")

                for strike in sorted(atm_strikes)[:10]:
                    call = strikes[strike]['call']
                    put = strikes[strike]['put']

                    if call and put:
                        call_mark = float(call.get('mark', 0))
                        put_mark = float(put.get('mark', 0))

                        # Calculate SPX using put-call parity
                        spx_calc = (call_mark - put_mark) + strike

                        print(f"\n  Strike ${strike:.0f}:")
                        print(f"    Call Mark: ${call_mark:.2f} | Put Mark: ${put_mark:.2f}")
                        print(f"    Put-Call Parity SPX: ${spx_calc:.2f}")
                        print(f"    Difference from underlying: ${spx_calc - underlying:.2f}")
            else:
                print(f"\nShowing first 10 strikes:")
                for strike in sorted_strikes[:10]:
                    call = strikes[strike]['call']
                    put = strikes[strike]['put']

                    if call and put:
                        call_mark = float(call.get('mark', 0))
                        put_mark = float(put.get('mark', 0))
                        spx_calc = (call_mark - put_mark) + strike

                        print(f"\n  Strike ${strike:.0f}: SPX = ${spx_calc:.2f}")

except Exception as e:
    print(f"Exception: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
