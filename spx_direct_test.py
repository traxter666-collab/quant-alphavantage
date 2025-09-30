import os
import requests
from datetime import datetime

def test_spx_tickers():
    """Test different SPX ticker symbols to find the right one"""
    
    api_key = os.getenv('ALPHAVANTAGE_API_KEY', 'ZFL38ZY98GSN7E1S')
    base_url = "https://www.alphavantage.co/query"
    
    # Possible SPX tickers to test
    tickers_to_test = [
        'SPX',      # Standard SPX
        'SPXW',     # SPX Weeklys (options related)  
        'SPX.X',    # Some platforms use .X suffix
        'SPXUSD',   # SPX in USD
        '$SPX',     # With $ prefix
        '^SPX',     # Yahoo-style prefix
        'SPX500',   # Full name variant
        'GSPC',     # S&P 500 index symbol (some use this)
        '^GSPC'     # Yahoo variant
    ]
    
    print("Testing SPX Direct Tickers")
    print("=" * 40)
    print(f"Current time: {datetime.now()}")
    print()
    
    for ticker in tickers_to_test:
        print(f"Testing: {ticker}")
        
        try:
            # Test GLOBAL_QUOTE
            url = f"{base_url}?function=GLOBAL_QUOTE&symbol={ticker}&entitlement=realtime&apikey={api_key}"
            response = requests.get(url)
            data = response.json()
            
            if "Global Quote" in data and data["Global Quote"]:
                quote = data["Global Quote"]
                symbol = quote.get('01. symbol', 'N/A')
                price = quote.get('05. price', 'N/A')
                trading_day = quote.get('07. latest trading day', 'N/A')
                
                print(f"  ✅ SUCCESS: {symbol}")
                print(f"     Price: {price}")
                print(f"     Date: {trading_day}")
                
                # If price is reasonable for SPX (4000-7000 range)
                if price != 'N/A':
                    try:
                        price_val = float(price)
                        if 4000 <= price_val <= 7000:
                            print(f"     🎯 LIKELY CORRECT SPX TICKER!")
                            return ticker
                    except:
                        pass
                        
            elif "Error Message" in data:
                print(f"  ❌ Error: {data['Error Message']}")
            elif "Note" in data:
                print(f"  ⚠️  Rate Limited: {data['Note'][:50]}...")
            else:
                print(f"  ❌ No data or unexpected format")
                
        except Exception as e:
            print(f"  ❌ Exception: {e}")
            
        print()
    
    print("No valid SPX ticker found in Alphavantage.")
    print("SPX index data may not be available in free tier.")
    print()
    
    # Test if we can get intraday data for any working ticker
    print("Testing INTRADAY data access...")
    for ticker in ['SPX', 'SPXW']:
        try:
            url = f"{base_url}?function=TIME_SERIES_INTRADAY&symbol={ticker}&interval=1min&entitlement=realtime&apikey={api_key}"
            response = requests.get(url)
            data = response.json()
            
            if "Time Series (1min)" in data:
                print(f"✅ {ticker}: Intraday data available")
                time_series = data["Time Series (1min)"]
                latest_time = list(time_series.keys())[0]
                latest_data = time_series[latest_time]
                print(f"   Latest: {latest_time}")
                print(f"   Close: {latest_data.get('4. close', 'N/A')}")
                return ticker
            else:
                print(f"❌ {ticker}: No intraday data")
                
        except Exception as e:
            print(f"❌ {ticker}: Error - {e}")
    
    return None

if __name__ == "__main__":
    working_ticker = test_spx_tickers()
    
    if working_ticker:
        print(f"\n🎉 RECOMMENDED SPX TICKER: {working_ticker}")
    else:
        print(f"\n⚠️  No direct SPX ticker found.")
        print("Alphavantage free tier may not include SPX index data.")
        print("Consider:")
        print("1. Using SPY ETF as proxy (SPY * 10 ≈ SPX)")  
        print("2. Upgrading to Alphavantage premium")
        print("3. Using alternative data source for SPX")