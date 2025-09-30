#!/usr/bin/env python3
"""
Smart Futures Integration - Enhanced Logic + Original System
Combines enhanced trading logic with existing futures integration
"""

import os
import json
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional

# Import existing modules
try:
    from futures_integration import FuturesIntegration
    from enhanced_futures_logic import EnhancedFuturesLogic
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure futures_integration.py and enhanced_futures_logic.py are in the same directory")
    sys.exit(1)

class SmartFuturesIntegration:
    """Intelligent futures trading system with enhanced logic"""

    def __init__(self):
        # Initialize both systems
        self.futures_base = FuturesIntegration()
        self.futures_enhanced = EnhancedFuturesLogic()

        # Performance tracking
        self.trade_history = []
        self.enhanced_features_enabled = True

        print("Smart Futures Integration initialized")
        print("Combining base futures analysis with enhanced market intelligence")

    def smart_futures_analysis(self, symbol: str, account_size: float = 25000) -> Dict[str, Any]:
        """Complete smart futures analysis combining both systems"""

        print(f"\n{'='*70}")
        print(f"SMART {symbol.upper()} FUTURES ANALYSIS")
        print(f"{'='*70}")

        # Step 1: Get base analysis
        print("Step 1: Running base futures analysis...")
        base_analysis = self.futures_base.analyze_futures_contract(symbol)

        if 'error' in base_analysis:
            return base_analysis

        # Step 2: Get enhanced analysis
        print("Step 2: Running enhanced market intelligence...")
        price_data = base_analysis['price_data']
        enhanced_analysis = self.futures_enhanced.generate_enhanced_trading_signals(symbol, price_data)

        # Step 3: Combine insights
        print("Step 3: Combining analysis systems...")
        combined_analysis = self._combine_analyses(base_analysis, enhanced_analysis, account_size)

        # Step 4: Generate final recommendation
        print("Step 4: Generating intelligent recommendation...")
        final_recommendation = self._generate_smart_recommendation(combined_analysis)

        # Compile complete result
        smart_result = {
            'symbol': symbol,
            'base_analysis': base_analysis,
            'enhanced_analysis': enhanced_analysis,
            'combined_insights': combined_analysis,
            'final_recommendation': final_recommendation,
            'timestamp': datetime.now().isoformat()
        }

        # Display results
        self._display_smart_results(smart_result)

        # Save results
        self._save_smart_results(smart_result, symbol)

        return smart_result

    def _combine_analyses(self, base: Dict, enhanced: Dict, account_size: float) -> Dict[str, Any]:
        """Combine base and enhanced analyses intelligently"""

        base_consensus = base.get('consensus', {})
        enhanced_recommendation = enhanced.get('recommendation', {})
        enhanced_sizing = enhanced.get('position_sizing', {})

        # Consensus scoring (average of both systems)
        base_score = base_consensus.get('percentage', 50)
        enhanced_score = enhanced['enhanced_analysis']['signal_strength']['percentage']

        # Weight the scores (base 60%, enhanced 40%)
        combined_score = (base_score * 0.6) + (enhanced_score * 0.4)

        # Direction agreement
        base_direction = base_consensus.get('direction', 'NEUTRAL')
        enhanced_action = enhanced_recommendation.get('action', 'AVOID')

        # Convert enhanced action to direction
        if enhanced_action in ['STRONG_BUY', 'BUY']:
            enhanced_direction = 'BULLISH'
        elif enhanced_action in ['CONSIDER']:
            enhanced_direction = 'NEUTRAL'
        else:
            enhanced_direction = 'BEARISH'

        direction_agreement = base_direction == enhanced_direction

        # Position sizing (use enhanced system's sophisticated calculation)
        smart_position_size = enhanced_sizing.get('recommended_contracts', 1)

        # Risk assessment
        base_risk = base.get('position_sizing', {}).get('risk_percent', 10)
        enhanced_risk = enhanced_sizing.get('risk_percent_of_account', 10)
        combined_risk = (base_risk + enhanced_risk) / 2

        # Market conditions
        market_conditions = enhanced['enhanced_analysis']

        return {
            'combined_score': combined_score,
            'base_score': base_score,
            'enhanced_score': enhanced_score,
            'direction_agreement': direction_agreement,
            'base_direction': base_direction,
            'enhanced_direction': enhanced_direction,
            'smart_position_size': smart_position_size,
            'combined_risk_percent': combined_risk,
            'market_conditions': market_conditions,
            'account_size': account_size
        }

    def _generate_smart_recommendation(self, combined: Dict) -> Dict[str, Any]:
        """Generate intelligent final recommendation"""

        combined_score = combined['combined_score']
        direction_agreement = combined['direction_agreement']
        base_direction = combined['base_direction']
        enhanced_direction = combined['enhanced_direction']
        position_size = combined['smart_position_size']
        risk_percent = combined['combined_risk_percent']

        # Smart decision logic
        if combined_score >= 75 and direction_agreement and risk_percent <= 15:
            action = 'STRONG_BUY' if base_direction == 'BULLISH' else 'STRONG_SELL'
            confidence = 'VERY_HIGH'
            size_multiplier = 1.0
        elif combined_score >= 65 and direction_agreement:
            action = 'BUY' if base_direction == 'BULLISH' else 'SELL'
            confidence = 'HIGH'
            size_multiplier = 0.8
        elif combined_score >= 55:
            if direction_agreement:
                action = 'CONSIDER' if base_direction == 'BULLISH' else 'CONSIDER_SHORT'
                confidence = 'MEDIUM'
                size_multiplier = 0.6
            else:
                action = 'WAIT'
                confidence = 'LOW'
                size_multiplier = 0.0
        else:
            action = 'AVOID'
            confidence = 'VERY_LOW'
            size_multiplier = 0.0

        # Adjust position size
        final_contracts = max(0, int(position_size * size_multiplier))

        # Risk override
        if risk_percent > 20:
            action = 'AVOID'
            confidence = 'RISK_TOO_HIGH'
            final_contracts = 0

        return {
            'action': action,
            'confidence': confidence,
            'contracts': final_contracts,
            'combined_score': combined_score,
            'direction_agreement': direction_agreement,
            'risk_percent': risk_percent,
            'reasoning': self._generate_reasoning(combined_score, direction_agreement, base_direction, risk_percent),
            'market_session': combined['market_conditions']['session']['session'],
            'volatility_regime': combined['market_conditions']['volatility']['regime'],
            'risk_regime': combined['market_conditions']['correlation'].get('risk_regime', 'UNKNOWN')
        }

    def _generate_reasoning(self, score: float, agreement: bool, direction: str, risk: float) -> str:
        """Generate human-readable reasoning for recommendation"""

        reasons = []

        # Score component
        if score >= 75:
            reasons.append(f"Strong consensus ({score:.1f}%)")
        elif score >= 65:
            reasons.append(f"Good consensus ({score:.1f}%)")
        elif score >= 55:
            reasons.append(f"Moderate consensus ({score:.1f}%)")
        else:
            reasons.append(f"Weak consensus ({score:.1f}%)")

        # Agreement component
        if agreement:
            reasons.append(f"Both systems agree on {direction.lower()} direction")
        else:
            reasons.append("Systems disagree on direction")

        # Risk component
        if risk <= 10:
            reasons.append(f"Low risk ({risk:.1f}%)")
        elif risk <= 15:
            reasons.append(f"Moderate risk ({risk:.1f}%)")
        else:
            reasons.append(f"High risk ({risk:.1f}%)")

        return "; ".join(reasons)

    def _display_smart_results(self, result: Dict) -> None:
        """Display comprehensive smart analysis results"""

        symbol = result['symbol']
        base = result['base_analysis']
        enhanced = result['enhanced_analysis']
        combined = result['combined_insights']
        recommendation = result['final_recommendation']

        print(f"\n{'='*70}")
        print(f"SMART {symbol.upper()} TRADING RECOMMENDATION")
        print(f"{'='*70}")

        # Current price
        price_data = base['price_data']
        print(f"Current Price: ${price_data['price']:.2f} ({price_data['change_percent']:+.2f}%)")

        # Combined scores
        print(f"\nANALYSIS SCORES:")
        print(f"Base System: {combined['base_score']:.1f}%")
        print(f"Enhanced System: {combined['enhanced_score']:.1f}%")
        print(f"Combined Score: {combined['combined_score']:.1f}%")
        print(f"Direction Agreement: {'YES' if combined['direction_agreement'] else 'NO'}")

        # Market conditions
        conditions = combined['market_conditions']
        print(f"\nMARKET CONDITIONS:")
        print(f"Session: {conditions['session']['session'].upper()}")
        print(f"Volatility: {conditions['volatility']['regime'].upper()}")
        print(f"Risk Regime: {conditions['correlation'].get('risk_regime', 'UNKNOWN')}")

        # Final recommendation
        print(f"\nFINAL RECOMMENDATION:")
        print(f"Action: {recommendation['action']}")
        print(f"Confidence: {recommendation['confidence']}")
        print(f"Contracts: {recommendation['contracts']}")
        print(f"Risk: {recommendation['risk_percent']:.1f}% of account")
        print(f"Reasoning: {recommendation['reasoning']}")

        # Trade setup (if action is to trade)
        if recommendation['contracts'] > 0:
            # Use base analysis for trade details
            signals = base.get('signals', [])
            if signals:
                signal = signals[0]
                print(f"\nTRADE SETUP:")
                print(f"Entry: ${signal['entry_price']:.2f}")
                print(f"Stop Loss: ${signal['stop_loss']:.2f}")
                print(f"Profit Target: ${signal['profit_target']:.2f}")
                print(f"Risk/Reward: {signal['risk_reward']}")
                print(f"Margin Required: ${signal['margin_required']:,.0f}")

    def _save_smart_results(self, result: Dict, symbol: str) -> None:
        """Save smart analysis results"""

        try:
            os.makedirs('.spx', exist_ok=True)
            filename = f'.spx/smart_{symbol.lower()}_analysis.json'

            with open(filename, 'w') as f:
                json.dump(result, f, indent=2)

            print(f"\nSmart analysis saved to {filename}")

            # Also update trade history
            self.trade_history.append({
                'symbol': symbol,
                'timestamp': result['timestamp'],
                'action': result['final_recommendation']['action'],
                'confidence': result['final_recommendation']['confidence'],
                'combined_score': result['combined_insights']['combined_score']
            })

            # Save trade history
            with open('.spx/smart_trade_history.json', 'w') as f:
                json.dump(self.trade_history, f, indent=2)

        except Exception as e:
            print(f"Warning: Could not save smart results: {e}")

    def multi_smart_analysis(self, symbols: List[str] = None, account_size: float = 25000) -> Dict[str, Any]:
        """Run smart analysis on multiple futures contracts"""

        if symbols is None:
            symbols = ['ES', 'NQ', 'GC']

        print("SMART MULTI-FUTURES ANALYSIS")
        print("Enhanced logic + Base analysis for all contracts")
        print("=" * 80)

        results = {}
        recommendations = []

        for symbol in symbols:
            print(f"\nAnalyzing {symbol}...")
            result = self.smart_futures_analysis(symbol, account_size)
            results[symbol] = result

            # Collect recommendations
            if result['final_recommendation']['contracts'] > 0:
                recommendations.append({
                    'symbol': symbol,
                    'action': result['final_recommendation']['action'],
                    'confidence': result['final_recommendation']['confidence'],
                    'contracts': result['final_recommendation']['contracts'],
                    'score': result['combined_insights']['combined_score']
                })

        # Sort recommendations by score
        recommendations.sort(key=lambda x: x['score'], reverse=True)

        # Display top recommendations
        print(f"\n{'='*80}")
        print(f"TOP SMART FUTURES OPPORTUNITIES")
        print(f"{'='*80}")

        if recommendations:
            print(f"RANKED BY COMBINED SCORE:")
            for i, rec in enumerate(recommendations[:3], 1):
                print(f"{i}. {rec['action']} {rec['symbol']} - {rec['contracts']} contracts")
                print(f"   Score: {rec['score']:.1f}% | Confidence: {rec['confidence']}")
        else:
            print("No high-confidence trading opportunities currently")

        # Save multi-analysis results
        multi_result = {
            'individual_analyses': results,
            'top_recommendations': recommendations,
            'analysis_timestamp': datetime.now().isoformat()
        }

        try:
            with open('.spx/smart_multi_futures_analysis.json', 'w') as f:
                json.dump(multi_result, f, indent=2)
            print(f"\nMulti-futures analysis saved to .spx/smart_multi_futures_analysis.json")
        except Exception as e:
            print(f"Warning: Could not save multi-analysis: {e}")

        return multi_result

def main():
    """Main execution for smart futures integration"""
    import sys

    smart_system = SmartFuturesIntegration()

    if len(sys.argv) > 1:
        symbol = sys.argv[1].upper()
        if symbol in ['ES', 'NQ', 'GC']:
            smart_system.smart_futures_analysis(symbol)
        elif symbol == 'MULTI':
            smart_system.multi_smart_analysis()
        else:
            print(f"Unsupported symbol: {symbol}")
            print("Supported: ES, NQ, GC, or MULTI")
    else:
        # Default: run smart analysis on ES
        smart_system.smart_futures_analysis('ES')

if __name__ == "__main__":
    main()