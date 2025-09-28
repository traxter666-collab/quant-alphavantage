#!/usr/bin/env python3
"""
SPX Data Integration - Production Ready System
Integrates enhanced SPX data with existing trading analysis
"""

from enhanced_spx_data import EnhancedSPXData
import json
from datetime import datetime

class SPXTradingIntegration:
    def __init__(self):
        self.spx_data = EnhancedSPXData()
        
    def get_current_spx_analysis(self) -> dict:
        """Get comprehensive SPX analysis with accurate data"""
        
        print("Getting real-time SPX data...")
        spx_result = self.spx_data.get_best_spx_price()
        
        if 'error' in spx_result:
            return {'error': 'Unable to get SPX data'}
        
        current_price = spx_result['price']
        
        # Calculate key levels based on actual SPX price
        support_levels = [
            current_price - 20,  # Strong support
            current_price - 10,  # Near support
            current_price - 5    # Immediate support
        ]
        
        resistance_levels = [
            current_price + 5,   # Immediate resistance
            current_price + 10,  # Near resistance  
            current_price + 20   # Strong resistance
        ]
        
        # Generate optimal SPXW strikes
        optimal_calls = []
        optimal_puts = []
        
        for i, distance in enumerate([5, 10, 15, 20]):
            call_strike = int((current_price + distance) / 5) * 5  # Round to nearest 5
            put_strike = int((current_price - distance) / 5) * 5
            
            optimal_calls.append({
                'strike': call_strike,
                'distance_otm': call_strike - current_price,
                'symbol': f'SPXW{call_strike}C'
            })
            
            optimal_puts.append({
                'strike': put_strike,
                'distance_otm': current_price - put_strike,
                'symbol': f'SPXW{put_strike}P'
            })
        
        analysis = {
            'timestamp': datetime.now().isoformat(),
            'spx_data': spx_result,
            'current_price': current_price,
            'support_levels': support_levels,
            'resistance_levels': resistance_levels,
            'optimal_calls': optimal_calls,
            'optimal_puts': optimal_puts,
            'data_quality': {
                'source': spx_result.get('source', 'unknown'),
                'accuracy': spx_result.get('validation', {}).get('accuracy', 'UNKNOWN'),
                'consensus_sources': spx_result.get('consensus', {}).get('sources_count', 1)
            }
        }
        
        return analysis
    
    def recommend_best_contracts(self, time_to_expiry_hours: float = 1.0) -> dict:
        """Recommend best SPXW contracts with accurate SPX data"""
        
        analysis = self.get_current_spx_analysis()
        if 'error' in analysis:
            return analysis
        
        current_price = analysis['current_price']
        
        # Time decay factor (higher = more time decay risk)
        time_factor = min(1.0, time_to_expiry_hours / 6.0)  # 6 hours = normal
        
        recommendations = {
            'bullish': [],
            'bearish': [],
            'best_overall': None
        }
        
        # Analyze call options
        for call in analysis['optimal_calls']:
            distance = call['distance_otm']
            
            # Probability estimate (closer = higher probability)
            probability = max(0.1, 0.8 - (distance / current_price) * 20)
            
            # Adjust for time decay
            adjusted_prob = probability * time_factor
            
            # Risk/reward calculation
            estimated_premium = max(0.5, 3.0 - distance * 0.1)  # Rough estimate
            potential_return = (distance / estimated_premium) * 100 if estimated_premium > 0 else 0
            
            call_analysis = {
                'contract': call['symbol'],
                'strike': call['strike'],
                'distance': distance,
                'probability': adjusted_prob,
                'estimated_premium': estimated_premium,
                'potential_return': potential_return,
                'risk_reward': potential_return / 100 if potential_return > 0 else 0,
                'recommendation': 'BUY' if adjusted_prob > 0.3 and potential_return > 50 else 'CONSIDER' if adjusted_prob > 0.2 else 'AVOID'
            }
            
            recommendations['bullish'].append(call_analysis)
        
        # Analyze put options
        for put in analysis['optimal_puts']:
            distance = put['distance_otm']
            
            probability = max(0.1, 0.8 - (distance / current_price) * 20)
            adjusted_prob = probability * time_factor
            
            estimated_premium = max(0.5, 3.0 - distance * 0.1)
            potential_return = (distance / estimated_premium) * 100 if estimated_premium > 0 else 0
            
            put_analysis = {
                'contract': put['symbol'],
                'strike': put['strike'],
                'distance': distance,
                'probability': adjusted_prob,
                'estimated_premium': estimated_premium,
                'potential_return': potential_return,
                'risk_reward': potential_return / 100 if potential_return > 0 else 0,
                'recommendation': 'BUY' if adjusted_prob > 0.3 and potential_return > 50 else 'CONSIDER' if adjusted_prob > 0.2 else 'AVOID'
            }
            
            recommendations['bearish'].append(put_analysis)
        
        # Find best overall recommendation
        all_contracts = recommendations['bullish'] + recommendations['bearish']
        best_contract = max(all_contracts, 
                          key=lambda x: x['probability'] * x['risk_reward'] 
                          if x['recommendation'] != 'AVOID' else 0)
        
        recommendations['best_overall'] = best_contract
        recommendations['analysis_meta'] = analysis['data_quality']
        
        return recommendations

def test_integration():
    """Test the SPX trading integration"""
    print("SPX TRADING INTEGRATION TEST")
    print("=" * 40)
    
    integration = SPXTradingIntegration()
    
    # Test current analysis
    analysis = integration.get_current_spx_analysis()
    
    if 'error' not in analysis:
        print(f"SPX Price: ${analysis['current_price']:.2f}")
        print(f"Data Source: {analysis['data_quality']['source']}")
        print(f"Accuracy: {analysis['data_quality']['accuracy']}")
        print()
        
        # Test contract recommendations
        recommendations = integration.recommend_best_contracts(time_to_expiry_hours=1.5)
        
        if 'error' not in recommendations:
            best = recommendations['best_overall']
            print(f"BEST CONTRACT: {best['contract']}")
            print(f"Strike: ${best['strike']}")
            print(f"Probability: {best['probability']:.1%}")
            print(f"Est. Return: {best['potential_return']:.0f}%")
            print(f"Recommendation: {best['recommendation']}")
            
            return True
    
    return False

if __name__ == "__main__":
    success = test_integration()
    print(f"\nIntegration Test: {'PASSED' if success else 'FAILED'}")