#!/usr/bin/env python3
"""
Real-Time Trading Notifications System
Advanced alert system with priority levels and multiple notification channels
"""

import requests
import json
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import queue

class TradingAlertsEngine:
    def __init__(self):
        self.api_key = 'ZFL38ZY98GSN7E1S'
        self.discord_webhook = 'https://discord.com/api/webhooks/1409686499745595432/BcxhXaFGMLy2rSPBMsN9Tb0wpKWxVYOnZnsfmETvHOeEJGsRep3N-lhZQcKxzrbMfHgk'
        self.alert_queue = queue.PriorityQueue()
        self.monitoring = False
        self.alert_history = []

        # Alert thresholds
        self.price_change_threshold = 0.5  # 0.5% price moves
        self.volume_surge_threshold = 2.0   # 2x average volume
        self.rsi_extreme_threshold = 75     # RSI > 75 or < 25

        # Rate limiting
        self.last_discord_send = 0
        self.discord_cooldown = 3  # 3 seconds between Discord messages

    def create_alert(self, priority: int, alert_type: str, message: str, data: Dict) -> Dict:
        """Create standardized alert object"""
        return {
            'priority': priority,  # 1=CRITICAL, 2=HIGH, 3=MEDIUM, 4=LOW, 5=INFO
            'type': alert_type,
            'message': message,
            'data': data,
            'timestamp': datetime.now(),
            'id': f"{alert_type}_{int(time.time())}"
        }

    def send_discord_alert(self, alert: Dict) -> bool:
        """Send alert to Discord with rate limiting"""
        try:
            # Rate limiting check
            current_time = time.time()
            if current_time - self.last_discord_send < self.discord_cooldown:
                print(f"Discord rate limited, queuing alert: {alert['type']}")
                return False

            # Color coding by priority
            colors = {
                1: 0xFF0000,  # Red - Critical
                2: 0xFF8C00,  # Orange - High
                3: 0xFFD700,  # Yellow - Medium
                4: 0x00BFFF,  # Blue - Low
                5: 0x808080   # Gray - Info
            }

            priority_names = {
                1: "🚨 CRITICAL",
                2: "⚠️ HIGH",
                3: "📊 MEDIUM",
                4: "📈 LOW",
                5: "ℹ️ INFO"
            }

            embed = {
                "title": f"{priority_names.get(alert['priority'], '📊')} {alert['type']}",
                "description": alert['message'],
                "color": colors.get(alert['priority'], 0x00BFFF),
                "timestamp": alert['timestamp'].isoformat(),
                "fields": []
            }

            # Add data fields
            for key, value in alert['data'].items():
                if key not in ['timestamp', 'id']:
                    embed['fields'].append({
                        "name": key.replace('_', ' ').title(),
                        "value": str(value),
                        "inline": True
                    })

            payload = {
                "embeds": [embed],
                "username": "SPX Trading System"
            }

            response = requests.post(self.discord_webhook, json=payload, timeout=10)

            if response.status_code == 204:
                self.last_discord_send = current_time
                print(f"SUCCESS Discord alert sent: {alert['type']}")
                return True
            else:
                print(f"ERROR Discord error {response.status_code}: {alert['type']}")
                return False

        except Exception as e:
            print(f"ERROR Discord send error: {e}")
            return False

    def monitor_price_movements(self, symbols: List[str]) -> List[Dict]:
        """Monitor for significant price movements"""
        alerts = []

        for symbol in symbols:
            try:
                # Get current quote
                url = f'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={self.api_key}'
                response = requests.get(url, timeout=10)
                data = response.json()

                if 'Global Quote' in data:
                    quote = data['Global Quote']
                    price = float(quote['05. price'])
                    change_pct = float(quote['10. change percent'].rstrip('%'))
                    volume = int(quote['06. volume'])

                    # Check for significant price moves
                    if abs(change_pct) >= self.price_change_threshold:
                        priority = 1 if abs(change_pct) >= 2.0 else 2 if abs(change_pct) >= 1.0 else 3

                        alert = self.create_alert(
                            priority=priority,
                            alert_type="PRICE_MOVE",
                            message=f"{symbol} significant price movement: {change_pct:+.2f}%",
                            data={
                                'symbol': symbol,
                                'price': f"${price:.2f}",
                                'change_pct': f"{change_pct:+.2f}%",
                                'volume': f"{volume:,}",
                                'threshold': f"{self.price_change_threshold}%"
                            }
                        )
                        alerts.append(alert)

            except Exception as e:
                print(f"Error monitoring {symbol}: {e}")

        return alerts

    def monitor_rsi_extremes(self, symbols: List[str]) -> List[Dict]:
        """Monitor for RSI extreme conditions"""
        alerts = []

        for symbol in symbols:
            try:
                # Get RSI data
                url = f'https://www.alphavantage.co/query?function=RSI&symbol={symbol}&interval=5min&time_period=14&series_type=close&apikey={self.api_key}'
                response = requests.get(url, timeout=15)
                data = response.json()

                if 'Technical Analysis: RSI' in data:
                    rsi_data = data['Technical Analysis: RSI']
                    latest_date = max(rsi_data.keys())
                    rsi_value = float(rsi_data[latest_date]['RSI'])

                    # Check for extreme RSI conditions
                    if rsi_value >= self.rsi_extreme_threshold or rsi_value <= (100 - self.rsi_extreme_threshold):
                        condition = "OVERBOUGHT" if rsi_value >= self.rsi_extreme_threshold else "OVERSOLD"
                        priority = 1 if rsi_value >= 85 or rsi_value <= 15 else 2

                        alert = self.create_alert(
                            priority=priority,
                            alert_type=f"RSI_{condition}",
                            message=f"{symbol} RSI extreme: {rsi_value:.1f} ({condition})",
                            data={
                                'symbol': symbol,
                                'rsi': f"{rsi_value:.1f}",
                                'condition': condition,
                                'timestamp': latest_date,
                                'signal': "REVERSAL_LIKELY" if priority == 1 else "MONITOR_CLOSELY"
                            }
                        )
                        alerts.append(alert)

            except Exception as e:
                print(f"Error monitoring RSI for {symbol}: {e}")

        return alerts

    def monitor_volume_surges(self, symbols: List[str]) -> List[Dict]:
        """Monitor for unusual volume activity"""
        alerts = []

        for symbol in symbols:
            try:
                # Get intraday volume data
                url = f'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval=5min&apikey={self.api_key}'
                response = requests.get(url, timeout=15)
                data = response.json()

                if 'Time Series (5min)' in data:
                    time_series = data['Time Series (5min)']
                    latest_bars = list(time_series.items())[:20]  # Last 20 bars

                    if len(latest_bars) >= 10:
                        # Calculate average volume
                        volumes = [int(bar[1]['5. volume']) for bar in latest_bars[1:]]  # Exclude current bar
                        avg_volume = sum(volumes) / len(volumes)

                        # Check current volume
                        current_volume = int(latest_bars[0][1]['5. volume'])
                        volume_ratio = current_volume / avg_volume if avg_volume > 0 else 0

                        if volume_ratio >= self.volume_surge_threshold:
                            priority = 1 if volume_ratio >= 5.0 else 2 if volume_ratio >= 3.0 else 3

                            alert = self.create_alert(
                                priority=priority,
                                alert_type="VOLUME_SURGE",
                                message=f"{symbol} volume surge: {volume_ratio:.1f}x average",
                                data={
                                    'symbol': symbol,
                                    'current_volume': f"{current_volume:,}",
                                    'average_volume': f"{int(avg_volume):,}",
                                    'surge_ratio': f"{volume_ratio:.1f}x",
                                    'signal': "INSTITUTIONAL_ACTIVITY"
                                }
                            )
                            alerts.append(alert)

            except Exception as e:
                print(f"Error monitoring volume for {symbol}: {e}")

        return alerts

    def run_monitoring_cycle(self, symbols: List[str]) -> None:
        """Run one complete monitoring cycle"""
        print(f"RUNNING monitoring cycle at {datetime.now().strftime('%H:%M:%S')}")

        all_alerts = []

        # Monitor different conditions
        all_alerts.extend(self.monitor_price_movements(symbols))
        all_alerts.extend(self.monitor_rsi_extremes(symbols))
        all_alerts.extend(self.monitor_volume_surges(symbols))

        # Process alerts by priority
        all_alerts.sort(key=lambda x: x['priority'])

        for alert in all_alerts:
            # Add to history
            self.alert_history.append(alert)

            # Send to Discord
            self.send_discord_alert(alert)

            # Print to console
            priority_names = {1: "CRITICAL", 2: "HIGH", 3: "MEDIUM", 4: "LOW", 5: "INFO"}
            print(f"{priority_names.get(alert['priority'], 'MEDIUM')} {alert['type']}: {alert['message']}")

    def start_monitoring(self, symbols: List[str], interval_minutes: int = 5) -> None:
        """Start continuous monitoring"""
        print(f"STARTING real-time monitoring for {symbols}")
        print(f"MONITORING interval: {interval_minutes} minutes")
        print(f"PRICE threshold: {self.price_change_threshold}%")
        print(f"VOLUME threshold: {self.volume_surge_threshold}x")
        print(f"RSI threshold: {self.rsi_extreme_threshold}")
        print("-" * 50)

        self.monitoring = True

        while self.monitoring:
            try:
                self.run_monitoring_cycle(symbols)

                # Wait for next cycle
                time.sleep(interval_minutes * 60)

            except KeyboardInterrupt:
                print("\nSTOPPED Monitoring stopped by user")
                self.monitoring = False
                break
            except Exception as e:
                print(f"ERROR Monitoring error: {e}")
                time.sleep(30)  # Wait 30 seconds before retrying

    def send_test_alert(self) -> None:
        """Send test alert to verify Discord integration"""
        test_alert = self.create_alert(
            priority=3,
            alert_type="SYSTEM_TEST",
            message="Trading alert system test - all systems operational",
            data={
                'test_time': datetime.now().strftime('%H:%M:%S'),
                'status': 'OPERATIONAL',
                'monitoring': 'ACTIVE',
                'discord': 'CONNECTED'
            }
        )

        success = self.send_discord_alert(test_alert)
        if success:
            print("SUCCESS Test alert sent successfully")
        else:
            print("ERROR Test alert failed")

    def get_alert_summary(self) -> str:
        """Get summary of recent alerts"""
        if not self.alert_history:
            return "No alerts in history"

        recent = [a for a in self.alert_history if a['timestamp'] > datetime.now() - timedelta(hours=24)]

        if not recent:
            return "No alerts in last 24 hours"

        summary = []
        summary.append(f"ALERT SUMMARY - Last 24 Hours ({len(recent)} alerts)")
        summary.append("=" * 50)

        # Group by type
        by_type = {}
        for alert in recent:
            alert_type = alert['type']
            if alert_type not in by_type:
                by_type[alert_type] = []
            by_type[alert_type].append(alert)

        for alert_type, alerts in by_type.items():
            priority_counts = {}
            for alert in alerts:
                priority = alert['priority']
                priority_counts[priority] = priority_counts.get(priority, 0) + 1

            priority_str = ", ".join([f"P{p}: {c}" for p, c in sorted(priority_counts.items())])
            summary.append(f"{alert_type}: {len(alerts)} alerts ({priority_str})")

        return "\n".join(summary)

def main():
    """Test trading alerts system"""
    alerts = TradingAlertsEngine()

    print("TRADING ALERTS SYSTEM")
    print("=" * 30)

    # Send test alert
    print("Sending test alert...")
    alerts.send_test_alert()

    print("\nTo start monitoring, use:")
    print("alerts.start_monitoring(['SPY', 'QQQ', 'IWM'], interval_minutes=5)")

if __name__ == "__main__":
    main()