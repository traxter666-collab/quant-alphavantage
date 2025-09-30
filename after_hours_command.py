#!/usr/bin/env python3
"""
Seamless After-Hours Command Interface
Provides easy access to after-hours pricing for any stock using Polygon API
Usage: python after_hours_command.py SYMBOL
"""

import sys
import requests
import json
from datetime import datetime

def get_after_hours_price(symbol, api_key='_u0zA0CH5ZspOHecb2G8uBxd2DUo4r9D'):
    """
    Get real-time after-hours price for any stock symbol using Polygon API
    """

    try:
        # Get latest quote
        url = f'https://api.polygon.io/v3/quotes/{symbol.upper()}?limit=1&apikey={api_key}'

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

            # Simple session detection
            session = 'AFTER_HOURS' if dt.hour < 9 or dt.hour >= 16 else 'REGULAR'

            return {
                'success': True,
                'symbol': symbol.upper(),
                'current_price': mid_price,
                'bid': bid_price,
                'ask': ask_price,
                'timestamp': dt,
                'session': session,
                'raw_timestamp': timestamp
            }
        else:
            return {
                'success': False,
                'error': f'No quote data for {symbol.upper()}',
                'response': data
            }

    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def main():
    """
    Command line interface for after-hours pricing
    """

    if len(sys.argv) < 2:
        print("Usage: python after_hours_command.py SYMBOL")
        print("Example: python after_hours_command.py AAPL")
        return

    symbol = sys.argv[1].upper()

    print(f"POLYGON AFTER-HOURS: {symbol}")
    print("=" * 40)

    result = get_after_hours_price(symbol)

    if result['success']:
        print(f"PRICE: ${result['current_price']:.2f}")
        print(f"BID/ASK: ${result['bid']:.2f} / ${result['ask']:.2f}")
        print(f"SESSION: {result['session']}")
        print(f"TIME: {result['timestamp'].strftime('%H:%M:%S')}")

        if result['session'] == 'AFTER_HOURS':
            print("AFTER-HOURS TRADING ACTIVE")
        else:
            print("REGULAR TRADING HOURS")

    else:
        print(f"ERROR: {result['error']}")

if __name__ == "__main__":
    main()