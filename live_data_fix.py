#!/usr/bin/env python3
"""
Live Market Data Fix - Force real-time data when market is open
"""

import requests
import json
from datetime import datetime

def get_live_spy_multiple_sources():
    """Try multiple sources for current SPY price"""

    sources = []

    # Source 1: Yahoo Finance Quote
    try:
        url = "https://query2.finance.yahoo.com/v8/finance/chart/SPY?interval=1m&range=1d"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=5)
        data = response.json()

        if 'chart' in data and data['chart']['result']:
            meta = data['chart']['result'][0]['meta']
            price = meta['regularMarketPrice']
            change = meta.get('regularMarketChange', 0)

            sources.append({
                'source': 'Yahoo Finance',
                'spy_price': price,
                'spy_change': change,
                'spx_price': price * 10,
                'timestamp': datetime.now().isoformat(),
                'success': True
            })
    except Exception as e:
        sources.append({
            'source': 'Yahoo Finance',
            'error': str(e),
            'success': False
        })

    # Source 2: Alternative Yahoo endpoint
    try:
        url = "https://finance.yahoo.com/quote/SPY"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=5)

        # Simple text parsing for price
        text = response.text
        if 'regularMarketPrice' in text:
            # Look for price pattern
            import re
            price_match = re.search(r'"regularMarketPrice":\{"raw":([\d.]+)', text)
            if price_match:
                price = float(price_match.group(1))
                sources.append({
                    'source': 'Yahoo Web Scrape',
                    'spy_price': price,
                    'spy_change': 0,
                    'spx_price': price * 10,
                    'timestamp': datetime.now().isoformat(),
                    'success': True
                })
    except Exception as e:
        sources.append({
            'source': 'Yahoo Web Scrape',
            'error': str(e),
            'success': False
        })

    # Source 3: MarketWatch
    try:
        url = "https://www.marketwatch.com/investing/fund/spy"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=5)

        # Look for price in HTML
        text = response.text
        import re
        price_match = re.search(r'data-module="LastPrice">[\s]*\$?([\d,]+\.[\d]+)', text)
        if price_match:
            price_str = price_match.group(1).replace(',', '')
            price = float(price_str)
            sources.append({
                'source': 'MarketWatch',
                'spy_price': price,
                'spy_change': 0,
                'spx_price': price * 10,
                'timestamp': datetime.now().isoformat(),
                'success': True
            })
    except Exception as e:
        sources.append({
            'source': 'MarketWatch',
            'error': str(e),
            'success': False
        })

    # Source 4: Google Finance
    try:
        url = "https://www.google.com/finance/quote/SPY:NYSEARCA"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=5)

        text = response.text
        import re
        price_match = re.search(r'data-last-price="([\d.]+)"', text)
        if price_match:
            price = float(price_match.group(1))
            sources.append({
                'source': 'Google Finance',
                'spy_price': price,
                'spy_change': 0,
                'spx_price': price * 10,
                'timestamp': datetime.now().isoformat(),
                'success': True
            })
    except Exception as e:
        sources.append({
            'source': 'Google Finance',
            'error': str(e),
            'success': False
        })

    return sources

def main():
    print("LIVE MARKET DATA FIX - TESTING REAL-TIME SOURCES")
    print("=" * 60)
    print(f"Test Time: {datetime.now()}")
    print()

    sources = get_live_spy_multiple_sources()

    successful_sources = [s for s in sources if s.get('success')]
    failed_sources = [s for s in sources if not s.get('success')]

    if successful_sources:
        print("SUCCESS - WORKING SOURCES:")
        for source in successful_sources:
            spy_price = source['spy_price']
            spx_price = source['spx_price']
            print(f"   {source['source']}: SPY ${spy_price:.2f} | SPX ${spx_price:.0f}")

        # Use first successful source
        best_source = successful_sources[0]
        print()
        print("BEST LIVE DATA:")
        print(f"   SPY: ${best_source['spy_price']:.2f}")
        print(f"   SPX: ${best_source['spx_price']:.0f}")
        print(f"   Source: {best_source['source']}")

        # Save to cache
        try:
            with open('.spx/live_price_cache.json', 'w') as f:
                json.dump(best_source, f, indent=2)
            print("   Cached: SUCCESS")
        except:
            print("   Cached: FAILED")

    if failed_sources:
        print()
        print("FAILED SOURCES:")
        for source in failed_sources:
            print(f"   {source['source']}: {source.get('error', 'Unknown error')}")

    print()
    print("=" * 60)

    if successful_sources:
        return successful_sources[0]
    else:
        print("WARNING: NO LIVE DATA SOURCES AVAILABLE")
        return None

if __name__ == "__main__":
    main()