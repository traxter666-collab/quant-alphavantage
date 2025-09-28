import os
import requests
from datetime import datetime

def get_spx_data():
    """Get SPX data: Alphavantage first, Yahoo backup"""
    
    print("Getting live SPX data...")
    
    # Try Alphavantage (SPY proxy) first
    api_key = os.getenv('ALPHAVANTAGE_API_KEY', 'ZFL38ZY98GSN7E1S')
    if api_key:
        try:
            url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=SPY&entitlement=realtime&apikey={api_key}"
            response = requests.get(url, timeout=8)
            data = response.json()
            
            if "Global Quote" in data and data["Global Quote"]:
                quote = data["Global Quote"]
                spy_price = float(quote["05. price"])
                trading_day = quote.get("07. latest trading day", "")
                today = datetime.now().strftime('%Y-%m-%d')
                
                # Check if current day
                if trading_day == today:
                    spx_price = spy_price * 10
                    spx_change = float(quote["09. change"]) * 10
                    
                    print(f"SUCCESS - Alphavantage: SPX ${spx_price:.2f}")
                    return {
                        'price': spx_price,
                        'change': spx_change,
                        'change_pct': (spx_change / (spx_price - spx_change)) * 100,
                        'high': float(quote["03. high"]) * 10,
                        'low': float(quote["04. low"]) * 10,
                        'source': 'Alphavantage',
                        'current': True
                    }
                else:
                    print(f"Alphavantage data is stale ({trading_day})")
                    
        except Exception as e:
            print(f"Alphavantage failed: {e}")
    
    # Yahoo Finance backup
    try:
        print("Trying Yahoo Finance backup...")
        url = "https://query1.finance.yahoo.com/v8/finance/chart/%5EGSPC"
        headers = {'User-Agent': 'Mozilla/5.0'}
        
        response = requests.get(url, headers=headers, timeout=8)
        data = response.json()
        
        if 'chart' in data and data['chart']['result']:
            result = data['chart']['result'][0]
            meta = result['meta']
            
            price = meta.get('regularMarketPrice')
            prev_close = meta.get('previousClose')
            
            if price and prev_close:
                change = price - prev_close
                
                print(f"SUCCESS - Yahoo Finance: SPX ${price:.2f}")
                return {
                    'price': price,
                    'change': change,
                    'change_pct': (change / prev_close) * 100,
                    'high': meta.get('regularMarketDayHigh', price),
                    'low': meta.get('regularMarketDayLow', price),
                    'source': 'Yahoo Finance',
                    'current': True
                }
                
    except Exception as e:
        print(f"Yahoo Finance failed: {e}")
    
    # Both failed
    print("All sources failed - manual input required")
    return None

def analyze_spx_now():
    """Run current SPX analysis with live data"""
    
    print("SPX LIVE ANALYSIS")
    print("=" * 20)
    
    # Get data
    data = get_spx_data()
    if not data:
        print("No data available. Please provide SPX manually.")
        return
    
    price = data['price']
    change = data['change']
    change_pct = data['change_pct']
    high = data['high']
    low = data['low']
    source = data['source']
    
    print(f"\nCURRENT DATA ({source}):")
    print(f"SPX: ${price:.2f} ({change:+.2f}, {change_pct:+.2f}%)")
    print(f"Range: ${low:.2f} - ${high:.2f}")
    
    # Quant levels analysis
    print(f"\nQUANT ANALYSIS:")
    
    if price >= 6560:
        bias = "BEARISH REVERSAL"
        strategy = "FADE - High reversal probability zone"
        strike = int((price - 10) / 5) * 5
        trade = f"SPXW250910P{strike}.0"
        
    elif price >= 6555:
        bias = "APPROACHING REVERSAL"  
        strategy = "Caution - Near 6560 reversal zone"
        strike = int((price - 5) / 5) * 5
        trade = f"SPXW250910P{strike}.0"
        
    elif price >= 6542:
        bias = "BULLISH (in resistance zone)"
        strategy = "Continuation toward 6560"
        strike = int((price + 5) / 5) * 5
        trade = f"SPXW250910C{strike}.0"
        
    elif price >= 6510:
        bias = "BULLISH" 
        strategy = "Above key resistance"
        strike = int((price + 10) / 5) * 5
        trade = f"SPXW250910C{strike}.0"
        
    else:
        bias = "BEARISH"
        strategy = "Below key resistance - target 6498"
        strike = int((price - 10) / 5) * 5  
        trade = f"SPXW250910P{strike}.0"
    
    print(f"Bias: {bias}")
    print(f"Strategy: {strategy}")
    print(f"Trade: {trade}")
    
    # Key levels
    print(f"\nKEY LEVELS:")
    print(f"6560: High reversal probability")
    print(f"6542: Resistance zone")
    print(f"6510: Key resistance")
    print(f"6498: Strong support")

if __name__ == "__main__":
    analyze_spx_now()