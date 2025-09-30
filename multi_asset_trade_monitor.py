#!/usr/bin/env python3
"""
MULTI-ASSET AUTOMATED TRADE MONITOR
SPX + SPY + QQQ + IWM + NDX monitoring with Polygon real-time pricing
Auto-generates trade setups and sends Discord alerts
"""

import os
import sys
import time
import json
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dual_api_system import DualAPISystem

class MultiAssetTradeMonitor:
    def __init__(self):
        self.dual_api = DualAPISystem()
        self.last_alerts = {}  # Track last alert per asset to avoid spam

        # Define key levels for each asset
        self.levels = {
            'SPX': {
                'resistance': (6680, 6694),
                'support': (6620, 6626),
                'gamma_flip': (6607, 6610)
            },
            'SPY': {
                'resistance': (668, 669.4),
                'support': (662, 662.6),
                'gamma_flip': (660.7, 661)
            },
            'QQQ': {
                'resistance': (605, 610),
                'support': (590, 595),
                'gamma_flip': (585, 587)
            },
            'IWM': {
                'resistance': (245, 248),
                'support': (238, 240),
                'gamma_flip': (235, 237)
            },
            'NDX': {
                'resistance': (20600, 20700),
                'support': (20400, 20500),
                'gamma_flip': (20200, 20300)
            }
        }

    def get_asset_data(self, symbol):
        """Get current price for asset"""

        if symbol == 'SPX':
            result = self.dual_api.get_spx_data_with_failover()
            if result['success']:
                return result['spx_price']
        elif symbol == 'NDX':
            # NDX via direct I:NDX endpoint (ACCURATE)
            result = self.dual_api.get_ndx_data_with_failover()
            if result['success']:
                return result['ndx_price']
        else:
            result = self.dual_api.get_stock_quote_with_failover(symbol)
            if result['success']:
                return result['price']

        return None

    def check_asset_setups(self, symbol, price):
        """Check for trade setups on specific asset"""

        if symbol not in self.levels:
            return []

        levels = self.levels[symbol]
        setups = []

        # Resistance setup
        res_lower, res_upper = levels['resistance']
        if price >= res_lower - (res_lower * 0.015) and price <= res_upper + (res_upper * 0.008):
            setups.append({
                'asset': symbol,
                'type': 'RESISTANCE_REJECTION',
                'confidence': 75,
                'active': price >= res_lower,
                'direction': 'PUT',
                'current_price': price,
                'entry_zone': f'{res_lower:.2f}-{res_upper:.2f}',
                'target': levels['support'][1],
                'stop': res_upper
            })

        # Support setup
        sup_lower, sup_upper = levels['support']
        if price <= sup_upper + (sup_upper * 0.015) and price >= sup_lower - (sup_lower * 0.008):
            setups.append({
                'asset': symbol,
                'type': 'SUPPORT_BOUNCE',
                'confidence': 75,
                'active': price <= sup_upper,
                'direction': 'CALL',
                'current_price': price,
                'entry_zone': f'{sup_lower:.2f}-{sup_upper:.2f}',
                'target': levels['resistance'][0],
                'stop': sup_lower
            })

        # Gamma flip setup
        gamma_lower, gamma_upper = levels['gamma_flip']
        if price <= gamma_upper + (gamma_upper * 0.045):
            setups.append({
                'asset': symbol,
                'type': 'GAMMA_FLIP_REVERSAL',
                'confidence': 85,
                'active': price <= gamma_upper,
                'direction': 'CALL',
                'current_price': price,
                'entry_zone': f'{gamma_lower:.2f}-{gamma_upper:.2f}',
                'target': levels['resistance'][0],
                'stop': gamma_lower
            })

        return setups

    def format_alert(self, setup):
        """Format setup for Discord alert"""

        status = "🔥 ACTIVE" if setup['active'] else "⚪ STANDBY"
        emoji = "🚨" if setup['active'] else "📊"

        return f"""
{emoji} {setup['asset']} - {setup['type']}
{'='*60}

Status: {status}
Confidence: {setup['confidence']}%

💰 CURRENT PRICE: ${setup['current_price']:.2f}
📍 Entry Zone: {setup['entry_zone']}

💡 TRADE:
   Direction: {setup['direction']}
   Target: ${setup['target']:.2f}
   Stop: ${setup['stop']:.2f}

⏰ {datetime.now().strftime('%I:%M:%S %p ET')}
{'='*60}
"""

    def send_discord_alert(self, setup):
        """Send alert to Discord with retry logic"""

        import subprocess

        status = "ACTIVE" if setup['active'] else "STANDBY"
        title = f"{setup['asset']} {setup['type']} - {status}"

        message = f"""Confidence: {setup['confidence']}%
Price: ${setup['current_price']:.2f}
Entry Zone: {setup['entry_zone']}

Direction: {setup['direction']}
Target: ${setup['target']:.2f}
Stop: ${setup['stop']:.2f}

{datetime.now().strftime('%I:%M:%S %p ET')}"""

        # Retry logic with exponential backoff
        max_retries = 3
        retry_delay = 2  # seconds

        for attempt in range(max_retries):
            try:
                result = subprocess.run([
                    'python', 'send_discord.py', title, message
                ], timeout=15, capture_output=True, text=True,
                   cwd=os.path.dirname(os.path.abspath(__file__)))

                # Check if subprocess succeeded
                if result.returncode == 0:
                    return True
                else:
                    print(f"Discord attempt {attempt + 1} failed: {result.stderr}")
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay * (attempt + 1))  # Exponential backoff

            except subprocess.TimeoutExpired:
                print(f"Discord timeout on attempt {attempt + 1}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay * (attempt + 1))

            except Exception as e:
                print(f"Discord error on attempt {attempt + 1}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay * (attempt + 1))

        print(f"❌ Discord alert failed after {max_retries} attempts")
        return False

    def monitor(self):
        """Main monitoring loop with market hours check"""

        # Check market hours
        current_hour = datetime.now().hour
        if current_hour < 9 or current_hour >= 16:
            print('='*70)
            print('⚠️  MARKET CLOSED')
            print('Trading hours: 9:30 AM - 4:00 PM ET (6:30 AM - 1:00 PM PT)')
            print('Current time:', datetime.now().strftime('%I:%M %p ET'))
            print('='*70)
            print('\nMonitor stopped - market is closed')
            return

        print('='*70)
        print('MULTI-ASSET AUTOMATED TRADE MONITOR')
        print('SPX | SPY | QQQ | IWM | NDX')
        print('Polygon Real-Time Pricing')
        print('='*70)
        print()
        print('Monitoring all assets for trade setups...')
        print('Updates every 15 seconds (cascaded to avoid rate limits)')
        print('Press Ctrl+C to stop')
        print()

        cycle = 0

        try:
            while True:
                # Check if market closed during monitoring
                current_hour = datetime.now().hour
                if current_hour < 9 or current_hour >= 16:
                    print('\n⚠️  Market closed - stopping monitor')
                    break

                cycle += 1
                timestamp = datetime.now().strftime('%I:%M:%S')

                # Get prices for all assets with cascading (prevent simultaneous API calls)
                prices = {}
                for i, symbol in enumerate(['SPX', 'SPY', 'QQQ', 'IWM', 'NDX']):
                    # Add 2-second delay between each asset to cascade API calls
                    if i > 0:
                        time.sleep(2)

                    price = self.get_asset_data(symbol)
                    if price:
                        prices[symbol] = price

                # Print status update
                status_line = f"[{timestamp}] "
                for symbol, price in prices.items():
                    status_line += f"{symbol}: ${price:.2f} | "
                print(status_line.rstrip(' | '))

                # Check each asset for setups
                total_active = 0
                for symbol, price in prices.items():
                    setups = self.check_asset_setups(symbol, price)

                    for setup in setups:
                        if setup['active']:
                            total_active += 1

                            # Create unique key for this setup
                            setup_key = f"{symbol}_{setup['type']}"

                            # Only alert if not recently alerted
                            if setup_key != self.last_alerts.get(symbol):
                                print(self.format_alert(setup))

                                # Send to Discord
                                if self.send_discord_alert(setup):
                                    print(f"✅ {symbol} alert sent to Discord")

                                # Update last alert
                                self.last_alerts[symbol] = setup_key

                # Reset alerts if no active setups
                for symbol in prices.keys():
                    has_active = False
                    setups = self.check_asset_setups(symbol, prices[symbol])
                    for setup in setups:
                        if setup['active']:
                            has_active = True
                            break

                    if not has_active and symbol in self.last_alerts:
                        del self.last_alerts[symbol]

                if total_active > 0:
                    print(f"📊 Active Setups: {total_active}")

                # Wait 15 seconds
                time.sleep(15)

        except KeyboardInterrupt:
            print('\n\n✅ Monitor stopped')
            print(f'Total cycles: {cycle}')
            print(f'Assets monitored: SPX, SPY, QQQ, IWM, NDX')

if __name__ == "__main__":
    monitor = MultiAssetTradeMonitor()
    monitor.monitor()
