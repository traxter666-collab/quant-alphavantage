#!/usr/bin/env python3
"""
ENHANCED MULTI-ASSET TRADE MONITOR v2.0
Features: VIX monitoring, volume surge detection, correlation tracking
"""

import os
import sys
import time
import json
import subprocess
from datetime import datetime
from collections import deque

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dual_api_system import DualAPISystem

class EnhancedMultiAssetMonitor:
    def __init__(self):
        self.dual_api = DualAPISystem()
        self.last_alerts = {}
        self.alert_thresholds = {
            'price_change': 0.5,  # Alert on 0.5%+ price moves
            'vix_change': 1.0,     # Alert on 1.0+ VIX moves
            'volume_surge': 2.0,   # Alert on 2x+ volume spikes
            'correlation_break': 0.2  # Alert on 0.2+ correlation changes
        }
        self.last_discord_alert = {}  # Track last Discord alert time

        # Price history for correlation tracking (last 20 data points)
        self.price_history = {
            'SPX': deque(maxlen=20),
            'NDX': deque(maxlen=20),
            'SPY': deque(maxlen=20),
            'QQQ': deque(maxlen=20),
            'IWM': deque(maxlen=20),
            'VIX': deque(maxlen=20)
        }

        # Volume history for surge detection (last 10 data points)
        self.volume_history = {
            'SPY': deque(maxlen=10),
            'QQQ': deque(maxlen=10),
            'IWM': deque(maxlen=10)
        }

        # VIX thresholds
        self.vix_levels = {
            'ultra_low': 12,
            'low': 16,
            'normal': 20,
            'elevated': 25,
            'high': 30
        }

        # Load key levels from todays_levels.json if available
        try:
            with open('todays_levels.json', 'r') as f:
                levels_data = json.load(f)
                self.levels = self._convert_levels_format(levels_data)
        except:
            # Fallback to default levels
            self.levels = {
                'SPX': {
                    'resistance': (6680, 6690),
                    'support': (6630, 6635),
                    'gamma_flip': (6610, 6615)
                },
                'SPY': {
                    'resistance': (668, 669),
                    'support': (663, 661),
                    'gamma_flip': (661, 663)
                },
                'QQQ': {
                    'resistance': (602, 604),
                    'support': (597, 595),
                    'gamma_flip': (595, 597)
                },
                'IWM': {
                    'resistance': (243, 244),
                    'support': (239, 237),
                    'gamma_flip': (237, 239)
                },
                'NDX': {
                    'resistance': (24800, 24900),
                    'support': (24600, 24500),
                    'gamma_flip': (24500, 24600)
                }
            }

    def _convert_levels_format(self, levels_data):
        """Convert todays_levels.json format to monitor format"""
        converted = {}
        for symbol in ['SPX', 'SPY', 'QQQ', 'IWM', 'NDX']:
            symbol_lower = symbol.lower()
            if symbol_lower in levels_data:
                data = levels_data[symbol_lower]
                converted[symbol] = {
                    'resistance': (data['resistance']['r1'], data['resistance']['r2']),
                    'support': (data['support']['s1'], data['support']['s2']),
                    'gamma_flip': tuple(data.get('gamma_flip', {}).get('range', [0, 0]))
                }
        return converted

    def get_vix(self):
        """Get VIX level using Polygon API"""
        try:
            result = self.dual_api.get_stock_quote_with_failover('VIX')
            if result['success']:
                return result['price']
        except Exception as e:
            print(f"VIX fetch error: {e}")
        return None

    def analyze_vix_regime(self, vix_price):
        """Analyze VIX regime and provide volatility assessment"""
        if vix_price is None:
            return {'regime': 'UNKNOWN', 'risk_level': 'NORMAL', 'position_multiplier': 1.0}

        if vix_price < self.vix_levels['ultra_low']:
            regime = 'ULTRA_LOW'
            risk_level = 'VERY_LOW'
            position_multiplier = 1.2  # Can increase size
        elif vix_price < self.vix_levels['low']:
            regime = 'LOW'
            risk_level = 'LOW'
            position_multiplier = 1.1
        elif vix_price < self.vix_levels['normal']:
            regime = 'NORMAL'
            risk_level = 'NORMAL'
            position_multiplier = 1.0
        elif vix_price < self.vix_levels['elevated']:
            regime = 'ELEVATED'
            risk_level = 'ELEVATED'
            position_multiplier = 0.75  # Reduce size
        elif vix_price < self.vix_levels['high']:
            regime = 'HIGH'
            risk_level = 'HIGH'
            position_multiplier = 0.5  # Significantly reduce
        else:
            regime = 'EXTREME'
            risk_level = 'EXTREME'
            position_multiplier = 0.25  # Minimal size

        return {
            'regime': regime,
            'risk_level': risk_level,
            'position_multiplier': position_multiplier,
            'vix_level': vix_price
        }

    def detect_volume_surge(self, symbol, current_volume):
        """Detect institutional volume surges"""
        if symbol not in self.volume_history:
            return {'surge': False, 'ratio': 1.0, 'type': 'NORMAL'}

        # Add current volume to history
        self.volume_history[symbol].append(current_volume)

        # Need at least 3 data points for comparison
        if len(self.volume_history[symbol]) < 3:
            return {'surge': False, 'ratio': 1.0, 'type': 'NORMAL'}

        # Calculate average volume (excluding current)
        avg_volume = sum(list(self.volume_history[symbol])[:-1]) / (len(self.volume_history[symbol]) - 1)

        if avg_volume == 0:
            return {'surge': False, 'ratio': 1.0, 'type': 'NORMAL'}

        ratio = current_volume / avg_volume

        # Determine surge type
        if ratio >= 3.0:
            surge_type = 'EXTREME_INSTITUTIONAL'
            surge = True
        elif ratio >= 2.0:
            surge_type = 'STRONG_INSTITUTIONAL'
            surge = True
        elif ratio >= 1.5:
            surge_type = 'MODERATE_SURGE'
            surge = True
        else:
            surge_type = 'NORMAL'
            surge = False

        return {
            'surge': surge,
            'ratio': ratio,
            'type': surge_type,
            'avg_volume': avg_volume,
            'current_volume': current_volume
        }

    def calculate_correlation(self, asset1, asset2):
        """Calculate correlation between two assets"""
        if len(self.price_history[asset1]) < 10 or len(self.price_history[asset2]) < 10:
            return None

        # Get price changes (returns)
        returns1 = []
        returns2 = []

        for i in range(1, min(len(self.price_history[asset1]), len(self.price_history[asset2]))):
            r1 = (self.price_history[asset1][i] - self.price_history[asset1][i-1]) / self.price_history[asset1][i-1]
            r2 = (self.price_history[asset2][i] - self.price_history[asset2][i-1]) / self.price_history[asset2][i-1]
            returns1.append(r1)
            returns2.append(r2)

        # Calculate correlation coefficient
        if len(returns1) < 2:
            return None

        mean1 = sum(returns1) / len(returns1)
        mean2 = sum(returns2) / len(returns2)

        numerator = sum((returns1[i] - mean1) * (returns2[i] - mean2) for i in range(len(returns1)))

        variance1 = sum((r - mean1) ** 2 for r in returns1)
        variance2 = sum((r - mean2) ** 2 for r in returns2)

        if variance1 == 0 or variance2 == 0:
            return None

        correlation = numerator / (variance1 * variance2) ** 0.5

        return correlation

    def analyze_correlations(self):
        """Analyze correlations between all assets"""
        correlations = {}

        pairs = [
            ('SPX', 'NDX'),
            ('SPX', 'SPY'),
            ('SPX', 'IWM'),
            ('NDX', 'QQQ'),
            ('SPY', 'QQQ'),
            ('SPY', 'IWM')
        ]

        for asset1, asset2 in pairs:
            corr = self.calculate_correlation(asset1, asset2)
            if corr is not None:
                correlations[f'{asset1}_vs_{asset2}'] = {
                    'correlation': corr,
                    'strength': self._correlation_strength(corr)
                }

        return correlations

    def _correlation_strength(self, corr):
        """Classify correlation strength"""
        abs_corr = abs(corr)
        if abs_corr >= 0.9:
            return 'VERY_STRONG'
        elif abs_corr >= 0.7:
            return 'STRONG'
        elif abs_corr >= 0.5:
            return 'MODERATE'
        elif abs_corr >= 0.3:
            return 'WEAK'
        else:
            return 'VERY_WEAK'

    def should_send_alert(self, alert_type, value, symbol=None):
        """Determine if alert meets significance threshold for Discord notification"""
        import time

        current_time = time.time()
        alert_key = f"{alert_type}_{symbol}" if symbol else alert_type

        # Check if enough time has passed since last alert (minimum 5 minutes)
        if alert_key in self.last_discord_alert:
            if current_time - self.last_discord_alert[alert_key] < 300:
                return False

        # Check alert significance thresholds
        should_alert = False

        if alert_type == 'price_move' and abs(value) >= self.alert_thresholds['price_change']:
            should_alert = True
        elif alert_type == 'vix_move' and abs(value) >= self.alert_thresholds['vix_change']:
            should_alert = True
        elif alert_type == 'volume_surge' and value >= self.alert_thresholds['volume_surge']:
            should_alert = True
        elif alert_type == 'correlation_break' and abs(value) >= self.alert_thresholds['correlation_break']:
            should_alert = True

        if should_alert:
            self.last_discord_alert[alert_key] = current_time

        return should_alert

    def send_discord_alert(self, title, message, priority='medium'):
        """Send alert to Discord with priority-based formatting"""
        try:
            # Priority colors: critical=red, high=orange, medium=yellow, info=blue
            priority_emojis = {
                'critical': '🚨',
                'high': '⚠️',
                'medium': '📊',
                'info': 'ℹ️'
            }

            emoji = priority_emojis.get(priority, '📊')
            formatted_title = f"{emoji} {title}"

            subprocess.run(
                ['python', 'send_discord.py', formatted_title, message],
                capture_output=True,
                text=True,
                timeout=10
            )
        except Exception as e:
            print(f"Discord alert failed: {e}")

    def get_asset_price(self, symbol):
        """Get current price for any asset"""
        if symbol == 'SPX':
            result = self.dual_api.get_spx_data_with_failover()
            if result['success']:
                return result.get('spx_price')
        elif symbol == 'NDX':
            result = self.dual_api.get_ndx_data_with_failover()
            if result['success']:
                return result.get('ndx_price')
        elif symbol in ['SPY', 'QQQ', 'IWM']:
            method = getattr(self.dual_api, f'get_{symbol.lower()}_data_with_failover')
            result = method()
            if result['success']:
                return result.get('price')
        return None

    def monitor_cycle(self):
        """Single monitoring cycle with enhanced features"""
        print(f"\n{'='*80}")
        print(f"ENHANCED MONITOR CYCLE - {datetime.now().strftime('%I:%M:%S %p ET')}")
        print(f"{'='*80}\n")

        # 1. Get VIX and analyze regime
        vix_price = self.get_vix()
        vix_analysis = self.analyze_vix_regime(vix_price)

        if vix_price:
            # Check for VIX spike/drop before adding to history
            if len(self.price_history['VIX']) > 0:
                prev_vix = self.price_history['VIX'][-1]
                vix_change = vix_price - prev_vix

                # Send alert if VIX moves significantly
                if self.should_send_alert('vix_move', vix_change):
                    priority = 'critical' if abs(vix_change) >= 2.0 else 'high'
                    direction = 'SPIKE' if vix_change > 0 else 'DROP'
                    self.send_discord_alert(
                        f'VIX {direction}: {abs(vix_change):.2f} pts',
                        f"**VIX Alert**\n"
                        f"Previous: ${prev_vix:.2f}\n"
                        f"Current: ${vix_price:.2f}\n"
                        f"Change: {vix_change:+.2f} pts\n"
                        f"Regime: {vix_analysis['regime']}\n"
                        f"Position Multiplier: {vix_analysis['position_multiplier']:.2f}x",
                        priority=priority
                    )

            self.price_history['VIX'].append(vix_price)
            print(f"📊 VIX: ${vix_price:.2f} | Regime: {vix_analysis['regime']} | "
                  f"Risk: {vix_analysis['risk_level']} | "
                  f"Position Multiplier: {vix_analysis['position_multiplier']:.2f}x\n")

        # 2. Get all asset prices and update history
        prices = {}
        for symbol in ['SPX', 'NDX', 'SPY', 'QQQ', 'IWM']:
            price = self.get_asset_price(symbol)
            if price:
                # Check for significant price moves
                if len(self.price_history[symbol]) > 0:
                    prev_price = self.price_history[symbol][-1]
                    price_change_pct = ((price - prev_price) / prev_price) * 100

                    # Send alert if price moves significantly
                    if self.should_send_alert('price_move', price_change_pct, symbol):
                        priority = 'high' if abs(price_change_pct) >= 1.0 else 'medium'
                        direction = 'BREAKOUT' if price_change_pct > 0 else 'BREAKDOWN'
                        self.send_discord_alert(
                            f'{symbol} {direction}: {abs(price_change_pct):.2f}%',
                            f"**{symbol} Price Alert**\n"
                            f"Previous: ${prev_price:.2f}\n"
                            f"Current: ${price:.2f}\n"
                            f"Change: {price_change_pct:+.2f}%\n"
                            f"Move: ${price - prev_price:+.2f}",
                            priority=priority
                        )

                prices[symbol] = price
                self.price_history[symbol].append(price)
                print(f"{symbol}: ${price:.2f}")

        print()

        # 3. Check volume surges for ETFs (would need volume data from API)
        # For now, placeholder - would integrate with real volume data
        volume_alerts = []
        # volume_surge_spy = self.detect_volume_surge('SPY', current_spy_volume)
        # if volume_surge_spy['surge']:
        #     volume_alerts.append(f"SPY Volume Surge: {volume_surge_spy['type']} ({volume_surge_spy['ratio']:.1f}x)")

        if volume_alerts:
            print("🔊 VOLUME SURGES DETECTED:")
            for alert in volume_alerts:
                print(f"  • {alert}")
            print()

        # 4. Analyze correlations
        correlations = self.analyze_correlations()
        if correlations:
            print("🔗 CORRELATION ANALYSIS:")
            for pair, data in correlations.items():
                print(f"  {pair}: {data['correlation']:.2f} ({data['strength']})")
            print()

        # 5. Alert on correlation breakdowns
        if correlations:
            # SPX vs SPY should be very high
            spx_spy = correlations.get('SPX_vs_SPY', {})
            if spx_spy.get('correlation', 1.0) < 0.8:
                print(f"⚠️  CORRELATION ALERT: SPX vs SPY correlation dropped to {spx_spy['correlation']:.2f}")
                print(f"   Potential arbitrage opportunity or data issue\n")

        # 6. Position sizing recommendations based on VIX
        if vix_analysis['position_multiplier'] != 1.0:
            print(f"💡 POSITION SIZING ADJUSTMENT:")
            print(f"   VIX {vix_analysis['regime']} regime suggests "
                  f"{vix_analysis['position_multiplier']:.0%} of normal position size\n")

        print(f"{'='*80}\n")

    def run(self, update_interval=10):
        """Run enhanced monitor with specified update interval"""
        print(f"\n🚀 ENHANCED MULTI-ASSET MONITOR STARTED")
        print(f"📊 Monitoring: SPX, SPY, QQQ, IWM, NDX + VIX")
        print(f"🔄 Update Interval: {update_interval} seconds")
        print(f"⏰ Started: {datetime.now().strftime('%I:%M:%S %p ET')}\n")

        while True:
            try:
                self.monitor_cycle()
                time.sleep(update_interval)

            except KeyboardInterrupt:
                print("\n\n⏹️  Monitor stopped by user")
                break
            except Exception as e:
                print(f"\n❌ Monitor error: {e}")
                print("Retrying in 30 seconds...")
                time.sleep(30)

def main():
    monitor = EnhancedMultiAssetMonitor()
    monitor.run(update_interval=10)

if __name__ == "__main__":
    main()
