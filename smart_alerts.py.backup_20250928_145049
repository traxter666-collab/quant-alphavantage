#!/usr/bin/env python3
"""
Smart Alert System
Automated alert generation with priority-based Discord notifications
"""

import json
import os
import requests
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

class AlertPriority(Enum):
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4
    INFO = 5

@dataclass
class Alert:
    message: str
    priority: AlertPriority
    timestamp: datetime
    alert_type: str
    data: Dict
    sent: bool = False

class SmartAlertSystem:
    """Intelligent alert system with priority-based notifications"""

    def __init__(self):
        self.discord_webhook = "https://discord.com/api/webhooks/1409686499745595432/BcxhXaFGMLy2rSPBMsN9Tb0wpKWxVYOnZnsfmETvHOeEJGsRep3N-lhZQcKxzrbMfHgk"
        self.alert_queue = []
        self.rate_limit_per_minute = 25
        self.last_alerts_sent = []
        self.alert_history_file = ".spx/alert_history.json"
        self.system_config_file = ".spx/alert_config.json"
        self.load_configuration()

    def load_configuration(self):
        """Load alert system configuration"""
        try:
            if os.path.exists(self.system_config_file):
                with open(self.system_config_file, 'r') as f:
                    config = json.load(f)
                    self.rate_limit_per_minute = config.get('rate_limit_per_minute', 25)
                    self.discord_webhook = config.get('discord_webhook', self.discord_webhook)
        except Exception as e:
            print(f"Error loading alert configuration: {e}")

    def create_system_health_alert(self, health_data: Dict) -> Optional[Alert]:
        """Create system health alert based on health status"""
        health_percentage = health_data.get('system_health_percentage', 100.0)

        if health_percentage < 90:
            priority = AlertPriority.CRITICAL
            message = f"🚨 CRITICAL: System health dropped to {health_percentage}%"
        elif health_percentage < 95:
            priority = AlertPriority.HIGH
            message = f"⚠️ WARNING: System health at {health_percentage}%"
        elif health_percentage < 98:
            priority = AlertPriority.MEDIUM
            message = f"🟡 NOTICE: System health at {health_percentage}%"
        else:
            # Don't alert for healthy systems unless it's a recovery
            if health_percentage == 100.0 and self._was_system_unhealthy():
                priority = AlertPriority.INFO
                message = f"✅ RECOVERY: System health restored to 100%"
            else:
                return None

        return Alert(
            message=message,
            priority=priority,
            timestamp=datetime.now(),
            alert_type="system_health",
            data=health_data
        )

    def create_trading_signal_alert(self, signal_data: Dict) -> Optional[Alert]:
        """Create trading signal alert based on confidence and consensus"""
        consensus_score = signal_data.get('consensus_score', 0)
        confidence_level = signal_data.get('confidence_level', '')
        pattern_confidence = signal_data.get('pattern_confidence', 0)

        # Determine priority based on signal strength
        if consensus_score >= 250 and pattern_confidence >= 90:
            priority = AlertPriority.CRITICAL
            message = f"🔥 ULTRA-HIGH SIGNAL: {consensus_score}/275 consensus, {pattern_confidence}% pattern confidence"
        elif consensus_score >= 220 and pattern_confidence >= 85:
            priority = AlertPriority.HIGH
            message = f"🎯 HIGH CONFIDENCE: {consensus_score}/275 consensus, {pattern_confidence}% pattern confidence"
        elif consensus_score >= 200 and pattern_confidence >= 75:
            priority = AlertPriority.MEDIUM
            message = f"📊 MEDIUM SIGNAL: {consensus_score}/275 consensus, {pattern_confidence}% pattern confidence"
        elif consensus_score >= 180:
            priority = AlertPriority.LOW
            message = f"🟡 LOW SIGNAL: {consensus_score}/275 consensus"
        else:
            return None  # Don't alert for weak signals

        # Add trade details
        if 'recommended_trade' in signal_data:
            trade = signal_data['recommended_trade']
            message += f"\n📈 Trade: {trade.get('symbol', 'SPX')} {trade.get('strike', '')} {trade.get('type', '')}"
            message += f"\n💰 Entry: ${trade.get('entry_price', 'N/A')} | Target: ${trade.get('target_price', 'N/A')}"

        return Alert(
            message=message,
            priority=priority,
            timestamp=datetime.now(),
            alert_type="trading_signal",
            data=signal_data
        )

    def create_portfolio_heat_alert(self, portfolio_data: Dict) -> Optional[Alert]:
        """Create portfolio heat monitoring alert"""
        current_heat = portfolio_data.get('current_heat_percentage', 0)
        max_heat_limit = portfolio_data.get('max_heat_limit', 15)

        heat_ratio = current_heat / max_heat_limit

        if heat_ratio >= 0.95:  # 95% of limit
            priority = AlertPriority.CRITICAL
            message = f"🚨 PORTFOLIO HEAT CRITICAL: {current_heat}% (Limit: {max_heat_limit}%)"
        elif heat_ratio >= 0.85:  # 85% of limit
            priority = AlertPriority.HIGH
            message = f"⚠️ PORTFOLIO HEAT HIGH: {current_heat}% (Limit: {max_heat_limit}%)"
        elif heat_ratio >= 0.70:  # 70% of limit
            priority = AlertPriority.MEDIUM
            message = f"🟡 PORTFOLIO HEAT ELEVATED: {current_heat}% (Limit: {max_heat_limit}%)"
        else:
            return None  # Don't alert for normal heat levels

        return Alert(
            message=message,
            priority=priority,
            timestamp=datetime.now(),
            alert_type="portfolio_heat",
            data=portfolio_data
        )

    def create_pattern_alert(self, pattern_data: Dict) -> Optional[Alert]:
        """Create pattern detection alert"""
        pattern_name = pattern_data.get('pattern_name', 'Unknown')
        confidence = pattern_data.get('confidence_score', 0)
        pattern_type = pattern_data.get('pattern_type', 'Unknown')

        if confidence >= 90:
            priority = AlertPriority.HIGH
            message = f"🎪 PATTERN DETECTED: {pattern_name} ({confidence}% confidence)"
        elif confidence >= 80:
            priority = AlertPriority.MEDIUM
            message = f"📊 PATTERN: {pattern_name} ({confidence}% confidence)"
        elif confidence >= 70:
            priority = AlertPriority.LOW
            message = f"🟡 WEAK PATTERN: {pattern_name} ({confidence}% confidence)"
        else:
            return None

        # Add pattern details
        if 'direction' in pattern_data:
            message += f"\n📈 Direction: {pattern_data['direction'].upper()}"
        if 'expected_move' in pattern_data:
            message += f"\n🎯 Expected Move: {pattern_data['expected_move']}"

        return Alert(
            message=message,
            priority=priority,
            timestamp=datetime.now(),
            alert_type="pattern_detection",
            data=pattern_data
        )

    def create_performance_alert(self, performance_data: Dict) -> Optional[Alert]:
        """Create performance milestone alert"""
        win_rate = performance_data.get('win_rate', 0)
        total_trades = performance_data.get('total_trades', 0)
        daily_pnl = performance_data.get('daily_pnl_percent', 0)

        # Milestone alerts
        if total_trades >= 10:  # Only alert after minimum trades
            if win_rate >= 85:
                priority = AlertPriority.HIGH
                message = f"🏆 EXCELLENT PERFORMANCE: {win_rate}% win rate over {total_trades} trades"
            elif win_rate >= 75:
                priority = AlertPriority.MEDIUM
                message = f"✅ GOOD PERFORMANCE: {win_rate}% win rate over {total_trades} trades"
            elif win_rate < 60:
                priority = AlertPriority.HIGH
                message = f"⚠️ PERFORMANCE CONCERN: {win_rate}% win rate over {total_trades} trades"
            else:
                return None
        else:
            return None

        # Add daily P&L context
        if abs(daily_pnl) >= 5:
            message += f"\n💰 Daily P&L: {daily_pnl:+.1f}%"

        return Alert(
            message=message,
            priority=priority,
            timestamp=datetime.now(),
            alert_type="performance",
            data=performance_data
        )

    def create_market_condition_alert(self, market_data: Dict) -> Optional[Alert]:
        """Create market condition change alert"""
        vix_level = market_data.get('vix', 0)
        market_regime = market_data.get('market_regime', 'UNKNOWN')
        chop_score = market_data.get('chop_score', 0)

        alerts = []

        # VIX spike alert
        if vix_level >= 30:
            alerts.append({
                'priority': AlertPriority.HIGH,
                'message': f"🌪️ VIX SPIKE: {vix_level} - High volatility environment"
            })
        elif vix_level >= 25:
            alerts.append({
                'priority': AlertPriority.MEDIUM,
                'message': f"⚡ ELEVATED VIX: {vix_level} - Increased volatility"
            })

        # Chop zone alert
        if chop_score >= 70:
            alerts.append({
                'priority': AlertPriority.HIGH,
                'message': f"🚫 CHOP ZONE: {chop_score} - Trading blocked"
            })

        # Market regime change
        if market_regime in ['HIGH_VOLATILITY', 'TRANSITION']:
            alerts.append({
                'priority': AlertPriority.MEDIUM,
                'message': f"🔄 REGIME CHANGE: {market_regime}"
            })

        # Return highest priority alert
        if alerts:
            highest_priority_alert = min(alerts, key=lambda x: x['priority'].value)
            return Alert(
                message=highest_priority_alert['message'],
                priority=highest_priority_alert['priority'],
                timestamp=datetime.now(),
                alert_type="market_condition",
                data=market_data
            )

        return None

    def add_alert(self, alert: Alert):
        """Add alert to queue"""
        if alert:
            self.alert_queue.append(alert)
            self.alert_queue.sort(key=lambda x: x.priority.value)  # Sort by priority

    def process_alert_queue(self) -> Dict:
        """Process all queued alerts respecting rate limits"""
        processed_count = 0
        failed_count = 0
        skipped_count = 0

        # Clean old rate limit tracking
        one_minute_ago = datetime.now() - timedelta(minutes=1)
        self.last_alerts_sent = [
            timestamp for timestamp in self.last_alerts_sent
            if timestamp > one_minute_ago
        ]

        while self.alert_queue and len(self.last_alerts_sent) < self.rate_limit_per_minute:
            alert = self.alert_queue.pop(0)

            try:
                if self._send_discord_alert(alert):
                    processed_count += 1
                    alert.sent = True
                    self.last_alerts_sent.append(datetime.now())
                    self._save_alert_to_history(alert)

                    # Brief delay to respect Discord rate limits
                    time.sleep(0.5)
                else:
                    failed_count += 1

            except Exception as e:
                print(f"Error processing alert: {e}")
                failed_count += 1

        # Count remaining alerts as skipped (rate limited)
        skipped_count = len(self.alert_queue)

        return {
            "processed": processed_count,
            "failed": failed_count,
            "skipped": skipped_count,
            "remaining_in_queue": len(self.alert_queue)
        }

    def _send_discord_alert(self, alert: Alert) -> bool:
        """Send alert to Discord webhook"""
        try:
            # Determine embed color based on priority
            color_map = {
                AlertPriority.CRITICAL: 0xFF0000,  # Red
                AlertPriority.HIGH: 0xFF8C00,      # Orange
                AlertPriority.MEDIUM: 0xFFD700,    # Gold
                AlertPriority.LOW: 0x00CED1,       # Dark Turquoise
                AlertPriority.INFO: 0x87CEEB       # Sky Blue
            }

            embed = {
                "title": f"{alert.priority.name} ALERT",
                "description": alert.message[:4090],  # Discord limit
                "color": color_map[alert.priority],
                "timestamp": alert.timestamp.isoformat(),
                "footer": {
                    "text": f"Four-Asset Trading System | {alert.alert_type}"
                }
            }

            # Add fields for additional data
            if alert.data:
                fields = []
                for key, value in alert.data.items():
                    if len(fields) < 3:  # Limit fields
                        fields.append({
                            "name": key.replace('_', ' ').title(),
                            "value": str(value)[:1024],  # Discord field limit
                            "inline": True
                        })
                embed["fields"] = fields

            payload = {"embeds": [embed]}

            response = requests.post(
                self.discord_webhook,
                json=payload,
                timeout=10
            )

            return response.status_code == 204

        except Exception as e:
            print(f"Error sending Discord alert: {e}")
            return False

    def _save_alert_to_history(self, alert: Alert):
        """Save alert to history file"""
        try:
            os.makedirs(".spx", exist_ok=True)

            history_entry = {
                "timestamp": alert.timestamp.isoformat(),
                "priority": alert.priority.name,
                "alert_type": alert.alert_type,
                "message": alert.message,
                "data": alert.data,
                "sent": alert.sent
            }

            # Load existing history
            history = []
            if os.path.exists(self.alert_history_file):
                with open(self.alert_history_file, 'r') as f:
                    history = json.load(f)

            # Add new entry and keep last 100 alerts
            history.append(history_entry)
            history = history[-100:]

            # Save updated history
            with open(self.alert_history_file, 'w') as f:
                json.dump(history, f, indent=2)

        except Exception as e:
            print(f"Error saving alert history: {e}")

    def _was_system_unhealthy(self) -> bool:
        """Check if system was recently unhealthy"""
        try:
            if os.path.exists(self.alert_history_file):
                with open(self.alert_history_file, 'r') as f:
                    history = json.load(f)

                # Check last 5 alerts for system health issues
                recent_alerts = history[-5:]
                for alert in recent_alerts:
                    if (alert.get('alert_type') == 'system_health' and
                        alert.get('priority') in ['CRITICAL', 'HIGH']):
                        return True
        except Exception:
            pass
        return False

    def get_alert_statistics(self) -> Dict:
        """Get alert system statistics"""
        stats = {
            "alerts_in_queue": len(self.alert_queue),
            "rate_limit_remaining": self.rate_limit_per_minute - len(self.last_alerts_sent),
            "alert_history_count": 0,
            "recent_alert_types": {},
            "priority_distribution": {}
        }

        try:
            if os.path.exists(self.alert_history_file):
                with open(self.alert_history_file, 'r') as f:
                    history = json.load(f)

                stats["alert_history_count"] = len(history)

                # Analyze recent alerts (last 24 hours)
                one_day_ago = datetime.now() - timedelta(days=1)
                recent_alerts = [
                    alert for alert in history
                    if datetime.fromisoformat(alert['timestamp']) > one_day_ago
                ]

                # Count alert types
                for alert in recent_alerts:
                    alert_type = alert.get('alert_type', 'unknown')
                    priority = alert.get('priority', 'unknown')

                    stats["recent_alert_types"][alert_type] = stats["recent_alert_types"].get(alert_type, 0) + 1
                    stats["priority_distribution"][priority] = stats["priority_distribution"].get(priority, 0) + 1

        except Exception as e:
            print(f"Error calculating alert statistics: {e}")

        return stats

def main():
    """Test Smart Alert System"""
    alert_system = SmartAlertSystem()

    print("🚨 Smart Alert System Test")
    print("=" * 50)

    # Test system health alert
    health_data = {
        "system_health_percentage": 92.5,
        "api_tests_passed": 4,
        "api_tests_total": 5,
        "response_time": 1.8
    }
    health_alert = alert_system.create_system_health_alert(health_data)
    if health_alert:
        alert_system.add_alert(health_alert)
        print(f"✅ System Health Alert Created: {health_alert.priority.name}")

    # Test trading signal alert
    signal_data = {
        "consensus_score": 245,
        "confidence_level": "HIGH_CONFIDENCE",
        "pattern_confidence": 87,
        "recommended_trade": {
            "symbol": "SPXW",
            "strike": "6650C",
            "type": "CALL",
            "entry_price": 5.50,
            "target_price": 8.25
        }
    }
    signal_alert = alert_system.create_trading_signal_alert(signal_data)
    if signal_alert:
        alert_system.add_alert(signal_alert)
        print(f"✅ Trading Signal Alert Created: {signal_alert.priority.name}")

    # Test portfolio heat alert
    portfolio_data = {
        "current_heat_percentage": 13.8,
        "max_heat_limit": 15.0,
        "active_positions": 3
    }
    heat_alert = alert_system.create_portfolio_heat_alert(portfolio_data)
    if heat_alert:
        alert_system.add_alert(heat_alert)
        print(f"✅ Portfolio Heat Alert Created: {heat_alert.priority.name}")

    # Process alerts
    print(f"\nProcessing {len(alert_system.alert_queue)} alerts...")
    results = alert_system.process_alert_queue()

    print(f"Processed: {results['processed']}")
    print(f"Failed: {results['failed']}")
    print(f"Skipped: {results['skipped']}")

    # Get statistics
    stats = alert_system.get_alert_statistics()
    print(f"\nAlert Statistics:")
    print(f"- Queue: {stats['alerts_in_queue']} alerts")
    print(f"- Rate Limit: {stats['rate_limit_remaining']} remaining this minute")
    print(f"- History: {stats['alert_history_count']} total alerts")

    print("\n✅ Smart Alert System initialized successfully!")

if __name__ == "__main__":
    main()