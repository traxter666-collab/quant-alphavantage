"""
Multi-Asset Trade Opportunity Scanner
Analyzes SPX, NDX, QQQ, SPY, IWM for trading opportunities
Generates actionable trade recommendations with entry/exit levels
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
WEBHOOK_SPX = "https://discord.com/api/webhooks/1422930069290225694/PKiahdQzpgIZuceHRU254dgpmSEOcgho0-o-DpkQXeCUsQ5AYH1mv3OmJ_gG-1eB7FU-"
WEBHOOK_NDX = "https://discord.com/api/webhooks/1422964068464988292/U6sdcQEyh9biXh2UTkZ2P9qNTIvU-wngGwYxbo3wxUmCDxMEqNITMz3LXRQdvMbxNJ6G"

# Trading Levels
SPX_LEVELS = {
    'resistance': [6742, 6734, 6730, 6700, 6690],
    'support': [6647, 6642, 6633, 6621, 6620, 6600, 6595],
    'pivot': 6659
}

NDX_LEVELS = {
    'resistance': [24850, 24800, 24750, 24700, 24650],
    'support': [24500, 24450, 24400, 24350, 24300, 24250, 24200],
    'pivot': 24550
}

# Asset Configuration
ASSETS = {
    'SPX': {'type': 'index', 'ticker': 'I:SPX', 'levels': SPX_LEVELS, 'webhook': WEBHOOK_SPX},
    'NDX': {'type': 'index', 'ticker': 'I:NDX', 'levels': NDX_LEVELS, 'webhook': WEBHOOK_NDX},
    'QQQ': {'type': 'etf', 'ticker': 'QQQ', 'webhook': WEBHOOK_ALERTS},
    'SPY': {'type': 'etf', 'ticker': 'SPY', 'webhook': WEBHOOK_ALERTS},
    'IWM': {'type': 'etf', 'ticker': 'IWM', 'webhook': WEBHOOK_ALERTS}
}

class TradeScanner:
    def __init__(self):
        self.running = False
        self.prices = {}
        self.previous_prices = {}
        self.trades = {}
        self.last_trade_alert = {}

    def get_price(self, asset_name):
        """Get current price for any asset"""
        try:
            asset = ASSETS[asset_name]

            if asset['type'] == 'index':
                url = f"https://api.polygon.io/v3/snapshot/indices?ticker={asset['ticker']}&apikey={POLYGON_PRIMARY}"
                response = requests.get(url, timeout=5, verify=True)
                if response.status_code == 200:
                    data = response.json()
                    if 'results' in data and len(data['results']) > 0:
                        return data['results'][0]['value']
            else:
                url = f"https://api.polygon.io/v3/quotes/{asset['ticker']}?limit=1&apikey={POLYGON_PRIMARY}"
                response = requests.get(url, timeout=5, verify=True)
                if response.status_code == 200:
                    data = response.json()
                    if 'results' in data and len(data['results']) > 0:
                        quote = data['results'][0]
                        bid = quote.get('bid_price', 0)
                        ask = quote.get('ask_price', 0)
                        if bid > 0 and ask > 0:
                            return (bid + ask) / 2
            return None
        except Exception as e:
            print(f"❌ Error getting {asset_name} price: {e}")
            return None

    def calculate_momentum(self, asset_name):
        """Calculate simple momentum (bullish/bearish/neutral)"""
        if asset_name not in self.prices or asset_name not in self.previous_prices:
            return 'NEUTRAL'

        current = self.prices[asset_name]
        previous = self.previous_prices[asset_name]

        change_pct = ((current - previous) / previous) * 100

        if change_pct > 0.05:
            return 'BULLISH'
        elif change_pct < -0.05:
            return 'BEARISH'
        else:
            return 'NEUTRAL'

    def find_nearest_levels(self, asset_name, price):
        """Find nearest support and resistance levels"""
        if asset_name not in ['SPX', 'NDX']:
            return None, None

        levels = ASSETS[asset_name]['levels']

        # Find nearest resistance (above current price)
        resistances = [r for r in levels['resistance'] if r > price]
        nearest_resistance = min(resistances) if resistances else None

        # Find nearest support (below current price)
        supports = [s for s in levels['support'] if s < price]
        nearest_support = max(supports) if supports else None

        return nearest_support, nearest_resistance

    def calculate_option_strike(self, asset_name, price, trade_type, target):
        """Calculate optimal option strike based on trade setup"""
        from datetime import datetime, timedelta

        # Determine if 0DTE or next expiration
        now = datetime.now()
        # Assume 0DTE for intraday, Friday for weekly
        expiry = now.strftime('%Y%m%d')  # 0DTE format

        if asset_name in ['SPX', 'NDX']:
            # Index options - round to nearest 5 or 10
            if trade_type == 'LONG':
                # Calls: slightly OTM for leverage
                strike = int((price + 5) / 5) * 5
            else:
                # Puts: slightly OTM for leverage
                strike = int((price - 5) / 5) * 5

            ticker = 'SPXW' if asset_name == 'SPX' else 'NDXP'
            option_type = 'C' if trade_type == 'LONG' else 'P'
            contract = f"{ticker}{expiry}{option_type}{strike}"

        else:
            # ETF options - round to nearest 1 or 0.5
            if trade_type == 'LONG':
                strike = int(price + 0.5)
            else:
                strike = int(price - 0.5)

            ticker = asset_name
            option_type = 'C' if trade_type == 'LONG' else 'P'
            contract = f"{ticker}{expiry}{option_type}{strike}"

        return contract, strike

    def generate_trade_setup(self, asset_name, price, momentum):
        """Generate trade setup based on price, levels, and momentum"""
        trade_key = f"{asset_name}_{int(price)}"
        current_time = time.time()

        # Check cooldown (only alert same trade once per 5 minutes)
        if trade_key in self.last_trade_alert:
            if current_time - self.last_trade_alert[trade_key] < 300:
                return None

        if asset_name in ['SPX', 'NDX']:
            support, resistance = self.find_nearest_levels(asset_name, price)

            if support and resistance:
                distance_to_support = price - support
                distance_to_resistance = resistance - price

                # Near support with bullish momentum = LONG setup
                if distance_to_support <= 10 and momentum in ['BULLISH', 'NEUTRAL']:
                    self.last_trade_alert[trade_key] = current_time
                    target1 = round(price + (distance_to_resistance * 0.5), 2)
                    contract, strike = self.calculate_option_strike(asset_name, price, 'LONG', target1)

                    return {
                        'asset': asset_name,
                        'type': 'LONG',
                        'reason': f'Near support {support} with {momentum} momentum',
                        'entry': round(price, 2),
                        'stop': round(support - 5, 2),
                        'target1': target1,
                        'target2': round(resistance - 5, 2),
                        'confidence': 'HIGH' if momentum == 'BULLISH' else 'MEDIUM',
                        'contract': contract,
                        'strike': strike,
                        'option_type': 'CALL'
                    }

                # Near resistance with bearish momentum = SHORT setup
                elif distance_to_resistance <= 10 and momentum in ['BEARISH', 'NEUTRAL']:
                    self.last_trade_alert[trade_key] = current_time
                    target1 = round(price - (distance_to_support * 0.5), 2)
                    contract, strike = self.calculate_option_strike(asset_name, price, 'SHORT', target1)

                    return {
                        'asset': asset_name,
                        'type': 'SHORT',
                        'reason': f'Near resistance {resistance} with {momentum} momentum',
                        'entry': round(price, 2),
                        'stop': round(resistance + 5, 2),
                        'target1': target1,
                        'target2': round(support + 5, 2),
                        'confidence': 'HIGH' if momentum == 'BEARISH' else 'MEDIUM',
                        'contract': contract,
                        'strike': strike,
                        'option_type': 'PUT'
                    }

        # ETF momentum trades (simpler logic)
        elif momentum == 'BULLISH':
            self.last_trade_alert[trade_key] = current_time
            target1 = round(price * 1.005, 2)
            contract, strike = self.calculate_option_strike(asset_name, price, 'LONG', target1)

            return {
                'asset': asset_name,
                'type': 'LONG',
                'reason': f'Strong bullish momentum',
                'entry': round(price, 2),
                'stop': round(price * 0.995, 2),  # 0.5% stop
                'target1': target1,  # 0.5% target
                'target2': round(price * 1.010, 2),  # 1% target
                'confidence': 'MEDIUM',
                'contract': contract,
                'strike': strike,
                'option_type': 'CALL'
            }
        elif momentum == 'BEARISH':
            self.last_trade_alert[trade_key] = current_time
            target1 = round(price * 0.995, 2)
            contract, strike = self.calculate_option_strike(asset_name, price, 'SHORT', target1)

            return {
                'asset': asset_name,
                'type': 'SHORT',
                'reason': f'Strong bearish momentum',
                'entry': round(price, 2),
                'stop': round(price * 1.005, 2),  # 0.5% stop
                'target1': target1,  # 0.5% target
                'target2': round(price * 0.990, 2),  # 1% target
                'confidence': 'MEDIUM',
                'contract': contract,
                'strike': strike,
                'option_type': 'PUT'
            }

        return None

    def send_trade_alert(self, trade):
        """Send trade setup to Discord"""
        asset = trade['asset']
        webhook = ASSETS[asset]['webhook']

        # Color based on trade type
        color = 3066993 if trade['type'] == 'LONG' else 15158332  # Green for LONG, Red for SHORT
        emoji = '🟢' if trade['type'] == 'LONG' else '🔴'

        # Confidence emoji
        conf_emoji = '🔥' if trade['confidence'] == 'HIGH' else '⚡'

        title = f"{emoji} {conf_emoji} {asset} {trade['type']} SETUP - {trade['confidence']} CONFIDENCE"

        payload = {
            'username': f'{emoji} Trade Scanner',
            'embeds': [{
                'title': title,
                'description': f"**{trade['reason']}**\n\n📄 **CONTRACT:** `{trade['contract']}`",
                'color': color,
                'timestamp': datetime.utcnow().isoformat(),
                'fields': [
                    {
                        'name': '📍 Entry (Underlying)',
                        'value': f"${trade['entry']:,.2f}",
                        'inline': True
                    },
                    {
                        'name': '📄 Option Strike',
                        'value': f"${trade['strike']:,} {trade['option_type']}",
                        'inline': True
                    },
                    {
                        'name': '🛑 Stop Loss',
                        'value': f"${trade['stop']:,.2f}",
                        'inline': True
                    },
                    {
                        'name': '🎯 Target 1',
                        'value': f"${trade['target1']:,.2f}",
                        'inline': True
                    },
                    {
                        'name': '🎯 Target 2',
                        'value': f"${trade['target2']:,.2f}",
                        'inline': True
                    },
                    {
                        'name': '🔥 Confidence',
                        'value': trade['confidence'],
                        'inline': True
                    }
                ],
                'footer': {
                    'text': f'Multi-Asset Trade Scanner | {trade["asset"]} {trade["type"]}'
                }
            }]
        }

        try:
            response = requests.post(webhook, json=payload, timeout=10)
            if response.status_code == 204:
                print(f"✅ Trade alert sent: {asset} {trade['type']} @ ${trade['entry']}")
            else:
                print(f"❌ Trade alert failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Error sending trade alert: {e}")

    def scan_markets(self):
        """Scan all markets for trade opportunities"""
        print(f"\n{'='*80}")
        print(f"🔍 SCANNING MARKETS FOR TRADE OPPORTUNITIES - {datetime.now().strftime('%H:%M:%S')}")
        print(f"{'='*80}")

        # Update previous prices
        self.previous_prices = self.prices.copy()

        # Get current prices
        for asset_name in ASSETS.keys():
            price = self.get_price(asset_name)
            if price:
                self.prices[asset_name] = price

        # Analyze each asset
        trades_found = []
        for asset_name in ASSETS.keys():
            if asset_name in self.prices:
                price = self.prices[asset_name]
                momentum = self.calculate_momentum(asset_name)

                # Generate trade setup
                trade = self.generate_trade_setup(asset_name, price, momentum)

                if trade:
                    trades_found.append(trade)
                    print(f"\n🎯 TRADE OPPORTUNITY FOUND:")
                    print(f"   Asset: {trade['asset']} | Type: {trade['type']} | Confidence: {trade['confidence']}")
                    print(f"   Entry: ${trade['entry']:,.2f} | Stop: ${trade['stop']:,.2f}")
                    print(f"   Target1: ${trade['target1']:,.2f} | Target2: ${trade['target2']:,.2f}")
                    print(f"   Reason: {trade['reason']}")

                    # Send Discord alert
                    self.send_trade_alert(trade)
                else:
                    print(f"  {asset_name}: ${price:,.2f} | Momentum: {momentum} | No setup")

        if not trades_found:
            print("\n  ✓ No high-probability trade setups at current levels")

        print(f"{'='*80}\n")

    def start(self):
        """Start trade scanner"""
        print("="*80)
        print("🚀 MULTI-ASSET TRADE SCANNER STARTED")
        print("="*80)
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S ET')}")
        print(f"Assets: SPX, NDX, QQQ, SPY, IWM")
        print(f"Scan Interval: 30 seconds")
        print(f"Discord: Trade alerts enabled")
        print("="*80)

        self.running = True
        iteration = 0

        while self.running:
            iteration += 1

            # Scan markets for opportunities
            self.scan_markets()

            # Wait 30 seconds before next scan
            time.sleep(30)

    def stop(self):
        """Stop trade scanner"""
        self.running = False
        print("\n" + "="*80)
        print("🛑 TRADE SCANNER STOPPED")
        print("="*80)

if __name__ == "__main__":
    scanner = TradeScanner()

    try:
        scanner.start()
    except KeyboardInterrupt:
        print("\n\nReceived interrupt signal...")
        scanner.stop()
