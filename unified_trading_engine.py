#!/usr/bin/env python3
"""
Unified Trading Engine - Consistent Implementation of All Systems
Resolves methodology conflicts and provides coherent trading decisions
"""

import json
import pandas as pd
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Union
from dataclasses import dataclass
from pathlib import Path

# Import our fixed components
from gex_analyzer_fixed import GEXAnalyzerFixed
from heatseeker_touch_tracker import HeatSeekerTouchTracker

@dataclass
class UnifiedMarketState:
    """Unified representation of current market state"""
    timestamp: str
    spy_price: float
    spx_price: float
    volume: float

    # GEX/DEX Analysis
    gex_data: Dict
    key_levels: Dict

    # Heatseeker Analysis
    touch_probabilities: Dict
    node_classifications: Dict

    # Risk Metrics
    volatility_regime: str
    portfolio_heat: float

    # System Consensus
    consensus_score: float
    directional_bias: str
    confidence_level: str

@dataclass
class TradingRecommendation:
    """Unified trading recommendation"""
    action: str  # BUY, SELL, HOLD, AVOID
    instrument: str  # SPY 662C, SPXW 6650C, etc.
    entry_price: float
    stop_loss: float
    profit_targets: List[float]
    position_size: float  # As percentage of portfolio

    # Justification
    primary_reason: str
    supporting_factors: List[str]
    risk_factors: List[str]

    # Probabilities
    success_probability: float
    risk_reward_ratio: float
    expected_return: float

    # System Attribution
    gex_score: float
    heatseeker_score: float
    consensus_score: float

class UnifiedTradingEngine:
    """
    Main trading engine that unifies all methodologies

    Resolves conflicts between:
    - GEX/DEX analysis vs Heatseeker methodology
    - King Node definitions (dealer preference vs absolute GEX)
    - Touch probability vs GEX calculations
    - Multiple confidence scoring systems
    """

    def __init__(self, session_dir: str = ".spx"):
        self.session_dir = Path(session_dir)
        self.session_dir.mkdir(exist_ok=True)

        # Initialize components
        self.gex_analyzer = GEXAnalyzerFixed()
        self.touch_tracker = HeatSeekerTouchTracker(self.session_dir / "touch_history.json")

        # Configuration
        self.config = self._load_config()

        # State tracking
        self.last_market_state: Optional[UnifiedMarketState] = None
        self.active_recommendations: List[TradingRecommendation] = []

    def _load_config(self) -> Dict:
        """Load configuration with methodology unification rules"""
        return {
            # UNIFIED KING NODE DEFINITION
            'king_node_definition': 'HIGHEST_ABSOLUTE_GEX',  # Resolves conflict
            'king_node_tolerance': 10.0,  # SPX points

            # UNIFIED PROBABILITY WEIGHTING
            'gex_weight': 0.4,
            'heatseeker_weight': 0.4,
            'volume_weight': 0.2,

            # UNIFIED CONFIDENCE THRESHOLDS
            'minimum_consensus': 70.0,  # Out of 100
            'high_confidence_threshold': 85.0,
            'maximum_confidence_threshold': 95.0,

            # RISK MANAGEMENT
            'max_portfolio_heat': 15.0,  # Percentage
            'max_single_position': 4.0,  # Percentage
            'max_correlation_exposure': 6.0,  # Percentage

            # METHODOLOGY RESOLUTION RULES
            'gex_heatseeker_conflict_resolution': 'CONSERVATIVE',  # or 'AGGRESSIVE'
            'multiple_signal_requirement': True,
            'volume_confirmation_required': True
        }

    def analyze_market(self, spy_price: float, volume: float = None,
                      options_data_url: str = None) -> UnifiedMarketState:
        """
        Perform unified market analysis combining all methodologies

        Returns comprehensive market state with resolved conflicts
        """
        timestamp = datetime.now().isoformat()
        spx_price = spy_price * 10  # Conversion

        print(f"UNIFIED MARKET ANALYSIS - {timestamp}")
        print("=" * 60)

        # 1. GEX/DEX ANALYSIS
        print("Phase 1: GEX/DEX Analysis...")
        if options_data_url:
            df = self.gex_analyzer.parse_options_data(options_data_url)
            gex_data = self.gex_analyzer.calculate_gex_by_strike_fixed(df, spy_price)
            key_levels = self.gex_analyzer.identify_key_levels_fixed(gex_data, spy_price)
        else:
            # Use mock data for testing
            gex_data = self._generate_mock_gex_data(spy_price)
            key_levels = self._generate_mock_key_levels(spy_price)

        print(f"GEX Analysis Complete: {len(gex_data)} strikes analyzed")

        # 2. HEATSEEKER ANALYSIS
        print("Phase 2: Heatseeker Analysis...")
        touch_probabilities = {}
        node_classifications = {}

        # Analyze key levels for touch probabilities
        for level_type, level_value in key_levels.get('spx_levels', {}).items():
            if level_value:
                spx_level = level_value
                prob_data = self.touch_tracker.get_touch_probability(spx_level)
                touch_probabilities[spx_level] = prob_data

                # Classify node type
                if level_type == 'call_wall_spx':
                    node_classifications[spx_level] = 'GATEKEEPER'
                elif level_type == 'gamma_flip_spx':
                    node_classifications[spx_level] = 'GAMMA_FLIP'
                else:
                    node_classifications[spx_level] = self._classify_heatseeker_node(
                        spx_level, spx_price, gex_data)

        print(f"Heatseeker Analysis Complete: {len(touch_probabilities)} levels analyzed")

        # 3. METHODOLOGY UNIFICATION
        print("Phase 3: Methodology Unification...")
        unified_classifications = self._unify_node_classifications(
            key_levels, touch_probabilities, gex_data, spx_price)

        # 4. VOLATILITY REGIME DETECTION
        volatility_regime = key_levels.get('market_regime', 'UNKNOWN')

        # 5. CONSENSUS SCORING
        consensus_score, directional_bias, confidence_level = self._calculate_unified_consensus(
            key_levels, touch_probabilities, spx_price)

        print(f"Unification Complete: {consensus_score:.1f}/100 consensus")

        # Create unified market state
        market_state = UnifiedMarketState(
            timestamp=timestamp,
            spy_price=spy_price,
            spx_price=spx_price,
            volume=volume or 0,
            gex_data=gex_data,
            key_levels=key_levels,
            touch_probabilities=touch_probabilities,
            node_classifications=unified_classifications,
            volatility_regime=volatility_regime,
            portfolio_heat=0.0,  # Would calculate from active positions
            consensus_score=consensus_score,
            directional_bias=directional_bias,
            confidence_level=confidence_level
        )

        self.last_market_state = market_state
        self._save_market_state(market_state)

        return market_state

    def _unify_node_classifications(self, key_levels: Dict, touch_probabilities: Dict,
                                  gex_data: Dict, current_spx: float) -> Dict:
        """
        CRITICAL: Resolve conflicts between GEX and Heatseeker classifications
        """
        unified = {}

        # RESOLVE KING NODE DEFINITION CONFLICT
        if self.config['king_node_definition'] == 'HIGHEST_ABSOLUTE_GEX':
            # Use GEX-based definition (absolute value)
            max_absolute_gex = 0
            king_node_spx = None

            for spy_strike, data in gex_data.items():
                abs_gex = abs(data['net_gex'])
                if abs_gex > max_absolute_gex:
                    max_absolute_gex = abs_gex
                    king_node_spx = spy_strike * 10  # Convert to SPX

            if king_node_spx:
                unified[king_node_spx] = {
                    'type': 'KING_NODE',
                    'source': 'GEX_ABSOLUTE',
                    'confidence': 'HIGH',
                    'gex_value': max_absolute_gex,
                    'touch_probability': touch_probabilities.get(king_node_spx, {}).get('probability', 0.9)
                }

        # ADD GATEKEEPER NODES (High GEX concentration points)
        heatseeker_nodes = key_levels.get('heatseeker_nodes', {})
        for node_type, node_data in heatseeker_nodes.items():
            spx_level = node_data['spx_level']

            if node_type == 'GATEKEEPER':
                unified[spx_level] = {
                    'type': 'GATEKEEPER',
                    'source': 'GEX_RESISTANCE',
                    'confidence': 'HIGH',
                    'gex_value': node_data.get('gex_value', 0),
                    'touch_probability': touch_probabilities.get(spx_level, {}).get('probability', 0.9)
                }

        # ADD GAMMA FLIP POINTS
        gamma_flip_spx = key_levels.get('spx_levels', {}).get('gamma_flip_spx')
        if gamma_flip_spx:
            unified[gamma_flip_spx] = {
                'type': 'GAMMA_FLIP',
                'source': 'GEX_CALCULATION',
                'confidence': 'HIGH',
                'volatility_impact': 'EXTREME',
                'touch_probability': touch_probabilities.get(gamma_flip_spx, {}).get('probability', 0.5)
            }

        return unified

    def _calculate_unified_consensus(self, key_levels: Dict, touch_probabilities: Dict,
                                   current_spx: float) -> Tuple[float, str, str]:
        """
        Calculate unified consensus score resolving double-application issues
        """
        scores = []

        # GEX Score (40% weight)
        gex_score = self._calculate_gex_score(key_levels, current_spx)
        scores.append(('GEX', gex_score, 0.4))

        # Heatseeker Score (40% weight)
        heatseeker_score = self._calculate_heatseeker_score(touch_probabilities, current_spx)
        scores.append(('HEATSEEKER', heatseeker_score, 0.4))

        # Volume Score (20% weight)
        volume_score = 75.0  # Would calculate from real volume data
        scores.append(('VOLUME', volume_score, 0.2))

        # Calculate weighted consensus (avoiding double-application)
        consensus = sum(score * weight for _, score, weight in scores)

        # Determine directional bias
        if consensus >= 60:
            directional_bias = 'BULLISH'
        elif consensus <= 40:
            directional_bias = 'BEARISH'
        else:
            directional_bias = 'NEUTRAL'

        # Determine confidence level
        if consensus >= self.config['maximum_confidence_threshold']:
            confidence = 'MAXIMUM'
        elif consensus >= self.config['high_confidence_threshold']:
            confidence = 'HIGH'
        elif consensus >= self.config['minimum_consensus']:
            confidence = 'MEDIUM'
        else:
            confidence = 'LOW'

        return consensus, directional_bias, confidence

    def _calculate_gex_score(self, key_levels: Dict, current_spx: float) -> float:
        """Calculate GEX-based score (0-100)"""
        score = 50.0  # Neutral baseline

        # Distance to gamma flip
        gamma_flip = key_levels.get('spx_levels', {}).get('gamma_flip_spx')
        if gamma_flip:
            distance = abs(current_spx - gamma_flip)
            if current_spx > gamma_flip:
                score += 15  # Positive gamma regime
            else:
                score -= 15  # Negative gamma regime

        # Call wall proximity
        call_wall = key_levels.get('spx_levels', {}).get('call_wall_spx')
        if call_wall:
            distance_to_call_wall = call_wall - current_spx
            if 0 < distance_to_call_wall < 20:  # Approaching resistance
                score += 10  # Bullish momentum
            elif distance_to_call_wall <= 0:  # Above call wall
                score += 20  # Strong bullish

        return max(0, min(100, score))

    def _calculate_heatseeker_score(self, touch_probabilities: Dict, current_spx: float) -> float:
        """Calculate Heatseeker-based score (0-100)"""
        score = 50.0  # Neutral baseline

        # Find nearest levels and their probabilities
        levels_above = [(level, data) for level, data in touch_probabilities.items() if level > current_spx]
        levels_below = [(level, data) for level, data in touch_probabilities.items() if level < current_spx]

        # Score based on nearest resistance probability
        if levels_above:
            nearest_resistance = min(levels_above, key=lambda x: x[0])
            resistance_prob = nearest_resistance[1]['probability']
            score += (resistance_prob - 0.5) * 40  # Scale to +/-20 points

        # Score based on nearest support probability
        if levels_below:
            nearest_support = max(levels_below, key=lambda x: x[0])
            support_prob = nearest_support[1]['probability']
            score += (support_prob - 0.5) * 40  # Scale to +/-20 points

        return max(0, min(100, score))

    def generate_trading_recommendation(self, market_state: UnifiedMarketState) -> TradingRecommendation:
        """
        Generate unified trading recommendation based on complete analysis
        """
        print("GENERATING UNIFIED TRADING RECOMMENDATION")
        print("=" * 60)

        # Check minimum consensus requirement
        if market_state.consensus_score < self.config['minimum_consensus']:
            return TradingRecommendation(
                action='AVOID',
                instrument='NONE',
                entry_price=0.0,
                stop_loss=0.0,
                profit_targets=[],
                position_size=0.0,
                primary_reason=f'Consensus too low: {market_state.consensus_score:.1f}/100',
                supporting_factors=[],
                risk_factors=['Low system agreement'],
                success_probability=0.0,
                risk_reward_ratio=0.0,
                expected_return=0.0,
                gex_score=0.0,
                heatseeker_score=0.0,
                consensus_score=market_state.consensus_score
            )

        # Determine optimal trade based on unified analysis
        recommendation = self._analyze_optimal_trade(market_state)

        print(f"Recommendation: {recommendation.action} {recommendation.instrument}")
        print(f"   Consensus: {recommendation.consensus_score:.1f}/100")
        print(f"   Success Probability: {recommendation.success_probability:.1%}")
        print(f"   Risk/Reward: {recommendation.risk_reward_ratio:.2f}")

        return recommendation

    def _analyze_optimal_trade(self, state: UnifiedMarketState) -> TradingRecommendation:
        """Analyze optimal trade based on unified methodology"""

        # Find best opportunity
        opportunities = []

        # Analyze each significant level
        for spx_level, node_data in state.node_classifications.items():
            spy_level = spx_level / 10
            distance = abs(spx_level - state.spx_price)

            if distance < 50:  # Within reasonable range
                opp = self._evaluate_level_opportunity(spx_level, node_data, state)
                if opp:
                    opportunities.append(opp)

        if not opportunities:
            return self._create_no_trade_recommendation(state, "No viable opportunities")

        # Select best opportunity
        best_opp = max(opportunities, key=lambda x: x['expected_value'])

        return self._create_recommendation_from_opportunity(best_opp, state)

    def _evaluate_level_opportunity(self, spx_level: float, node_data: Dict,
                                  state: UnifiedMarketState) -> Optional[Dict]:
        """Evaluate trading opportunity at a specific level"""

        distance = spx_level - state.spx_price
        spy_strike = spx_level / 10

        if abs(distance) < 2:  # Too close
            return None

        # Determine trade direction
        if distance > 0:  # Level above current price
            trade_type = 'CALL'
            probability = node_data['touch_probability']
        else:  # Level below current price
            trade_type = 'PUT'
            probability = 1 - node_data['touch_probability']  # Inverse for puts

        # Calculate expected value
        risk_amount = 100  # Base risk
        reward_amount = abs(distance) * 20  # Rough option pricing

        expected_value = (probability * reward_amount) - ((1 - probability) * risk_amount)

        if expected_value <= 0:
            return None

        return {
            'spx_level': spx_level,
            'spy_strike': spy_strike,
            'trade_type': trade_type,
            'probability': probability,
            'expected_value': expected_value,
            'risk_reward': reward_amount / risk_amount if risk_amount > 0 else 0,
            'node_type': node_data['type'],
            'confidence': node_data['confidence']
        }

    def _create_recommendation_from_opportunity(self, opportunity: Dict,
                                              state: UnifiedMarketState) -> TradingRecommendation:
        """Create formal recommendation from opportunity analysis"""

        spy_strike = int(opportunity['spy_strike'])
        instrument = f"SPY {spy_strike}{opportunity['trade_type'][0]}"

        # Estimate option pricing (simplified)
        distance = abs(opportunity['spx_level'] - state.spx_price)
        estimated_premium = max(0.5, distance * 0.1)

        return TradingRecommendation(
            action='BUY',
            instrument=instrument,
            entry_price=estimated_premium,
            stop_loss=estimated_premium * 0.5,
            profit_targets=[estimated_premium * 1.5, estimated_premium * 2.5],
            position_size=min(self.config['max_single_position'],
                            opportunity['probability'] * 5),  # Scale by probability
            primary_reason=f"{opportunity['node_type']} level at {opportunity['spx_level']}",
            supporting_factors=[
                f"{opportunity['probability']:.1%} probability",
                f"{opportunity['confidence']} confidence",
                f"Unified consensus: {state.consensus_score:.1f}/100"
            ],
            risk_factors=[
                f"Time decay" if distance < 10 else "Distance risk",
                f"Volatility regime: {state.volatility_regime}"
            ],
            success_probability=opportunity['probability'],
            risk_reward_ratio=opportunity['risk_reward'],
            expected_return=opportunity['expected_value'],
            gex_score=self._calculate_gex_score(state.key_levels, state.spx_price),
            heatseeker_score=self._calculate_heatseeker_score(state.touch_probabilities, state.spx_price),
            consensus_score=state.consensus_score
        )

    def _create_no_trade_recommendation(self, state: UnifiedMarketState, reason: str) -> TradingRecommendation:
        """Create no-trade recommendation"""
        return TradingRecommendation(
            action='HOLD',
            instrument='NONE',
            entry_price=0.0,
            stop_loss=0.0,
            profit_targets=[],
            position_size=0.0,
            primary_reason=reason,
            supporting_factors=[],
            risk_factors=[],
            success_probability=0.0,
            risk_reward_ratio=0.0,
            expected_return=0.0,
            gex_score=self._calculate_gex_score(state.key_levels, state.spx_price),
            heatseeker_score=self._calculate_heatseeker_score(state.touch_probabilities, state.spx_price),
            consensus_score=state.consensus_score
        )

    def _classify_heatseeker_node(self, spx_level: float, current_spx: float, gex_data: Dict) -> str:
        """Classify node type using unified methodology"""
        # Implementation would analyze GEX data and distance to classify
        return 'MINOR'

    def _generate_mock_gex_data(self, spy_price: float) -> Dict:
        """Generate mock GEX data for testing"""
        mock_data = {}
        for strike in range(int(spy_price) - 10, int(spy_price) + 11):
            mock_data[float(strike)] = {
                'net_gex': (strike - spy_price) * 10,  # Mock calculation
                'call_gex': max(0, (strike - spy_price) * 15),
                'put_gex': max(0, (spy_price - strike) * 15),
                'total_oi': 1000,
                'volume_weight': 500
            }
        return mock_data

    def _generate_mock_key_levels(self, spy_price: float) -> Dict:
        """Generate mock key levels for testing"""
        spx_price = spy_price * 10
        return {
            'gamma_flip': spy_price - 2,
            'call_wall': spy_price + 5,
            'put_wall': spy_price - 8,
            'market_regime': 'POSITIVE_GAMMA',
            'spx_levels': {
                'current_spx': spx_price,
                'call_wall_spx': (spy_price + 5) * 10,
                'put_wall_spx': (spy_price - 8) * 10,
                'gamma_flip_spx': (spy_price - 2) * 10
            }
        }

    def _save_market_state(self, state: UnifiedMarketState):
        """Save market state to file"""
        try:
            state_file = self.session_dir / "unified_market_state.json"
            with open(state_file, 'w') as f:
                # Convert to serializable format
                state_dict = {
                    'timestamp': state.timestamp,
                    'spy_price': state.spy_price,
                    'spx_price': state.spx_price,
                    'volume': state.volume,
                    'consensus_score': state.consensus_score,
                    'directional_bias': state.directional_bias,
                    'confidence_level': state.confidence_level,
                    'volatility_regime': state.volatility_regime,
                    'node_classifications': state.node_classifications
                }
                json.dump(state_dict, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save market state: {e}")

def test_unified_engine():
    """Test the unified trading engine"""
    print("TESTING UNIFIED TRADING ENGINE")
    print("=" * 60)

    engine = UnifiedTradingEngine()

    # Test market analysis
    spy_price = 661.74  # Current SPY price from data

    market_state = engine.analyze_market(spy_price, volume=50000)

    print(f"\nMARKET STATE SUMMARY:")
    print(f"SPX: {market_state.spx_price:.2f}")
    print(f"Consensus: {market_state.consensus_score:.1f}/100")
    print(f"Bias: {market_state.directional_bias}")
    print(f"Confidence: {market_state.confidence_level}")
    print(f"Regime: {market_state.volatility_regime}")

    # Generate recommendation
    recommendation = engine.generate_trading_recommendation(market_state)

    print(f"\nTRADING RECOMMENDATION:")
    print(f"Action: {recommendation.action}")
    print(f"Instrument: {recommendation.instrument}")
    print(f"Entry: ${recommendation.entry_price:.2f}")
    print(f"Targets: {[f'${t:.2f}' for t in recommendation.profit_targets]}")
    print(f"Position Size: {recommendation.position_size:.1f}%")
    print(f"Success Probability: {recommendation.success_probability:.1%}")
    print(f"Risk/Reward: {recommendation.risk_reward_ratio:.2f}")

    print(f"\nUNIFIED ENGINE TEST COMPLETE")

    return engine, market_state, recommendation

if __name__ == "__main__":
    test_unified_engine()