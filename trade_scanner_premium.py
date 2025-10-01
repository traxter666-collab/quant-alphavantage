"""
Premium Multi-Asset Trade Scanner with Enhanced Analytics
Only generates HIGH CONFIDENCE (75-80%+) trade setups
Tracks active trades with entry/exit alerts and P&L monitoring
"""

import requests
import json
import time
from datetime import datetime
import os

# API Keys
POLYGON_PRIMARY = "_u0zA0CH5ZspOHecb2G8uBxd2DUo4r9D"
POLYGON_BACKUP = "CiDDZJqQS88A0QhaoJbn0rLqaenps6Pq"

# Discord Webhooks
WEBHOOK_SPX = "https://discord.com/api/webhooks/1422930069290225694/PKiahdQzpgIZuceHRU254dgpmSEOcgho0-o-DpkQXeCUsQ5AYH1mv3OmJ_gG-1eB7FU-"
WEBHOOK_NDX = "https://discord.com/api/webhooks/1422964068464988292/U6sdcQEyh9biXh2UTkZ2P9qNTIvU-wngGwYxbo3wxUmCDxMEqNITMz3LXRQdvMbxNJ6G"
WEBHOOK_ALERTS = "https://discord.com/api/webhooks/1422763517974417478/0AAxHmLLjC389OXRi5KY_P2puAY8BhGAgEYTXSxj7TiKlqK_WH1PXPW6d_osA219ZFPu"

# Trading Levels (Updated quant levels)
SPX_LEVELS = {
    'resistance': [6742, 6734, 6730, 6700, 6690],
    'support': [6647, 6642, 6633, 6621, 6620, 6600, 6595],
    'pivot': 6659,
    'high_probability_reversal': [6734, 6730, 6633]
}

NDX_LEVELS = {
    'resistance': [24850, 24800, 24750, 24700, 24650],
    'support': [24500, 24450, 24400, 24350, 24300, 24250, 24200],
    'pivot': 24550,
    'high_probability_reversal': [24800, 24750, 24400]
}

# Asset Configuration
ASSETS = {
    'SPX': {'type': 'index', 'ticker': 'I:SPX', 'levels': SPX_LEVELS, 'webhook': WEBHOOK_SPX},
    'NDX': {'type': 'index', 'ticker': 'I:NDX', 'levels': NDX_LEVELS, 'webhook': WEBHOOK_NDX},
    'QQQ': {'type': 'etf', 'ticker': 'QQQ', 'webhook': WEBHOOK_ALERTS},
    'SPY': {'type': 'etf', 'ticker': 'SPY', 'webhook': WEBHOOK_ALERTS},
    'IWM': {'type': 'etf', 'ticker': 'IWM', 'webhook': WEBHOOK_ALERTS}
}

class PremiumTradeScanner:
    def __init__(self):
        self.running = False
        self.prices = {}
        self.previous_prices = {}
        self.price_history = {}  # Store last 10 prices for trend analysis
        self.active_trades = {}  # Track active trades
        self.trade_history = []  # Store completed trades
        self.last_trade_alert = {}

        # Ensure .spx directory exists
        os.makedirs('.spx', exist_ok=True)

        # Load trade history if exists
        self.load_trade_history()

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

    def update_price_history(self, asset_name, price):
        """Maintain price history for trend analysis"""
        if asset_name not in self.price_history:
            self.price_history[asset_name] = []

        self.price_history[asset_name].append(price)

        # Keep last 10 prices
        if len(self.price_history[asset_name]) > 10:
            self.price_history[asset_name].pop(0)

    def calculate_confidence_score(self, asset_name, price, momentum, trade_type):
        """Calculate confidence score (0-100%) based on multiple factors"""
        score = 0
        reasons = []

        # Factor 1: Momentum alignment (30 points)
        if trade_type == 'LONG' and momentum == 'BULLISH':
            score += 30
            reasons.append('Strong bullish momentum')
        elif trade_type == 'SHORT' and momentum == 'BEARISH':
            score += 30
            reasons.append('Strong bearish momentum')
        elif momentum == 'NEUTRAL':
            score += 15
            reasons.append('Neutral momentum')

        # Factor 2: Level proximity for index options (25 points)
        if asset_name in ['SPX', 'NDX']:
            support, resistance = self.find_nearest_levels(asset_name, price)
            if support and resistance:
                dist_support = price - support
                dist_resistance = resistance - price

                if trade_type == 'LONG' and dist_support <= 5:
                    score += 25
                    reasons.append(f'Excellent support proximity ({dist_support:.1f} pts)')
                elif trade_type == 'LONG' and dist_support <= 10:
                    score += 15
                    reasons.append(f'Good support proximity ({dist_support:.1f} pts)')

                if trade_type == 'SHORT' and dist_resistance <= 5:
                    score += 25
                    reasons.append(f'Excellent resistance proximity ({dist_resistance:.1f} pts)')
                elif trade_type == 'SHORT' and dist_resistance <= 10:
                    score += 15
                    reasons.append(f'Good resistance proximity ({dist_resistance:.1f} pts)')

                # High probability reversal zones (bonus 10 points)
                levels = ASSETS[asset_name]['levels']
                for hpr_level in levels.get('high_probability_reversal', []):
                    if abs(price - hpr_level) <= 3:
                        score += 10
                        reasons.append(f'At high-prob reversal zone {hpr_level}')
                        break

        # Factor 3: Price trend consistency (20 points)
        if asset_name in self.price_history and len(self.price_history[asset_name]) >= 3:
            prices = self.price_history[asset_name]

            if trade_type == 'LONG':
                # Check for consistent uptrend
                if all(prices[i] < prices[i+1] for i in range(len(prices)-1)):
                    score += 20
                    reasons.append('Consistent uptrend')
                elif prices[-1] > prices[-3]:
                    score += 10
                    reasons.append('Recent upward movement')
            else:  # SHORT
                # Check for consistent downtrend
                if all(prices[i] > prices[i+1] for i in range(len(prices)-1)):
                    score += 20
                    reasons.append('Consistent downtrend')
                elif prices[-1] < prices[-3]:
                    score += 10
                    reasons.append('Recent downward movement')

        # Factor 4: Risk/reward ratio (15 points)
        if asset_name in ['SPX', 'NDX']:
            support, resistance = self.find_nearest_levels(asset_name, price)
            if support and resistance:
                if trade_type == 'LONG':
                    risk = price - (support - 5)
                    reward = (resistance - 5) - price
                    if reward / risk >= 2.0:
                        score += 15
                        reasons.append(f'Excellent R:R {reward/risk:.1f}:1')
                    elif reward / risk >= 1.5:
                        score += 10
                        reasons.append(f'Good R:R {reward/risk:.1f}:1')
                else:  # SHORT
                    risk = (resistance + 5) - price
                    reward = price - (support + 5)
                    if reward / risk >= 2.0:
                        score += 15
                        reasons.append(f'Excellent R:R {reward/risk:.1f}:1')
                    elif reward / risk >= 1.5:
                        score += 10
                        reasons.append(f'Good R:R {reward/risk:.1f}:1')

        # Factor 5: Volume/volatility context (10 points) - placeholder for now
        score += 5  # Base volatility score

        return min(score, 100), reasons

    def calculate_momentum(self, asset_name):
        """Calculate momentum with enhanced thresholds"""
        if asset_name not in self.prices or asset_name not in self.previous_prices:
            return 'NEUTRAL'

        current = self.prices[asset_name]
        previous = self.previous_prices[asset_name]

        change_pct = ((current - previous) / previous) * 100

        # Stricter thresholds for momentum
        if change_pct > 0.08:
            return 'BULLISH'
        elif change_pct < -0.08:
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
        """Calculate optimal option strike"""
        from datetime import datetime
        now = datetime.now()
        expiry = now.strftime('%Y%m%d')  # 0DTE format

        if asset_name in ['SPX', 'NDX']:
            if trade_type == 'LONG':
                strike = int((price + 5) / 5) * 5
            else:
                strike = int((price - 5) / 5) * 5

            ticker = 'SPXW' if asset_name == 'SPX' else 'NDXP'
            option_type = 'C' if trade_type == 'LONG' else 'P'
            contract = f"{ticker}{expiry}{option_type}{strike}"
        else:
            if trade_type == 'LONG':
                strike = int(price + 0.5)
            else:
                strike = int(price - 0.5)

            ticker = asset_name
            option_type = 'C' if trade_type == 'LONG' else 'P'
            contract = f"{ticker}{expiry}{option_type}{strike}"

        return contract, strike

    def generate_trade_setup(self, asset_name, price, momentum):
        """Generate HIGH CONFIDENCE trade setups only (75%+ confidence)"""
        trade_key = f"{asset_name}_{int(price)}"
        current_time = time.time()

        # Check cooldown
        if trade_key in self.last_trade_alert:
            if current_time - self.last_trade_alert[trade_key] < 300:
                return None

        if asset_name in ['SPX', 'NDX']:
            support, resistance = self.find_nearest_levels(asset_name, price)

            if support and resistance:
                distance_to_support = price - support
                distance_to_resistance = resistance - price

                # LONG setup: Near support with bullish momentum
                if distance_to_support <= 10 and momentum in ['BULLISH', 'NEUTRAL']:
                    confidence_score, confidence_reasons = self.calculate_confidence_score(
                        asset_name, price, momentum, 'LONG'
                    )

                    # Only alert if confidence >= 75%
                    if confidence_score < 75:
                        return None

                    self.last_trade_alert[trade_key] = current_time
                    target1 = round(price + (distance_to_resistance * 0.5), 2)
                    contract, strike = self.calculate_option_strike(asset_name, price, 'LONG', target1)

                    trade = {
                        'asset': asset_name,
                        'type': 'LONG',
                        'reason': f'Near support {support} with {momentum} momentum',
                        'entry': round(price, 2),
                        'stop': round(support - 5, 2),
                        'target1': target1,
                        'target2': round(resistance - 5, 2),
                        'confidence_score': confidence_score,
                        'confidence_reasons': confidence_reasons,
                        'contract': contract,
                        'strike': strike,
                        'option_type': 'CALL',
                        'timestamp': datetime.now().isoformat()
                    }

                    return trade

                # SHORT setup: Near resistance with bearish momentum
                elif distance_to_resistance <= 10 and momentum in ['BEARISH', 'NEUTRAL']:
                    confidence_score, confidence_reasons = self.calculate_confidence_score(
                        asset_name, price, momentum, 'SHORT'
                    )

                    # Only alert if confidence >= 75%
                    if confidence_score < 75:
                        return None

                    self.last_trade_alert[trade_key] = current_time
                    target1 = round(price - (distance_to_support * 0.5), 2)
                    contract, strike = self.calculate_option_strike(asset_name, price, 'SHORT', target1)

                    trade = {
                        'asset': asset_name,
                        'type': 'SHORT',
                        'reason': f'Near resistance {resistance} with {momentum} momentum',
                        'entry': round(price, 2),
                        'stop': round(resistance + 5, 2),
                        'target1': target1,
                        'target2': round(support + 5, 2),
                        'confidence_score': confidence_score,
                        'confidence_reasons': confidence_reasons,
                        'contract': contract,
                        'strike': strike,
                        'option_type': 'PUT',
                        'timestamp': datetime.now().isoformat()
                    }

                    return trade

        return None

    def check_exit_conditions(self, trade_id, current_price):
        """Monitor active trades for exit conditions"""
        if trade_id not in self.active_trades:
            return None

        trade = self.active_trades[trade_id]
        entry_price = trade['entry']
        stop_price = trade['stop']
        target1_price = trade['target1']
        target2_price = trade['target2']

        exit_reason = None
        exit_action = None

        if trade['type'] == 'LONG':
            # Check stop loss
            if current_price <= stop_price:
                exit_reason = f"🛑 STOP LOSS HIT at ${current_price:,.2f}"
                exit_action = 'STOP_LOSS'
            # Check target 1
            elif current_price >= target1_price and not trade.get('target1_hit'):
                exit_reason = f"🎯 TARGET 1 HIT at ${current_price:,.2f} - Consider taking 50% profit"
                exit_action = 'TARGET1'
                trade['target1_hit'] = True
            # Check target 2
            elif current_price >= target2_price:
                exit_reason = f"🎯 TARGET 2 HIT at ${current_price:,.2f} - TAKE PROFITS!"
                exit_action = 'TARGET2'

        else:  # SHORT
            # Check stop loss
            if current_price >= stop_price:
                exit_reason = f"🛑 STOP LOSS HIT at ${current_price:,.2f}"
                exit_action = 'STOP_LOSS'
            # Check target 1
            elif current_price <= target1_price and not trade.get('target1_hit'):
                exit_reason = f"🎯 TARGET 1 HIT at ${current_price:,.2f} - Consider taking 50% profit"
                exit_action = 'TARGET1'
                trade['target1_hit'] = True
            # Check target 2
            elif current_price <= target2_price:
                exit_reason = f"🎯 TARGET 2 HIT at ${current_price:,.2f} - TAKE PROFITS!"
                exit_action = 'TARGET2'

        if exit_reason:
            # Calculate P&L
            if trade['type'] == 'LONG':
                pnl_pct = ((current_price - entry_price) / entry_price) * 100
            else:
                pnl_pct = ((entry_price - current_price) / entry_price) * 100

            return {
                'trade_id': trade_id,
                'exit_reason': exit_reason,
                'exit_action': exit_action,
                'current_price': current_price,
                'pnl_pct': round(pnl_pct, 2),
                'trade': trade
            }

        return None

    def send_trade_alert(self, trade):
        """Send trade setup alert to Discord"""
        asset = trade['asset']
        webhook = ASSETS[asset]['webhook']

        color = 3066993 if trade['type'] == 'LONG' else 15158332
        emoji = '🟢' if trade['type'] == 'LONG' else '🔴'

        title = f"{emoji} 🔥 {asset} {trade['type']} SETUP - {trade['confidence_score']}% CONFIDENCE"

        # Format confidence reasons
        reasons_text = "\n".join([f"✓ {r}" for r in trade['confidence_reasons']])

        payload = {
            'username': f'{emoji} Premium Trade Scanner',
            'embeds': [{
                'title': title,
                'description': f"**{trade['reason']}**\n\n📄 **CONTRACT:** `{trade['contract']}`\n\n**Confidence Factors:**\n{reasons_text}",
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
                        'name': '🎯 Target 1 (50%)',
                        'value': f"${trade['target1']:,.2f}",
                        'inline': True
                    },
                    {
                        'name': '🎯 Target 2 (100%)',
                        'value': f"${trade['target2']:,.2f}",
                        'inline': True
                    },
                    {
                        'name': '🔥 Confidence',
                        'value': f"{trade['confidence_score']}%",
                        'inline': True
                    }
                ],
                'footer': {
                    'text': f'Premium Trade Scanner | {asset} {trade["type"]} | Entry Alert'
                }
            }]
        }

        try:
            response = requests.post(webhook, json=payload, timeout=10)
            if response.status_code == 204:
                print(f"✅ Trade alert sent: {asset} {trade['type']} @ ${trade['entry']} ({trade['confidence_score']}%)")

                # Add to active trades
                trade_id = f"{asset}_{trade['timestamp']}"
                self.active_trades[trade_id] = trade
                self.save_trade_history()
            else:
                print(f"❌ Trade alert failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Error sending trade alert: {e}")

    def send_exit_alert(self, exit_info):
        """Send exit alert to Discord"""
        trade = exit_info['trade']
        asset = trade['asset']
        webhook = ASSETS[asset]['webhook']

        # Color based on P&L
        if exit_info['pnl_pct'] > 0:
            color = 3066993  # Green
            emoji = '💰'
        else:
            color = 15158332  # Red
            emoji = '⚠️'

        title = f"{emoji} {asset} {trade['type']} - {exit_info['exit_action']}"

        payload = {
            'username': f'{emoji} Trade Exit Alert',
            'embeds': [{
                'title': title,
                'description': f"**{exit_info['exit_reason']}**\n\n📄 **CONTRACT:** `{trade['contract']}`",
                'color': color,
                'timestamp': datetime.utcnow().isoformat(),
                'fields': [
                    {
                        'name': '📍 Entry Price',
                        'value': f"${trade['entry']:,.2f}",
                        'inline': True
                    },
                    {
                        'name': '📍 Current Price',
                        'value': f"${exit_info['current_price']:,.2f}",
                        'inline': True
                    },
                    {
                        'name': '💵 P&L',
                        'value': f"{exit_info['pnl_pct']:+.2f}%",
                        'inline': True
                    }
                ],
                'footer': {
                    'text': f'Premium Trade Scanner | Exit Alert'
                }
            }]
        }

        try:
            response = requests.post(webhook, json=payload, timeout=10)
            if response.status_code == 204:
                print(f"✅ Exit alert sent: {asset} {exit_info['exit_action']} @ ${exit_info['current_price']}")
            else:
                print(f"❌ Exit alert failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Error sending exit alert: {e}")

    def save_trade_history(self):
        """Save trade history to file"""
        try:
            data = {
                'active_trades': self.active_trades,
                'trade_history': self.trade_history
            }
            with open('.spx/trade_tracker.json', 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"❌ Error saving trade history: {e}")

    def load_trade_history(self):
        """Load trade history from file"""
        try:
            if os.path.exists('.spx/trade_tracker.json'):
                with open('.spx/trade_tracker.json', 'r') as f:
                    data = json.load(f)
                    self.active_trades = data.get('active_trades', {})
                    self.trade_history = data.get('trade_history', [])
                    print(f"✅ Loaded {len(self.active_trades)} active trades")
        except Exception as e:
            print(f"❌ Error loading trade history: {e}")

    def scan_markets(self):
        """Scan markets for HIGH CONFIDENCE opportunities and monitor active trades"""
        print(f"\n{'='*80}")
        print(f"🔍 PREMIUM SCANNER - {datetime.now().strftime('%H:%M:%S')} | Active Trades: {len(self.active_trades)}")
        print(f"{'='*80}")

        # Update previous prices
        self.previous_prices = self.prices.copy()

        # Get current prices
        for asset_name in ASSETS.keys():
            price = self.get_price(asset_name)
            if price:
                self.prices[asset_name] = price
                self.update_price_history(asset_name, price)

        # Check active trades for exit conditions
        exits_to_process = []
        for trade_id in list(self.active_trades.keys()):
            trade = self.active_trades[trade_id]
            asset_name = trade['asset']

            if asset_name in self.prices:
                current_price = self.prices[asset_name]
                exit_info = self.check_exit_conditions(trade_id, current_price)

                if exit_info:
                    exits_to_process.append(exit_info)

        # Process exits
        for exit_info in exits_to_process:
            self.send_exit_alert(exit_info)

            # Move to history if TARGET2 or STOP_LOSS
            if exit_info['exit_action'] in ['TARGET2', 'STOP_LOSS']:
                trade_id = exit_info['trade_id']
                self.trade_history.append({
                    'trade': self.active_trades[trade_id],
                    'exit_info': exit_info
                })
                del self.active_trades[trade_id]
                self.save_trade_history()

        # Scan for new opportunities
        trades_found = []
        for asset_name in ASSETS.keys():
            if asset_name in self.prices:
                price = self.prices[asset_name]
                momentum = self.calculate_momentum(asset_name)

                trade = self.generate_trade_setup(asset_name, price, momentum)

                if trade:
                    trades_found.append(trade)
                    print(f"\n🎯 HIGH CONFIDENCE TRADE:")
                    print(f"   {trade['asset']} {trade['type']} @ ${trade['entry']:,.2f} - {trade['confidence_score']}% confidence")
                    print(f"   Contract: {trade['contract']}")
                    print(f"   Reasons: {', '.join(trade['confidence_reasons'])}")

                    self.send_trade_alert(trade)

        if not trades_found and not exits_to_process:
            print("\n  ✓ No 75%+ confidence setups at current levels")

        print(f"{'='*80}\n")

    def start(self):
        """Start premium trade scanner"""
        print("="*80)
        print("🚀 PREMIUM TRADE SCANNER - HIGH CONFIDENCE ONLY (75%+)")
        print("="*80)
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S ET')}")
        print(f"Assets: SPX, NDX, QQQ, SPY, IWM")
        print(f"Scan Interval: 30 seconds")
        print(f"Confidence Threshold: 75% minimum")
        print(f"Trade Tracking: Active with entry/exit alerts")
        print("="*80)

        self.running = True
        iteration = 0

        while self.running:
            iteration += 1
            self.scan_markets()
            time.sleep(30)

    def stop(self):
        """Stop scanner"""
        self.running = False
        print("\n" + "="*80)
        print("🛑 PREMIUM TRADE SCANNER STOPPED")
        print(f"Final Stats: {len(self.active_trades)} active, {len(self.trade_history)} completed")
        print("="*80)

if __name__ == "__main__":
    scanner = PremiumTradeScanner()

    try:
        scanner.start()
    except KeyboardInterrupt:
        print("\n\nReceived interrupt signal...")
        scanner.stop()
