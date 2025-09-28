#!/usr/bin/env python3
"""
Real-Time Performance Analytics Engine
Advanced performance tracking with attribution analysis and optimization
"""

import json
import os
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
import math

@dataclass
class TradeRecord:
    """Individual trade record for tracking"""
    timestamp: str
    symbol: str
    direction: str  # CALL/PUT
    entry_price: float
    exit_price: float
    quantity: int
    hold_time_minutes: int
    return_percent: float
    return_absolute: float
    consensus_score: int
    pattern_confidence: float
    system_attribution: Dict
    market_conditions: Dict
    profitable: bool

class PerformanceAnalytics:
    """Real-time performance analytics with system attribution"""

    def __init__(self):
        self.trade_history_file = ".spx/trade_history.jsonl"
        self.performance_summary_file = ".spx/performance_summary.json"
        self.system_attribution_file = ".spx/system_attribution.json"
        self.daily_performance_file = ".spx/daily_performance.json"
        self.trade_records = []
        self.load_trade_history()

    def load_trade_history(self):
        """Load existing trade history"""
        try:
            if os.path.exists(self.trade_history_file):
                with open(self.trade_history_file, 'r') as f:
                    for line in f:
                        if line.strip():
                            trade_data = json.loads(line)
                            self.trade_records.append(TradeRecord(**trade_data))
        except Exception as e:
            print(f"Error loading trade history: {e}")
            self.trade_records = []

    def record_trade(self, trade_data: Dict) -> TradeRecord:
        """Record a new trade with complete attribution"""
        try:
            # Calculate trade metrics
            entry_price = trade_data['entry_price']
            exit_price = trade_data['exit_price']
            quantity = trade_data.get('quantity', 1)

            return_absolute = (exit_price - entry_price) * quantity
            return_percent = ((exit_price - entry_price) / entry_price) * 100

            trade_record = TradeRecord(
                timestamp=trade_data.get('timestamp', datetime.now().isoformat()),
                symbol=trade_data['symbol'],
                direction=trade_data['direction'],
                entry_price=entry_price,
                exit_price=exit_price,
                quantity=quantity,
                hold_time_minutes=trade_data.get('hold_time_minutes', 0),
                return_percent=return_percent,
                return_absolute=return_absolute,
                consensus_score=trade_data.get('consensus_score', 0),
                pattern_confidence=trade_data.get('pattern_confidence', 0),
                system_attribution=trade_data.get('system_attribution', {}),
                market_conditions=trade_data.get('market_conditions', {}),
                profitable=return_percent > 0
            )

            # Add to records and save
            self.trade_records.append(trade_record)
            self._save_trade_record(trade_record)
            self._update_performance_summary()
            self._update_system_attribution()

            return trade_record

        except Exception as e:
            print(f"Error recording trade: {e}")
            return None

    def get_real_time_performance(self) -> Dict:
        """Get current real-time performance metrics"""
        if not self.trade_records:
            return self._empty_performance_metrics()

        try:
            # Filter trades by time periods
            today_trades = self._get_trades_by_period(days=0)
            week_trades = self._get_trades_by_period(days=7)
            month_trades = self._get_trades_by_period(days=30)
            all_trades = self.trade_records

            return {
                "overview": {
                    "total_trades": len(all_trades),
                    "total_return_percent": sum(t.return_percent for t in all_trades),
                    "total_return_absolute": sum(t.return_absolute for t in all_trades),
                    "win_rate": self._calculate_win_rate(all_trades),
                    "profit_factor": self._calculate_profit_factor(all_trades),
                    "sharpe_ratio": self._calculate_sharpe_ratio(all_trades),
                    "max_drawdown": self._calculate_max_drawdown(all_trades),
                    "average_hold_time": self._calculate_average_hold_time(all_trades)
                },
                "today": {
                    "trades": len(today_trades),
                    "return_percent": sum(t.return_percent for t in today_trades),
                    "win_rate": self._calculate_win_rate(today_trades),
                    "best_trade": self._get_best_trade(today_trades),
                    "worst_trade": self._get_worst_trade(today_trades)
                },
                "this_week": {
                    "trades": len(week_trades),
                    "return_percent": sum(t.return_percent for t in week_trades),
                    "win_rate": self._calculate_win_rate(week_trades),
                    "profit_factor": self._calculate_profit_factor(week_trades)
                },
                "this_month": {
                    "trades": len(month_trades),
                    "return_percent": sum(t.return_percent for t in month_trades),
                    "win_rate": self._calculate_win_rate(month_trades),
                    "sharpe_ratio": self._calculate_sharpe_ratio(month_trades)
                },
                "system_performance": self._get_system_performance(),
                "optimization_suggestions": self._get_optimization_suggestions()
            }

        except Exception as e:
            print(f"Error calculating real-time performance: {e}")
            return self._empty_performance_metrics()

    def get_system_attribution_analysis(self) -> Dict:
        """Analyze performance attribution by system components"""
        attribution = {
            "consensus_score_analysis": {},
            "pattern_confidence_analysis": {},
            "system_component_analysis": {},
            "market_condition_analysis": {},
            "recommendations": []
        }

        if not self.trade_records:
            return attribution

        try:
            # Consensus score analysis
            attribution["consensus_score_analysis"] = self._analyze_by_consensus_score()

            # Pattern confidence analysis
            attribution["pattern_confidence_analysis"] = self._analyze_by_pattern_confidence()

            # Individual system component analysis
            attribution["system_component_analysis"] = self._analyze_by_system_components()

            # Market condition analysis
            attribution["market_condition_analysis"] = self._analyze_by_market_conditions()

            # Generate optimization recommendations
            attribution["recommendations"] = self._generate_optimization_recommendations()

        except Exception as e:
            print(f"Error in system attribution analysis: {e}")

        return attribution

    def get_performance_trends(self) -> Dict:
        """Analyze performance trends and patterns"""
        trends = {
            "win_rate_trend": [],
            "return_trend": [],
            "volume_trend": [],
            "best_performing_periods": [],
            "worst_performing_periods": [],
            "performance_by_day_of_week": {},
            "performance_by_time_of_day": {}
        }

        if len(self.trade_records) < 5:
            return trends

        try:
            # Calculate rolling metrics
            trends["win_rate_trend"] = self._calculate_rolling_win_rate()
            trends["return_trend"] = self._calculate_rolling_returns()

            # Performance by day of week
            trends["performance_by_day_of_week"] = self._analyze_by_day_of_week()

            # Performance by time of day
            trends["performance_by_time_of_day"] = self._analyze_by_time_of_day()

            # Best and worst periods
            trends["best_performing_periods"] = self._find_best_periods()
            trends["worst_performing_periods"] = self._find_worst_periods()

        except Exception as e:
            print(f"Error calculating performance trends: {e}")

        return trends

    def get_risk_metrics(self) -> Dict:
        """Calculate comprehensive risk metrics"""
        if not self.trade_records:
            return {}

        returns = [t.return_percent for t in self.trade_records]

        try:
            return {
                "value_at_risk_95": self._calculate_var(returns, 0.95),
                "value_at_risk_99": self._calculate_var(returns, 0.99),
                "expected_shortfall_95": self._calculate_expected_shortfall(returns, 0.95),
                "maximum_drawdown": self._calculate_max_drawdown(self.trade_records),
                "volatility": statistics.stdev(returns) if len(returns) > 1 else 0,
                "downside_deviation": self._calculate_downside_deviation(returns),
                "calmar_ratio": self._calculate_calmar_ratio(),
                "sortino_ratio": self._calculate_sortino_ratio(returns),
                "beta": self._calculate_beta(),
                "tracking_error": self._calculate_tracking_error()
            }
        except Exception as e:
            print(f"Error calculating risk metrics: {e}")
            return {}

    def _get_trades_by_period(self, days: int) -> List[TradeRecord]:
        """Get trades from specified period"""
        if days == 0:  # Today only
            today = datetime.now().date()
            return [
                t for t in self.trade_records
                if datetime.fromisoformat(t.timestamp).date() == today
            ]
        else:
            cutoff = datetime.now() - timedelta(days=days)
            return [
                t for t in self.trade_records
                if datetime.fromisoformat(t.timestamp) >= cutoff
            ]

    def _calculate_win_rate(self, trades: List[TradeRecord]) -> float:
        """Calculate win rate for given trades"""
        if not trades:
            return 0.0
        winning_trades = sum(1 for t in trades if t.profitable)
        return round((winning_trades / len(trades)) * 100, 1)

    def _calculate_profit_factor(self, trades: List[TradeRecord]) -> float:
        """Calculate profit factor (gross profit / gross loss)"""
        if not trades:
            return 0.0

        gross_profit = sum(t.return_absolute for t in trades if t.profitable)
        gross_loss = abs(sum(t.return_absolute for t in trades if not t.profitable))

        if gross_loss == 0:
            return float('inf') if gross_profit > 0 else 0.0

        return round(gross_profit / gross_loss, 2)

    def _calculate_sharpe_ratio(self, trades: List[TradeRecord]) -> float:
        """Calculate Sharpe ratio"""
        if len(trades) < 2:
            return 0.0

        returns = [t.return_percent for t in trades]
        mean_return = statistics.mean(returns)
        std_return = statistics.stdev(returns)

        if std_return == 0:
            return 0.0

        return round(mean_return / std_return, 2)

    def _calculate_max_drawdown(self, trades: List[TradeRecord]) -> float:
        """Calculate maximum drawdown"""
        if not trades:
            return 0.0

        # Calculate cumulative returns
        cumulative_returns = []
        running_total = 0
        for trade in trades:
            running_total += trade.return_percent
            cumulative_returns.append(running_total)

        # Find maximum drawdown
        peak = cumulative_returns[0]
        max_drawdown = 0

        for return_val in cumulative_returns:
            if return_val > peak:
                peak = return_val
            drawdown = peak - return_val
            if drawdown > max_drawdown:
                max_drawdown = drawdown

        return round(max_drawdown, 2)

    def _calculate_average_hold_time(self, trades: List[TradeRecord]) -> float:
        """Calculate average hold time in minutes"""
        if not trades:
            return 0.0
        return round(statistics.mean([t.hold_time_minutes for t in trades]), 1)

    def _analyze_by_consensus_score(self) -> Dict:
        """Analyze performance by consensus score ranges"""
        score_ranges = {
            "250+": [],
            "225-249": [],
            "200-224": [],
            "175-199": [],
            "<175": []
        }

        for trade in self.trade_records:
            score = trade.consensus_score
            if score >= 250:
                score_ranges["250+"].append(trade)
            elif score >= 225:
                score_ranges["225-249"].append(trade)
            elif score >= 200:
                score_ranges["200-224"].append(trade)
            elif score >= 175:
                score_ranges["175-199"].append(trade)
            else:
                score_ranges["<175"].append(trade)

        analysis = {}
        for range_name, trades in score_ranges.items():
            if trades:
                analysis[range_name] = {
                    "trades": len(trades),
                    "win_rate": self._calculate_win_rate(trades),
                    "average_return": round(statistics.mean([t.return_percent for t in trades]), 2),
                    "profit_factor": self._calculate_profit_factor(trades)
                }

        return analysis

    def _analyze_by_pattern_confidence(self) -> Dict:
        """Analyze performance by pattern confidence levels"""
        confidence_ranges = {
            "90+": [],
            "80-89": [],
            "70-79": [],
            "<70": []
        }

        for trade in self.trade_records:
            confidence = trade.pattern_confidence
            if confidence >= 90:
                confidence_ranges["90+"].append(trade)
            elif confidence >= 80:
                confidence_ranges["80-89"].append(trade)
            elif confidence >= 70:
                confidence_ranges["70-79"].append(trade)
            else:
                confidence_ranges["<70"].append(trade)

        analysis = {}
        for range_name, trades in confidence_ranges.items():
            if trades:
                analysis[range_name] = {
                    "trades": len(trades),
                    "win_rate": self._calculate_win_rate(trades),
                    "average_return": round(statistics.mean([t.return_percent for t in trades]), 2)
                }

        return analysis

    def _generate_optimization_recommendations(self) -> List[str]:
        """Generate performance optimization recommendations"""
        recommendations = []

        if not self.trade_records:
            return recommendations

        try:
            # Analyze consensus score performance
            consensus_analysis = self._analyze_by_consensus_score()

            # Recommend higher consensus thresholds if beneficial
            if "250+" in consensus_analysis and "200-224" in consensus_analysis:
                high_score_wr = consensus_analysis["250+"]["win_rate"]
                medium_score_wr = consensus_analysis["200-224"]["win_rate"]

                if high_score_wr > medium_score_wr + 10:
                    recommendations.append(
                        f"Consider raising consensus threshold to 250+ "
                        f"(Win rate: {high_score_wr}% vs {medium_score_wr}%)"
                    )

            # Analyze hold time optimization
            avg_hold_time = self._calculate_average_hold_time(self.trade_records)
            if avg_hold_time > 60:
                recommendations.append(
                    f"Consider shorter hold times (current average: {avg_hold_time:.1f} minutes)"
                )

            # Win rate recommendations
            overall_win_rate = self._calculate_win_rate(self.trade_records)
            if overall_win_rate < 70:
                recommendations.append(
                    f"Focus on improving signal quality (current win rate: {overall_win_rate}%)"
                )

            # Pattern confidence recommendations
            pattern_analysis = self._analyze_by_pattern_confidence()
            if "90+" in pattern_analysis:
                high_conf_wr = pattern_analysis["90+"]["win_rate"]
                if high_conf_wr > overall_win_rate + 15:
                    recommendations.append(
                        f"Prioritize trades with 90%+ pattern confidence "
                        f"(Win rate: {high_conf_wr}% vs overall {overall_win_rate}%)"
                    )

        except Exception as e:
            print(f"Error generating recommendations: {e}")

        return recommendations

    def _empty_performance_metrics(self) -> Dict:
        """Return empty performance metrics structure"""
        return {
            "overview": {
                "total_trades": 0,
                "total_return_percent": 0,
                "win_rate": 0,
                "profit_factor": 0,
                "sharpe_ratio": 0
            },
            "today": {"trades": 0, "return_percent": 0},
            "this_week": {"trades": 0, "return_percent": 0},
            "this_month": {"trades": 0, "return_percent": 0}
        }

    def _save_trade_record(self, trade_record: TradeRecord):
        """Save trade record to JSONL file"""
        try:
            os.makedirs(".spx", exist_ok=True)
            with open(self.trade_history_file, 'a') as f:
                f.write(json.dumps(asdict(trade_record)) + '\n')
        except Exception as e:
            print(f"Error saving trade record: {e}")

    def _update_performance_summary(self):
        """Update performance summary file"""
        try:
            performance = self.get_real_time_performance()
            with open(self.performance_summary_file, 'w') as f:
                json.dump(performance, f, indent=2)
        except Exception as e:
            print(f"Error updating performance summary: {e}")

    def _update_system_attribution(self):
        """Update system attribution analysis"""
        try:
            attribution = self.get_system_attribution_analysis()
            with open(self.system_attribution_file, 'w') as f:
                json.dump(attribution, f, indent=2)
        except Exception as e:
            print(f"Error updating system attribution: {e}")

    def get_performance_dashboard_data(self) -> Dict:
        """Get all data needed for performance dashboard"""
        return {
            "real_time_performance": self.get_real_time_performance(),
            "system_attribution": self.get_system_attribution_analysis(),
            "performance_trends": self.get_performance_trends(),
            "risk_metrics": self.get_risk_metrics(),
            "recent_trades": [asdict(t) for t in self.trade_records[-10:]],
            "last_updated": datetime.now().isoformat()
        }

def main():
    """Test Performance Analytics Engine"""
    analytics = PerformanceAnalytics()

    print("📊 Performance Analytics Engine Test")
    print("=" * 50)

    # Sample trade data
    sample_trades = [
        {
            "symbol": "SPXW6650C",
            "direction": "CALL",
            "entry_price": 5.50,
            "exit_price": 8.25,
            "quantity": 10,
            "hold_time_minutes": 45,
            "consensus_score": 245,
            "pattern_confidence": 87.5,
            "system_attribution": {
                "ema_contribution": 18,
                "pattern_contribution": 22,
                "momentum_contribution": 15
            },
            "market_conditions": {
                "vix": 18.5,
                "market_regime": "TRENDING_BULL"
            }
        },
        {
            "symbol": "SPXW6640P",
            "direction": "PUT",
            "entry_price": 3.25,
            "exit_price": 2.10,
            "quantity": 15,
            "hold_time_minutes": 30,
            "consensus_score": 210,
            "pattern_confidence": 72.0,
            "system_attribution": {
                "ema_contribution": 15,
                "pattern_contribution": 18,
                "momentum_contribution": 12
            },
            "market_conditions": {
                "vix": 22.1,
                "market_regime": "HIGH_VOLATILITY"
            }
        }
    ]

    # Record sample trades
    for trade_data in sample_trades:
        trade_record = analytics.record_trade(trade_data)
        if trade_record:
            print(f"✅ Recorded trade: {trade_record.symbol} "
                  f"({trade_record.return_percent:+.1f}%)")

    # Get performance metrics
    performance = analytics.get_real_time_performance()
    print(f"\n📈 Performance Overview:")
    print(f"- Total Trades: {performance['overview']['total_trades']}")
    print(f"- Win Rate: {performance['overview']['win_rate']}%")
    print(f"- Total Return: {performance['overview']['total_return_percent']:+.1f}%")
    print(f"- Profit Factor: {performance['overview']['profit_factor']}")

    # Get system attribution
    attribution = analytics.get_system_attribution_analysis()
    if attribution['recommendations']:
        print(f"\n💡 Optimization Recommendations:")
        for rec in attribution['recommendations']:
            print(f"- {rec}")

    print("\n✅ Performance Analytics Engine initialized successfully!")

if __name__ == "__main__":
    main()