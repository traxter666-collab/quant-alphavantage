"""
NDX (NASDAQ-100) Real-Time Enhanced Streaming System
Complete trading intelligence with momentum, trade setups, confidence scoring,
entry/exit tracking, and P&L monitoring
"""

import requests
import json
import time
from datetime import datetime
import threading

# API Keys
POLYGON_PRIMARY = "_u0zA0CH5ZspOHecb2G8uBxd2DUo4r9D"
POLYGON_BACKUP = "CiDDZJqQS88A0QhaoJbn0rLqaenps6Pq"

# Discord Webhook - NDX Only
WEBHOOK_NDX = "https://discord.com/api/webhooks/1422964068464988292/U6sdcQEyh9biXh2UTkZ2P9qNTIvU-wngGwYxbo3wxUmCDxNJ6G"

# NDX Quant Levels for Today (scaled from SPX levels)
# NDX/SPX ratio ~ 3.69 (24,670 / 6,685)
NDX_LEVELS = {
    'resistance': [24850, 24800, 24750, 24700, 24650],
    'pivot': 24550,
    'support': [24500, 24450, 24400, 24350, 24300, 24250, 24200],
    'high_probability_reversal': [24800, 24750, 24400],  # High likelihood reversal zones
    'key_tech_levels': [24700, 24500, 24300]  # Major tech sector levels
}

class NDXStreamingSystem:
    def __init__(self):
        self.running = False
        self.last_price = None
        self.previous_price = None
        self.last_alert_time = {}
        self.alert_cooldown = 60  # 60 seconds between similar alerts
        self.price_history = []  # Track price history for momentum
        self.active_trades = {}  # Track active positions
        self.last_trade_alert = {}  # Cooldown for trade alerts

    def get_ndx_price(self):
        """Get real-time NDX price using Polygon direct NDX indices endpoint"""
        try:
            # Primary Polygon API key - Direct NDX index data
            url = f'https://api.polygon.io/v3/snapshot/indices?ticker=I%3ANDX&apikey={POLYGON_PRIMARY}'
            response = requests.get(url, timeout=5, verify=True)

            if response.status_code == 200:
                data = response.json()
                if 'results' in data and len(data['results']) > 0:
                    ndx_value = data['results'][0]['value']
                    return ndx_value

            # Try backup key if primary fails
            url = f'https://api.polygon.io/v3/snapshot/indices?ticker=I%3ANDX&apikey={POLYGON_BACKUP}'
            response = requests.get(url, timeout=5, verify=True)

            if response.status_code == 200:
                data = response.json()
                if 'results' in data and len(data['results']) > 0:
                    ndx_value = data['results'][0]['value']
                    return ndx_value

            return None

        except Exception as e:
            print(f"Error getting NDX price: {e}")
            return None

    def calculate_momentum(self, current_price):
        """Calculate momentum based on price history"""
        if len(self.price_history) < 5:
            return 'NEUTRAL', 0

        # Get recent prices
        recent_prices = self.price_history[-10:]

        # Calculate price change percentage
        price_change_pct = ((current_price - recent_prices[0]) / recent_prices[0]) * 100

        # Calculate trend (positive count vs negative count)
        positive_moves = sum(1 for i in range(1, len(recent_prices)) if recent_prices[i] > recent_prices[i-1])
        total_moves = len(recent_prices) - 1

        trend_strength = (positive_moves / total_moves) * 100 if total_moves > 0 else 50

        # Determine momentum
        if price_change_pct > 0.15 and trend_strength > 60:
            return 'BULLISH', min(int(price_change_pct * 100), 100)
        elif price_change_pct < -0.15 and trend_strength < 40:
            return 'BEARISH', min(int(abs(price_change_pct) * 100), 100)
        else:
            return 'NEUTRAL', 50

    def analyze_king_nodes(self, current_price):
        """Detect king nodes and call/put walls"""
        walls = []

        # Analyze resistance levels as call walls
        for level in NDX_LEVELS['resistance']:
            if level > current_price:
                distance = level - current_price
                strength = max(0, 100 - (distance / current_price * 1000))
                if strength > 30:  # Significant wall
                    walls.append({
                        'type': 'CALL_WALL',
                        'level': level,
                        'strength': round(strength, 1),
                        'distance': round(distance, 2)
                    })

        # Analyze support levels as put walls
        for level in NDX_LEVELS['support']:
            if level < current_price:
                distance = current_price - level
                strength = max(0, 100 - (distance / current_price * 1000))
                if strength > 30:  # Significant wall
                    walls.append({
                        'type': 'PUT_WALL',
                        'level': level,
                        'strength': round(strength, 1),
                        'distance': round(distance, 2)
                    })

        # Find king node (highest strength)
        if walls:
            king_node = max(walls, key=lambda x: x['strength'])
            king_node['is_king_node'] = True
            return king_node, walls

        return None, walls

    def calculate_confidence_score(self, current_price, momentum, momentum_strength, king_node, walls):
        """Calculate multi-factor confidence score (0-100)"""
        score = 0

        # Momentum component (30 points max)
        if momentum == 'BULLISH':
            score += min(momentum_strength * 0.3, 30)
        elif momentum == 'BEARISH':
            score += min(momentum_strength * 0.3, 30)
        else:
            score += 10  # Neutral gets base points

        # Level proximity (25 points max)
        nearest_support = max([s for s in NDX_LEVELS['support'] if s < current_price], default=None)
        nearest_resistance = min([r for r in NDX_LEVELS['resistance'] if r > current_price], default=None)

        if nearest_support:
            support_distance = current_price - nearest_support
            if support_distance <= 20:
                score += 25 * (1 - support_distance / 20)

        if nearest_resistance:
            resistance_distance = nearest_resistance - current_price
            if resistance_distance <= 20:
                score += 25 * (1 - resistance_distance / 20)

        # King node / wall strength (20 points max)
        if king_node:
            score += min(king_node['strength'] * 0.2, 20)

        # Reversal zone proximity (15 points max)
        for level in NDX_LEVELS['high_probability_reversal']:
            distance = abs(current_price - level)
            if distance <= 15:
                score += 15 * (1 - distance / 15)
                break

        # Trend consistency (10 points max)
        if len(self.price_history) >= 5:
            recent = self.price_history[-5:]
            if all(recent[i] < recent[i+1] for i in range(len(recent)-1)):
                score += 10  # Strong uptrend
            elif all(recent[i] > recent[i+1] for i in range(len(recent)-1)):
                score += 10  # Strong downtrend
            else:
                score += 5  # Mixed

        return min(score, 100)

    def generate_trade_setup(self, current_price, momentum, confidence_score, king_node):
        """Generate NDXP trade setup with entry/exit levels"""
        trade_key = f"NDX_{int(current_price)}"
        current_time = time.time()

        # Check cooldown (5 minutes)
        if trade_key in self.last_trade_alert:
            if current_time - self.last_trade_alert[trade_key] < 300:
                return None

        # Only generate trades with 85%+ confidence
        if confidence_score < 85:
            return None

        # Determine trade direction
        nearest_support = max([s for s in NDX_LEVELS['support'] if s < current_price], default=current_price - 100)
        nearest_resistance = min([r for r in NDX_LEVELS['resistance'] if r > current_price], default=current_price + 100)

        distance_to_support = current_price - nearest_support
        distance_to_resistance = nearest_resistance - current_price

        trade = None

        # LONG setup: Near support with bullish momentum
        if distance_to_support <= 20 and momentum in ['BULLISH', 'NEUTRAL'] and confidence_score >= 85:
            strike = int((current_price + 10) / 5) * 5  # Slightly OTM call
            target1 = round(current_price + (distance_to_resistance * 0.5), 2)
            target2 = round(nearest_resistance - 10, 2)
            stop = round(nearest_support - 10, 2)

            trade = {
                'type': 'LONG',
                'asset': 'NDX',
                'contract': f'NDXP{datetime.now().strftime("%Y%m%d")}C{strike}',
                'strike': strike,
                'option_type': 'CALL',
                'entry': round(current_price, 2),
                'stop': stop,
                'target1': target1,
                'target2': target2,
                'confidence': confidence_score,
                'reason': f'Near support {nearest_support} with {momentum} momentum (confidence: {confidence_score:.1f}%)'
            }

        # SHORT setup: Near resistance with bearish momentum
        elif distance_to_resistance <= 20 and momentum in ['BEARISH', 'NEUTRAL'] and confidence_score >= 85:
            strike = int((current_price - 10) / 5) * 5  # Slightly OTM put
            target1 = round(current_price - (distance_to_support * 0.5), 2)
            target2 = round(nearest_support + 10, 2)
            stop = round(nearest_resistance + 10, 2)

            trade = {
                'type': 'SHORT',
                'asset': 'NDX',
                'contract': f'NDXP{datetime.now().strftime("%Y%m%d")}P{strike}',
                'strike': strike,
                'option_type': 'PUT',
                'entry': round(current_price, 2),
                'stop': stop,
                'target1': target1,
                'target2': target2,
                'confidence': confidence_score,
                'reason': f'Near resistance {nearest_resistance} with {momentum} momentum (confidence: {confidence_score:.1f}%)'
            }

        if trade:
            self.last_trade_alert[trade_key] = current_time
            # Track trade
            trade_id = f"{trade['asset']}_{trade['contract']}_{int(current_time)}"
            self.active_trades[trade_id] = {
                **trade,
                'entry_time': datetime.now().isoformat(),
                'status': 'ACTIVE',
                'pnl': 0
            }

        return trade

    def send_trade_alert(self, trade):
        """Send comprehensive trade alert to Discord"""
        color = 3066993 if trade['type'] == 'LONG' else 15158332  # Green for LONG, Red for SHORT
        emoji = '🟢' if trade['type'] == 'LONG' else '🔴'

        confidence_emoji = '🔥🔥🔥' if trade['confidence'] >= 95 else '🔥🔥' if trade['confidence'] >= 90 else '🔥'

        title = f"{emoji} {confidence_emoji} NDX {trade['type']} SETUP - {trade['confidence']:.1f}% CONFIDENCE"

        payload = {
            'username': f'{emoji} NDX Elite Trader',
            'embeds': [{
                'title': title,
                'description': f"**{trade['reason']}**\n\nCONTRACT: `{trade['contract']}`",
                'color': color,
                'timestamp': datetime.utcnow().isoformat(),
                'fields': [
                    {
                        'name': 'Entry (Underlying)',
                        'value': f"${trade['entry']:,.2f}",
                        'inline': True
                    },
                    {
                        'name': 'Option Strike',
                        'value': f"${trade['strike']:,} {trade['option_type']}",
                        'inline': True
                    },
                    {
                        'name': 'Stop Loss',
                        'value': f"${trade['stop']:,.2f}",
                        'inline': True
                    },
                    {
                        'name': 'Target 1',
                        'value': f"${trade['target1']:,.2f}",
                        'inline': True
                    },
                    {
                        'name': 'Target 2',
                        'value': f"${trade['target2']:,.2f}",
                        'inline': True
                    },
                    {
                        'name': 'Confidence Score',
                        'value': f"{trade['confidence']:.1f}%",
                        'inline': True
                    }
                ],
                'footer': {
                    'text': f'NDX Enhanced Trading System | {trade["asset"]} {trade["type"]}'
                }
            }]
        }

        try:
            response = requests.post(WEBHOOK_NDX, json=payload, timeout=10)
            if response.status_code == 204:
                print(f"✅ Trade alert sent: {trade['asset']} {trade['type']} @ ${trade['entry']} (Confidence: {trade['confidence']:.1f}%)")
            else:
                print(f"❌ Trade alert failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Error sending trade alert: {e}")

    def check_level_proximity(self, price):
        """Check if price is near key NDX quant levels"""
        alerts = []

        # Check resistance levels
        for level in NDX_LEVELS['resistance']:
            distance = abs(price - level)
            if distance <= 20:  # Within 20 points for NDX
                alerts.append({
                    'type': 'RESISTANCE',
                    'level': level,
                    'distance': round(distance, 2),
                    'price': round(price, 2)
                })

        # Check support levels
        for level in NDX_LEVELS['support']:
            distance = abs(price - level)
            if distance <= 20:
                alerts.append({
                    'type': 'SUPPORT',
                    'level': level,
                    'distance': round(distance, 2),
                    'price': round(price, 2)
                })

        # Check pivot
        if abs(price - NDX_LEVELS['pivot']) <= 15:
            alerts.append({
                'type': 'PIVOT',
                'level': NDX_LEVELS['pivot'],
                'distance': round(abs(price - NDX_LEVELS['pivot']), 2),
                'price': round(price, 2)
            })

        # Check high probability reversal zones
        for level in NDX_LEVELS['high_probability_reversal']:
            distance = abs(price - level)
            if distance <= 15:
                alerts.append({
                    'type': 'HIGH_PROB_REVERSAL',
                    'level': level,
                    'distance': round(distance, 2),
                    'price': round(price, 2)
                })

        return alerts

    def send_discord_alert(self, alert):
        """Send alert to NDX Discord channel"""
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

        # Determine color and emoji
        if alert_type == 'RESISTANCE':
            color = 15158332  # Red
            emoji = '🔴'
            title = f'🔴 NDX AT RESISTANCE - {level}'
            description = f'**NDX Price: ${price:,.2f}**\nDistance: {distance} points from resistance {level}'
        elif alert_type == 'SUPPORT':
            color = 3066993  # Green
            emoji = '🟢'
            title = f'🟢 NDX AT SUPPORT - {level}'
            description = f'**NDX Price: ${price:,.2f}**\nDistance: {distance} points from support {level}'
        elif alert_type == 'HIGH_PROB_REVERSAL':
            color = 16744272  # Orange
            emoji = '⚠️'
            title = f'⚠️ NDX HIGH PROBABILITY REVERSAL ZONE - {level}'
            description = f'**NDX Price: ${price:,.2f}**\nDistance: {distance} points from HIGH PROB reversal zone {level}'
        else:  # PIVOT
            color = 15844367  # Gold
            emoji = '⚖️'
            title = f'⚖️ NDX AT PIVOT - {level}'
            description = f'**NDX Price: ${price:,.2f}**\nDistance: {distance} points from pivot'

        payload = {
            'username': f'{emoji} NDX Level Alert',
            'embeds': [{
                'title': title,
                'description': description,
                'color': color,
                'timestamp': datetime.utcnow().isoformat(),
                'fields': [
                    {
                        'name': '📊 Current Price',
                        'value': f'${price:,.2f}',
                        'inline': True
                    },
                    {
                        'name': '🎯 Key Level',
                        'value': f'${level:,}',
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
                    'text': 'NDX Real-Time Streaming System'
                }
            }]
        }

        try:
            response = requests.post(WEBHOOK_NDX, json=payload, timeout=10)
            if response.status_code == 204:
                print(f"✅ NDX Alert sent: {alert_type} {level} (NDX: ${price:,.2f})")
            else:
                print(f"❌ NDX Alert failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Error sending NDX alert: {e}")

    def start(self):
        """Start enhanced NDX trading system"""
        print("="*80)
        print("🚀 NDX ENHANCED TRADING SYSTEM STARTED")
        print("="*80)
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S ET')}")
        print(f"Features: Momentum, King Nodes, Confidence Scoring, Trade Setups, P&L Tracking")
        print(f"Minimum Confidence: 85% for trade alerts")
        print(f"Refresh Interval: 10 seconds")
        print(f"Discord Channel: NDX Dedicated Channel")
        print(f"Quant Levels Loaded: {len(NDX_LEVELS['resistance']) + len(NDX_LEVELS['support']) + 1} levels")
        print("="*80)

        self.running = True
        iteration = 0

        while self.running:
            iteration += 1
            current_time = datetime.now().strftime('%H:%M:%S')

            # Get current price
            ndx_price = self.get_ndx_price()

            if ndx_price:
                # Update price history
                self.price_history.append(ndx_price)
                if len(self.price_history) > 10:
                    self.price_history.pop(0)

                print(f"\n[{current_time}] Iteration {iteration} - NDX: ${ndx_price:,.2f}")

                # Calculate momentum
                momentum, momentum_strength = self.calculate_momentum(ndx_price)
                print(f"  📈 Momentum: {momentum} (strength: {momentum_strength})")

                # Analyze king nodes and walls
                king_node, walls = self.analyze_king_nodes(ndx_price)
                if king_node:
                    print(f"  👑 King Node: {king_node['type']} at {king_node['level']} (strength: {king_node['strength']})")
                if len(walls) > 0:
                    print(f"  🛡️ Active Walls: {len(walls)} detected")

                # Calculate confidence score
                confidence_score = self.calculate_confidence_score(
                    ndx_price, momentum, momentum_strength, king_node, walls
                )
                print(f"  🎯 Confidence Score: {confidence_score:.1f}%")

                # Generate trade setup if confidence >= 85%
                trade_setup = self.generate_trade_setup(
                    ndx_price, momentum, confidence_score, king_node
                )

                if trade_setup:
                    print(f"\n  🔥 HIGH-CONFIDENCE TRADE DETECTED:")
                    print(f"     Type: {trade_setup['type']}")
                    print(f"     Contract: {trade_setup['contract']}")
                    print(f"     Entry: ${trade_setup['entry']:,.2f}")
                    print(f"     Stop: ${trade_setup['stop']:,.2f}")
                    print(f"     Target1: ${trade_setup['target1']:,.2f} | Target2: ${trade_setup['target2']:,.2f}")
                    print(f"     Confidence: {trade_setup['confidence']:.1f}%")
                    print(f"     Reason: {trade_setup['reason']}")

                    # Send Discord alert
                    self.send_trade_alert(trade_setup)

                # Check for level proximity alerts
                alerts = self.check_level_proximity(ndx_price)

                if alerts:
                    print(f"  📍 Level Alerts: {len(alerts)} nearby")
                    for alert in alerts:
                        print(f"     {alert['type']}: {alert['level']} (distance: {alert['distance']} pts)")
                        self.send_discord_alert(alert)

                # Update active trades P&L
                if self.active_trades:
                    print(f"  💼 Active Trades: {len(self.active_trades)}")
                    for trade_id, trade in self.active_trades.items():
                        entry_price = trade['entry']
                        if trade['type'] == 'LONG':
                            pnl_pct = ((ndx_price - entry_price) / entry_price) * 100
                        else:
                            pnl_pct = ((entry_price - ndx_price) / entry_price) * 100

                        trade['pnl'] = pnl_pct
                        print(f"     {trade['contract']}: {pnl_pct:+.2f}%")

                self.previous_price = ndx_price
                self.last_price = ndx_price
            else:
                print(f"[{current_time}] ❌ Failed to get NDX price")

            # Wait 10 seconds before next poll
            time.sleep(10)

    def stop(self):
        """Stop NDX polling system"""
        self.running = False
        print("\n" + "="*70)
        print("🛑 NDX STREAMING SYSTEM STOPPED")
        print("="*70)

if __name__ == "__main__":
    system = NDXStreamingSystem()

    try:
        system.start()
    except KeyboardInterrupt:
        print("\n\nReceived interrupt signal...")
        system.stop()
