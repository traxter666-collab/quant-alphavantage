#!/usr/bin/env python3
"""
Quick SPY Price - Fast real-time data
"""
import requests
from datetime import datetime

def get_spy_fast():
    try:
        # Yahoo Finance - fastest
        url = "https://query1.finance.yahoo.com/v8/finance/chart/SPY"
        response = requests.get(url, timeout=3)
        data = response.json()
        price = data['chart']['result'][0]['meta']['regularMarketPrice']
        after_hours = data['chart']['result'][0]['meta'].get('postMarketPrice')

        print(f"SPY: ${price:.2f}")
        if after_hours and after_hours != price:
            print(f"After Hours: ${after_hours:.2f}")
        print(f"SPX: ${price*10:.0f}")

    except:
        print("Data unavailable")

if __name__ == "__main__":
    get_spy_fast()