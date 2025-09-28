#!/usr/bin/env python3
"""
Integrated Trading Dashboard
Unified automation interface with real-time monitoring and one-click analysis
"""

import json
import os
import time
import subprocess
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import threading
from dataclasses import dataclass, asdict

# Import our enhanced systems
from ml_pattern_engine import MLPatternEngine
from smart_alerts import SmartAlertSystem, Alert, AlertPriority
from performance_analytics import PerformanceAnalytics

@dataclass
class SystemHealth:
    """System health status"""
    overall_health: float
    api_connectivity: bool
    response_time: float
    data_accuracy: float
    last_updated: str
    status: str

@dataclass
class TradingSignal:
    """Trading signal with complete analysis"""
    timestamp: str
    symbol: str
    direction: str
    consensus_score: int
    pattern_confidence: float
    recommended_action: str
    entry_price: float
    target_price: float
    stop_loss: float
    position_size: float
    risk_reward: float
    hold_time_estimate: int

class TradingDashboard:
    """Comprehensive trading dashboard with automation"""

    def __init__(self):
        self.ml_engine = MLPatternEngine()
        self.alert_system = SmartAlertSystem()
        self.performance_analytics = PerformanceAnalytics()

        self.dashboard_state = {
            "auto_mode": False,
            "monitoring_active": False,
            "last_analysis": None,
            "active_signals": [],
            "system_health": None,
            "portfolio_heat": 0.0,
            "alerts_pending": 0
        }

        self.config_file = ".spx/dashboard_config.json"
        self.state_file = ".spx/dashboard_state.json"
        self.load_configuration()

    def load_configuration(self):
        """Load dashboard configuration"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    self.config = json.load(f)
            else:
                self.config = self.get_default_config()
                self.save_configuration()
        except Exception as e:
            print(f"Error loading dashboard configuration: {e}")
            self.config = self.get_default_config()

    def get_default_config(self) -> Dict:
        """Get default dashboard configuration"""
        return {
            "auto_analysis_interval": 300,  # 5 minutes
            "health_check_interval": 60,    # 1 minute
            "alert_processing_interval": 30, # 30 seconds
            "performance_update_interval": 120, # 2 minutes
            "min_consensus_score": 200,
            "min_pattern_confidence": 75,
            "max_portfolio_heat": 15.0,
            "auto_discord_alerts": True,
            "auto_save_results": True,
            "market_hours_only": True,
            "emergency_stop_loss": 50.0
        }

    def save_configuration(self):
        """Save dashboard configuration"""
        try:
            os.makedirs(".spx", exist_ok=True)
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Error saving dashboard configuration: {e}")

    def start_dashboard(self, auto_mode: bool = False):
        """Start the trading dashboard"""
        print("🎪 TRADING DASHBOARD STARTING")
        print("=" * 60)

        self.dashboard_state["auto_mode"] = auto_mode
        self.dashboard_state["monitoring_active"] = True

        # Initial system health check
        self.check_system_health()

        # Display initial status
        self.display_dashboard_status()

        if auto_mode:
            print("🤖 AUTO MODE ACTIVATED - Continuous monitoring enabled")
            self.start_auto_monitoring()
        else:
            print("📊 MANUAL MODE - Use commands for analysis")
            self.display_available_commands()

    def start_auto_monitoring(self):
        """Start automated monitoring threads"""
        # Health monitoring thread
        health_thread = threading.Thread(
            target=self.continuous_health_monitoring,
            daemon=True
        )
        health_thread.start()

        # Market analysis thread
        analysis_thread = threading.Thread(
            target=self.continuous_market_analysis,
            daemon=True
        )
        analysis_thread.start()

        # Alert processing thread
        alert_thread = threading.Thread(
            target=self.continuous_alert_processing,
            daemon=True
        )
        alert_thread.start()

        # Performance tracking thread
        performance_thread = threading.Thread(
            target=self.continuous_performance_tracking,
            daemon=True
        )
        performance_thread.start()

        print("✅ All monitoring threads started successfully")

    def continuous_health_monitoring(self):
        """Continuous system health monitoring"""
        while self.dashboard_state["monitoring_active"]:
            try:
                self.check_system_health()

                # Generate health alerts if needed
                if self.dashboard_state["system_health"]:
                    health_alert = self.alert_system.create_system_health_alert(
                        asdict(self.dashboard_state["system_health"])
                    )
                    if health_alert:
                        self.alert_system.add_alert(health_alert)

                time.sleep(self.config["health_check_interval"])
            except Exception as e:
                print(f"Error in health monitoring: {e}")
                time.sleep(60)  # Wait longer on error

    def continuous_market_analysis(self):
        """Continuous market analysis and signal generation"""
        while self.dashboard_state["monitoring_active"]:
            try:
                # Only analyze during market hours if configured
                if self.config["market_hours_only"] and not self.is_market_hours():
                    time.sleep(300)  # Check every 5 minutes when market closed
                    continue

                # Perform comprehensive analysis
                analysis_result = self.perform_comprehensive_analysis()

                if analysis_result and analysis_result.get("signals"):
                    # Process trading signals
                    for signal in analysis_result["signals"]:
                        if self.is_signal_worthy(signal):
                            self.process_trading_signal(signal)

                time.sleep(self.config["auto_analysis_interval"])
            except Exception as e:
                print(f"Error in market analysis: {e}")
                time.sleep(300)  # Wait longer on error

    def continuous_alert_processing(self):
        """Continuous alert queue processing"""
        while self.dashboard_state["monitoring_active"]:
            try:
                # Process pending alerts
                results = self.alert_system.process_alert_queue()
                self.dashboard_state["alerts_pending"] = results.get("remaining_in_queue", 0)

                time.sleep(self.config["alert_processing_interval"])
            except Exception as e:
                print(f"Error in alert processing: {e}")
                time.sleep(60)

    def continuous_performance_tracking(self):
        """Continuous performance monitoring and updates"""
        while self.dashboard_state["monitoring_active"]:
            try:
                # Update performance metrics
                performance = self.performance_analytics.get_real_time_performance()

                # Check for performance alerts
                if performance["overview"]["total_trades"] >= 5:
                    perf_alert = self.alert_system.create_performance_alert(performance["overview"])
                    if perf_alert:
                        self.alert_system.add_alert(perf_alert)

                time.sleep(self.config["performance_update_interval"])
            except Exception as e:
                print(f"Error in performance tracking: {e}")
                time.sleep(120)

    def perform_comprehensive_analysis(self) -> Dict:
        """Perform complete market analysis with all systems"""
        try:
            print(f"\n🔄 Running comprehensive analysis at {datetime.now().strftime('%H:%M:%S')}")

            # Run system validation first
            health_result = self.run_system_validation()

            if not health_result.get("healthy", False):
                print("⚠️ System health check failed - skipping analysis")
                return None

            # Get fresh market data
            market_data = self.get_market_data()

            if not market_data:
                print("❌ Failed to get market data")
                return None

            # Run ML pattern analysis
            pattern_results = self.ml_engine.detect_patterns(market_data)

            # Generate trading signals
            signals = self.generate_trading_signals(market_data, pattern_results)

            # Save analysis results
            analysis_result = {
                "timestamp": datetime.now().isoformat(),
                "market_data": market_data,
                "pattern_results": pattern_results,
                "signals": signals,
                "system_health": asdict(self.dashboard_state["system_health"]) if self.dashboard_state["system_health"] else None
            }

            if self.config["auto_save_results"]:
                self.save_analysis_result(analysis_result)

            self.dashboard_state["last_analysis"] = analysis_result

            print(f"✅ Analysis complete - {len(signals)} signals generated")
            return analysis_result

        except Exception as e:
            print(f"Error in comprehensive analysis: {e}")
            return None

    def generate_trading_signals(self, market_data: Dict, pattern_results: Dict) -> List[TradingSignal]:
        """Generate actionable trading signals"""
        signals = []

        try:
            # Calculate consensus score (simplified for dashboard)
            consensus_score = self.calculate_consensus_score(market_data, pattern_results)

            # Get highest confidence pattern
            highest_pattern = pattern_results.get("highest_confidence")

            if not highest_pattern:
                return signals

            pattern_confidence = highest_pattern.get("confidence", 0)
            pattern_name = highest_pattern.get("pattern", "unknown")

            # Check if signal meets minimum thresholds
            if (consensus_score >= self.config["min_consensus_score"] and
                pattern_confidence >= self.config["min_pattern_confidence"]):

                # Generate signal
                signal = TradingSignal(
                    timestamp=datetime.now().isoformat(),
                    symbol="SPXW",
                    direction="CALL" if market_data.get("ema_9", 0) > market_data.get("ema_21", 0) else "PUT",
                    consensus_score=consensus_score,
                    pattern_confidence=pattern_confidence,
                    recommended_action="ENTER_POSITION",
                    entry_price=self.calculate_entry_price(market_data),
                    target_price=self.calculate_target_price(market_data, pattern_confidence),
                    stop_loss=self.calculate_stop_loss(market_data),
                    position_size=self.calculate_position_size(consensus_score, pattern_confidence),
                    risk_reward=2.0,  # Target 2:1 risk/reward
                    hold_time_estimate=45  # 45 minutes average
                )

                signals.append(signal)

                # Create trading signal alert
                signal_alert = self.alert_system.create_trading_signal_alert({
                    "consensus_score": consensus_score,
                    "pattern_confidence": pattern_confidence,
                    "recommended_trade": {
                        "symbol": signal.symbol,
                        "strike": f"{int(signal.entry_price * 100)}{'C' if signal.direction == 'CALL' else 'P'}",
                        "type": signal.direction,
                        "entry_price": signal.entry_price,
                        "target_price": signal.target_price
                    }
                })

                if signal_alert:
                    self.alert_system.add_alert(signal_alert)

        except Exception as e:
            print(f"Error generating trading signals: {e}")

        return signals

    def run_system_validation(self) -> Dict:
        """Run system validation and return results"""
        try:
            # Run the system validation script
            result = subprocess.run(
                ["python", "system_validation.py"],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                # Parse output for health percentage
                output_lines = result.stdout.split('\n')
                health_percentage = 100.0  # Default assumption

                for line in output_lines:
                    if "SYSTEM HEALTH:" in line:
                        try:
                            health_str = line.split("SYSTEM HEALTH:")[1].strip()
                            health_percentage = float(health_str.replace('%', ''))
                        except:
                            pass

                return {
                    "healthy": health_percentage >= 95.0,
                    "health_percentage": health_percentage,
                    "output": result.stdout
                }
            else:
                return {
                    "healthy": False,
                    "health_percentage": 0.0,
                    "error": result.stderr
                }

        except Exception as e:
            return {
                "healthy": False,
                "health_percentage": 0.0,
                "error": str(e)
            }

    def get_market_data(self) -> Optional[Dict]:
        """Get current market data (simplified for dashboard)"""
        try:
            # This would integrate with your existing market data systems
            # For now, return sample data structure
            return {
                "current_price": 6650.0,
                "volume": 45000,
                "average_volume": 35000,
                "rsi": 58.2,
                "ema_9": 6648.0,
                "ema_21": 6645.0,
                "ema_50": 6640.0,
                "resistance": 6660.0,
                "support": 6635.0,
                "price_change": 5.5,
                "vix": 18.5,
                "market_regime": "TRENDING_BULL"
            }
        except Exception as e:
            print(f"Error getting market data: {e}")
            return None

    def calculate_consensus_score(self, market_data: Dict, pattern_results: Dict) -> int:
        """Calculate simplified consensus score"""
        score = 0

        # EMA alignment (40 points max)
        ema_9 = market_data.get("ema_9", 0)
        ema_21 = market_data.get("ema_21", 0)
        ema_50 = market_data.get("ema_50", 0)

        if ema_9 > ema_21 > ema_50:  # Bull alignment
            score += 40
        elif ema_9 > ema_21:  # Partial alignment
            score += 25

        # Volume confirmation (30 points max)
        volume = market_data.get("volume", 0)
        avg_volume = market_data.get("average_volume", volume)
        if volume > avg_volume * 1.5:
            score += 30
        elif volume > avg_volume:
            score += 15

        # RSI momentum (30 points max)
        rsi = market_data.get("rsi", 50)
        if 45 <= rsi <= 75:  # Optimal range
            score += 30
        elif 35 <= rsi <= 85:  # Acceptable range
            score += 20

        # Pattern confidence contribution (100 points max)
        pattern_confidence = pattern_results.get("highest_confidence", {}).get("confidence", 0)
        score += int(pattern_confidence)

        return min(score, 275)  # Cap at 275 points

    def calculate_entry_price(self, market_data: Dict) -> float:
        """Calculate optimal entry price"""
        current_price = market_data.get("current_price", 6650.0)
        # Simplified calculation - in reality would use options pricing
        return round(current_price * 0.0008, 2)  # Rough options premium estimate

    def calculate_target_price(self, market_data: Dict, pattern_confidence: float) -> float:
        """Calculate target price based on pattern confidence"""
        entry_price = self.calculate_entry_price(market_data)
        # Higher confidence = higher targets
        multiplier = 1.5 + (pattern_confidence / 100)
        return round(entry_price * multiplier, 2)

    def calculate_stop_loss(self, market_data: Dict) -> float:
        """Calculate stop loss price"""
        entry_price = self.calculate_entry_price(market_data)
        return round(entry_price * 0.5, 2)  # 50% stop loss

    def calculate_position_size(self, consensus_score: int, pattern_confidence: float) -> float:
        """Calculate position size based on confidence"""
        base_size = 1.0  # 1% base position

        # Adjust based on consensus score
        if consensus_score >= 250:
            base_size *= 2.0
        elif consensus_score >= 225:
            base_size *= 1.5

        # Adjust based on pattern confidence
        if pattern_confidence >= 90:
            base_size *= 1.5
        elif pattern_confidence >= 80:
            base_size *= 1.25

        # Cap at maximum position size
        return min(base_size, 3.0)

    def is_signal_worthy(self, signal: TradingSignal) -> bool:
        """Check if signal meets quality thresholds"""
        return (signal.consensus_score >= self.config["min_consensus_score"] and
                signal.pattern_confidence >= self.config["min_pattern_confidence"] and
                signal.risk_reward >= 1.5)

    def process_trading_signal(self, signal: TradingSignal):
        """Process a trading signal"""
        try:
            print(f"\n🎯 TRADING SIGNAL GENERATED")
            print(f"Symbol: {signal.symbol}")
            print(f"Direction: {signal.direction}")
            print(f"Consensus: {signal.consensus_score}/275")
            print(f"Pattern Confidence: {signal.pattern_confidence}%")
            print(f"Entry: ${signal.entry_price}")
            print(f"Target: ${signal.target_price}")
            print(f"Stop: ${signal.stop_loss}")
            print(f"Position Size: {signal.position_size}%")

            # Add to active signals
            self.dashboard_state["active_signals"].append(asdict(signal))

            # Save signal to file
            self.save_trading_signal(signal)

        except Exception as e:
            print(f"Error processing trading signal: {e}")

    def check_system_health(self):
        """Check and update system health"""
        try:
            health_result = self.run_system_validation()

            self.dashboard_state["system_health"] = SystemHealth(
                overall_health=health_result.get("health_percentage", 0.0),
                api_connectivity=health_result.get("healthy", False),
                response_time=1.5,  # Would be calculated from actual response times
                data_accuracy=99.9,  # Would be calculated from validation
                last_updated=datetime.now().isoformat(),
                status="HEALTHY" if health_result.get("healthy", False) else "DEGRADED"
            )

        except Exception as e:
            print(f"Error checking system health: {e}")

    def is_market_hours(self) -> bool:
        """Check if market is currently open"""
        now = datetime.now()
        # Simplified check - 9:30 AM to 4:00 PM ET on weekdays
        return (now.weekday() < 5 and  # Monday-Friday
                9.5 <= now.hour + now.minute/60 <= 16.0)

    def display_dashboard_status(self):
        """Display current dashboard status"""
        print(f"\n🎪 DASHBOARD STATUS - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)

        # System Health
        if self.dashboard_state["system_health"]:
            health = self.dashboard_state["system_health"]
            print(f"🏥 System Health: {health.overall_health}% ({health.status})")

        # Active Signals
        active_count = len(self.dashboard_state["active_signals"])
        print(f"📊 Active Signals: {active_count}")

        # Alerts Pending
        print(f"🚨 Alerts Pending: {self.dashboard_state['alerts_pending']}")

        # Portfolio Heat
        print(f"🔥 Portfolio Heat: {self.dashboard_state['portfolio_heat']:.1f}%")

        # Auto Mode Status
        mode = "AUTO" if self.dashboard_state["auto_mode"] else "MANUAL"
        print(f"🤖 Mode: {mode}")

    def display_available_commands(self):
        """Display available dashboard commands"""
        print(f"\n📋 AVAILABLE COMMANDS:")
        print("=" * 40)
        print("analyze          - Run full market analysis")
        print("health           - Check system health")
        print("signals          - Show active signals")
        print("performance      - Show performance metrics")
        print("alerts           - Process pending alerts")
        print("auto             - Start auto mode")
        print("stop             - Stop dashboard")
        print("status           - Show dashboard status")

    def save_analysis_result(self, result: Dict):
        """Save analysis result to file"""
        try:
            os.makedirs(".spx", exist_ok=True)
            filename = f".spx/analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w') as f:
                json.dump(result, f, indent=2)
        except Exception as e:
            print(f"Error saving analysis result: {e}")

    def save_trading_signal(self, signal: TradingSignal):
        """Save trading signal to file"""
        try:
            os.makedirs(".spx", exist_ok=True)
            signals_file = ".spx/trading_signals.jsonl"
            with open(signals_file, 'a') as f:
                f.write(json.dumps(asdict(signal)) + '\n')
        except Exception as e:
            print(f"Error saving trading signal: {e}")

    def stop_dashboard(self):
        """Stop the dashboard"""
        print("\n🛑 Stopping Trading Dashboard...")
        self.dashboard_state["monitoring_active"] = False

        # Save final state
        try:
            with open(self.state_file, 'w') as f:
                json.dump(self.dashboard_state, f, indent=2, default=str)
        except Exception as e:
            print(f"Error saving dashboard state: {e}")

        print("✅ Dashboard stopped successfully")

def main():
    """Main dashboard interface"""
    dashboard = TradingDashboard()

    print("🎪 INTEGRATED TRADING DASHBOARD")
    print("Advanced automation interface with real-time monitoring")
    print("=" * 70)

    try:
        # Start dashboard in manual mode
        dashboard.start_dashboard(auto_mode=False)

        # Command loop
        while dashboard.dashboard_state["monitoring_active"]:
            try:
                command = input("\n💡 Enter command (or 'help' for options): ").strip().lower()

                if command == "analyze":
                    result = dashboard.perform_comprehensive_analysis()
                    if result:
                        print("✅ Analysis completed successfully")

                elif command == "health":
                    dashboard.check_system_health()
                    dashboard.display_dashboard_status()

                elif command == "signals":
                    signals = dashboard.dashboard_state["active_signals"]
                    print(f"\n📊 Active Signals ({len(signals)}):")
                    for i, signal in enumerate(signals[-5:], 1):  # Show last 5
                        print(f"{i}. {signal['symbol']} {signal['direction']} - "
                              f"Consensus: {signal['consensus_score']}")

                elif command == "performance":
                    perf = dashboard.performance_analytics.get_real_time_performance()
                    overview = perf["overview"]
                    print(f"\n📈 Performance Overview:")
                    print(f"- Total Trades: {overview['total_trades']}")
                    print(f"- Win Rate: {overview['win_rate']}%")
                    print(f"- Total Return: {overview['total_return_percent']:+.1f}%")
                    print(f"- Profit Factor: {overview['profit_factor']}")

                elif command == "alerts":
                    results = dashboard.alert_system.process_alert_queue()
                    print(f"📨 Processed {results['processed']} alerts")

                elif command == "auto":
                    print("🤖 Starting auto mode...")
                    dashboard.start_auto_monitoring()
                    dashboard.dashboard_state["auto_mode"] = True

                elif command == "status":
                    dashboard.display_dashboard_status()

                elif command == "help":
                    dashboard.display_available_commands()

                elif command in ["stop", "exit", "quit"]:
                    break

                else:
                    print("❌ Unknown command. Type 'help' for available commands.")

            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error processing command: {e}")

    finally:
        dashboard.stop_dashboard()

if __name__ == "__main__":
    main()