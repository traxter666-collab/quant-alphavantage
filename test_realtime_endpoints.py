#!/usr/bin/env python3
"""
Test different AlphaVantage endpoints for real-time data
"""

import os
import requests
from datetime import datetime

def test_endpoint(endpoint_name, url):
    """Test a specific endpoint and report results"""
    print(f"\n{endpoint_name}:")
    print("-" * 40)

    try:
        response = requests.get(url, timeout=10)
        data = response.json()

        # Check for errors
        if "Error Message" in data:
            print(f"ERROR: {data['Error Message']}")
            return
        elif "Note" in data:
            print(f"RATE LIMITED: {data['Note']}")
            return

        # Extract timestamp and price info
        if "Global Quote" in data:
            quote = data["Global Quote"]
            timestamp = quote.get("07. latest trading day", "N/A")
            price = quote.get("05. price", "N/A")
            print(f"Timestamp: {timestamp}")
            print(f"Price: ${price}")

        elif "Time Series (5min)" in data:
            series = data["Time Series (5min)"]
            latest_time = list(series.keys())[0]
            latest_data = series[latest_time]
            price = latest_data.get("4. close", "N/A")
            print(f"Timestamp: {latest_time}")
            print(f"Price: ${price}")

        elif "Time Series (1min)" in data:
            series = data["Time Series (1min)"]
            latest_time = list(series.keys())[0]
            latest_data = series[latest_time]
            price = latest_data.get("4. close", "N/A")
            print(f"Timestamp: {latest_time}")
            print(f"Price: ${price}")

        else:
            print(f"Unexpected response structure")
            print(f"Keys: {list(data.keys())}")

    except Exception as e:
        print(f"ERROR: {e}")

def main():
    api_key = os.getenv('ALPHAVANTAGE_API_KEY', 'ZFL38ZY98GSN7E1S')
    base_url = "https://www.alphavantage.co/query"

    print("ALPHAVANTAGE REAL-TIME ENDPOINT TESTING")
    print("=" * 50)
    print(f"Current Time: {datetime.now()}")
    print(f"API Key: {api_key[:4]}...{api_key[-4:]}")

    # Test different endpoints for SPY
    endpoints = [
        ("GLOBAL_QUOTE (Standard)", f"{base_url}?function=GLOBAL_QUOTE&symbol=SPY&apikey={api_key}"),
        ("GLOBAL_QUOTE (Real-time)", f"{base_url}?function=GLOBAL_QUOTE&symbol=SPY&entitlement=realtime&apikey={api_key}"),
        ("INTRADAY_5MIN (Standard)", f"{base_url}?function=TIME_SERIES_INTRADAY&symbol=SPY&interval=5min&apikey={api_key}"),
        ("INTRADAY_5MIN (Real-time)", f"{base_url}?function=TIME_SERIES_INTRADAY&symbol=SPY&interval=5min&entitlement=realtime&apikey={api_key}"),
        ("INTRADAY_1MIN (Real-time)", f"{base_url}?function=TIME_SERIES_INTRADAY&symbol=SPY&interval=1min&entitlement=realtime&apikey={api_key}"),
    ]

    for name, url in endpoints:
        test_endpoint(name, url)

    print(f"\n{'='*50}")
    print("ANALYSIS:")
    print("- If all timestamps show old dates, market may be closed")
    print("- If real-time shows same as standard, entitlement may not be active")
    print("- 1min intervals should show most recent data if market is open")

if __name__ == "__main__":
    main()