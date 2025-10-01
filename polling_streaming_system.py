"""
Polling-Based SPX Streaming System
Uses synchronous requests (working) instead of async aiohttp (failing)
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

class PollingStreamingSystem:
    def __init__(self):
        self.running = False
        self.last_price = None
        self.last_alert_time = {}
        self.alert_cooldown = 60  # 60 seconds between similar alerts

    def get_spx_price(self):
        """Get real-time SPX price using Polygon direct SPX indices endpoint"""
        try:
            # Primary Polygon API key - Direct SPX index data
            url = f'https://api.polygon.io/v3/snapshot/indices?ticker=I%3ASPX&apikey={POLYGON_PRIMARY}'
            response = requests.get(url, timeout=5, verify=True)

            if response.status_code == 200:
                data = response.json()
                if 'results' in data and len(data['results']) > 0:
                    spx_value = data['results'][0]['value']
                    return spx_value

            # Try backup key if primary fails
            url = f'https://api.polygon.io/v3/snapshot/indices?ticker=I%3ASPX&apikey={POLYGON_BACKUP}'
            response = requests.get(url, timeout=5, verify=True)

            if response.status_code == 200:
                data = response.json()
                if 'results' in data and len(data['results']) > 0:
                    spx_value = data['results'][0]['value']
                    return spx_value

            return None

        except Exception as e:
            print(f"Error getting SPX price: {e}")
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

    def send_discord_alert(self, alert):
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

        payload = {
            'username': f'{emoji} SPX Level Alert',
            'embeds': [{
                'title': title,
                'description': description,
                'color': color,
                'timestamp': datetime.utcnow().isoformat(),
                'fields': [
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
                ],
                'footer': {
                    'text': 'SPX Polling Streaming System'
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
        """Start polling system"""
        print("=" * 70)
        print("🚀 POLLING STREAMING SYSTEM STARTED")
        print("=" * 70)
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S ET')}")
        print(f"Refresh Interval: 10 seconds")
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

                # Check for level proximity
                alerts = self.check_level_proximity(spx_price)

                if alerts:
                    print(f"  🎯 Found {len(alerts)} level(s) nearby:")
                    for alert in alerts:
                        print(f"     {alert['type']}: {alert['level']} (distance: {alert['distance']} pts)")
                        self.send_discord_alert(alert)
                else:
                    print(f"  ✓ No key levels nearby (closest level check)")

                self.last_price = spx_price
            else:
                print(f"[{current_time}] ❌ Failed to get price")

            # Wait 10 seconds before next poll
            time.sleep(10)

    def stop(self):
        """Stop polling system"""
        self.running = False
        print("\n" + "=" * 70)
        print("🛑 POLLING STREAMING SYSTEM STOPPED")
        print("=" * 70)

if __name__ == "__main__":
    system = PollingStreamingSystem()

    try:
        system.start()
    except KeyboardInterrupt:
        print("\n\nReceived interrupt signal...")
        system.stop()
