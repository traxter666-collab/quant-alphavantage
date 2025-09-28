#!/usr/bin/env python3
"""
Alphavantage API Key Validation Script
Tests the API key functionality with real market data calls
"""

import os
import requests
import json
from datetime import datetime

def validate_alphavantage_api():
    """Validate Alphavantage API key with multiple endpoint tests"""
    
    # Get API key - premium real-time access
    api_key = os.getenv('ALPHAVANTAGE_API_KEY', 'ZFL38ZY98GSN7E1S')
    if not api_key:
        print("ERROR: ALPHAVANTAGE_API_KEY not available")
        print("Using default premium key for real-time access")
        api_key = 'ZFL38ZY98GSN7E1S'
    
    print(f"API Key found: {api_key[:4]}...{api_key[-4:]} (masked)")
    
    base_url = "https://www.alphavantage.co/query"
    
    # Test 1: Market Status
    print("\nTesting Market Status...")
    try:
        response = requests.get(f"{base_url}?function=MARKET_STATUS&apikey={api_key}")
        data = response.json()
        
        if "Error Message" in data:
            print(f"API Error: {data['Error Message']}")
            return False
        elif "Note" in data:
            print(f"Rate Limited: {data['Note']}")
            return False
        elif "markets" in data:
            print("Market Status API working")
            print(f"   Markets found: {len(data.get('markets', []))}")
        else:
            print(f"ERROR: Unexpected response: {data}")
            return False
            
    except Exception as e:
        print(f"ERROR: Market Status test failed: {e}")
        return False
    
    # Test 2: SPY Quote
    print("\nTesting SPY Quote...")
    try:
        response = requests.get(f"{base_url}?function=GLOBAL_QUOTE&symbol=SPY&entitlement=realtime&apikey={api_key}")
        data = response.json()
        
        if "Error Message" in data:
            print(f"ERROR: API Error: {data['Error Message']}")
            return False
        elif "Note" in data:
            print(f"WARNING: Rate Limited: {data['Note']}")
            return False
        elif "Global Quote" in data:
            quote = data["Global Quote"]
            price = quote.get("05. price", "N/A")
            change = quote.get("09. change", "N/A")
            print("SUCCESS: SPY Quote API working")
            print(f"   SPY Price: ${price}")
            print(f"   Change: {change}")
        else:
            print(f"ERROR: Unexpected response: {data}")
            return False
            
    except Exception as e:
        print(f"ERROR: SPY Quote test failed: {e}")
        return False
    
    # Test 3: RSI Indicator
    print("\nTesting RSI Indicator...")
    try:
        response = requests.get(f"{base_url}?function=RSI&symbol=SPY&interval=5min&time_period=14&series_type=close&apikey={api_key}")
        data = response.json()
        
        if "Error Message" in data:
            print(f"ERROR: API Error: {data['Error Message']}")
            return False
        elif "Note" in data:
            print(f"WARNING: Rate Limited: {data['Note']}")
            return False
        elif "Technical Analysis: RSI" in data:
            rsi_data = data["Technical Analysis: RSI"]
            latest_timestamp = list(rsi_data.keys())[0] if rsi_data else None
            if latest_timestamp:
                latest_rsi = rsi_data[latest_timestamp]["RSI"]
                print("SUCCESS: RSI Indicator API working")
                print(f"   Latest RSI (5min): {float(latest_rsi):.2f}")
                print(f"   Timestamp: {latest_timestamp}")
            else:
                print("ERROR: No RSI data returned")
                return False
        else:
            print(f"ERROR: Unexpected response: {data}")
            return False
            
    except Exception as e:
        print(f"ERROR: RSI test failed: {e}")
        return False
    
    # Test 4: Intraday Data
    print("\nTesting Intraday Data...")
    try:
        response = requests.get(f"{base_url}?function=TIME_SERIES_INTRADAY&symbol=SPY&interval=5min&apikey={api_key}")
        data = response.json()
        
        if "Error Message" in data:
            print(f"ERROR: API Error: {data['Error Message']}")
            return False
        elif "Note" in data:
            print(f"WARNING: Rate Limited: {data['Note']}")
            return False
        elif "Time Series (5min)" in data:
            time_series = data["Time Series (5min)"]
            latest_timestamp = list(time_series.keys())[0] if time_series else None
            if latest_timestamp:
                latest_data = time_series[latest_timestamp]
                close_price = latest_data["4. close"]
                volume = latest_data["5. volume"]
                print("SUCCESS: Intraday Data API working")
                print(f"   Latest Close: ${close_price}")
                print(f"   Volume: {volume}")
                print(f"   Timestamp: {latest_timestamp}")
            else:
                print("ERROR: No intraday data returned")
                return False
        else:
            print(f"ERROR: Unexpected response: {data}")
            return False
            
    except Exception as e:
        print(f"ERROR: Intraday data test failed: {e}")
        return False
    
    print("\nAPI Validation Summary:")
    print("SUCCESS: All Alphavantage API endpoints working correctly")
    print("SUCCESS: Market data access confirmed")
    print("SUCCESS: Technical indicators functional")
    print("SUCCESS: Real-time data available")
    print(f"\nValidation completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return True

def calculate_spx_estimate_from_spy():
    """Calculate SPX estimate from SPY price (SPY × 10 ≈ SPX)"""
    
    api_key = os.getenv('ALPHAVANTAGE_API_KEY', 'ZFL38ZY98GSN7E1S')
    if not api_key:
        print("ERROR: API key not available")
        api_key = 'ZFL38ZY98GSN7E1S'
    
    try:
        base_url = "https://www.alphavantage.co/query"
        response = requests.get(f"{base_url}?function=GLOBAL_QUOTE&symbol=SPY&apikey={api_key}")
        data = response.json()
        
        if "Global Quote" in data:
            spy_price = float(data["Global Quote"]["05. price"])
            spx_estimate = spy_price * 10
            
            print(f"\nSPX Conversion:")
            print(f"   SPY Price: ${spy_price:.2f}")
            print(f"   SPX Estimate: ${spx_estimate:.2f}")
            
            return spx_estimate
        else:
            print("ERROR: Could not get SPY price for SPX conversion")
            return None
            
    except Exception as e:
        print(f"ERROR: SPX calculation failed: {e}")
        return None

if __name__ == "__main__":
    print("Alphavantage API Key Validation")
    print("=" * 50)
    
    # Run validation
    success = validate_alphavantage_api()
    
    if success:
        # Calculate SPX estimate
        calculate_spx_estimate_from_spy()
        print("\nValidation completed successfully!")
        print("Your Alphavantage API key is working correctly.")
    else:
        print("\nERROR: Validation failed!")
        print("Please check your API key and try again.")