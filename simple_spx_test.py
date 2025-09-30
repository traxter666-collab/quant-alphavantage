import os
import requests

api_key = os.getenv('ALPHAVANTAGE_API_KEY', 'ZFL38ZY98GSN7E1S')

# Test direct SPX tickers
tickers = ['SPX', 'SPXW', '^GSPC', 'GSPC']

print("SPX Ticker Test")
print("=" * 30)

for ticker in tickers:
    print(f"\nTesting: {ticker}")
    url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={ticker}&entitlement=realtime&apikey={api_key}"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        if "Global Quote" in data and data["Global Quote"]:
            quote = data["Global Quote"]
            price = quote.get('05. price', 'N/A')
            symbol = quote.get('01. symbol', 'N/A')
            date = quote.get('07. latest trading day', 'N/A')
            
            print(f"SUCCESS - Symbol: {symbol}")
            print(f"Price: {price}")  
            print(f"Date: {date}")
            
            # Check if reasonable SPX price
            if price != 'N/A':
                try:
                    price_val = float(price)
                    if 4000 <= price_val <= 7000:
                        print(f"*** VALID SPX DATA! ***")
                except:
                    pass
                    
        elif "Error Message" in data:
            print(f"Error: {data['Error Message']}")
        elif "Note" in data:
            print("Rate limited")
        else:
            print("No valid data")
            
    except Exception as e:
        print(f"Exception: {e}")

print(f"\nAlternative: Check if SPX options (SPXW) data exists...")
spxw_url = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol=SPXW&interval=5min&entitlement=realtime&apikey={api_key}"

try:
    response = requests.get(spxw_url)
    data = response.json()
    
    if "Time Series (5min)" in data:
        print("SPXW intraday data available!")
        time_series = data["Time Series (5min)"]
        latest = list(time_series.keys())[0]
        print(f"Latest: {latest}")
        print(f"Close: {time_series[latest]['4. close']}")
    else:
        print("SPXW intraday not available")
        print("Response keys:", list(data.keys()))
        
except Exception as e:
    print(f"SPXW test failed: {e}")