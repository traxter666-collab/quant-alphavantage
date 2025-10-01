"""
AlphaVantage Real-Time SPX Streaming System
Uses AlphaVantage Premium API with real-time entitlement for SPX price tracking
"""

import requests
import json
import time
from datetime import datetime
import threading

# API Keys
ALPHA_VANTAGE_KEY = "ZFL38ZY98GSN7E1S"

# Discord Webhooks
WEBHOOK_TESTING = "https://discord.com/api/webhooks/1422928703972970516/59EBn9XvN6VautbSfjE8p_pFDNX4qIrU6ephGS--UvSiD7nSahftbhQDSW66fQwfXajp"
WEBHOOK_ALERTS = "https://discord.com/api/webhooks/1422763517974417478/0AAxHmLLjC389OXRi5KY_P2puAY8BhGAgEYTXSxj7TiKlqK_WH1PXPW6d_osA219ZFPu"
WEBHOOK_SPX = "https://discord.com/api/webhooks/1422930069290225694/PKiahdQzpgIZuceHRU254dgpmSEOcgho0-o-DpkQXeCUsQ5AYH1mv3OmJ_gG-1eB7FU-"
WEBHOOK_SPX_PREMIUM = "https://discord.com/api/webhooks/1422931192205807677/fddndOqTq-nS1e9Mtevrh7EhR-6ikKNoLWvYvSjUdydCwor9TkwYvJrukPX6TFo-T64a"

# Quant Levels for Today
QUANT_LEVELS = {
    'resistance': [6742, 6734, 6730, 6700, 6690],
    'pivot': 6659,
    'support': [6647, 6642, 6633, 6621, 6620, 6600, 6595],
    'high_probability_reversal': [6734, 6730, 6633],  # High likelihood reversal zones
    'gamma_flip': [6621, 6620],  # Gamma flip zone
    'ema_9d': [6647, 6642],  # 9-day EMA
    'ema_21d': [6600, 6595]  # 21-day EMA strong support
}

class AlphaVantageStreamingSystem:
    def __init__(self):
        self.running = False
        self.last_price = None
        self.last_alert_time = {}
        self.alert_cooldown = 60  # 60 seconds between similar alerts

    def get_spx_price(self):
        """Get real-time SPX price using AlphaVantage SPXW options with put-call parity"""
        try:
            # AlphaVantage real-time SPXW options
            url = f"https://www.alphavantage.co/query?function=REALTIME_OPTIONS&symbol=SPXW&entitlement=realtime&apikey={ALPHA_VANTAGE_KEY}"
            response = requests.get(url, timeout=15)

            if response.status_code == 200:
                data = response.json()

                # Parse options data for put-call parity
                if 'data' in data and len(data['data']) > 0:
                    # Get underlying price estimate first
                    underlying_est = None
                    first_option = data['data'][0]
                    if 'underlying_price' in first_option:
                        underlying_est = float(first_option.get('underlying_price', 0))

                    # Find today's 0DTE options with both call and put
                    strikes = {}
                    for option in data['data']:
                        strike_val = float(option.get('strike', 0))
                        exp = option.get('expiration', '')
                        opt_type = option.get('type', '')

                        # Focus on 0DTE (today's expiration: 2025-10-01)
                        if '2025-10-01' in exp:
                            if strike_val not in strikes:
                                strikes[strike_val] = {'call': None, 'put': None}

                            if opt_type == 'call':
                                strikes[strike_val]['call'] = option
                            elif opt_type == 'put':
                                strikes[strike_val]['put'] = option

                    # Calculate SPX using first available strike with both call/put
                    for strike, options in sorted(strikes.items()):
                        if options['call'] and options['put']:
                            call_mark = float(options['call'].get('mark', 0))
                            put_mark = float(options['put'].get('mark', 0))

                            if call_mark > 0:  # Ensure valid data
                                # SPX = (Call_Mark - Put_Mark) + Strike
                                spx_price = (call_mark - put_mark) + strike
                                return spx_price

                    # Fallback: Use underlying_price if available
                    if underlying_est and underlying_est > 0:
                        return underlying_est

            return None

        except Exception as e:
            print(f"Error getting SPX price from AlphaVantage SPXW options: {e}")
            return None

    def get_spy_intraday_data(self):
        """Get real-time SPY intraday data for additional context"""
        try:
            url = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol=SPY&interval=1min&entitlement=realtime&apikey={ALPHA_VANTAGE_KEY}"
            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                data = response.json()
                if 'Time Series (1min)' in data:
                    # Get latest bar
                    time_series = data['Time Series (1min)']
                    latest_time = list(time_series.keys())[0]
                    latest_bar = time_series[latest_time]

                    return {
                        'timestamp': latest_time,
                        'open': float(latest_bar['1. open']),
                        'high': float(latest_bar['2. high']),
                        'low': float(latest_bar['3. low']),
                        'close': float(latest_bar['4. close']),
                        'volume': int(latest_bar['5. volume'])
                    }

            return None

        except Exception as e:
            print(f"Error getting intraday data: {e}")
            return None

    def check_level_proximity(self, price):
        """Check if price is near key quant levels"""
        alerts = []

        # Check resistance levels
        for level in QUANT_LEVELS['resistance']:
            distance = abs(price - level)
            if distance <= 5:  # Within 5 points
                alerts.append({
                    'type': 'RESISTANCE',
                    'level': level,
                    'distance': round(distance, 2),
                    'price': round(price, 2)
                })

        # Check support levels
        for level in QUANT_LEVELS['support']:
            distance = abs(price - level)
            if distance <= 5:
                alerts.append({
                    'type': 'SUPPORT',
                    'level': level,
                    'distance': round(distance, 2),
                    'price': round(price, 2)
                })

        # Check pivot
        if abs(price - QUANT_LEVELS['pivot']) <= 3:
            alerts.append({
                'type': 'PIVOT',
                'level': QUANT_LEVELS['pivot'],
                'distance': round(abs(price - QUANT_LEVELS['pivot']), 2),
                'price': round(price, 2)
            })

        return alerts

    def send_discord_alert(self, alert, intraday_data=None):
        """Send alert to appropriate Discord channel"""
        alert_type = alert['type']
        level = alert['level']
        price = alert['price']
        distance = alert['distance']

        # Check cooldown
        cooldown_key = f"{alert_type}_{level}"
        current_time = time.time()

        if cooldown_key in self.last_alert_time:
            if current_time - self.last_alert_time[cooldown_key] < self.alert_cooldown:
                return  # Skip due to cooldown

        self.last_alert_time[cooldown_key] = current_time

        # Determine webhook and color
        if alert_type == 'RESISTANCE':
            webhook = WEBHOOK_SPX
            color = 15158332  # Red
            emoji = '🔴'
            title = f'🔴 SPX AT RESISTANCE - {level}'
            description = f'**SPX Price: ${price}**\nDistance: {distance} points from resistance {level}'
        elif alert_type == 'SUPPORT':
            webhook = WEBHOOK_SPX
            color = 3066993  # Green
            emoji = '🟢'
            title = f'🟢 SPX AT SUPPORT - {level}'
            description = f'**SPX Price: ${price}**\nDistance: {distance} points from support {level}'
        else:  # PIVOT
            webhook = WEBHOOK_SPX
            color = 15844367  # Gold
            emoji = '⚖️'
            title = f'⚖️ SPX AT PIVOT - {level}'
            description = f'**SPX Price: ${price}**\nDistance: {distance} points from pivot'

        # Add intraday data if available
        fields = [
            {
                'name': '📊 Current Price',
                'value': f'${price}',
                'inline': True
            },
            {
                'name': '🎯 Key Level',
                'value': f'${level}',
                'inline': True
            },
            {
                'name': '📏 Distance',
                'value': f'{distance} points',
                'inline': True
            },
            {
                'name': '⏰ Time',
                'value': datetime.now().strftime('%H:%M:%S ET'),
                'inline': True
            }
        ]

        if intraday_data:
            fields.append({
                'name': '📈 Volume',
                'value': f'{intraday_data["volume"]:,}',
                'inline': True
            })

        payload = {
            'username': f'{emoji} SPX Level Alert',
            'embeds': [{
                'title': title,
                'description': description,
                'color': color,
                'timestamp': datetime.utcnow().isoformat(),
                'fields': fields,
                'footer': {
                    'text': 'AlphaVantage Real-Time Streaming System'
                }
            }]
        }

        try:
            response = requests.post(webhook, json=payload, timeout=10)
            if response.status_code == 204:
                print(f"✅ Alert sent: {alert_type} {level} (SPX: ${price})")
            else:
                print(f"❌ Alert failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Error sending alert: {e}")

    def start(self):
        """Start streaming system"""
        print("=" * 70)
        print("🚀 ALPHAVANTAGE REAL-TIME STREAMING SYSTEM STARTED")
        print("=" * 70)
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S ET')}")
        print(f"Refresh Interval: 12 seconds (API rate limit)")
        print(f"Data Source: AlphaVantage Premium with real-time entitlement")
        print(f"Discord Channels: SPX Trades (standard + premium)")
        print(f"Quant Levels Loaded: {len(QUANT_LEVELS['resistance']) + len(QUANT_LEVELS['support']) + 1} levels")
        print("=" * 70)

        self.running = True
        iteration = 0

        while self.running:
            iteration += 1
            current_time = datetime.now().strftime('%H:%M:%S')

            # Get current price
            spx_price = self.get_spx_price()

            if spx_price:
                print(f"\n[{current_time}] Iteration {iteration} - SPX: ${spx_price:.2f}")

                # Get intraday data for context (every 5th iteration to conserve API calls)
                intraday_data = None
                if iteration % 5 == 0:
                    intraday_data = self.get_spy_intraday_data()
                    if intraday_data:
                        print(f"  📊 Volume: {intraday_data['volume']:,} | Timestamp: {intraday_data['timestamp']}")

                # Check for level proximity
                alerts = self.check_level_proximity(spx_price)

                if alerts:
                    print(f"  🎯 Found {len(alerts)} level(s) nearby:")
                    for alert in alerts:
                        print(f"     {alert['type']}: {alert['level']} (distance: {alert['distance']} pts)")
                        self.send_discord_alert(alert, intraday_data)
                else:
                    print(f"  ✓ No key levels nearby (closest level check)")

                self.last_price = spx_price
            else:
                print(f"[{current_time}] ❌ Failed to get price from AlphaVantage")

            # Wait 12 seconds before next poll (AlphaVantage rate limit: 5 calls/min)
            time.sleep(12)

    def stop(self):
        """Stop streaming system"""
        self.running = False
        print("\n" + "=" * 70)
        print("🛑 ALPHAVANTAGE STREAMING SYSTEM STOPPED")
        print("=" * 70)

if __name__ == "__main__":
    system = AlphaVantageStreamingSystem()

    try:
        system.start()
    except KeyboardInterrupt:
        print("\n\nReceived interrupt signal...")
        system.stop()
