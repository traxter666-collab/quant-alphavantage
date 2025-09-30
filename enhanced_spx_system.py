#!/usr/bin/env python3
"""
Enhanced SPX Trading System
Integration of SPX + QQQ/IWM analysis + Real-time alerts + Backtesting
"""

import os
import sys
from datetime import datetime

# Import all our new systems
from multi_asset_analysis import MultiAssetAnalyzer
from trading_alerts import TradingAlertsEngine
from backtesting_engine import BacktestingEngine

class EnhancedSPXSystem:
    def __init__(self):
        self.multi_asset = MultiAssetAnalyzer()
        self.alerts = TradingAlertsEngine()
        self.backtest = BacktestingEngine()

    def enhanced_analysis(self) -> str:
        """Run comprehensive analysis across all assets"""
        output = []

        output.append("ENHANCED SPX TRADING SYSTEM")
        output.append("=" * 50)
        output.append(f"Analysis Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        output.append("")

        # Run multi-asset analysis
        multi_result = self.multi_asset.run_full_multi_asset_analysis()
        output.append(multi_result)

        return "\n".join(output)

    def start_live_monitoring(self, symbols: list = None, interval: int = 5):
        """Start real-time alert monitoring"""
        if symbols is None:
            symbols = ['SPY', 'QQQ', 'IWM']

        print("STARTING ENHANCED LIVE MONITORING")
        print("=" * 40)
        print(f"Symbols: {', '.join(symbols)}")
        print(f"Interval: {interval} minutes")
        print("Discord alerts enabled")
        print("")

        # Start monitoring
        self.alerts.start_monitoring(symbols, interval)

    def run_strategy_validation(self, period_days: int = 30) -> str:
        """Run backtesting validation"""
        output = []

        output.append("STRATEGY VALIDATION RESULTS")
        output.append("=" * 40)

        # Test common strategies
        symbols = ['SPY', 'QQQ', 'IWM']
        strategies = ['RSI_REVERSAL', 'EMA_MOMENTUM']

        backtest_result = self.backtest.run_comprehensive_backtest(symbols, strategies, period_days)
        output.append(backtest_result)

        return "\n".join(output)

    def send_discord_update(self, message: str):
        """Send custom message to Discord"""
        alert = self.alerts.create_alert(
            priority=3,
            alert_type="CUSTOM_UPDATE",
            message=message,
            data={'timestamp': datetime.now().isoformat()}
        )
        return self.alerts.send_discord_alert(alert)

    def system_status(self) -> str:
        """Get comprehensive system status"""
        output = []

        output.append("ENHANCED SPX SYSTEM STATUS")
        output.append("=" * 35)

        # Check if session files exist
        session_files = [
            ".spx/session.json",
            ".spx/multi_asset_session.json",
            ".spx/backtest_results.json"
        ]

        output.append("FILE STATUS:")
        for file_path in session_files:
            if os.path.exists(file_path):
                stat = os.stat(file_path)
                mod_time = datetime.fromtimestamp(stat.st_mtime)
                output.append(f"  {file_path}: EXISTS (modified {mod_time.strftime('%H:%M:%S')})")
            else:
                output.append(f"  {file_path}: NOT FOUND")

        output.append("")
        output.append("SYSTEM CAPABILITIES:")
        output.append("  Multi-Asset Analysis: SPX/QQQ/IWM cross-correlation")
        output.append("  Real-time Alerts: Price/RSI/Volume monitoring")
        output.append("  Discord Integration: Live notifications")
        output.append("  Backtesting: Historical strategy validation")
        output.append("  Session Management: Persistent context")

        return "\n".join(output)

def main():
    """Command-line interface for enhanced system"""
    system = EnhancedSPXSystem()

    if len(sys.argv) < 2:
        print("ENHANCED SPX SYSTEM COMMANDS:")
        print("=" * 35)
        print("python enhanced_spx_system.py analysis     # Multi-asset analysis")
        print("python enhanced_spx_system.py monitor      # Start live monitoring")
        print("python enhanced_spx_system.py backtest     # Run strategy validation")
        print("python enhanced_spx_system.py status       # System status")
        print("python enhanced_spx_system.py discord 'msg' # Send Discord message")
        return

    command = sys.argv[1].lower()

    if command == "analysis":
        result = system.enhanced_analysis()
        print(result)

    elif command == "monitor":
        # Optional: custom symbols and interval
        symbols = ['SPY', 'QQQ', 'IWM']
        interval = 5

        if len(sys.argv) > 2:
            try:
                interval = int(sys.argv[2])
            except:
                pass

        system.start_live_monitoring(symbols, interval)

    elif command == "backtest":
        # Optional: custom period
        period = 30
        if len(sys.argv) > 2:
            try:
                period = int(sys.argv[2])
            except:
                pass

        result = system.run_strategy_validation(period)
        print(result)

    elif command == "status":
        result = system.system_status()
        print(result)

    elif command == "discord":
        if len(sys.argv) > 2:
            message = sys.argv[2]
            success = system.send_discord_update(message)
            print(f"Discord message sent: {success}")
        else:
            print("Usage: python enhanced_spx_system.py discord 'your message'")

    else:
        print(f"Unknown command: {command}")
        print("Use 'python enhanced_spx_system.py' for help")

if __name__ == "__main__":
    main()