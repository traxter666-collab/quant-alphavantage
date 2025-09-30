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

if __name__ == "__main__":
    main()