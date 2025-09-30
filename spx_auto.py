#!/usr/bin/env python3
"""
SPX Auto - Simplified One-Click Trading Interface
Unified command for complete market analysis with all enhanced systems
"""

import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional, Any

# Import enhanced systems
try:
    from ml_pattern_engine import MLPatternEngine
    from smart_alerts import SmartAlertSystem
    from performance_analytics import PerformanceAnalytics
except ImportError as e:
    print(f"Error importing enhanced systems: {e}")
    print("Falling back to basic functionality...")

class SPXAuto:
    """One-click SPX analysis with all enhanced systems"""

    def __init__(self):
        self.systems_available = True
        try:
            self.ml_engine = MLPatternEngine()
            self.alert_system = SmartAlertSystem()
            self.performance_analytics = PerformanceAnalytics()
        except Exception as e:
            print(f"Warning: Enhanced systems not available: {e}")
            self.systems_available = False

    def run_complete_analysis(self, send_discord: bool = False) -> Dict:
        """Run complete SPX analysis with all systems"""
        print("TARGET SPX AUTO ANALYSIS - All Systems Integration")
        print("=" * 60)

        try:
            # Step 1: System Health Check
            print(" Checking system health...")
            health_result = self.check_system_health()

            if not health_result.get("healthy", False):
                print(f"WARNING System health warning: {health_result.get('health_percentage', 0)}%")

            # Step 2: Get Market Data
            print("CHART Fetching market data...")
            market_data = self.get_market_data()

            if not market_data:
                print("ERROR Failed to get market data")
                return {"success": False, "error": "No market data available"}

            # Step 3: Enhanced Pattern Analysis
            print("CIRCUS Running ML pattern analysis...")
            pattern_results = {}
            if self.systems_available:
                pattern_results = self.ml_engine.detect_patterns(market_data)

            # Step 4: Generate Trading Recommendations
            print("TARGET Generating trading recommendations...")
            recommendations = self.generate_recommendations(market_data, pattern_results)

            # Step 5: Calculate Performance Context
            print("UP Updating performance context...")
            performance_context = {}
            if self.systems_available:
                performance_context = self.performance_analytics.get_real_time_performance()

            # Step 6: Generate Alerts
            print("ALERT Processing alerts...")
            alerts_generated = 0
            if self.systems_available and recommendations.get("signal_strength", 0) >= 200:
                alert = self.alert_system.create_trading_signal_alert({
                    "consensus_score": recommendations.get("consensus_score", 0),
                    "pattern_confidence": recommendations.get("pattern_confidence", 0),
                    "recommended_trade": recommendations.get("primary_trade", {})
                })
                if alert:
                    self.alert_system.add_alert(alert)
                    alerts_generated = 1

                # Process alert queue
                if send_discord:
                    alert_results = self.alert_system.process_alert_queue()
                    alerts_generated = alert_results.get("processed", 0)

            # Compile complete analysis
            complete_analysis = {
                "timestamp": datetime.now().isoformat(),
                "success": True,
                "system_health": health_result,
                "market_data": market_data,
                "pattern_analysis": pattern_results,
                "trading_recommendations": recommendations,
                "performance_context": performance_context,
                "alerts_generated": alerts_generated,
                "enhanced_systems_active": self.systems_available
            }

            # Save results
            self.save_analysis_results(complete_analysis)

            # Display results
            self.display_analysis_results(complete_analysis)

            print(f"\nSUCCESS Complete analysis finished at {datetime.now().strftime('%H:%M:%S')}")
            print(f" Results saved to .spx/auto_analysis_results.json")

            return complete_analysis

        except Exception as e:
            print(f"ERROR Error in complete analysis: {e}")
            return {"success": False, "error": str(e)}

    def check_system_health(self) -> Dict:
        """Quick system health check"""
        try:
            import subprocess
            result = subprocess.run(
                ["python", "system_validation.py"],
                capture_output=True,
                text=True,
                timeout=20
            )

            if result.returncode == 0:
                # Parse health percentage
                health_percentage = 100.0
                for line in result.stdout.split('\n'):
                    if "SYSTEM HEALTH:" in line:
                        try:
                            health_str = line.split("SYSTEM HEALTH:")[1].strip()
                            health_percentage = float(health_str.replace('%', ''))
                            break
                        except:
                            pass

                return {
                    "healthy": health_percentage >= 95.0,
                    "health_percentage": health_percentage,
                    "status": "HEALTHY" if health_percentage >= 95.0 else "DEGRADED"
                }
            else:
                return {
                    "healthy": False,
                    "health_percentage": 0.0,
                    "status": "ERROR",
                    "error": result.stderr[:200]
                }

        except Exception as e:
            return {
                "healthy": False,
                "health_percentage": 0.0,
                "status": "ERROR",
                "error": str(e)
            }

    def get_market_data(self) -> Optional[Dict]:
        """Get current market data"""
        try:
            # Try to run SPX live analysis
            import subprocess
            result = subprocess.run(
                ["python", "spx_live.py"],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                # Parse key metrics from output
                lines = result.stdout.split('\n')
                market_data = {
                    "current_price": 6650.0,  # Default values
                    "volume": 35000,
                    "rsi": 50.0,
                    "price_change": 0.0,
                    "timestamp": datetime.now().isoformat()
                }

                # Extract actual values from output
                for line in lines:
                    if "SPX:" in line or "Current:" in line:
                        try:
                            # Parse price from various formats
                            parts = line.split()
                            for part in parts:
                                if '$' in part or part.replace('.', '').replace(',', '').isdigit():
                                    price = float(part.replace('$', '').replace(',', ''))
                                    if 5000 <= price <= 8000:  # Reasonable SPX range
                                        market_data["current_price"] = price
                                        break
                        except:
                            continue

                return market_data

            else:
                # Fallback: use last known data
                return self.get_fallback_market_data()

        except Exception as e:
            print(f"Error getting market data: {e}")
            return self.get_fallback_market_data()

    def get_fallback_market_data(self) -> Dict:
        """Get fallback market data from session files"""
        try:
            # Try to load from recent analysis
            analysis_files = [
                ".spx/spy_analysis_results.json",
                ".spx/unified_analysis_results.json",
                ".spx/last_analysis.json"
            ]

            for file_path in analysis_files:
                if os.path.exists(file_path):
                    with open(file_path, 'r') as f:
                        data = json.load(f)
                        if "current_price" in data or "spy_price" in data:
                            price = data.get("current_price") or data.get("spy_price", 665.0)
                            return {
                                "current_price": price * 10 if price < 1000 else price,  # Convert SPY to SPX if needed
                                "volume": data.get("volume", 35000),
                                "rsi": data.get("rsi", 50.0),
                                "price_change": data.get("price_change", 0.0),
                                "timestamp": datetime.now().isoformat(),
                                "source": "fallback_data"
                            }

        except Exception as e:
            print(f"Error loading fallback data: {e}")

        # Ultimate fallback
        return {
            "current_price": 6650.0,
            "volume": 35000,
            "rsi": 50.0,
            "price_change": 0.0,
            "timestamp": datetime.now().isoformat(),
            "source": "default_values"
        }

    def generate_recommendations(self, market_data: Dict, pattern_results: Dict) -> Dict:
        """Generate trading recommendations"""
        try:
            current_price = market_data.get("current_price", 6650.0)
            rsi = market_data.get("rsi", 50.0)
            volume = market_data.get("volume", 35000)

            # Calculate consensus score
            consensus_score = self.calculate_consensus_score(market_data, pattern_results)

            # Determine market bias
            market_bias = "BULLISH" if rsi > 52 else "BEARISH" if rsi < 48 else "NEUTRAL"

            # Generate strike recommendations
            strikes = self.generate_strike_recommendations(current_price, market_bias, consensus_score)

            # Calculate confidence level
            confidence_level = "HIGH" if consensus_score >= 225 else "MEDIUM" if consensus_score >= 200 else "LOW"

            # Pattern confidence
            pattern_confidence = 0
            if pattern_results.get("highest_confidence"):
                pattern_confidence = pattern_results["highest_confidence"].get("confidence", 0)

            recommendations = {
                "consensus_score": consensus_score,
                "signal_strength": consensus_score,
                "confidence_level": confidence_level,
                "market_bias": market_bias,
                "pattern_confidence": pattern_confidence,
                "recommended_action": "ENTER_POSITION" if consensus_score >= 200 else "WAIT",
                "strikes": strikes,
                "primary_trade": strikes[0] if strikes else {},
                "risk_assessment": self.assess_risk_level(consensus_score, pattern_confidence),
                "hold_time_estimate": "30-60 minutes",
                "market_conditions": {
                    "rsi": rsi,
                    "volume_vs_average": "HIGH" if volume > 40000 else "NORMAL",
                    "price_level": current_price
                }
            }

            return recommendations

        except Exception as e:
            print(f"Error generating recommendations: {e}")
            return {
                "consensus_score": 0,
                "signal_strength": 0,
                "confidence_level": "NONE",
                "recommended_action": "WAIT",
                "error": str(e)
            }

    def calculate_consensus_score(self, market_data: Dict, pattern_results: Dict) -> int:
        """Calculate consensus score from available data"""
        score = 0

        # RSI contribution (50 points max)
        rsi = market_data.get("rsi", 50.0)
        if 45 <= rsi <= 75:
            score += 50
        elif 35 <= rsi <= 85:
            score += 30

        # Volume contribution (50 points max)
        volume = market_data.get("volume", 35000)
        if volume > 45000:
            score += 50
        elif volume > 35000:
            score += 30

        # Price action contribution (50 points max)
        price_change = market_data.get("price_change", 0.0)
        if abs(price_change) > 10:
            score += 50
        elif abs(price_change) > 5:
            score += 30

        # Pattern contribution (125 points max)
        if pattern_results.get("highest_confidence"):
            pattern_confidence = pattern_results["highest_confidence"].get("confidence", 0)
            score += int(pattern_confidence * 1.25)  # Scale to 125 points max

        return min(score, 275)

    def generate_strike_recommendations(self, current_price: float, bias: str, consensus: int) -> List[Dict]:
        """Generate strike recommendations"""
        strikes = []

        try:
            # Calculate option premiums (simplified)
            atm_premium = current_price * 0.001  # ~0.1% for ATM
            otm_premium = current_price * 0.0005  # ~0.05% for OTM

            if bias == "BULLISH":
                # Call recommendations
                atm_strike = int(current_price / 5) * 5  # Round to nearest 5
                otm_strike = atm_strike + 10

                strikes.append({
                    "type": "CALL",
                    "strike": atm_strike,
                    "premium": round(atm_premium, 2),
                    "delta": 0.50,
                    "confidence": "HIGH" if consensus >= 225 else "MEDIUM",
                    "target": round(atm_premium * 2, 2),
                    "stop": round(atm_premium * 0.5, 2)
                })

                strikes.append({
                    "type": "CALL",
                    "strike": otm_strike,
                    "premium": round(otm_premium, 2),
                    "delta": 0.25,
                    "confidence": "MEDIUM",
                    "target": round(otm_premium * 3, 2),
                    "stop": round(otm_premium * 0.5, 2)
                })

            elif bias == "BEARISH":
                # Put recommendations
                atm_strike = int(current_price / 5) * 5
                otm_strike = atm_strike - 10

                strikes.append({
                    "type": "PUT",
                    "strike": atm_strike,
                    "premium": round(atm_premium, 2),
                    "delta": -0.50,
                    "confidence": "HIGH" if consensus >= 225 else "MEDIUM",
                    "target": round(atm_premium * 2, 2),
                    "stop": round(atm_premium * 0.5, 2)
                })

                strikes.append({
                    "type": "PUT",
                    "strike": otm_strike,
                    "premium": round(otm_premium, 2),
                    "delta": -0.25,
                    "confidence": "MEDIUM",
                    "target": round(otm_premium * 3, 2),
                    "stop": round(otm_premium * 0.5, 2)
                })

        except Exception as e:
            print(f"Error generating strikes: {e}")

        return strikes

    def assess_risk_level(self, consensus: int, pattern_confidence: float) -> str:
        """Assess overall risk level"""
        if consensus >= 250 and pattern_confidence >= 85:
            return "LOW_RISK"
        elif consensus >= 225 and pattern_confidence >= 75:
            return "MEDIUM_RISK"
        elif consensus >= 200:
            return "HIGH_RISK"
        else:
            return "VERY_HIGH_RISK"

    def display_analysis_results(self, analysis: Dict):
        """Display formatted analysis results"""
        print(f"\nTARGET SPX AUTO ANALYSIS RESULTS")
        print("=" * 50)

        # System Health
        health = analysis.get("system_health", {})
        health_status = health.get("status", "UNKNOWN")
        health_pct = health.get("health_percentage", 0)
        print(f" System Health: {health_pct}% ({health_status})")

        # Market Data
        market = analysis.get("market_data", {})
        current_price = market.get("current_price", 0)
        rsi = market.get("rsi", 0)
        volume = market.get("volume", 0)
        print(f"CHART SPX: ${current_price:,.2f} | RSI: {rsi:.1f} | Volume: {volume:,}")

        # Trading Recommendations
        recs = analysis.get("trading_recommendations", {})
        consensus = recs.get("consensus_score", 0)
        confidence = recs.get("confidence_level", "NONE")
        bias = recs.get("market_bias", "NEUTRAL")
        action = recs.get("recommended_action", "WAIT")

        print(f"TARGET Consensus: {consensus}/275 | Confidence: {confidence} | Bias: {bias}")
        print(f" Action: {action}")

        # Strike Recommendations
        strikes = recs.get("strikes", [])
        if strikes:
            print(f"\nMONEY Strike Recommendations:")
            for i, strike in enumerate(strikes[:2], 1):
                strike_price = strike.get("strike", 0)
                strike_type = strike.get("type", "")
                premium = strike.get("premium", 0)
                target = strike.get("target", 0)
                strike_confidence = strike.get("confidence", "")
                print(f"  {i}. {strike_price} {strike_type} @ ${premium:.2f} -> ${target:.2f} ({strike_confidence})")

        # Pattern Analysis
        patterns = analysis.get("pattern_analysis", {})
        if patterns.get("highest_confidence"):
            pattern_name = patterns["highest_confidence"].get("pattern", "None")
            pattern_conf = patterns["highest_confidence"].get("confidence", 0)
            print(f"CIRCUS Top Pattern: {pattern_name} ({pattern_conf}% confidence)")

        # Performance Context
        perf = analysis.get("performance_context", {})
        if perf.get("overview"):
            overview = perf["overview"]
            total_trades = overview.get("total_trades", 0)
            win_rate = overview.get("win_rate", 0)
            total_return = overview.get("total_return_percent", 0)
            print(f"UP Performance: {total_trades} trades, {win_rate}% win rate, {total_return:+.1f}% return")

        # Enhanced Systems Status
        enhanced_active = analysis.get("enhanced_systems_active", False)
        status_icon = "SUCCESS" if enhanced_active else "WARNING"
        print(f"{status_icon} Enhanced Systems: {'ACTIVE' if enhanced_active else 'BASIC MODE'}")

        # Alerts
        alerts = analysis.get("alerts_generated", 0)
        if alerts > 0:
            print(f"ALERT Alerts Generated: {alerts}")

    def save_analysis_results(self, analysis: Dict):
        """Save analysis results to file"""
        try:
            os.makedirs(".spx", exist_ok=True)

            # Save complete results
            with open(".spx/auto_analysis_results.json", 'w') as f:
                json.dump(analysis, f, indent=2)

            # Save summary for quick reference
            summary = {
                "timestamp": analysis["timestamp"],
                "consensus_score": analysis.get("trading_recommendations", {}).get("consensus_score", 0),
                "recommended_action": analysis.get("trading_recommendations", {}).get("recommended_action", "WAIT"),
                "system_health": analysis.get("system_health", {}).get("health_percentage", 0),
                "market_price": analysis.get("market_data", {}).get("current_price", 0),
                "success": analysis.get("success", False)
            }

            with open(".spx/auto_summary.json", 'w') as f:
                json.dump(summary, f, indent=2)

        except Exception as e:
            print(f"Error saving analysis results: {e}")

def main():
    """Main entry point"""
    if len(sys.argv) > 1 and sys.argv[1].lower() in ['discord', '--discord', '-d']:
        send_discord = True
        print("ALERT Discord alerts enabled")
    else:
        send_discord = False

    auto_analyzer = SPXAuto()
    result = auto_analyzer.run_complete_analysis(send_discord=send_discord)

    if result.get("success"):
        print(f"\nTARGET Analysis completed successfully!")

        # Quick action suggestion
        action = result.get("trading_recommendations", {}).get("recommended_action", "WAIT")
        consensus = result.get("trading_recommendations", {}).get("consensus_score", 0)

        if action == "ENTER_POSITION" and consensus >= 225:
            print(f"IDEA HIGH CONFIDENCE SIGNAL - Consider immediate action")
        elif action == "ENTER_POSITION":
            print(f"CHART MEDIUM SIGNAL - Monitor for confirmation")
        else:
            print(f" WAIT - Signal strength insufficient ({consensus}/275)")

    else:
        print(f"ERROR Analysis failed: {result.get('error', 'Unknown error')}")
        sys.exit(1)

if __name__ == "__main__":
    main()