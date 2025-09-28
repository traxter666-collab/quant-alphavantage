#!/usr/bin/env python3
"""
SPX Price Fix - Get accurate real-time SPX pricing
"""

import requests
import json
from datetime import datetime

def get_direct_spx_price():
    """Get SPX price directly from multiple sources"""

    sources = []

    # Source 1: Yahoo Finance SPX Direct
    try:
        url = "https://query2.finance.yahoo.com/v8/finance/chart/%5ESPX?interval=1m&range=1d"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=5)
        data = response.json()

        if 'chart' in data and data['chart']['result']:
            meta = data['chart']['result'][0]['meta']
            spx_price = meta['regularMarketPrice']

            sources.append({
                'source': 'Yahoo SPX Direct',
                'spx_price': spx_price,
                'spy_equivalent': spx_price / 10,
                'timestamp': datetime.now().isoformat(),
                'success': True
            })
    except Exception as e:
        sources.append({
            'source': 'Yahoo SPX Direct',
            'error': str(e),
            'success': False
        })

    # Source 2: MarketWatch SPX
    try:
        url = "https://www.marketwatch.com/investing/index/spx"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=5)

        text = response.text
        import re
        # Look for SPX price patterns
        price_patterns = [
            r'data-module="LastPrice">[\s]*\$?([\d,]+\.[\d]+)',
            r'class="value">[\s]*\$?([\d,]+\.[\d]+)',
            r'"last":"([\d,]+\.[\d]+)"'
        ]

        for pattern in price_patterns:
            price_match = re.search(pattern, text)
            if price_match:
                price_str = price_match.group(1).replace(',', '')
                spx_price = float(price_str)

                # Sanity check - SPX should be 5000-7000 range
                if 5000 < spx_price < 7000:
                    sources.append({
                        'source': 'MarketWatch SPX',
                        'spx_price': spx_price,
                        'spy_equivalent': spx_price / 10,
                        'timestamp': datetime.now().isoformat(),
                        'success': True
                    })
                    break
    except Exception as e:
        sources.append({
            'source': 'MarketWatch SPX',
            'error': str(e),
            'success': False
        })

    # Source 3: Google Finance SPX
    try:
        url = "https://www.google.com/finance/quote/SPX:INDEXSP"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=5)

        text = response.text
        import re
        price_patterns = [
            r'data-last-price="([\d.]+)"',
            r'class=".*?YMlKec.*?">([\d,]+\.[\d]+)',
        ]

        for pattern in price_patterns:
            price_match = re.search(pattern, text)
            if price_match:
                price_str = price_match.group(1).replace(',', '')
                spx_price = float(price_str)

                # Sanity check
                if 5000 < spx_price < 7000:
                    sources.append({
                        'source': 'Google SPX',
                        'spx_price': spx_price,
                        'spy_equivalent': spx_price / 10,
                        'timestamp': datetime.now().isoformat(),
                        'success': True
                    })
                    break
    except Exception as e:
        sources.append({
            'source': 'Google SPX',
            'error': str(e),
            'success': False
        })

    # Source 4: SPY to SPX conversion (backup)
    try:
        url = "https://query2.finance.yahoo.com/v8/finance/chart/SPY?interval=1m&range=1d"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=5)
        data = response.json()

        if 'chart' in data and data['chart']['result']:
            meta = data['chart']['result'][0]['meta']
            spy_price = meta['regularMarketPrice']
            spx_price = spy_price * 10  # Simple conversion

            sources.append({
                'source': 'SPY to SPX Conversion',
                'spx_price': spx_price,
                'spy_equivalent': spy_price,
                'timestamp': datetime.now().isoformat(),
                'success': True,
                'note': 'Converted from SPY'
            })
    except Exception as e:
        sources.append({
            'source': 'SPY to SPX Conversion',
            'error': str(e),
            'success': False
        })

    return sources

def get_spx_options_price():
    """Try to get SPX from options data"""
    try:
        # This would need SPXW options data
        # For now, return None as we don't have options API access
        return None
    except:
        return None

def main():
    print("SPX PRICE ACCURACY FIX")
    print("=" * 50)
    print(f"Test Time: {datetime.now()}")
    print()

    # Get all sources
    sources = get_direct_spx_price()

    successful_sources = [s for s in sources if s.get('success')]
    failed_sources = [s for s in sources if not s.get('success')]

    if successful_sources:
        print("SUCCESSFUL SPX SOURCES:")
        for source in successful_sources:
            spx_price = source['spx_price']
            spy_equiv = source['spy_equivalent']
            print(f"   {source['source']}: SPX ${spx_price:.2f} | SPY equiv ${spy_equiv:.2f}")

        # Find consensus
        spx_prices = [s['spx_price'] for s in successful_sources]
        avg_spx = sum(spx_prices) / len(spx_prices)

        print()
        print("CONSENSUS SPX PRICE:")
        print(f"   Average: ${avg_spx:.2f}")
        print(f"   Range: ${min(spx_prices):.2f} - ${max(spx_prices):.2f}")

        # Use most reliable source (Yahoo Direct if available)
        best_source = successful_sources[0]
        for source in successful_sources:
            if 'Direct' in source['source']:
                best_source = source
                break

        print()
        print("BEST SPX DATA:")
        print(f"   SPX: ${best_source['spx_price']:.2f}")
        print(f"   Source: {best_source['source']}")

        # Save to cache
        try:
            with open('.spx/spx_price_cache.json', 'w') as f:
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
    print("=" * 50)

    return successful_sources[0] if successful_sources else None

if __name__ == "__main__":
    main()