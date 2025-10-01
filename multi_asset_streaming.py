"""
Multi-Asset Real-Time Streaming System
Tracks SPX, NDX, QQQ, SPY, IWM with Polygon API
"""

import requests
import json
import time
from datetime import datetime
import threading

# API Keys
POLYGON_PRIMARY = "_u0zA0CH5ZspOHecb2G8uBxd2DUo4r9D"
POLYGON_BACKUP = "CiDDZJqQS88A0QhaoJbn0rLqaenps6Pq"

# Discord Webhooks
WEBHOOK_TESTING = "https://discord.com/api/webhooks/1422928703972970516/59EBn9XvN6VautbSfjE8p_pFDNX4qIrU6ephGS--UvSiD7nSahftbhQDSW66fQwfXajp"
WEBHOOK_ALERTS = "https://discord.com/api/webhooks/1422763517974417478/0AAxHmLLjC389OXRi5KY_P2puAY8BhGAgEYTXSxj7TiKlqK_WH1PXPW6d_osA219ZFPu"

# Asset Configuration
ASSETS = {
    'SPX': {
        'type': 'index',
        'ticker': 'I:SPX',
        'name': 'S&P 500',
        'url_template': 'https://api.polygon.io/v3/snapshot/indices?ticker={ticker}&apikey={key}'
    },
    'NDX': {
        'type': 'index',
        'ticker': 'I:NDX',
        'name': 'NASDAQ-100',
        'url_template': 'https://api.polygon.io/v3/snapshot/indices?ticker={ticker}&apikey={key}'
    },
    'QQQ': {
        'type': 'etf',
        'ticker': 'QQQ',
        'name': 'NASDAQ-100 ETF',
        'url_template': 'https://api.polygon.io/v3/quotes/{ticker}?limit=1&apikey={key}'
    },
    'SPY': {
        'type': 'etf',
        'ticker': 'SPY',
        'name': 'S&P 500 ETF',
        'url_template': 'https://api.polygon.io/v3/quotes/{ticker}?limit=1&apikey={key}'
    },
    'IWM': {
        'type': 'etf',
        'ticker': 'IWM',
        'name': 'Russell 2000 ETF',
        'url_template': 'https://api.polygon.io/v3/quotes/{ticker}?limit=1&apikey={key}'
    }
}

class MultiAssetStreamingSystem:
    def __init__(self):
        self.running = False
        self.prices = {}
        self.last_update = {}

    def get_asset_price(self, asset_name, asset_config):
        """Get real-time price for any asset"""
        try:
            # Try primary key
            url = asset_config['url_template'].format(
                ticker=asset_config['ticker'],
                key=POLYGON_PRIMARY
            )
            response = requests.get(url, timeout=5, verify=True)

            if response.status_code == 200:
                data = response.json()

                if asset_config['type'] == 'index':
                    # Index data
                    if 'results' in data and len(data['results']) > 0:
                        return data['results'][0]['value']
                else:
                    # ETF data
                    if 'results' in data and len(data['results']) > 0:
                        quote = data['results'][0]
                        bid = quote.get('bid_price', 0)
                        ask = quote.get('ask_price', 0)
                        if bid > 0 and ask > 0:
                            return (bid + ask) / 2
                        return quote.get('last_price')

            # Try backup key if primary fails
            url = asset_config['url_template'].format(
                ticker=asset_config['ticker'],
                key=POLYGON_BACKUP
            )
            response = requests.get(url, timeout=5, verify=True)

            if response.status_code == 200:
                data = response.json()

                if asset_config['type'] == 'index':
                    if 'results' in data and len(data['results']) > 0:
                        return data['results'][0]['value']
                else:
                    if 'results' in data and len(data['results']) > 0:
                        quote = data['results'][0]
                        bid = quote.get('bid_price', 0)
                        ask = quote.get('ask_price', 0)
                        if bid > 0 and ask > 0:
                            return (bid + ask) / 2
                        return quote.get('last_price')

            return None

        except Exception as e:
            print(f"❌ Error getting {asset_name} price: {e}")
            return None

    def update_all_prices(self):
        """Update prices for all assets"""
        for asset_name, asset_config in ASSETS.items():
            price = self.get_asset_price(asset_name, asset_config)
            if price:
                self.prices[asset_name] = price
                self.last_update[asset_name] = datetime.now()

    def display_prices(self):
        """Display all current prices"""
        current_time = datetime.now().strftime('%H:%M:%S')
        print(f"\n{'='*80}")
        print(f"📊 MULTI-ASSET DASHBOARD - {current_time}")
        print(f"{'='*80}")

        for asset_name in ['SPX', 'NDX', 'QQQ', 'SPY', 'IWM']:
            if asset_name in self.prices:
                price = self.prices[asset_name]
                asset_type = ASSETS[asset_name]['type'].upper()
                name = ASSETS[asset_name]['name']

                if asset_name in ['SPX', 'NDX']:
                    print(f"  {asset_name}: ${price:,.2f} ({name} {asset_type})")
                else:
                    print(f"  {asset_name}: ${price:.2f} ({name} {asset_type})")
            else:
                print(f"  {asset_name}: No data")

        print(f"{'='*80}\n")

    def start(self):
        """Start multi-asset streaming"""
        print("="*80)
        print("🚀 MULTI-ASSET REAL-TIME STREAMING SYSTEM STARTED")
        print("="*80)
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S ET')}")
        print(f"Assets: SPX, NDX, QQQ, SPY, IWM")
        print(f"Refresh Interval: 10 seconds")
        print(f"Data Source: Polygon Premium API")
        print("="*80)

        self.running = True
        iteration = 0

        while self.running:
            iteration += 1

            # Update all prices
            self.update_all_prices()

            # Display dashboard
            print(f"\n[Iteration {iteration}]")
            self.display_prices()

            # Wait 10 seconds before next update
            time.sleep(10)

    def stop(self):
        """Stop streaming system"""
        self.running = False
        print("\n" + "="*80)
        print("🛑 MULTI-ASSET STREAMING SYSTEM STOPPED")
        print("="*80)

if __name__ == "__main__":
    system = MultiAssetStreamingSystem()

    try:
        system.start()
    except KeyboardInterrupt:
        print("\n\nReceived interrupt signal...")
        system.stop()
