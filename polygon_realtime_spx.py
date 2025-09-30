#!/usr/bin/env python3
"""
Real-time SPX Price from Polygon API
Uses paid Polygon API key for real-time SPY quotes and converts to SPX
"""

import requests
import json
from datetime import datetime

def get_realtime_spx_from_polygon(api_key='_u0zA0CH5ZspOHecb2G8uBxd2DUo4r9D'):
    """
    Get real-time SPX price using Polygon SPY quotes
    """

    print("Getting real-time SPX from Polygon API...")

    try:
        # Get latest SPY quote
        url = f'https://api.polygon.io/v3/quotes/SPY?limit=1&apikey={api_key}'

        response = requests.get(url, timeout=15)
        data = response.json()

def get_aapl_polygon(api_key='_u0zA0CH5ZspOHecb2G8uBxd2DUo4r9D'):
    """
    Get real-time AAPL after-hours price using Polygon API
    """

    print("Getting AAPL after-hours data from Polygon API...")

    try:
        # Get latest AAPL quote
        url = f'https://api.polygon.io/v3/quotes/AAPL?limit=1&apikey={api_key}'

        response = requests.get(url, timeout=15)
        data = response.json()

        if 'results' in data and len(data['results']) > 0:
            latest_quote = data['results'][0]

            bid_price = latest_quote['bid_price']
            ask_price = latest_quote['ask_price']
            mid_price = (bid_price + ask_price) / 2
            timestamp = latest_quote['sip_timestamp']

            # Convert timestamp (nanoseconds to seconds)
            dt = datetime.fromtimestamp(timestamp / 1000000000)

            # Get previous close for after-hours change calculation
            # Assuming last close around $225 - this would need daily close data
            previous_close = 225.00  # This should come from daily close API

            change = mid_price - previous_close
            change_percent = (change / previous_close) * 100

            return {
                'success': True,
                'symbol': 'AAPL',
                'current_price': mid_price,
                'bid': bid_price,
                'ask': ask_price,
                'previous_close': previous_close,
                'change': change,
                'change_percent': change_percent,
                'timestamp': dt,
                'session': 'AFTER_HOURS' if dt.hour < 9 or dt.hour >= 16 else 'REGULAR',
                'raw_timestamp': timestamp
            }
        else:
            return {
                'success': False,
                'error': 'No AAPL quote data in response',
                'response': data
            }

    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

        if 'results' in data and len(data['results']) > 0:
            latest_quote = data['results'][0]

            bid_price = latest_quote['bid_price']
            ask_price = latest_quote['ask_price']
            mid_price = (bid_price + ask_price) / 2
            timestamp = latest_quote['sip_timestamp']

            # Convert timestamp (nanoseconds to seconds)
            dt = datetime.fromtimestamp(timestamp / 1000000000)

            # Convert SPY to SPX
            spx_price = mid_price * 10

            return {
                'success': True,
                'spx_price': spx_price,
                'spy_bid': bid_price,
                'spy_ask': ask_price,
                'spy_mid': mid_price,
                'timestamp': dt,
                'raw_timestamp': timestamp
            }
        else:
            return {
                'success': False,
                'error': 'No quote data in response',
                'response': data
            }

    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def main():
    """
    Test real-time SPX extraction
    """

    print("POLYGON REAL-TIME SPX EXTRACTOR")
    print("=" * 40)

    result = get_realtime_spx_from_polygon()

    if result['success']:
        print(f"SUCCESS - REAL-TIME SPX: ${result['spx_price']:.2f}")
        print(f"SPY Bid/Ask: ${result['spy_bid']:.2f} / ${result['spy_ask']:.2f}")
        print(f"SPY Mid: ${result['spy_mid']:.2f}")
        print(f"Timestamp: {result['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")

        # Compare to known close
        known_close = 6661.21
        difference = result['spx_price'] - known_close
        print(f"vs Known Close 6661.21: {difference:+.2f} points")

        if abs(difference) < 5:
            print("EXCELLENT: Price matches expected range")
        elif abs(difference) < 20:
            print("GOOD: Price within reasonable range")
        else:
            print("WARNING: Large price difference")

    else:
        print(f"ERROR: {result['error']}")
        if 'response' in result:
            print("Response:", json.dumps(result['response'], indent=2))

def test_aapl_polygon():
    """
    Test AAPL after-hours price extraction
    """

    print("POLYGON AAPL AFTER-HOURS EXTRACTOR")
    print("=" * 40)

    result = get_aapl_polygon()

    if result['success']:
        print(f"SUCCESS - AAPL AFTER-HOURS: ${result['current_price']:.2f}")
        print(f"Bid/Ask: ${result['bid']:.2f} / ${result['ask']:.2f}")
        print(f"Previous Close: ${result['previous_close']:.2f}")
        print(f"Change: ${result['change']:+.2f} ({result['change_percent']:+.2f}%)")
        print(f"Session: {result['session']}")
        print(f"Timestamp: {result['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")

        if result['session'] == 'AFTER_HOURS':
            print("AFTER-HOURS TRADING DETECTED")
        else:
            print("REGULAR TRADING HOURS")
    else:
        print(f"ERROR: {result['error']}")
        if 'response' in result:
            print("Response:", json.dumps(result['response'], indent=2))

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == 'aapl':
        test_aapl_polygon()
    else:
        main()