"""
Alternative Real-Time SPX Data Sources
Setup and implementation for live market data
"""

import requests
import json
import os
from datetime import datetime

def setup_yahoo_finance():
    """Yahoo Finance - Free, no API key required"""
    print("YAHOO FINANCE API - FREE")
    print("=" * 30)
    
    def get_spx_yahoo():
        # Yahoo uses ^GSPC for S&P 500
        url = "https://query1.finance.yahoo.com/v8/finance/chart/%5EGSPC"
        
        try:
            response = requests.get(url)
            data = response.json()
            
            if 'chart' in data and data['chart']['result']:
                result = data['chart']['result'][0]
                meta = result['meta']
                
                current_price = meta['regularMarketPrice']
                prev_close = meta['previousClose']
                change = current_price - prev_close
                change_pct = (change / prev_close) * 100
                
                return {
                    'symbol': '^GSPC (SPX)',
                    'price': current_price,
                    'change': change,
                    'change_pct': change_pct,
                    'high': meta.get('regularMarketDayHigh', 'N/A'),
                    'low': meta.get('regularMarketDayLow', 'N/A'),
                    'volume': meta.get('regularMarketVolume', 'N/A'),
                    'timestamp': datetime.fromtimestamp(meta['regularMarketTime'])
                }
            else:
                return None
                
        except Exception as e:
            print(f"Yahoo Finance error: {e}")
            return None
    
    # Test Yahoo Finance
    print("Testing Yahoo Finance...")
    spx_data = get_spx_yahoo()
    
    if spx_data:
        print("✅ SUCCESS!")
        print(f"SPX: ${spx_data['price']:.2f}")
        print(f"Change: {spx_data['change']:+.2f} ({spx_data['change_pct']:+.2f}%)")
        print(f"High: {spx_data['high']}")
        print(f"Low: {spx_data['low']}")
        print(f"Time: {spx_data['timestamp']}")
        return True
    else:
        print("❌ Failed")
        return False

def setup_polygon_io():
    """Polygon.io - Free tier available"""
    print("\nPOLYGON.IO API")
    print("=" * 20)
    print("Setup Instructions:")
    print("1. Go to polygon.io")
    print("2. Sign up for free account")
    print("3. Get API key")
    print("4. Set environment variable: POLYGON_API_KEY")
    print("5. Free tier: 5 calls/minute, delayed 15 min")
    
    api_key = os.getenv('POLYGON_API_KEY')
    if not api_key:
        print("❌ POLYGON_API_KEY not found")
        print("Set with: setx POLYGON_API_KEY \"your_key_here\"")
        return False
    
    def get_spx_polygon():
        # SPX ticker for Polygon
        url = f"https://api.polygon.io/v2/aggs/ticker/I:SPX/prev?adjusted=true&apikey={api_key}"
        
        try:
            response = requests.get(url)
            data = response.json()
            
            if 'results' in data and data['results']:
                result = data['results'][0]
                return {
                    'symbol': 'I:SPX',
                    'price': result['c'],  # close
                    'high': result['h'],
                    'low': result['l'], 
                    'volume': result['v'],
                    'timestamp': datetime.fromtimestamp(result['t']/1000)
                }
            return None
            
        except Exception as e:
            print(f"Polygon error: {e}")
            return None
    
    print("Testing Polygon.io...")
    spx_data = get_spx_polygon()
    
    if spx_data:
        print("✅ SUCCESS!")
        print(f"SPX: ${spx_data['price']:.2f}")
        return True
    else:
        print("❌ Failed or no API key")
        return False

def setup_iex_cloud():
    """IEX Cloud - Free tier available"""
    print("\nIEX CLOUD API")
    print("=" * 15)
    print("Setup Instructions:")
    print("1. Go to iexcloud.io")
    print("2. Sign up for free account")
    print("3. Get publishable API key")
    print("4. Set environment variable: IEX_API_KEY")
    print("5. Free tier: 500,000 calls/month")
    
    api_key = os.getenv('IEX_API_KEY')
    if not api_key:
        print("❌ IEX_API_KEY not found")
        return False
    
    def get_spx_iex():
        # IEX uses SPY as closest proxy, or direct index if available
        url = f"https://cloud.iexapis.com/stable/stock/spy/quote?token={api_key}"
        
        try:
            response = requests.get(url)
            data = response.json()
            
            if 'latestPrice' in data:
                # Convert SPY to SPX estimate
                spy_price = data['latestPrice']
                spx_estimate = spy_price * 10
                
                return {
                    'symbol': 'SPY→SPX',
                    'price': spx_estimate,
                    'spy_price': spy_price,
                    'change': data.get('change', 0) * 10,
                    'change_pct': data.get('changePercent', 0) * 100,
                    'high': data.get('high', 0) * 10,
                    'low': data.get('low', 0) * 10,
                    'volume': data.get('volume', 0),
                    'timestamp': data.get('latestUpdate', 0)
                }
            return None
            
        except Exception as e:
            print(f"IEX error: {e}")
            return None
    
    print("Testing IEX Cloud...")
    spx_data = get_spx_iex()
    
    if spx_data:
        print("✅ SUCCESS!")
        print(f"SPX Est: ${spx_data['price']:.2f} (via SPY ${spx_data['spy_price']:.2f})")
        return True
    else:
        print("❌ Failed")
        return False

def create_unified_spx_function():
    """Create a unified function that tries multiple sources"""
    
    code = '''
def get_live_spx_data():
    """Get live SPX data from multiple sources with fallback"""
    
    # Try Yahoo Finance first (free, no API key)
    try:
        url = "https://query1.finance.yahoo.com/v8/finance/chart/%5EGSPC"
        response = requests.get(url, timeout=5)
        data = response.json()
        
        if 'chart' in data and data['chart']['result']:
            result = data['chart']['result'][0]
            meta = result['meta']
            
            current_price = meta['regularMarketPrice']
            prev_close = meta['previousClose']
            change = current_price - prev_close
            
            return {
                'source': 'Yahoo Finance',
                'symbol': 'SPX',
                'price': current_price,
                'change': change,
                'change_pct': (change / prev_close) * 100,
                'high': meta.get('regularMarketDayHigh'),
                'low': meta.get('regularMarketDayLow'),
                'timestamp': datetime.fromtimestamp(meta['regularMarketTime']),
                'success': True
            }
    except:
        pass
    
    # Fallback to manual input
    return {
        'source': 'Manual Input Required',
        'success': False,
        'message': 'Please provide current SPX via screenshot or manual entry'
    }
'''
    
    with open('live_spx_data.py', 'w') as f:
        f.write('import requests\nimport json\nfrom datetime import datetime\n\n')
        f.write(code)
    
    print("\n📄 Created: live_spx_data.py")
    print("Use: from live_spx_data import get_live_spx_data")

def main():
    print("SPX REAL-TIME DATA SOURCES SETUP")
    print("=" * 40)
    
    # Test each source
    yahoo_works = setup_yahoo_finance()
    polygon_works = setup_polygon_io()
    iex_works = setup_iex_cloud()
    
    print(f"\nSUMMARY:")
    print(f"Yahoo Finance: {'✅ Working' if yahoo_works else '❌ Failed'}")
    print(f"Polygon.io: {'✅ Working' if polygon_works else '❌ Need API key'}")
    print(f"IEX Cloud: {'✅ Working' if iex_works else '❌ Need API key'}")
    
    if yahoo_works:
        print(f"\n🎉 RECOMMENDED: Yahoo Finance (free, working)")
        create_unified_spx_function()
    else:
        print(f"\n⚠️  Consider setting up Polygon.io or IEX Cloud API keys")
    
    print(f"\nFor 0DTE trading, also consider:")
    print(f"• Screenshot analysis (most reliable)")
    print(f"• TradingView alerts/webhooks") 
    print(f"• Broker API integration")

if __name__ == "__main__":
    main()