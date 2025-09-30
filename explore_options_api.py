#!/usr/bin/env python3
"""
Explore AlphaVantage API capabilities for options data and GEX/DEX analysis
"""

import os
import requests
import json
from datetime import datetime

def test_options_endpoints():
    """Test various AlphaVantage endpoints for options data"""

    api_key = os.getenv('ALPHAVANTAGE_API_KEY', 'ZFL38ZY98GSN7E1S')
    base_url = "https://www.alphavantage.co/query"

    print("EXPLORING ALPHAVANTAGE OPTIONS CAPABILITIES")
    print("=" * 50)
    print(f"API Key: {api_key[:4]}...{api_key[-4:]}")
    print()

    # Test 1: Check for options chain endpoint
    print("1. Testing Options Chain (SPY)...")
    try:
        response = requests.get(f"{base_url}?function=OPTIONS_CHAIN&symbol=SPY&apikey={api_key}")
        data = response.json()
        print("Response keys:", list(data.keys()))
        if "Error Message" in data:
            print(f"   Error: {data['Error Message']}")
        elif "Note" in data:
            print(f"   Note: {data['Note']}")
        else:
            print("   Raw response:", json.dumps(data, indent=2)[:500] + "...")
    except Exception as e:
        print(f"   Exception: {e}")

    print()

    # Test 2: Check for historical options
    print("2. Testing Historical Options...")
    try:
        response = requests.get(f"{base_url}?function=HISTORICAL_OPTIONS&symbol=SPY&apikey={api_key}")
        data = response.json()
        print("Response keys:", list(data.keys()))
        if "Error Message" in data:
            print(f"   Error: {data['Error Message']}")
        elif "Note" in data:
            print(f"   Note: {data['Note']}")
        else:
            print("   Raw response:", json.dumps(data, indent=2)[:500] + "...")
    except Exception as e:
        print(f"   Exception: {e}")

    print()

    # Test 3: Check for Greeks calculation
    print("3. Testing Greeks Calculation...")
    try:
        response = requests.get(f"{base_url}?function=GREEKS&symbol=SPY&apikey={api_key}")
        data = response.json()
        print("Response keys:", list(data.keys()))
        if "Error Message" in data:
            print(f"   Error: {data['Error Message']}")
        elif "Note" in data:
            print(f"   Note: {data['Note']}")
        else:
            print("   Raw response:", json.dumps(data, indent=2)[:500] + "...")
    except Exception as e:
        print(f"   Exception: {e}")

    print()

    # Test 4: Check for real-time options
    print("4. Testing Real-time Options...")
    try:
        response = requests.get(f"{base_url}?function=REAL_TIME_OPTIONS&symbol=SPY&apikey={api_key}")
        data = response.json()
        print("Response keys:", list(data.keys()))
        if "Error Message" in data:
            print(f"   Error: {data['Error Message']}")
        elif "Note" in data:
            print(f"   Note: {data['Note']}")
        else:
            print("   Raw response:", json.dumps(data, indent=2)[:500] + "...")
    except Exception as e:
        print(f"   Exception: {e}")

    print()

    # Test 5: Check for implied volatility
    print("5. Testing Implied Volatility...")
    try:
        response = requests.get(f"{base_url}?function=IV&symbol=SPY&apikey={api_key}")
        data = response.json()
        print("Response keys:", list(data.keys()))
        if "Error Message" in data:
            print(f"   Error: {data['Error Message']}")
        elif "Note" in data:
            print(f"   Note: {data['Note']}")
        else:
            print("   Raw response:", json.dumps(data, indent=2)[:500] + "...")
    except Exception as e:
        print(f"   Exception: {e}")

    print()

    # Test 6: Check available functions
    print("6. Testing Available Functions...")
    try:
        response = requests.get(f"{base_url}?function=FUNCTIONS&apikey={api_key}")
        data = response.json()
        print("Response keys:", list(data.keys()))
        if "functions" in data:
            functions = data["functions"]
            options_functions = [f for f in functions if "option" in f.lower() or "greek" in f.lower()]
            print(f"   Options-related functions found: {options_functions}")
        else:
            print("   Raw response:", json.dumps(data, indent=2)[:500] + "...")
    except Exception as e:
        print(f"   Exception: {e}")

def test_spx_data():
    """Test SPX-specific data availability"""

    api_key = os.getenv('ALPHAVANTAGE_API_KEY', 'ZFL38ZY98GSN7E1S')
    base_url = "https://www.alphavantage.co/query"

    print("\nSPX DATA AVAILABILITY TEST")
    print("=" * 30)

    # Test SPX direct quote
    print("Testing SPX Direct Quote...")
    try:
        response = requests.get(f"{base_url}?function=GLOBAL_QUOTE&symbol=SPX&apikey={api_key}")
        data = response.json()

        if "Global Quote" in data:
            quote = data["Global Quote"]
            price = quote.get("05. price", "N/A")
            print(f"   SPX Direct: ${price}")
        else:
            print(f"   SPX Error: {data}")
    except Exception as e:
        print(f"   SPX Exception: {e}")

    # Test SPXW (SPX Weeklys)
    print("\nTesting SPXW Quote...")
    try:
        response = requests.get(f"{base_url}?function=GLOBAL_QUOTE&symbol=SPXW&apikey={api_key}")
        data = response.json()

        if "Global Quote" in data:
            quote = data["Global Quote"]
            price = quote.get("05. price", "N/A")
            print(f"   SPXW: ${price}")
        else:
            print(f"   SPXW Error: {data}")
    except Exception as e:
        print(f"   SPXW Exception: {e}")

if __name__ == "__main__":
    test_options_endpoints()
    test_spx_data()

    print("\nEXPLORATION COMPLETE")
    print("Check output above for available options data capabilities")