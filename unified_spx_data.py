import os
import requests
import json
from datetime import datetime

def get_unified_spx_data():
    """
    Get SPX data with Alphavantage primary, Yahoo Finance backup
    Returns real-time SPX data from best available source
    """
    
    print("Fetching SPX data...")
    
    # Try Alphavantage first (via SPY proxy)
    api_key = os.getenv('ALPHAVANTAGE_API_KEY', 'ZFL38ZY98GSN7E1S')
    if api_key:
        try:
            print("Trying Alphavantage (SPY proxy)...")
            url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=SPY&entitlement=realtime&apikey={api_key}"
            response = requests.get(url, timeout=10)
            data = response.json()
            
            if "Global Quote" in data and data["Global Quote"]:
                quote = data["Global Quote"]
                spy_price = float(quote["05. price"])
                spy_change = float(quote["09. change"])
                spy_high = float(quote["03. high"])
                spy_low = float(quote["04. low"])
                trading_day = quote.get("07. latest trading day", "Unknown")
                
                # Convert to SPX
                spx_price = spy_price * 10
                spx_change = spy_change * 10
                spx_high = spy_high * 10
                spx_low = spy_low * 10
                
                # Check if data is recent (not yesterday's data)
                today = datetime.now().strftime('%Y-%m-%d')
                is_current = trading_day == today
                
                result = {
                    'source': 'Alphavantage (SPY→SPX)',
                    'price': spx_price,
                    'change': spx_change,
                    'change_pct': (spx_change / (spx_price - spx_change)) * 100,
                    'high': spx_high,
                    'low': spx_low,
                    'trading_day': trading_day,
                    'is_current': is_current,
                    'spy_price': spy_price,
                    'success': True
                }
                
                if is_current:
                    print(f"✅ Alphavantage: SPX ${spx_price:.2f} (current)")
                    return result
                else:
                    print(f"⚠️  Alphavantage: SPX ${spx_price:.2f} (stale - {trading_day})")
                    print("Falling back to Yahoo Finance...")
                    
        except Exception as e:
            print(f"❌ Alphavantage failed: {e}")
            print("Falling back to Yahoo Finance...")
    
    # Yahoo Finance backup
    try:
        print("Trying Yahoo Finance...")
        url = "https://query1.finance.yahoo.com/v8/finance/chart/%5EGSPC"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        data = response.json()
        
        if 'chart' in data and data['chart']['result']:
            result = data['chart']['result'][0]
            meta = result['meta']
            
            current_price = meta.get('regularMarketPrice')
            prev_close = meta.get('previousClose')
            high = meta.get('regularMarketDayHigh')
            low = meta.get('regularMarketDayLow')
            market_time = meta.get('regularMarketTime')
            
            if current_price and prev_close:
                change = current_price - prev_close
                change_pct = (change / prev_close) * 100
                
                result = {
                    'source': 'Yahoo Finance',
                    'price': current_price,
                    'change': change,
                    'change_pct': change_pct,
                    'high': high,
                    'low': low,
                    'timestamp': datetime.fromtimestamp(market_time) if market_time else datetime.now(),
                    'is_current': True,
                    'success': True
                }
                
                print(f"✅ Yahoo Finance: SPX ${current_price:.2f} (real-time)")
                return result
                
    except Exception as e:
        print(f"❌ Yahoo Finance failed: {e}")
    
    # Both failed
    return {
        'source': 'Manual Input Required',
        'success': False,
        'message': 'Both Alphavantage and Yahoo Finance failed. Please provide SPX manually or via screenshot.'
    }

def format_spx_data(spx_data):
    """Format SPX data for display"""
    
    if not spx_data['success']:
        return f"❌ {spx_data['message']}"
    
    price = spx_data['price']
    change = spx_data['change']
    change_pct = spx_data['change_pct']
    high = spx_data.get('high', 'N/A')
    low = spx_data.get('low', 'N/A')
    source = spx_data['source']
    
    formatted = f"""
SPX LIVE DATA ({source}):
Current: ${price:.2f} ({change:+.2f}, {change_pct:+.2f}%)
High: ${high:.2f} | Low: ${low:.2f}
Range: {high - low:.2f} points
"""
    
    if 'spy_price' in spx_data:
        formatted += f"SPY: ${spx_data['spy_price']:.2f} (×10 = SPX)\n"
    
    return formatted.strip()

def analyze_with_unified_data():
    """Run SPX analysis with unified data source"""
    
    # Get live data
    spx_data = get_unified_spx_data()
    
    if not spx_data['success']:
        print(spx_data['message'])
        return None
    
    # Display current data
    print("\n" + format_spx_data(spx_data))
    
    # Current price for analysis
    spx_current = spx_data['price']
    spx_high = spx_data.get('high', spx_current)
    spx_low = spx_data.get('low', spx_current)
    
    # Quant levels analysis
    print(f"\nQUANT LEVELS ANALYSIS:")
    
    if spx_current >= 6560:
        print(f"🚨 AT/ABOVE 6560 HIGH REVERSAL ZONE")
        print(f"Strategy: FADE/SHORT - High probability reversal")
        print(f"Primary: SPXW250910P{int((spx_current-10)/5)*5}.0")
        
    elif spx_current >= 6542:
        print(f"⚠️  ABOVE RESISTANCE ZONE (6542)")
        if spx_current >= 6555:
            print(f"Strategy: APPROACHING 6560 reversal - Fade rallies")
            print(f"Primary: SPXW250910P{int((spx_current-5)/5)*5}.0")
        else:
            print(f"Strategy: BULLISH continuation toward 6560")
            print(f"Primary: SPXW250910C{int((spx_current+5)/5)*5}.0")
            
    elif spx_current >= 6510:
        print(f"✅ ABOVE KEY RESISTANCE (6510)")
        print(f"Strategy: BULLISH bias toward 6542-6560")
        print(f"Primary: SPXW250910C{int((spx_current+10)/5)*5}.0")
        
    else:
        print(f"⬇️  BELOW KEY RESISTANCE (6510)")
        print(f"Strategy: BEARISH toward 6498 support")
        print(f"Primary: SPXW250910P{int((spx_current-10)/5)*5}.0")
    
    return spx_data

if __name__ == "__main__":
    print("UNIFIED SPX DATA TEST")
    print("=" * 25)
    
    result = analyze_with_unified_data()
    
    if result:
        print(f"\n✅ Data source working: {result['source']}")
    else:
        print(f"\n❌ All data sources failed")
        print(f"Use screenshot analysis or manual entry")