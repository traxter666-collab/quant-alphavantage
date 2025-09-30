#!/usr/bin/env python3
"""
MAGNIFICENT 7 REPORT
Real-time quotes for AAPL, MSFT, GOOGL, AMZN, NVDA, TSLA, META
"""

import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dual_api_system import DualAPISystem

def get_mag7_report():
    """Generate Magnificent 7 report"""

    mag7 = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'TSLA', 'META']
    api = DualAPISystem()

    print('='*70)
    print('MAGNIFICENT 7 REPORT - POLYGON API')
    print('='*70)
    print()

    results = []

    for symbol in mag7:
        result = api.get_stock_quote_with_failover(symbol)
        if result['success']:
            price = result['price']
            bid = result.get('bid', price)
            ask = result.get('ask', price)
            spread = ask - bid

            results.append({
                'symbol': symbol,
                'price': price,
                'bid': bid,
                'ask': ask,
                'spread': spread
            })

            print(f"{symbol:6s} | ${price:8.2f} | Bid: ${bid:8.2f} | Ask: ${ask:8.2f} | Spread: ${spread:.2f}")
        else:
            print(f"{symbol:6s} | ERROR: {result.get('error', 'Unknown')}")

        print()

    print('='*70)
    print(f"Time: {datetime.now().strftime('%I:%M:%S %p ET')}")
    print('='*70)

    return results

if __name__ == "__main__":
    get_mag7_report()
