#!/usr/bin/env python3
"""
Volatility Intelligence Engine
Advanced volatility analysis with regime detection and VIX term structure
"""

import json
import os
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import math

@dataclass
class VolatilityRegime:
    """Volatility regime classification"""
    regime_type: str
    vix_level: float
    realized_vol: float
    vol_percentile: float
    regime_confidence: float
    expected_duration: str
    trading_implications: List[str]

@dataclass
class VolatilitySignal:
    """Volatility-based trading signal"""
    signal_type: str
    strength: float
    direction: str
    reasoning: str
    optimal_strategies: List[str]
    risk_adjustment: float

class VolatilityIntelligence:
    """Advanced volatility analysis and regime detection"""

    def __init__(self):
        self.vix_history_file = ".spx/vix_history.json"
        self.volatility_analysis_file = ".spx/volatility_analysis.json"
        self.regime_history_file = ".spx/volatility_regimes.json"
        self.load_historical_data()

    def load_historical_data(self):
        """Load historical volatility data"""
        try:
            if os.path.exists(self.vix_history_file):
                with open(self.vix_history_file, 'r') as f:
                    self.vix_history = json.load(f)
            else:
                self.vix_history = self.initialize_vix_history()

            if os.path.exists(self.regime_history_file):
                with open(self.regime_history_file, 'r') as f:
                    self.regime_history = json.load(f)
            else:
                self.regime_history = []

        except Exception as e:
            print(f"Error loading volatility data: {e}")
            self.vix_history = self.initialize_vix_history()
            self.regime_history = []

    def initialize_vix_history(self) -> Dict:
        """Initialize VIX historical reference data"""
        return {
            "percentiles": {
                "5th": 12.0,
                "10th": 13.5,
                "25th": 16.0,
                "50th": 19.5,
                "75th": 24.0,
                "90th": 28.5,
                "95th": 32.0
            },
            "regime_thresholds": {
                "ultra_low": 12.0,
                "low": 16.0,
                "normal": 20.0,
                "elevated": 25.0,
                "high": 30.0,
                "extreme": 35.0
            },
            "mean_reversion_levels": {
                "strong_support": 15.0,
                "support": 18.0,
                "resistance": 25.0,
                "strong_resistance": 30.0
            }
        }

    def analyze_volatility_environment(self, market_data: Dict) -> Dict:
        """Comprehensive volatility environment analysis"""
        try:
            current_vix = market_data.get('vix', 20.0)
            spx_price = market_data.get('current_price', 6650.0)
            volume = market_data.get('volume', 35000)

            # Calculate realized volatility from price data
            realized_vol = self.calculate_realized_volatility(market_data)

            # Determine current regime
            current_regime = self.classify_volatility_regime(current_vix, realized_vol)

            # Analyze VIX term structure implications
            term_structure = self.analyze_vix_term_structure(current_vix)

            # Generate volatility signals
            vol_signals = self.generate_volatility_signals(current_vix, realized_vol, current_regime)

            # Calculate volatility risk adjustments
            risk_adjustments = self.calculate_risk_adjustments(current_regime, vol_signals)

            # Predict regime changes
            regime_prediction = self.predict_regime_changes(current_vix, realized_vol)

            analysis = {
                "timestamp": datetime.now().isoformat(),
                "current_vix": current_vix,
                "realized_volatility": realized_vol,
                "vix_percentile": self.calculate_vix_percentile(current_vix),
                "regime_classification": current_regime.__dict__,
                "term_structure_analysis": term_structure,
                "volatility_signals": [signal.__dict__ for signal in vol_signals],
                "risk_adjustments": risk_adjustments,
                "regime_prediction": regime_prediction,
                "trading_recommendations": self.generate_volatility_trading_recommendations(
                    current_regime, vol_signals, term_structure
                ),
                "position_sizing_adjustments": self.calculate_position_sizing_adjustments(current_regime)
            }

            # Save analysis
            self.save_volatility_analysis(analysis)

            return analysis

        except Exception as e:
            print(f"Error in volatility analysis: {e}")
            return self.get_default_volatility_analysis()

    def classify_volatility_regime(self, vix_level: float, realized_vol: float) -> VolatilityRegime:
        """Classify current volatility regime"""
        thresholds = self.vix_history["regime_thresholds"]

        if vix_level < thresholds["ultra_low"]:
            regime_type = "ULTRA_LOW_VOL"
            implications = [
                "High probability of volatility expansion",
                "Consider long volatility strategies",
                "Reduce position sizes due to complacency risk",
                "Monitor for volatility breakouts"
            ]
            expected_duration = "1-3 weeks"
            confidence = 0.85

        elif vix_level < thresholds["low"]:
            regime_type = "LOW_VOL"
            implications = [
                "Favorable for momentum strategies",
                "Consider selling volatility on spikes",
                "Normal position sizing acceptable",
                "Watch for trend continuation"
            ]
            expected_duration = "2-6 weeks"
            confidence = 0.80

        elif vix_level < thresholds["normal"]:
            regime_type = "NORMAL_VOL"
            implications = [
                "Balanced environment for most strategies",
                "Standard risk management applies",
                "Consider both direction and volatility plays",
                "Monitor for regime shifts"
            ]
            expected_duration = "1-3 months"
            confidence = 0.75

        elif vix_level < thresholds["elevated"]:
            regime_type = "ELEVATED_VOL"
            implications = [
                "Increased caution recommended",
                "Shorter holding periods",
                "Consider volatility selling opportunities",
                "Enhanced risk management"
            ]
            expected_duration = "1-4 weeks"
            confidence = 0.80

        elif vix_level < thresholds["high"]:
            regime_type = "HIGH_VOL"
            implications = [
                "High risk environment",
                "Reduce position sizes by 50%",
                "Consider defensive strategies",
                "Monitor for mean reversion signals"
            ]
            expected_duration = "1-2 weeks"
            confidence = 0.85

        else:
            regime_type = "EXTREME_VOL"
            implications = [
                "Crisis-level volatility",
                "Minimal position sizes only",
                "Focus on survival over profits",
                "Expect violent mean reversion"
            ]
            expected_duration = "Days to 2 weeks"
            confidence = 0.90

        # Calculate volatility percentile
        vol_percentile = self.calculate_vix_percentile(vix_level)

        return VolatilityRegime(
            regime_type=regime_type,
            vix_level=vix_level,
            realized_vol=realized_vol,
            vol_percentile=vol_percentile,
            regime_confidence=confidence,
            expected_duration=expected_duration,
            trading_implications=implications
        )

    def analyze_vix_term_structure(self, current_vix: float) -> Dict:
        """Analyze VIX term structure implications"""
        # Simplified term structure analysis
        # In production, would use actual VIX futures data

        # Estimate forward curve based on current VIX
        front_month = current_vix
        second_month = current_vix * 0.95  # Typically in backwardation during stress
        third_month = current_vix * 0.90

        if front_month > second_month:
            structure_type = "BACKWARDATION"
            implications = [
                "Stress environment - high short-term volatility",
                "Expect volatility to decline over time",
                "Favorable for volatility selling strategies",
                "Time decay benefits volatility sellers"
            ]
            confidence = 0.75
        else:
            structure_type = "CONTANGO"
            implications = [
                "Normal market conditions",
                "Volatility expected to rise over time",
                "Consider volatility buying strategies",
                "Time decay hurts volatility buyers"
            ]
            confidence = 0.70

        return {
            "structure_type": structure_type,
            "front_month_vix": front_month,
            "second_month_estimate": second_month,
            "slope": (second_month - front_month) / front_month * 100,
            "implications": implications,
            "confidence": confidence
        }

    def generate_volatility_signals(self, vix_level: float, realized_vol: float, regime: VolatilityRegime) -> List[VolatilitySignal]:
        """Generate volatility-based trading signals"""
        signals = []

        try:
            # VIX mean reversion signal
            mean_reversion_signal = self.analyze_vix_mean_reversion(vix_level)
            if mean_reversion_signal:
                signals.append(mean_reversion_signal)

            # Volatility breakout signal
            breakout_signal = self.analyze_volatility_breakout(vix_level, realized_vol)
            if breakout_signal:
                signals.append(breakout_signal)

            # Regime change signal
            regime_signal = self.analyze_regime_change_signal(regime)
            if regime_signal:
                signals.append(regime_signal)

            # Volatility skew signal
            skew_signal = self.analyze_volatility_skew(vix_level)
            if skew_signal:
                signals.append(skew_signal)

        except Exception as e:
            print(f"Error generating volatility signals: {e}")

        return signals

    def analyze_vix_mean_reversion(self, vix_level: float) -> Optional[VolatilitySignal]:
        """Analyze VIX mean reversion opportunities"""
        mean_reversion_levels = self.vix_history["mean_reversion_levels"]

        if vix_level >= mean_reversion_levels["strong_resistance"]:
            return VolatilitySignal(
                signal_type="VIX_MEAN_REVERSION",
                strength=0.85,
                direction="DOWN",
                reasoning=f"VIX at {vix_level} above strong resistance {mean_reversion_levels['strong_resistance']}",
                optimal_strategies=["Short VIX ETFs", "Sell volatility", "Calendar spreads"],
                risk_adjustment=0.3  # Reduce risk due to volatility
            )
        elif vix_level >= mean_reversion_levels["resistance"]:
            return VolatilitySignal(
                signal_type="VIX_MEAN_REVERSION",
                strength=0.65,
                direction="DOWN",
                reasoning=f"VIX at {vix_level} above resistance {mean_reversion_levels['resistance']}",
                optimal_strategies=["Consider volatility selling", "Short-term puts"],
                risk_adjustment=0.2
            )
        elif vix_level <= mean_reversion_levels["support"]:
            return VolatilitySignal(
                signal_type="VIX_EXPANSION",
                strength=0.70,
                direction="UP",
                reasoning=f"VIX at {vix_level} near support {mean_reversion_levels['support']}",
                optimal_strategies=["Long volatility", "Protective puts", "Straddles"],
                risk_adjustment=-0.1  # Slightly increase risk tolerance
            )

        return None

    def analyze_volatility_breakout(self, vix_level: float, realized_vol: float) -> Optional[VolatilitySignal]:
        """Analyze volatility breakout patterns"""
        vol_ratio = vix_level / realized_vol if realized_vol > 0 else 1.0

        if vol_ratio > 1.5:  # VIX significantly above realized
            return VolatilitySignal(
                signal_type="VOLATILITY_OVERSHOOT",
                strength=0.75,
                direction="DOWN",
                reasoning=f"VIX/Realized ratio {vol_ratio:.2f} indicates fear overshoot",
                optimal_strategies=["Sell volatility premium", "Short straddles", "Iron condors"],
                risk_adjustment=0.25
            )
        elif vol_ratio < 0.8:  # VIX below realized (rare)
            return VolatilitySignal(
                signal_type="VOLATILITY_UNDERPRICING",
                strength=0.80,
                direction="UP",
                reasoning=f"VIX/Realized ratio {vol_ratio:.2f} indicates complacency",
                optimal_strategies=["Buy volatility", "Long straddles", "Protective strategies"],
                risk_adjustment=-0.2
            )

        return None

    def analyze_regime_change_signal(self, regime: VolatilityRegime) -> Optional[VolatilitySignal]:
        """Analyze potential volatility regime changes"""
        if regime.regime_type in ["ULTRA_LOW_VOL", "LOW_VOL"] and regime.regime_confidence > 0.8:
            return VolatilitySignal(
                signal_type="REGIME_CHANGE_WARNING",
                strength=0.70,
                direction="UP",
                reasoning="Low volatility regime at high confidence - expansion risk",
                optimal_strategies=["Long volatility hedges", "Tail risk protection"],
                risk_adjustment=0.15
            )
        elif regime.regime_type in ["HIGH_VOL", "EXTREME_VOL"] and regime.regime_confidence > 0.8:
            return VolatilitySignal(
                signal_type="REGIME_NORMALIZATION",
                strength=0.75,
                direction="DOWN",
                reasoning="High volatility regime at high confidence - normalization expected",
                optimal_strategies=["Volatility selling", "Mean reversion plays"],
                risk_adjustment=0.3
            )

        return None

    def analyze_volatility_skew(self, vix_level: float) -> Optional[VolatilitySignal]:
        """Analyze volatility skew implications"""
        # Simplified skew analysis based on VIX level
        if vix_level > 25:  # High VIX typically means steep skew
            return VolatilitySignal(
                signal_type="HIGH_SKEW_ENVIRONMENT",
                strength=0.60,
                direction="NEUTRAL",
                reasoning="High VIX environment typically shows steep put skew",
                optimal_strategies=["Sell put spreads", "Call calendar spreads"],
                risk_adjustment=0.2
            )
        elif vix_level < 15:  # Low VIX typically means flat skew
            return VolatilitySignal(
                signal_type="LOW_SKEW_ENVIRONMENT",
                strength=0.55,
                direction="NEUTRAL",
                reasoning="Low VIX environment - consider skew-neutral strategies",
                optimal_strategies=["Long straddles", "Short iron condors"],
                risk_adjustment=-0.1
            )

        return None

    def calculate_realized_volatility(self, market_data: Dict) -> float:
        """Calculate realized volatility from price data"""
        try:
            # Simplified calculation - in production would use actual price series
            price_change = market_data.get('price_change', 0.0)
            current_price = market_data.get('current_price', 6650.0)

            if current_price > 0:
                daily_return = price_change / current_price
                # Annualized volatility estimate
                realized_vol = abs(daily_return) * math.sqrt(252) * 100
                return min(realized_vol, 100.0)  # Cap at 100%
            else:
                return 20.0  # Default estimate

        except Exception:
            return 20.0  # Default fallback

    def calculate_vix_percentile(self, vix_level: float) -> float:
        """Calculate VIX percentile based on historical data"""
        percentiles = self.vix_history["percentiles"]

        if vix_level <= percentiles["5th"]:
            return 5.0
        elif vix_level <= percentiles["10th"]:
            return 10.0
        elif vix_level <= percentiles["25th"]:
            return 25.0
        elif vix_level <= percentiles["50th"]:
            return 50.0
        elif vix_level <= percentiles["75th"]:
            return 75.0
        elif vix_level <= percentiles["90th"]:
            return 90.0
        elif vix_level <= percentiles["95th"]:
            return 95.0
        else:
            return 99.0

    def calculate_risk_adjustments(self, regime: VolatilityRegime, signals: List[VolatilitySignal]) -> Dict:
        """Calculate position sizing and risk adjustments"""
        base_adjustment = 1.0

        # Regime-based adjustments
        regime_adjustments = {
            "ULTRA_LOW_VOL": 0.8,   # Reduce size due to expansion risk
            "LOW_VOL": 1.0,         # Normal sizing
            "NORMAL_VOL": 1.0,      # Normal sizing
            "ELEVATED_VOL": 0.7,    # Reduce size
            "HIGH_VOL": 0.5,        # Significantly reduce
            "EXTREME_VOL": 0.3      # Minimal sizing
        }

        regime_adj = regime_adjustments.get(regime.regime_type, 1.0)

        # Signal-based adjustments
        signal_adj = 1.0
        for signal in signals:
            if signal.signal_type in ["VOLATILITY_EXPANSION", "REGIME_CHANGE_WARNING"]:
                signal_adj *= (1.0 + signal.risk_adjustment)

        final_adjustment = base_adjustment * regime_adj * signal_adj

        return {
            "position_size_multiplier": min(max(final_adjustment, 0.1), 2.0),  # Cap between 0.1x and 2.0x
            "regime_adjustment": regime_adj,
            "signal_adjustment": signal_adj,
            "stop_loss_tightening": 1.0 + (1.0 - regime_adj),  # Tighter stops in high vol
            "profit_target_adjustment": regime_adj,  # Lower targets in high vol
            "hold_time_adjustment": regime_adj  # Shorter holds in high vol
        }

    def predict_regime_changes(self, vix_level: float, realized_vol: float) -> Dict:
        """Predict potential volatility regime changes"""
        current_regime = self.classify_volatility_regime(vix_level, realized_vol)

        # Simple regime persistence model
        persistence_score = current_regime.regime_confidence

        # Factors that increase regime change probability
        change_factors = []
        change_probability = 0.1  # Base 10% chance of regime change

        if current_regime.regime_type == "ULTRA_LOW_VOL":
            change_probability += 0.3  # 30% additional chance
            change_factors.append("Unsustainably low volatility")

        if current_regime.regime_type == "EXTREME_VOL":
            change_probability += 0.4  # 40% additional chance
            change_factors.append("Extreme volatility unsustainable")

        if abs(vix_level - realized_vol) > 10:
            change_probability += 0.2
            change_factors.append("Large VIX/realized volatility gap")

        return {
            "current_regime": current_regime.regime_type,
            "regime_persistence": persistence_score,
            "change_probability": min(change_probability, 0.8),  # Cap at 80%
            "change_factors": change_factors,
            "expected_next_regime": self.predict_next_regime(current_regime),
            "time_to_change_estimate": current_regime.expected_duration
        }

    def predict_next_regime(self, current_regime: VolatilityRegime) -> str:
        """Predict most likely next regime"""
        regime_transitions = {
            "ULTRA_LOW_VOL": "LOW_VOL",
            "LOW_VOL": "NORMAL_VOL",
            "NORMAL_VOL": "LOW_VOL",  # Mean reversion tendency
            "ELEVATED_VOL": "NORMAL_VOL",
            "HIGH_VOL": "ELEVATED_VOL",
            "EXTREME_VOL": "HIGH_VOL"
        }

        return regime_transitions.get(current_regime.regime_type, "NORMAL_VOL")

    def generate_volatility_trading_recommendations(self, regime: VolatilityRegime,
                                                   signals: List[VolatilitySignal],
                                                   term_structure: Dict) -> List[Dict]:
        """Generate specific trading recommendations based on volatility analysis"""
        recommendations = []

        # Regime-based recommendations
        if regime.regime_type in ["ULTRA_LOW_VOL", "LOW_VOL"]:
            recommendations.append({
                "strategy": "Volatility Protection",
                "reasoning": "Low volatility regime - consider tail risk hedging",
                "specific_trades": ["Long VIX calls", "Protective puts", "Long straddles on spikes"],
                "confidence": 0.75
            })

        elif regime.regime_type in ["HIGH_VOL", "EXTREME_VOL"]:
            recommendations.append({
                "strategy": "Volatility Selling",
                "reasoning": "High volatility regime - mean reversion opportunity",
                "specific_trades": ["Short VIX calls", "Covered calls", "Iron condors"],
                "confidence": 0.80
            })

        # Signal-based recommendations
        for signal in signals:
            if signal.strength > 0.7:
                recommendations.append({
                    "strategy": signal.signal_type,
                    "reasoning": signal.reasoning,
                    "specific_trades": signal.optimal_strategies,
                    "confidence": signal.strength
                })

        return recommendations

    def calculate_position_sizing_adjustments(self, regime: VolatilityRegime) -> Dict:
        """Calculate specific position sizing adjustments for volatility regime"""
        base_size = 1.0  # 1% base position

        if regime.regime_type == "ULTRA_LOW_VOL":
            size_multiplier = 0.8
            rationale = "Reduce size due to volatility expansion risk"
        elif regime.regime_type == "LOW_VOL":
            size_multiplier = 1.0
            rationale = "Normal position sizing appropriate"
        elif regime.regime_type == "NORMAL_VOL":
            size_multiplier = 1.0
            rationale = "Standard volatility environment"
        elif regime.regime_type == "ELEVATED_VOL":
            size_multiplier = 0.7
            rationale = "Reduce size due to increased uncertainty"
        elif regime.regime_type == "HIGH_VOL":
            size_multiplier = 0.5
            rationale = "Significantly reduce size in high volatility"
        else:  # EXTREME_VOL
            size_multiplier = 0.3
            rationale = "Minimal positions only in extreme volatility"

        return {
            "base_position_size": base_size,
            "volatility_multiplier": size_multiplier,
            "adjusted_position_size": base_size * size_multiplier,
            "rationale": rationale,
            "max_portfolio_heat_adjustment": size_multiplier * 15.0,  # Adjust portfolio heat limit
            "stop_loss_tightening": 1.0 + (1.0 - size_multiplier)  # Tighter stops in high vol
        }

    def get_default_volatility_analysis(self) -> Dict:
        """Return default analysis in case of errors"""
        return {
            "timestamp": datetime.now().isoformat(),
            "current_vix": 20.0,
            "realized_volatility": 20.0,
            "vix_percentile": 50.0,
            "regime_classification": {
                "regime_type": "NORMAL_VOL",
                "regime_confidence": 0.5
            },
            "volatility_signals": [],
            "risk_adjustments": {
                "position_size_multiplier": 1.0
            },
            "trading_recommendations": [],
            "error": "Using default volatility analysis"
        }

    def save_volatility_analysis(self, analysis: Dict):
        """Save volatility analysis to file"""
        try:
            os.makedirs(".spx", exist_ok=True)
            with open(self.volatility_analysis_file, 'w') as f:
                json.dump(analysis, f, indent=2)

            # Update regime history
            regime_entry = {
                "timestamp": analysis["timestamp"],
                "regime": analysis["regime_classification"]["regime_type"],
                "vix_level": analysis["current_vix"],
                "confidence": analysis["regime_classification"]["regime_confidence"]
            }
            self.regime_history.append(regime_entry)

            # Keep only last 100 regime entries
            self.regime_history = self.regime_history[-100:]

            with open(self.regime_history_file, 'w') as f:
                json.dump(self.regime_history, f, indent=2)

        except Exception as e:
            print(f"Error saving volatility analysis: {e}")

def main():
    """Test Volatility Intelligence Engine"""
    volatility_engine = VolatilityIntelligence()

    print(" Volatility Intelligence Engine Test")
    print("=" * 50)

    # Sample market data
    sample_data = {
        "vix": 22.5,
        "current_price": 6650.0,
        "price_change": 15.0,
        "volume": 45000,
        "rsi": 58.0
    }

    print(f"Testing with VIX: {sample_data['vix']}")

    # Run volatility analysis
    analysis = volatility_engine.analyze_volatility_environment(sample_data)

    print(f"\nCHART Volatility Analysis Results:")
    print(f"- VIX Level: {analysis['current_vix']}")
    print(f"- VIX Percentile: {analysis['vix_percentile']}%")
    print(f"- Regime: {analysis['regime_classification']['regime_type']}")
    print(f"- Regime Confidence: {analysis['regime_classification']['regime_confidence']:.1%}")

    # Display signals
    signals = analysis.get('volatility_signals', [])
    print(f"\nALERT Volatility Signals ({len(signals)}):")
    for signal in signals:
        print(f"- {signal['signal_type']}: {signal['direction']} (Strength: {signal['strength']:.1%})")
        print(f"  Reasoning: {signal['reasoning']}")

    # Display recommendations
    recommendations = analysis.get('trading_recommendations', [])
    print(f"\nIDEA Trading Recommendations ({len(recommendations)}):")
    for rec in recommendations:
        print(f"- {rec['strategy']} (Confidence: {rec['confidence']:.1%})")
        print(f"  Reasoning: {rec['reasoning']}")

    # Risk adjustments
    risk_adj = analysis.get('risk_adjustments', {})
    pos_multiplier = risk_adj.get('position_size_multiplier', 1.0)
    print(f"\nSHIELD Risk Adjustments:")
    print(f"- Position Size Multiplier: {pos_multiplier:.1f}x")
    print(f"- Stop Loss Tightening: {risk_adj.get('stop_loss_tightening', 1.0):.1f}x")

    print("\nSUCCESS Volatility Intelligence Engine test completed!")

if __name__ == "__main__":
    main()