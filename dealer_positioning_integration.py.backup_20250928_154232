#!/usr/bin/env python3
"""
Dealer Positioning Integration with Existing SPX Trading System
Seamlessly integrates Heatseeker methodology with 275-point scoring system

Integration Features:
- Enhances existing consensus scoring with dealer positioning intelligence
- Adds King Node and Put/Call wall detection to current analysis
- Provides multi-strike analysis capabilities
- Maintains 100% compatibility with existing system
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dealer_positioning_engine import DealerPositioningEngine, NodeType, TouchSequence

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SPXDealerIntegration:
    """Integration layer between dealer positioning and existing SPX system"""

    def __init__(self, api_key: str = None):
        self.dealer_engine = DealerPositioningEngine(api_key)
        self.session_file = ".spx/integrated_analysis.json"

        # Ensure session directory exists
        os.makedirs(".spx", exist_ok=True)

        logger.info("SPX Dealer Integration initialized - Heatseeker + 275-point system")

    def enhanced_consensus_scoring(self, base_score: float, symbol: str = 'SPX') -> Dict[str, Any]:
        """Enhance existing 275-point scoring with dealer positioning intelligence"""
        try:
            # Get dealer positioning analysis
            positioning = self.dealer_engine.analyze_dealer_positioning([symbol])

            if symbol not in positioning:
                return {
                    'enhanced_score': base_score,
                    'dealer_adjustment': 0,
                    'positioning_insights': None,
                    'error': 'No positioning data available'
                }

            analysis = positioning[symbol]

            # Calculate dealer positioning adjustment (±25 points max)
            dealer_adjustment = 0

            # King Node proximity boost
            if analysis.primary_magnet:
                distance_pct = abs(analysis.primary_magnet.strike - analysis.underlying_price) / analysis.underlying_price * 100
                if distance_pct <= 2.0:  # Within 2%
                    king_boost = min(20, analysis.primary_magnet.confidence / 5)  # Up to +20 points
                    dealer_adjustment += king_boost

            # Put/Call wall proximity
            for wall in analysis.put_walls + analysis.call_walls:
                distance_pct = abs(wall.strike - analysis.underlying_price) / analysis.underlying_price * 100
                if distance_pct <= 1.0:  # Very close to wall
                    wall_boost = min(15, wall.confidence / 7)  # Up to +15 points
                    dealer_adjustment += wall_boost

            # Touch sequence adjustment
            if analysis.primary_magnet:
                touch_adjustments = {
                    TouchSequence.UNTESTED: 10,      # +10 points for untested levels
                    TouchSequence.FIRST: 5,          # +5 points for first touch
                    TouchSequence.SECOND: 0,         # Neutral for second touch
                    TouchSequence.THIRD_PLUS: -10    # -10 points for overused levels
                }
                dealer_adjustment += touch_adjustments.get(analysis.primary_magnet.touch_sequence, 0)

            # Confluence adjustment
            if analysis.confluence_score >= 80:
                dealer_adjustment += 15  # Strong confluence bonus
            elif analysis.confluence_score >= 60:
                dealer_adjustment += 8   # Moderate confluence bonus
            elif analysis.confluence_score < 40:
                dealer_adjustment -= 10  # Poor confluence penalty

            # OPEX and market regime adjustments
            dealer_adjustment *= analysis.opex_adjustment
            regime_adjustments = {
                'LOW_VOL': 1.1,
                'NORMAL_VOL': 1.0,
                'HIGH_VOL': 0.9,
                'EXTREME_VOL': 0.7
            }
            dealer_adjustment *= regime_adjustments.get(analysis.market_regime.value, 1.0)

            # Cap adjustment at ±25 points
            dealer_adjustment = max(-25, min(25, dealer_adjustment))

            # Calculate final enhanced score
            enhanced_score = base_score + dealer_adjustment

            # Generate positioning insights
            insights = self._generate_positioning_insights(analysis)

            return {
                'enhanced_score': enhanced_score,
                'base_score': base_score,
                'dealer_adjustment': dealer_adjustment,
                'positioning_insights': insights,
                'confluence_score': analysis.confluence_score,
                'market_regime': analysis.market_regime.value,
                'opex_adjustment': analysis.opex_adjustment,
                'primary_magnet': {
                    'strike': analysis.primary_magnet.strike,
                    'type': analysis.primary_magnet.node_type.value,
                    'distance': abs(analysis.primary_magnet.strike - analysis.underlying_price),
                    'confidence': analysis.primary_magnet.confidence,
                    'touch_sequence': analysis.primary_magnet.touch_sequence.value
                } if analysis.primary_magnet else None
            }

        except Exception as e:
            logger.error(f"Error in enhanced consensus scoring: {e}")
            return {
                'enhanced_score': base_score,
                'dealer_adjustment': 0,
                'positioning_insights': None,
                'error': str(e)
            }

    def _generate_positioning_insights(self, analysis) -> Dict[str, Any]:
        """Generate actionable positioning insights"""
        insights = {
            'key_levels': [],
            'trade_opportunities': [],
            'risk_warnings': [],
            'confluence_status': 'UNKNOWN'
        }

        # Key levels identification
        if analysis.primary_magnet:
            insights['key_levels'].append({
                'level': analysis.primary_magnet.strike,
                'type': 'PRIMARY_MAGNET',
                'strength': analysis.primary_magnet.magnet_strength,
                'touch_status': analysis.primary_magnet.touch_sequence.value
            })

        # Put/Call walls
        for wall in analysis.put_walls[:2]:  # Top 2 put walls
            insights['key_levels'].append({
                'level': wall.strike,
                'type': 'PUT_WALL',
                'strength': wall.magnet_strength,
                'confidence': wall.confidence
            })

        for wall in analysis.call_walls[:2]:  # Top 2 call walls
            insights['key_levels'].append({
                'level': wall.strike,
                'type': 'CALL_WALL',
                'strength': wall.magnet_strength,
                'confidence': wall.confidence
            })

        # Trade opportunities
        if analysis.primary_magnet:
            distance_pct = abs(analysis.primary_magnet.strike - analysis.underlying_price) / analysis.underlying_price * 100

            if distance_pct <= 1.5:
                opportunity_type = "PUT" if analysis.primary_magnet.strike < analysis.underlying_price else "CALL"
                insights['trade_opportunities'].append({
                    'type': opportunity_type,
                    'strike_target': analysis.primary_magnet.strike,
                    'confidence': analysis.primary_magnet.confidence,
                    'reasoning': f'King Node {analysis.primary_magnet.touch_sequence.value} touch opportunity'
                })

        # Risk warnings
        if analysis.confluence_score < 50:
            insights['risk_warnings'].append('LOW CONFLUENCE: SPX/SPY/QQQ showing disagreement')

        if analysis.market_regime.value == 'EXTREME_VOL':
            insights['risk_warnings'].append('EXTREME VOLATILITY: Reduced node reliability')

        if analysis.opex_adjustment < 1.0:
            insights['risk_warnings'].append('OPEX WEEK: Reduced positioning accuracy')

        # Range warnings
        range_position = (analysis.underlying_price - analysis.range_low) / (analysis.range_high - analysis.range_low)
        if 0.4 <= range_position <= 0.6:
            insights['risk_warnings'].append('RANGE MIDPOINT: Avoid trading in no-mans land')

        # Confluence status
        if analysis.confluence_score >= 80:
            insights['confluence_status'] = 'STRONG'
        elif analysis.confluence_score >= 60:
            insights['confluence_status'] = 'MODERATE'
        elif analysis.confluence_score >= 40:
            insights['confluence_status'] = 'WEAK'
        else:
            insights['confluence_status'] = 'POOR'

        return insights

    def multi_strike_analysis(self, symbols: List[str] = None, price_range: Tuple[float, float] = None) -> Dict[str, Any]:
        """Analyze multiple strikes simultaneously with dealer positioning"""
        if symbols is None:
            symbols = ['SPX', 'SPY', 'QQQ']

        logger.info(f"Starting multi-strike analysis for {symbols}")

        # Get dealer positioning for all symbols
        positioning_results = self.dealer_engine.analyze_dealer_positioning(symbols)

        multi_strike_analysis = {
            'timestamp': datetime.now().isoformat(),
            'symbols_analyzed': len(positioning_results),
            'cross_symbol_confluence': 0.0,
            'optimal_strikes': [],
            'range_analysis': {},
            'institutional_flow': {},
            'warnings': []
        }

        # Calculate cross-symbol confluence
        confluence_scores = [analysis.confluence_score for analysis in positioning_results.values()]
        if confluence_scores:
            multi_strike_analysis['cross_symbol_confluence'] = sum(confluence_scores) / len(confluence_scores)

        # Optimal strikes identification
        all_high_confidence_nodes = []
        for symbol, analysis in positioning_results.items():
            for node in analysis.king_nodes + analysis.put_walls + analysis.call_walls:
                if node.confidence >= 70:  # High confidence threshold
                    all_high_confidence_nodes.append({
                        'symbol': symbol,
                        'strike': node.strike,
                        'type': node.node_type.value,
                        'confidence': node.confidence,
                        'magnet_strength': node.magnet_strength,
                        'touch_sequence': node.touch_sequence.value,
                        'underlying_price': analysis.underlying_price
                    })

        # Sort by confidence and take top 10
        all_high_confidence_nodes.sort(key=lambda x: x['confidence'], reverse=True)
        multi_strike_analysis['optimal_strikes'] = all_high_confidence_nodes[:10]

        # Range analysis
        for symbol, analysis in positioning_results.items():
            range_width = analysis.range_high - analysis.range_low
            range_position = (analysis.underlying_price - analysis.range_low) / range_width

            multi_strike_analysis['range_analysis'][symbol] = {
                'range_low': analysis.range_low,
                'range_high': analysis.range_high,
                'range_width': range_width,
                'current_position': range_position,
                'midpoint_warning': 0.4 <= range_position <= 0.6
            }

        # Institutional flow analysis
        for symbol, analysis in positioning_results.items():
            total_put_walls = len(analysis.put_walls)
            total_call_walls = len(analysis.call_walls)

            if total_put_walls > total_call_walls:
                flow_bias = 'BEARISH'
            elif total_call_walls > total_put_walls:
                flow_bias = 'BULLISH'
            else:
                flow_bias = 'NEUTRAL'

            multi_strike_analysis['institutional_flow'][symbol] = {
                'bias': flow_bias,
                'put_walls': total_put_walls,
                'call_walls': total_call_walls,
                'primary_magnet_direction': 'UP' if analysis.primary_magnet and analysis.primary_magnet.strike > analysis.underlying_price else 'DOWN'
            }

        # Generate warnings
        if multi_strike_analysis['cross_symbol_confluence'] < 50:
            multi_strike_analysis['warnings'].append('POOR CROSS-SYMBOL CONFLUENCE: High divergence risk')

        # Check for conflicting institutional flows
        flows = [flow['bias'] for flow in multi_strike_analysis['institutional_flow'].values()]
        if len(set(flows)) > 1:
            multi_strike_analysis['warnings'].append('CONFLICTING INSTITUTIONAL FLOWS: Mixed dealer positioning')

        # OPEX warnings
        opex_adjustments = [analysis.opex_adjustment for analysis in positioning_results.values()]
        if any(adj < 1.0 for adj in opex_adjustments):
            multi_strike_analysis['warnings'].append('OPEX WEEK: Reduced positioning reliability')

        return multi_strike_analysis

    def generate_integrated_analysis_report(self, base_consensus_score: float = None) -> str:
        """Generate comprehensive integrated analysis report"""
        if base_consensus_score is None:
            base_consensus_score = 200  # Default base score

        # Get enhanced scoring
        enhanced_result = self.enhanced_consensus_scoring(base_consensus_score, 'SPX')

        # Get multi-strike analysis
        multi_strike = self.multi_strike_analysis(['SPX', 'SPY', 'QQQ'])

        # Get direct trading signals
        trading_signals = self.dealer_engine.get_trading_signals('SPX')

        # Generate report
        report = []
        report.append("INTEGRATED SPX ANALYSIS - HEATSEEKER + 275-POINT SYSTEM")
        report.append("=" * 65)
        report.append("")

        # Enhanced Scoring Section
        report.append("ENHANCED CONSENSUS SCORING:")
        report.append(f"Base Score: {enhanced_result['base_score']:.1f}/275")
        report.append(f"Dealer Adjustment: {enhanced_result['dealer_adjustment']:+.1f}")
        report.append(f"Enhanced Score: {enhanced_result['enhanced_score']:.1f}/300")

        if enhanced_result['enhanced_score'] >= 240:
            confidence_level = "EXTREME CONFIDENCE"
        elif enhanced_result['enhanced_score'] >= 220:
            confidence_level = "HIGH CONFIDENCE"
        elif enhanced_result['enhanced_score'] >= 200:
            confidence_level = "MEDIUM CONFIDENCE"
        else:
            confidence_level = "LOW CONFIDENCE"

        report.append(f"Confidence Level: {confidence_level}")
        report.append("")

        # Primary Magnet Section
        if enhanced_result.get('primary_magnet'):
            magnet = enhanced_result['primary_magnet']
            report.append("PRIMARY MAGNET ANALYSIS:")
            report.append(f"Strike: ${magnet['strike']:.2f}")
            report.append(f"Type: {magnet['type']}")
            report.append(f"Distance: ${magnet['distance']:.2f}")
            report.append(f"Confidence: {magnet['confidence']:.1f}%")
            report.append(f"Touch Status: {magnet['touch_sequence']}")
            report.append("")

        # Key Levels Section
        insights = enhanced_result.get('positioning_insights', {})
        if insights and insights.get('key_levels'):
            report.append("KEY DEALER LEVELS:")
            for level in insights['key_levels'][:5]:
                report.append(f"${level['level']:.2f}: {level['type']} (Strength: {level.get('strength', 0):.1f})")
            report.append("")

        # Trading Opportunities
        if insights and insights.get('trade_opportunities'):
            report.append("TRADING OPPORTUNITIES:")
            for opp in insights['trade_opportunities']:
                report.append(f"{opp['type']} Setup: Target ${opp['strike_target']:.2f}")
                report.append(f"  Confidence: {opp['confidence']:.1f}%")
                report.append(f"  Reasoning: {opp['reasoning']}")
            report.append("")

        # Multi-Strike Analysis
        report.append("MULTI-STRIKE ANALYSIS:")
        report.append(f"Cross-Symbol Confluence: {multi_strike['cross_symbol_confluence']:.1f}%")
        report.append(f"Symbols Analyzed: {multi_strike['symbols_analyzed']}")

        if multi_strike['optimal_strikes']:
            report.append("\nTop Optimal Strikes:")
            for i, strike in enumerate(multi_strike['optimal_strikes'][:3], 1):
                report.append(f"{i}. {strike['symbol']} ${strike['strike']:.2f}: {strike['confidence']:.1f}% ({strike['type']})")
        report.append("")

        # Institutional Flow
        report.append("INSTITUTIONAL FLOW:")
        for symbol, flow in multi_strike['institutional_flow'].items():
            report.append(f"{symbol}: {flow['bias']} bias ({flow['put_walls']} put walls, {flow['call_walls']} call walls)")
        report.append("")

        # Risk Warnings
        all_warnings = []
        if insights and insights.get('risk_warnings'):
            all_warnings.extend(insights['risk_warnings'])
        if multi_strike.get('warnings'):
            all_warnings.extend(multi_strike['warnings'])

        if all_warnings:
            report.append("RISK WARNINGS:")
            for warning in all_warnings:
                report.append(f"- {warning}")
            report.append("")

        # Market Context
        report.append("MARKET CONTEXT:")
        report.append(f"Market Regime: {enhanced_result.get('market_regime', 'UNKNOWN')}")
        report.append(f"Confluence Score: {enhanced_result.get('confluence_score', 0):.1f}%")
        report.append(f"OPEX Adjustment: {enhanced_result.get('opex_adjustment', 1.0):.1f}")
        report.append("")

        # Trading Signals
        if trading_signals.get('signals'):
            report.append("DIRECT TRADING SIGNALS:")
            for i, signal in enumerate(trading_signals['signals'][:3], 1):
                report.append(f"{i}. {signal['type']} ${signal['strike']:.2f}")
                report.append(f"   Confidence: {signal['confidence']:.1f}%")
                report.append(f"   Reason: {signal['entry_reason']}")
                report.append(f"   Distance: {signal['distance_pct']:.2f}%")
            report.append("")

        # Final Recommendation
        report.append("FINAL RECOMMENDATION:")
        if enhanced_result['enhanced_score'] >= 240:
            report.append("STRONG BUY/SELL signal - High dealer positioning confluence")
        elif enhanced_result['enhanced_score'] >= 220:
            report.append("BUY/SELL signal - Good dealer positioning support")
        elif enhanced_result['enhanced_score'] >= 200:
            report.append("CONSIDER position - Moderate dealer positioning")
        else:
            report.append("AVOID/WAIT - Insufficient dealer positioning confluence")

        return "\n".join(report)

def main():
    """Test integrated analysis"""
    try:
        integration = SPXDealerIntegration()

        print("TESTING INTEGRATED DEALER POSITIONING SYSTEM")
        print("=" * 55)

        # Test enhanced scoring
        base_score = 210  # Example base consensus score
        enhanced = integration.enhanced_consensus_scoring(base_score, 'SPX')

        print(f"\nENHANCED SCORING TEST:")
        print(f"Base Score: {enhanced['base_score']}/275")
        print(f"Dealer Adjustment: {enhanced['dealer_adjustment']:+.1f}")
        print(f"Enhanced Score: {enhanced['enhanced_score']:.1f}/300")

        # Test multi-strike analysis
        print(f"\nMULTI-STRIKE ANALYSIS TEST:")
        multi_strike = integration.multi_strike_analysis(['SPX', 'SPY', 'QQQ'])
        print(f"Cross-Symbol Confluence: {multi_strike['cross_symbol_confluence']:.1f}%")
        print(f"Optimal Strikes Found: {len(multi_strike['optimal_strikes'])}")

        # Generate full report
        print(f"\n" + "="*65)
        print("FULL INTEGRATED ANALYSIS REPORT:")
        print("="*65)
        report = integration.generate_integrated_analysis_report(base_score)
        print(report)

        print(f"\nIntegration test complete!")

    except Exception as e:
        print(f"Integration test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()