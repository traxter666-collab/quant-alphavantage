#!/usr/bin/env python3
"""
SPX REAL-TIME PRICE FROM OPTIONS
Extract accurate SPX price using SPXW options put-call parity
"""

import os
import requests
import json
from datetime import datetime

def get_spx_from_options():
    """
    Get accurate SPX price from SPXW options using put-call parity
    Method: SPX = (Call_Mark - Put_Mark) + Strike
    """

    api_key = os.getenv('ALPHAVANTAGE_API_KEY', 'ZFL38ZY98GSN7E1S')

    try:
        # Get SPXW options chain (0DTE or nearest expiration)
        url = f"https://www.alphavantage.co/query?function=REALTIME_OPTIONS&symbol=SPXW&apikey={api_key}"

        print("Fetching SPXW options data...")
        response = requests.get(url, timeout=15)
        data = response.json()

        if 'data' not in data or not data['data']:
            print(f"ERROR: No options data returned")
            return None

        options = data['data']
        print(f"Found {len(options)} SPXW options")

        # Find ATM options (closest to current price estimate)
        # Start with SPY proxy to estimate ATM
        spy_url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=SPY&entitlement=realtime&apikey={api_key}"
        spy_response = requests.get(spy_url, timeout=10)
        spy_data = spy_response.json()

        if "Global Quote" in spy_data:
            spy_price = float(spy_data["Global Quote"]["05. price"])
            estimated_spx = spy_price * 10
        else:
            estimated_spx = 6600  # Fallback estimate

        print(f"Estimated SPX: ${estimated_spx:.2f} (from SPY proxy)")

        # Find options near ATM strike
        calls = {}
        puts = {}

        for option in options:
            try:
                strike = float(option.get('strike', 0))
                option_type = option.get('type', '').lower()
                bid = float(option.get('bid', 0))
                ask = float(option.get('ask', 0))
                mark = (bid + ask) / 2 if bid > 0 and ask > 0 else float(option.get('mark', 0))

                # Only use liquid options with valid bid/ask
                if bid == 0 or ask == 0:
                    continue

                # Only consider strikes within 20 points of estimated ATM (tighter range)
                if abs(strike - estimated_spx) > 20:
                    continue

                # Filter out options with unrealistic spreads (>10% of mid)
                spread = ask - bid
                if spread > (mark * 0.10):
                    continue

                if option_type == 'call':
                    calls[strike] = {'mark': mark, 'bid': bid, 'ask': ask}
                elif option_type == 'put':
                    puts[strike] = {'mark': mark, 'bid': bid, 'ask': ask}

            except (ValueError, TypeError):
                continue

        if not calls or not puts:
            print(f"ERROR: Not enough liquid options found")
            return None

        # Find matching strikes with both calls and puts
        matching_strikes = set(calls.keys()) & set(puts.keys())

        if not matching_strikes:
            print(f"ERROR: No matching call/put strikes found")
            return None

        # Use strike closest to estimated ATM
        best_strike = min(matching_strikes, key=lambda x: abs(x - estimated_spx))

        call_data = calls[best_strike]
        put_data = puts[best_strike]

        call_mark = call_data['mark']
        put_mark = put_data['mark']

        # Put-Call Parity: SPX = (Call_Mark - Put_Mark) + Strike
        spx_price = (call_mark - put_mark) + best_strike

        result = {
            'source': 'SPXW Options (Put-Call Parity)',
            'price': spx_price,
            'strike_used': best_strike,
            'call_mark': call_mark,
            'put_mark': put_mark,
            'timestamp': datetime.now().isoformat(),
            'is_current': True,
            'success': True,
            'method': 'put-call-parity'
        }

        print(f"SUCCESS: SPX ${spx_price:.2f}")
        print(f"  Method: Put-Call Parity at ${best_strike:.2f} strike")
        print(f"  Call Mark: ${call_mark:.2f}, Put Mark: ${put_mark:.2f}")

        return result

    except Exception as e:
        print(f"ERROR: {e}")
        return None


def get_spx_price():
    """
    Get SPX price with SPXW options primary, fallbacks to SPY proxy
    """

    # Try SPXW options first (most accurate)
    result = get_spx_from_options()

    if result and result['success']:
        return result

    # Fallback to SPY proxy
    print("\nFalling back to SPY proxy method...")
    api_key = os.getenv('ALPHAVANTAGE_API_KEY', 'ZFL38ZY98GSN7E1S')

    try:
        url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=SPY&entitlement=realtime&apikey={api_key}"
        response = requests.get(url, timeout=10)
        data = response.json()

        if "Global Quote" in data:
            spy_price = float(data["Global Quote"]["05. price"])
            spy_change = float(data["Global Quote"]["09. change"])

            spx_price = spy_price * 10
            spx_change = spy_change * 10

            result = {
                'source': 'SPY Proxy (×10)',
                'price': spx_price,
                'change': spx_change,
                'change_pct': (spx_change / (spx_price - spx_change)) * 100,
                'spy_price': spy_price,
                'is_current': True,
                'success': True,
                'method': 'spy-proxy'
            }

            print(f"FALLBACK: SPX ${spx_price:.2f} (SPY proxy)")
            return result

    except Exception as e:
        print(f"ERROR in fallback: {e}")

    return {'success': False, 'error': 'All methods failed'}


if __name__ == "__main__":
    print("="*60)
    print("SPX REAL-TIME PRICE EXTRACTION")
    print("="*60)

    result = get_spx_price()

    if result and result['success']:
        print("\n" + "="*60)
        print("RESULT:")
        print(f"  SPX: ${result['price']:.2f}")
        print(f"  Source: {result['source']}")
        print(f"  Method: {result.get('method', 'unknown')}")
        if 'change' in result:
            print(f"  Change: ${result['change']:.2f} ({result.get('change_pct', 0):.2f}%)")
        print("="*60)
    else:
        print("\nFAILED to get SPX price")