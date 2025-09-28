#!/usr/bin/env python3
"""
Market Microstructure Analysis Engine
Advanced order flow analysis with institutional signature detection
"""

import json
import os
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import math

@dataclass
class OrderFlowSignal:
    """Order flow-based trading signal"""
    signal_type: str
    strength: float
    direction: str
    reasoning: str
    confidence: float
    time_horizon: str
    institutional_signature: bool

@dataclass
class LiquidityProfile:
    """Market liquidity assessment"""
    liquidity_level: str
    bid_ask_spread: float
    market_depth: float
    liquidity_score: float
    fragmentation_risk: str

@dataclass
class InstitutionalActivity:
    """Institutional trading activity analysis"""
    activity_level: str
    flow_direction: str
    block_size_analysis: Dict
    timing_patterns: List[str]
    confidence: float

class MarketMicrostructure:
    """Advanced market microstructure analysis engine"""

    def __init__(self):
        self.microstructure_file = ".spx/microstructure_analysis.json"
        self.order_flow_history_file = ".spx/order_flow_history.json"
        self.institutional_patterns_file = ".spx/institutional_patterns.json"
        self.load_historical_data()

    def load_historical_data(self):
        """Load historical microstructure data"""
        try:
            if os.path.exists(self.order_flow_history_file):
                with open(self.order_flow_history_file, 'r') as f:
                    self.order_flow_history = json.load(f)
            else:
                self.order_flow_history = []

            if os.path.exists(self.institutional_patterns_file):
                with open(self.institutional_patterns_file, 'r') as f:
                    self.institutional_patterns = json.load(f)
            else:
                self.institutional_patterns = self.initialize_institutional_patterns()

        except Exception as e:
            print(f"Error loading microstructure data: {e}")
            self.order_flow_history = []
            self.institutional_patterns = self.initialize_institutional_patterns()

    def initialize_institutional_patterns(self) -> Dict:
        """Initialize institutional trading pattern signatures"""
        return {
            "volume_thresholds": {
                "retail": 100,
                "small_institutional": 1000,
                "large_institutional": 5000,
                "whale": 20000
            },
            "timing_signatures": {
                "institutional_hours": [(9, 30, 11, 30), (13, 30, 15, 30)],  # 9:30-11:30, 1:30-3:30 ET
                "retail_hours": [(11, 30, 13, 30), (15, 30, 16, 0)],  # 11:30-1:30, 3:30-4:00 ET
                "algorithmic_hours": [(9, 30, 10, 0), (15, 45, 16, 0)]  # Open/close
            },
            "block_patterns": {
                "accumulation": "Large consistent buying over time",
                "distribution": "Large consistent selling over time",
                "momentum_following": "Large orders following price direction",
                "contrarian": "Large orders against price direction"
            },
            "spread_characteristics": {
                "tight": 0.01,  # $0.01 or less
                "normal": 0.05,  # $0.05 or less
                "wide": 0.10,   # $0.10 or more
                "very_wide": 0.25  # $0.25 or more
            }
        }

    def analyze_market_microstructure(self, market_data: Dict) -> Dict:
        """Comprehensive market microstructure analysis"""
        try:
            current_price = market_data.get('current_price', 6650.0)
            volume = market_data.get('volume', 35000)
            bid_ask_spread = market_data.get('bid_ask_spread', 0.05)

            # Analyze order flow patterns
            order_flow_analysis = self.analyze_order_flow(market_data)

            # Assess liquidity profile
            liquidity_profile = self.assess_liquidity_profile(market_data)

            # Detect institutional activity
            institutional_activity = self.detect_institutional_activity(market_data)

            # Analyze market depth and pressure
            market_pressure = self.analyze_market_pressure(market_data)

            # Generate microstructure signals
            microstructure_signals = self.generate_microstructure_signals(
                order_flow_analysis, liquidity_profile, institutional_activity
            )

            # Calculate execution quality metrics
            execution_metrics = self.calculate_execution_metrics(market_data, liquidity_profile)

            # Assess fragmentation risk
            fragmentation_risk = self.assess_fragmentation_risk(market_data)

            analysis = {
                "timestamp": datetime.now().isoformat(),
                "order_flow_analysis": order_flow_analysis,
                "liquidity_profile": liquidity_profile.__dict__,
                "institutional_activity": institutional_activity.__dict__,
                "market_pressure": market_pressure,
                "microstructure_signals": [signal.__dict__ for signal in microstructure_signals],
                "execution_metrics": execution_metrics,
                "fragmentation_risk": fragmentation_risk,
                "trading_recommendations": self.generate_microstructure_trading_recommendations(
                    microstructure_signals, liquidity_profile, institutional_activity
                ),
                "optimal_execution_strategy": self.recommend_execution_strategy(
                    liquidity_profile, market_pressure, volume
                )
            }

            # Save analysis
            self.save_microstructure_analysis(analysis)

            return analysis

        except Exception as e:
            print(f"Error in microstructure analysis: {e}")
            return self.get_default_microstructure_analysis()

    def analyze_order_flow(self, market_data: Dict) -> Dict:
        """Analyze order flow patterns and imbalances"""
        try:
            volume = market_data.get('volume', 35000)
            price_change = market_data.get('price_change', 0.0)
            current_price = market_data.get('current_price', 6650.0)

            # Estimate order flow components (simplified)
            if price_change > 0:
                buy_volume_estimate = volume * 0.6  # Assume 60% buying pressure
                sell_volume_estimate = volume * 0.4
            elif price_change < 0:
                buy_volume_estimate = volume * 0.4
                sell_volume_estimate = volume * 0.6  # Assume 60% selling pressure
            else:
                buy_volume_estimate = volume * 0.5
                sell_volume_estimate = volume * 0.5

            # Calculate order flow imbalance
            total_flow = buy_volume_estimate + sell_volume_estimate
            if total_flow > 0:
                order_imbalance = (buy_volume_estimate - sell_volume_estimate) / total_flow
            else:
                order_imbalance = 0.0

            # Determine flow direction
            if order_imbalance > 0.2:
                flow_direction = "STRONG_BUYING"
            elif order_imbalance > 0.05:
                flow_direction = "MODERATE_BUYING"
            elif order_imbalance < -0.2:
                flow_direction = "STRONG_SELLING"
            elif order_imbalance < -0.05:
                flow_direction = "MODERATE_SELLING"
            else:
                flow_direction = "BALANCED"

            # Calculate order flow intensity
            average_volume = market_data.get('average_volume', 30000)
            flow_intensity = volume / average_volume if average_volume > 0 else 1.0

            if flow_intensity > 2.0:
                intensity_level = "VERY_HIGH"
            elif flow_intensity > 1.5:
                intensity_level = "HIGH"
            elif flow_intensity > 1.2:
                intensity_level = "ELEVATED"
            else:
                intensity_level = "NORMAL"

            return {
                "buy_volume_estimate": buy_volume_estimate,
                "sell_volume_estimate": sell_volume_estimate,
                "order_imbalance": round(order_imbalance, 3),
                "flow_direction": flow_direction,
                "flow_intensity": flow_intensity,
                "intensity_level": intensity_level,
                "volume_profile": self.analyze_volume_profile(volume, average_volume)
            }

        except Exception as e:
            print(f"Error analyzing order flow: {e}")
            return {"flow_direction": "UNKNOWN", "order_imbalance": 0.0}

    def assess_liquidity_profile(self, market_data: Dict) -> LiquidityProfile:
        """Assess current market liquidity profile"""
        try:
            bid_ask_spread = market_data.get('bid_ask_spread', 0.05)
            volume = market_data.get('volume', 35000)
            current_price = market_data.get('current_price', 6650.0)

            # Assess spread characteristics
            spread_characteristics = self.institutional_patterns["spread_characteristics"]
            if bid_ask_spread <= spread_characteristics["tight"]:
                spread_category = "TIGHT"
            elif bid_ask_spread <= spread_characteristics["normal"]:
                spread_category = "NORMAL"
            elif bid_ask_spread <= spread_characteristics["wide"]:
                spread_category = "WIDE"
            else:
                spread_category = "VERY_WIDE"

            # Estimate market depth (simplified)
            if volume > 50000:
                market_depth = "DEEP"
                depth_score = 0.9
            elif volume > 35000:
                market_depth = "ADEQUATE"
                depth_score = 0.7
            elif volume > 20000:
                market_depth = "SHALLOW"
                depth_score = 0.4
            else:
                market_depth = "VERY_SHALLOW"
                depth_score = 0.2

            # Calculate liquidity score
            spread_score = 1.0 - min(bid_ask_spread / 0.10, 1.0)  # Normalize to 0-1
            liquidity_score = (spread_score * 0.6) + (depth_score * 0.4)

            # Determine overall liquidity level
            if liquidity_score > 0.8:
                liquidity_level = "HIGH"
            elif liquidity_score > 0.6:
                liquidity_level = "ADEQUATE"
            elif liquidity_score > 0.4:
                liquidity_level = "LOW"
            else:
                liquidity_level = "VERY_LOW"

            # Assess fragmentation risk
            if spread_category in ["WIDE", "VERY_WIDE"] and market_depth in ["SHALLOW", "VERY_SHALLOW"]:
                fragmentation_risk = "HIGH"
            elif spread_category in ["WIDE"] or market_depth == "SHALLOW":
                fragmentation_risk = "MEDIUM"
            else:
                fragmentation_risk = "LOW"

            return LiquidityProfile(
                liquidity_level=liquidity_level,
                bid_ask_spread=bid_ask_spread,
                market_depth=depth_score,
                liquidity_score=liquidity_score,
                fragmentation_risk=fragmentation_risk
            )

        except Exception as e:
            print(f"Error assessing liquidity profile: {e}")
            return LiquidityProfile("UNKNOWN", 0.05, 0.5, 0.5, "MEDIUM")

    def detect_institutional_activity(self, market_data: Dict) -> InstitutionalActivity:
        """Detect and analyze institutional trading activity"""
        try:
            volume = market_data.get('volume', 35000)
            price_change = market_data.get('price_change', 0.0)
            current_hour = datetime.now().hour
            current_minute = datetime.now().minute

            # Analyze volume characteristics
            volume_thresholds = self.institutional_patterns["volume_thresholds"]
            if volume >= volume_thresholds["whale"]:
                activity_level = "WHALE_ACTIVITY"
                confidence = 0.9
            elif volume >= volume_thresholds["large_institutional"]:
                activity_level = "LARGE_INSTITUTIONAL"
                confidence = 0.8
            elif volume >= volume_thresholds["small_institutional"]:
                activity_level = "SMALL_INSTITUTIONAL"
                confidence = 0.6
            else:
                activity_level = "RETAIL_DOMINATED"
                confidence = 0.4

            # Analyze timing patterns
            timing_patterns = []
            timing_signatures = self.institutional_patterns["timing_signatures"]

            for pattern_name, time_ranges in timing_signatures.items():
                for start_hour, start_min, end_hour, end_min in time_ranges:
                    current_time_minutes = current_hour * 60 + current_minute
                    start_time_minutes = start_hour * 60 + start_min
                    end_time_minutes = end_hour * 60 + end_min

                    if start_time_minutes <= current_time_minutes <= end_time_minutes:
                        timing_patterns.append(pattern_name)

            # Determine flow direction
            if price_change > 5.0 and volume > volume_thresholds["small_institutional"]:
                flow_direction = "STRONG_INSTITUTIONAL_BUYING"
            elif price_change < -5.0 and volume > volume_thresholds["small_institutional"]:
                flow_direction = "STRONG_INSTITUTIONAL_SELLING"
            elif price_change > 0:
                flow_direction = "NET_BUYING"
            elif price_change < 0:
                flow_direction = "NET_SELLING"
            else:
                flow_direction = "BALANCED"

            # Block size analysis
            block_size_analysis = self.analyze_block_sizes(volume, activity_level)

            return InstitutionalActivity(
                activity_level=activity_level,
                flow_direction=flow_direction,
                block_size_analysis=block_size_analysis,
                timing_patterns=timing_patterns,
                confidence=confidence
            )

        except Exception as e:
            print(f"Error detecting institutional activity: {e}")
            return InstitutionalActivity("UNKNOWN", "BALANCED", {}, [], 0.5)

    def analyze_block_sizes(self, volume: int, activity_level: str) -> Dict:
        """Analyze block size distribution"""
        # Simplified block size analysis
        if activity_level == "WHALE_ACTIVITY":
            return {
                "average_block_size": "VERY_LARGE",
                "block_frequency": "LOW",
                "institutional_signature": "STRONG",
                "estimated_participants": "FEW_LARGE_PLAYERS"
            }
        elif activity_level == "LARGE_INSTITUTIONAL":
            return {
                "average_block_size": "LARGE",
                "block_frequency": "MEDIUM",
                "institutional_signature": "MODERATE",
                "estimated_participants": "SEVERAL_INSTITUTIONS"
            }
        else:
            return {
                "average_block_size": "SMALL",
                "block_frequency": "HIGH",
                "institutional_signature": "WEAK",
                "estimated_participants": "MANY_RETAIL"
            }

    def analyze_market_pressure(self, market_data: Dict) -> Dict:
        """Analyze buying and selling pressure in the market"""
        try:
            volume = market_data.get('volume', 35000)
            price_change = market_data.get('price_change', 0.0)
            rsi = market_data.get('rsi', 50.0)

            # Calculate pressure metrics
            if price_change > 0 and volume > 40000:
                buying_pressure = "HIGH"
                selling_pressure = "LOW"
            elif price_change < 0 and volume > 40000:
                buying_pressure = "LOW"
                selling_pressure = "HIGH"
            elif volume > 30000:
                buying_pressure = "MEDIUM"
                selling_pressure = "MEDIUM"
            else:
                buying_pressure = "LOW"
                selling_pressure = "LOW"

            # Momentum pressure assessment
            if rsi > 70:
                momentum_pressure = "OVERBOUGHT"
            elif rsi < 30:
                momentum_pressure = "OVERSOLD"
            elif rsi > 55:
                momentum_pressure = "BULLISH"
            elif rsi < 45:
                momentum_pressure = "BEARISH"
            else:
                momentum_pressure = "NEUTRAL"

            # Overall pressure assessment
            if buying_pressure == "HIGH" and selling_pressure == "LOW":
                overall_pressure = "STRONG_BUYING"
            elif selling_pressure == "HIGH" and buying_pressure == "LOW":
                overall_pressure = "STRONG_SELLING"
            elif buying_pressure == "MEDIUM" or selling_pressure == "MEDIUM":
                overall_pressure = "MODERATE_ACTIVITY"
            else:
                overall_pressure = "LOW_ACTIVITY"

            return {
                "buying_pressure": buying_pressure,
                "selling_pressure": selling_pressure,
                "momentum_pressure": momentum_pressure,
                "overall_pressure": overall_pressure,
                "pressure_imbalance": self.calculate_pressure_imbalance(buying_pressure, selling_pressure)
            }

        except Exception as e:
            print(f"Error analyzing market pressure: {e}")
            return {"overall_pressure": "UNKNOWN"}

    def calculate_pressure_imbalance(self, buying_pressure: str, selling_pressure: str) -> float:
        """Calculate numerical pressure imbalance"""
        pressure_values = {"LOW": 1, "MEDIUM": 2, "HIGH": 3}
        buy_value = pressure_values.get(buying_pressure, 2)
        sell_value = pressure_values.get(selling_pressure, 2)

        total = buy_value + sell_value
        if total > 0:
            return (buy_value - sell_value) / total
        else:
            return 0.0

    def generate_microstructure_signals(self, order_flow: Dict, liquidity: LiquidityProfile,
                                      institutional: InstitutionalActivity) -> List[OrderFlowSignal]:
        """Generate trading signals based on microstructure analysis"""
        signals = []

        try:
            # Order flow imbalance signal
            order_imbalance = order_flow.get("order_imbalance", 0.0)
            if abs(order_imbalance) > 0.3:
                direction = "BULLISH" if order_imbalance > 0 else "BEARISH"
                signals.append(OrderFlowSignal(
                    signal_type="ORDER_FLOW_IMBALANCE",
                    strength=abs(order_imbalance),
                    direction=direction,
                    reasoning=f"Strong order flow imbalance: {order_imbalance:.2f}",
                    confidence=0.75,
                    time_horizon="SHORT_TERM",
                    institutional_signature=institutional.activity_level in ["LARGE_INSTITUTIONAL", "WHALE_ACTIVITY"]
                ))

            # Institutional flow signal
            if institutional.confidence > 0.7 and institutional.flow_direction in ["STRONG_INSTITUTIONAL_BUYING", "STRONG_INSTITUTIONAL_SELLING"]:
                direction = "BULLISH" if "BUYING" in institutional.flow_direction else "BEARISH"
                signals.append(OrderFlowSignal(
                    signal_type="INSTITUTIONAL_FLOW",
                    strength=institutional.confidence,
                    direction=direction,
                    reasoning=f"Institutional {direction.lower()} detected with {institutional.confidence:.1%} confidence",
                    confidence=institutional.confidence,
                    time_horizon="MEDIUM_TERM",
                    institutional_signature=True
                ))

            # Liquidity signal
            if liquidity.liquidity_level == "VERY_LOW" and liquidity.fragmentation_risk == "HIGH":
                signals.append(OrderFlowSignal(
                    signal_type="LIQUIDITY_RISK",
                    strength=0.8,
                    direction="NEUTRAL",
                    reasoning="Very low liquidity with high fragmentation risk",
                    confidence=0.85,
                    time_horizon="IMMEDIATE",
                    institutional_signature=False
                ))

            # Volume intensity signal
            flow_intensity = order_flow.get("flow_intensity", 1.0)
            if flow_intensity > 2.0:
                flow_direction = order_flow.get("flow_direction", "BALANCED")
                if flow_direction in ["STRONG_BUYING", "STRONG_SELLING"]:
                    direction = "BULLISH" if "BUYING" in flow_direction else "BEARISH"
                    signals.append(OrderFlowSignal(
                        signal_type="VOLUME_SURGE",
                        strength=min(flow_intensity / 3.0, 1.0),  # Normalize
                        direction=direction,
                        reasoning=f"Volume surge ({flow_intensity:.1f}x normal) with {flow_direction.lower()}",
                        confidence=0.70,
                        time_horizon="SHORT_TERM",
                        institutional_signature=flow_intensity > 3.0
                    ))

        except Exception as e:
            print(f"Error generating microstructure signals: {e}")

        return signals

    def calculate_execution_metrics(self, market_data: Dict, liquidity: LiquidityProfile) -> Dict:
        """Calculate optimal execution metrics and costs"""
        try:
            current_price = market_data.get('current_price', 6650.0)
            bid_ask_spread = liquidity.bid_ask_spread
            volume = market_data.get('volume', 35000)

            # Market impact estimation
            if liquidity.liquidity_level == "HIGH":
                market_impact_factor = 0.001  # 0.1%
            elif liquidity.liquidity_level == "ADEQUATE":
                market_impact_factor = 0.002  # 0.2%
            elif liquidity.liquidity_level == "LOW":
                market_impact_factor = 0.005  # 0.5%
            else:
                market_impact_factor = 0.010  # 1.0%

            # Execution cost estimates
            spread_cost = bid_ask_spread / 2  # Half spread cost
            market_impact_cost = current_price * market_impact_factor

            # Timing cost (based on liquidity)
            if liquidity.liquidity_level in ["HIGH", "ADEQUATE"]:
                timing_risk = "LOW"
                timing_cost_factor = 0.0005
            else:
                timing_risk = "HIGH"
                timing_cost_factor = 0.002

            timing_cost = current_price * timing_cost_factor

            # Total execution cost
            total_execution_cost = spread_cost + market_impact_cost + timing_cost

            return {
                "spread_cost": round(spread_cost, 4),
                "market_impact_cost": round(market_impact_cost, 4),
                "timing_cost": round(timing_cost, 4),
                "total_execution_cost": round(total_execution_cost, 4),
                "execution_cost_bps": round((total_execution_cost / current_price) * 10000, 2),
                "timing_risk": timing_risk,
                "optimal_order_size": self.calculate_optimal_order_size(volume, liquidity),
                "execution_urgency": self.assess_execution_urgency(liquidity)
            }

        except Exception as e:
            print(f"Error calculating execution metrics: {e}")
            return {"total_execution_cost": 0.0}

    def calculate_optimal_order_size(self, volume: int, liquidity: LiquidityProfile) -> str:
        """Calculate optimal order size based on liquidity"""
        if liquidity.liquidity_level == "HIGH":
            return "UP_TO_10_PERCENT_VOLUME"
        elif liquidity.liquidity_level == "ADEQUATE":
            return "UP_TO_5_PERCENT_VOLUME"
        elif liquidity.liquidity_level == "LOW":
            return "UP_TO_2_PERCENT_VOLUME"
        else:
            return "MINIMAL_SIZE_ONLY"

    def assess_execution_urgency(self, liquidity: LiquidityProfile) -> str:
        """Assess optimal execution urgency"""
        if liquidity.liquidity_level == "HIGH" and liquidity.fragmentation_risk == "LOW":
            return "CAN_EXECUTE_QUICKLY"
        elif liquidity.liquidity_level in ["ADEQUATE", "HIGH"]:
            return "MODERATE_PACE"
        else:
            return "EXECUTE_SLOWLY"

    def assess_fragmentation_risk(self, market_data: Dict) -> Dict:
        """Assess market fragmentation and venue risk"""
        volume = market_data.get('volume', 35000)
        bid_ask_spread = market_data.get('bid_ask_spread', 0.05)

        # Simplified fragmentation assessment
        if bid_ask_spread > 0.10 and volume < 20000:
            fragmentation_level = "HIGH"
            venue_risk = "SIGNIFICANT"
        elif bid_ask_spread > 0.05 or volume < 30000:
            fragmentation_level = "MEDIUM"
            venue_risk = "MODERATE"
        else:
            fragmentation_level = "LOW"
            venue_risk = "MINIMAL"

        return {
            "fragmentation_level": fragmentation_level,
            "venue_risk": venue_risk,
            "execution_complexity": "HIGH" if fragmentation_level == "HIGH" else "NORMAL",
            "routing_recommendations": self.get_routing_recommendations(fragmentation_level)
        }

    def get_routing_recommendations(self, fragmentation_level: str) -> List[str]:
        """Get order routing recommendations"""
        if fragmentation_level == "HIGH":
            return [
                "Use multiple venues",
                "Consider dark pools",
                "Implement time-weighted execution",
                "Monitor for better liquidity windows"
            ]
        elif fragmentation_level == "MEDIUM":
            return [
                "Primary venue execution acceptable",
                "Monitor alternative venues",
                "Consider order splitting"
            ]
        else:
            return [
                "Primary venue execution optimal",
                "Standard routing acceptable"
            ]

    def recommend_execution_strategy(self, liquidity: LiquidityProfile,
                                   market_pressure: Dict, volume: int) -> Dict:
        """Recommend optimal execution strategy"""
        try:
            strategy = {
                "execution_style": "MARKET_ORDER",
                "timing": "IMMEDIATE",
                "order_splitting": False,
                "dark_pool_usage": False,
                "rationale": []
            }

            # Adjust based on liquidity
            if liquidity.liquidity_level == "VERY_LOW":
                strategy["execution_style"] = "LIMIT_ORDER"
                strategy["timing"] = "PATIENT"
                strategy["order_splitting"] = True
                strategy["rationale"].append("Low liquidity requires patient execution")

            # Adjust based on market pressure
            overall_pressure = market_pressure.get("overall_pressure", "LOW_ACTIVITY")
            if overall_pressure in ["STRONG_BUYING", "STRONG_SELLING"]:
                strategy["timing"] = "IMMEDIATE"
                strategy["rationale"].append("Strong market pressure requires quick execution")

            # Adjust based on volume
            if volume > 50000:
                strategy["dark_pool_usage"] = True
                strategy["rationale"].append("High volume suggests dark pool availability")

            # Fragmentation considerations
            if liquidity.fragmentation_risk == "HIGH":
                strategy["order_splitting"] = True
                strategy["rationale"].append("High fragmentation risk requires order splitting")

            return strategy

        except Exception as e:
            print(f"Error recommending execution strategy: {e}")
            return {"execution_style": "MARKET_ORDER", "timing": "IMMEDIATE"}

    def generate_microstructure_trading_recommendations(self, signals: List[OrderFlowSignal],
                                                       liquidity: LiquidityProfile,
                                                       institutional: InstitutionalActivity) -> List[Dict]:
        """Generate specific trading recommendations based on microstructure analysis"""
        recommendations = []

        try:
            # Signal-based recommendations
            for signal in signals:
                if signal.strength > 0.7 and signal.confidence > 0.7:
                    recommendation = {
                        "strategy": self.get_strategy_for_microstructure_signal(signal),
                        "reasoning": signal.reasoning,
                        "confidence": signal.confidence,
                        "time_horizon": signal.time_horizon,
                        "execution_notes": self.get_execution_notes(signal, liquidity)
                    }
                    recommendations.append(recommendation)

            # Liquidity-based recommendations
            if liquidity.liquidity_level == "VERY_LOW":
                recommendations.append({
                    "strategy": "REDUCE_POSITION_SIZES",
                    "reasoning": "Very low liquidity environment requires caution",
                    "confidence": 0.85,
                    "time_horizon": "IMMEDIATE",
                    "execution_notes": ["Use limit orders", "Split large orders", "Be patient"]
                })

            # Institutional activity recommendations
            if institutional.activity_level in ["LARGE_INSTITUTIONAL", "WHALE_ACTIVITY"]:
                recommendations.append({
                    "strategy": "FOLLOW_INSTITUTIONAL_FLOW",
                    "reasoning": f"Strong institutional activity detected: {institutional.flow_direction}",
                    "confidence": institutional.confidence,
                    "time_horizon": "MEDIUM_TERM",
                    "execution_notes": ["Monitor for continuation", "Consider larger position sizes"]
                })

        except Exception as e:
            print(f"Error generating microstructure recommendations: {e}")

        return recommendations

    def get_strategy_for_microstructure_signal(self, signal: OrderFlowSignal) -> str:
        """Get specific strategy for microstructure signal"""
        if signal.signal_type == "ORDER_FLOW_IMBALANCE":
            return f"FLOW_FOLLOWING_{signal.direction}"
        elif signal.signal_type == "INSTITUTIONAL_FLOW":
            return f"INSTITUTIONAL_{signal.direction}_FOLLOW"
        elif signal.signal_type == "VOLUME_SURGE":
            return f"MOMENTUM_{signal.direction}"
        elif signal.signal_type == "LIQUIDITY_RISK":
            return "DEFENSIVE_POSITIONING"
        else:
            return "GENERAL_MICROSTRUCTURE_PLAY"

    def get_execution_notes(self, signal: OrderFlowSignal, liquidity: LiquidityProfile) -> List[str]:
        """Get execution notes for microstructure signal"""
        notes = []

        if signal.institutional_signature:
            notes.append("Large institutional orders likely - consider following")

        if liquidity.liquidity_level == "LOW":
            notes.append("Use limit orders due to low liquidity")

        if signal.time_horizon == "IMMEDIATE":
            notes.append("Act quickly - signal may be short-lived")

        if signal.strength > 0.8:
            notes.append("High confidence signal - consider larger position")

        return notes if notes else ["Standard execution acceptable"]

    def analyze_volume_profile(self, current_volume: int, average_volume: int) -> Dict:
        """Analyze volume profile characteristics"""
        volume_ratio = current_volume / average_volume if average_volume > 0 else 1.0

        if volume_ratio > 3.0:
            profile = "EXPLOSIVE"
        elif volume_ratio > 2.0:
            profile = "VERY_HIGH"
        elif volume_ratio > 1.5:
            profile = "HIGH"
        elif volume_ratio > 1.2:
            profile = "ELEVATED"
        elif volume_ratio > 0.8:
            profile = "NORMAL"
        else:
            profile = "LOW"

        return {
            "volume_profile": profile,
            "volume_ratio": round(volume_ratio, 2),
            "statistical_significance": "HIGH" if volume_ratio > 2.0 else "MEDIUM" if volume_ratio > 1.5 else "LOW"
        }

    def get_default_microstructure_analysis(self) -> Dict:
        """Return default analysis when data is insufficient"""
        return {
            "timestamp": datetime.now().isoformat(),
            "order_flow_analysis": {"flow_direction": "UNKNOWN"},
            "liquidity_profile": {
                "liquidity_level": "UNKNOWN",
                "fragmentation_risk": "MEDIUM"
            },
            "institutional_activity": {
                "activity_level": "UNKNOWN",
                "confidence": 0.5
            },
            "microstructure_signals": [],
            "trading_recommendations": [],
            "note": "Insufficient data for microstructure analysis"
        }

    def save_microstructure_analysis(self, analysis: Dict):
        """Save microstructure analysis to file"""
        try:
            os.makedirs(".spx", exist_ok=True)
            with open(self.microstructure_file, 'w') as f:
                json.dump(analysis, f, indent=2)

            # Update order flow history
            flow_entry = {
                "timestamp": analysis["timestamp"],
                "flow_direction": analysis["order_flow_analysis"].get("flow_direction", "UNKNOWN"),
                "order_imbalance": analysis["order_flow_analysis"].get("order_imbalance", 0.0),
                "liquidity_level": analysis["liquidity_profile"]["liquidity_level"]
            }
            self.order_flow_history.append(flow_entry)

            # Keep only last 100 entries
            self.order_flow_history = self.order_flow_history[-100:]

            with open(self.order_flow_history_file, 'w') as f:
                json.dump(self.order_flow_history, f, indent=2)

        except Exception as e:
            print(f"Error saving microstructure analysis: {e}")

def main():
    """Test Market Microstructure Engine"""
    microstructure_engine = MarketMicrostructure()

    print("🏗️ Market Microstructure Analysis Engine Test")
    print("=" * 50)

    # Sample market data
    sample_data = {
        "current_price": 6650.0,
        "volume": 52000,
        "average_volume": 35000,
        "price_change": 8.5,
        "bid_ask_spread": 0.08,
        "rsi": 62.0
    }

    print(f"Testing with Volume: {sample_data['volume']:,} (vs avg {sample_data['average_volume']:,})")
    print(f"Price Change: {sample_data['price_change']:+.1f}, Spread: ${sample_data['bid_ask_spread']:.3f}")

    # Run microstructure analysis
    analysis = microstructure_engine.analyze_market_microstructure(sample_data)

    print(f"\n📊 Microstructure Analysis Results:")

    # Order flow
    order_flow = analysis["order_flow_analysis"]
    print(f"- Order Flow Direction: {order_flow.get('flow_direction', 'N/A')}")
    print(f"- Order Imbalance: {order_flow.get('order_imbalance', 0):.3f}")
    print(f"- Flow Intensity: {order_flow.get('flow_intensity', 1):.1f}x normal")

    # Liquidity
    liquidity = analysis["liquidity_profile"]
    print(f"- Liquidity Level: {liquidity['liquidity_level']}")
    print(f"- Liquidity Score: {liquidity['liquidity_score']:.2f}")
    print(f"- Fragmentation Risk: {liquidity['fragmentation_risk']}")

    # Institutional activity
    institutional = analysis["institutional_activity"]
    print(f"- Institutional Activity: {institutional['activity_level']}")
    print(f"- Flow Direction: {institutional['flow_direction']}")
    print(f"- Confidence: {institutional['confidence']:.1%}")

    # Signals
    signals = analysis.get('microstructure_signals', [])
    print(f"\n🚨 Microstructure Signals ({len(signals)}):")
    for signal in signals:
        print(f"- {signal['signal_type']}: {signal['direction']} (Strength: {signal['strength']:.1%})")
        print(f"  {signal['reasoning']}")
        if signal['institutional_signature']:
            print(f"  ⭐ Institutional signature detected")

    # Execution metrics
    execution = analysis.get('execution_metrics', {})
    if execution:
        print(f"\n💰 Execution Metrics:")
        print(f"- Total Execution Cost: {execution.get('execution_cost_bps', 0):.1f} bps")
        print(f"- Optimal Order Size: {execution.get('optimal_order_size', 'N/A')}")
        print(f"- Execution Urgency: {execution.get('execution_urgency', 'N/A')}")

    # Recommendations
    recommendations = analysis.get('trading_recommendations', [])
    print(f"\n💡 Trading Recommendations ({len(recommendations)}):")
    for rec in recommendations:
        print(f"- {rec['strategy']} (Confidence: {rec['confidence']:.1%})")
        print(f"  {rec['reasoning']}")

    print("\n✅ Market Microstructure Engine test completed!")

if __name__ == "__main__":
    main()