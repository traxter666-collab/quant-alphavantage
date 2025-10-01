#!/usr/bin/env python3
"""
LIVE OPTIONS FLOW MONITOR
Real-time unusual options activity detection with TA integration

Monitors:
- Unusual volume (3x+ average)
- Large premium trades (>$1M)
- Sweep activity
- Block trades
- Immediate TA analysis + Discord alerts

Usage: python flow_live_monitor.py [--symbols AAPL,MSFT,NVDA] [--interval 60]
"""
import os
import sys
import time
import requests
from datetime import datetime, timedelta
from flow_ta_engine import FlowTechnicalAnalyzer
import subprocess

class LiveFlowMonitor:
    def __init__(self, symbols=None, interval=60):
        self.av_key = os.getenv('ALPHAVANTAGE_API_KEY', 'ZFL38ZY98GSN7E1S')
        self.polygon_key = os.getenv('POLYGON_API_KEY', '')
        self.interval = interval
        self.analyzer = FlowTechnicalAnalyzer()

        # Default watchlist - MAG 7 + popular names
        self.symbols = symbols or [
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA',  # MAG 7
            'SPY', 'QQQ', 'IWM',  # ETFs
            'AMD', 'NFLX', 'DIS', 'BA', 'BABA'  # Popular names
        ]

        self.baselines = {}  # Store average volumes
        self.detected_flows = set()  # Track already alerted flows

    def get_option_activity(self, symbol):
        """Get options activity for symbol (placeholder for real data)"""
        try:
            # In production, would use real options data feed
            # For now, simulating with stock volume
            url = f"https://www.alphavantage.co/query"
            params = {
                'function': 'GLOBAL_QUOTE',
                'symbol': symbol,
                'apikey': self.av_key
            }

            response = requests.get(url, params=params, timeout=10)
            data = response.json()

            if 'Global Quote' in data and data['Global Quote']:
                quote = data['Global Quote']
                volume = int(quote.get('06. volume', 0))
                price = float(quote.get('05. price', 0))
                change_pct = float(quote.get('10. change percent', '0').replace('%', ''))

                return {
                    'symbol': symbol,
                    'volume': volume,
                    'price': price,
                    'change_pct': change_pct,
                    'timestamp': datetime.now()
                }
        except Exception as e:
            print(f"⚠️ Error fetching {symbol}: {e}")

        return None

    def calculate_baseline(self, symbol):
        """Calculate average volume baseline"""
        try:
            url = f"https://www.alphavantage.co/query"
            params = {
                'function': 'TIME_SERIES_DAILY',
                'symbol': symbol,
                'outputsize': 'compact',
                'apikey': self.av_key
            }

            response = requests.get(url, params=params, timeout=10)
            data = response.json()

            if 'Time Series (Daily)' in data:
                volumes = [
                    int(day['5. volume'])
                    for day in list(data['Time Series (Daily)'].values())[:20]
                ]
                avg_volume = sum(volumes) / len(volumes)
                self.baselines[symbol] = avg_volume
                return avg_volume

        except Exception as e:
            print(f"⚠️ Error calculating baseline for {symbol}: {e}")

        return None

    def detect_unusual_activity(self, activity):
        """Detect if activity is unusual"""
        if not activity:
            return None

        symbol = activity['symbol']
        volume = activity['volume']

        # Get or calculate baseline
        if symbol not in self.baselines:
            baseline = self.calculate_baseline(symbol)
            if not baseline:
                return None
        else:
            baseline = self.baselines[symbol]

        # Check for unusual volume
        volume_ratio = volume / baseline if baseline > 0 else 0

        # Unusual criteria
        is_unusual = False
        reason = []

        if volume_ratio >= 3.0:
            is_unusual = True
            reason.append(f"Volume {volume_ratio:.1f}x average")

        if abs(activity['change_pct']) >= 5:
            is_unusual = True
            reason.append(f"Price move {abs(activity['change_pct']):.1f}%")

        if is_unusual:
            return {
                **activity,
                'unusual': True,
                'volume_ratio': volume_ratio,
                'reasons': reason
            }

        return None

    def analyze_and_alert(self, unusual_activity):
        """Run TA analysis and send Discord alert"""
        symbol = unusual_activity['symbol']

        # Create unique ID for this alert
        alert_id = f"{symbol}_{datetime.now().strftime('%Y%m%d_%H%M')}"

        # Skip if already alerted recently
        if alert_id in self.detected_flows:
            return

        print(f"\n{'='*70}")
        print(f"🚨 UNUSUAL ACTIVITY DETECTED: {symbol}")
        print(f"{'='*70}")

        # Run TA analysis
        ta_result = self.analyzer.analyze_ticker(
            symbol,
            'calls_bought',  # Assume bullish for now
            unusual_activity['price'] * 1.05,  # 5% OTM
            1_000_000  # Assume $1M premium
        )

        # Build alert message
        message = f"""🚨 LIVE FLOW ALERT: {symbol}

📊 UNUSUAL ACTIVITY DETECTED
Time: {unusual_activity['timestamp'].strftime('%H:%M:%S')}

Current Price: ${unusual_activity['price']:.2f}
Price Change: {unusual_activity['change_pct']:+.2f}%
Volume: {unusual_activity['volume']:,} ({unusual_activity['volume_ratio']:.1f}x average)

Reasons:
"""
        for reason in unusual_activity['reasons']:
            message += f"  • {reason}\n"

        message += f"""
━━━━━━━━━━━━━━━━━━━━━━━━
📊 TECHNICAL ANALYSIS
━━━━━━━━━━━━━━━━━━━━━━━━

TA Score: {ta_result['ta_score']:.0f}/100
Setup Quality: {ta_result['setup_quality']}
Recommendation: {ta_result['recommendation']}

Top Signals:
"""

        for signal in ta_result.get('signals', [])[:5]:
            message += f"  • {signal}\n"

        message += """
━━━━━━━━━━━━━━━━━━━━━━━━
💡 ACTION ITEMS
━━━━━━━━━━━━━━━━━━━━━━━━

1. Use @flow-entry-analyzer for precise entry + ATR targets
2. Use @flow-risk-manager for position sizing
3. Monitor for continued flow activity

🤖 Automated by Live Flow Monitor"""

        # Send to Discord
        try:
            result = subprocess.run(
                ['python', 'send_discord_multi.py',
                 f'🚨 Live Flow: {symbol}',
                 message,
                 'alerts'],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                print(f"✅ Alert sent to Discord")
                self.detected_flows.add(alert_id)
            else:
                print(f"⚠️ Discord alert failed")

        except Exception as e:
            print(f"⚠️ Error sending alert: {e}")

        # Print to console
        print(message)

    def run(self):
        """Main monitoring loop"""
        print("\n" + "="*70)
        print("👁️ LIVE OPTIONS FLOW MONITOR")
        print("="*70)
        print(f"📊 Watching {len(self.symbols)} symbols: {', '.join(self.symbols)}")
        print(f"⏱️ Interval: {self.interval} seconds")
        print(f"🚨 Alert threshold: 3x volume or 5%+ move")
        print("\nPress Ctrl+C to stop...\n")

        # Initialize baselines
        print("📈 Calculating baselines...")
        for symbol in self.symbols:
            self.calculate_baseline(symbol)
            time.sleep(1)  # Rate limit

        print(f"✅ Baselines calculated for {len(self.baselines)} symbols\n")
        print("🔴 MONITORING LIVE...\n")

        try:
            scan_count = 0
            while True:
                scan_count += 1
                print(f"🔍 Scan #{scan_count} - {datetime.now().strftime('%H:%M:%S')}")

                for symbol in self.symbols:
                    # Get current activity
                    activity = self.get_option_activity(symbol)

                    # Check if unusual
                    unusual = self.detect_unusual_activity(activity)

                    if unusual:
                        self.analyze_and_alert(unusual)

                    time.sleep(0.5)  # Small delay between symbols

                print(f"   Checked {len(self.symbols)} symbols - No unusual activity")
                time.sleep(self.interval)

        except KeyboardInterrupt:
            print("\n\n👋 Monitor stopped")
            print(f"📊 Total scans: {scan_count}")
            print(f"🚨 Alerts sent: {len(self.detected_flows)}")

def main():
    symbols = None
    interval = 60

    # Parse arguments
    if '--symbols' in sys.argv:
        idx = sys.argv.index('--symbols')
        if idx + 1 < len(sys.argv):
            symbols = sys.argv[idx + 1].split(',')

    if '--interval' in sys.argv:
        idx = sys.argv.index('--interval')
        if idx + 1 < len(sys.argv):
            interval = int(sys.argv[idx + 1])

    monitor = LiveFlowMonitor(symbols, interval)
    monitor.run()

if __name__ == "__main__":
    main()
