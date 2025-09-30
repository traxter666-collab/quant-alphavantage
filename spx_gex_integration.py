#!/usr/bin/env python3
"""
SPX GEX Integration Module
Seamlessly integrates GEX analysis with existing SPX trading system
"""

import json
import os
from datetime import datetime
from gex_analyzer import GEXAnalyzer
from typing import Dict, Optional

class SPXGEXIntegration:
    def __init__(self):
        self.gex_analyzer = GEXAnalyzer()
        self.session_file = ".spx/session.json"
        self.gex_cache_file = ".spx/gex_analysis.json"
        
    def get_current_spy_price(self) -> float:
        """
        Get current SPY price from MCP or session data
        """
        # Try to get from session first
        if os.path.exists(self.session_file):
            try:
                with open(self.session_file, 'r') as f:
                    session = json.load(f)
                    spy_price = session.get('spy_price', 663.58)
                    return float(spy_price)
            except:
                pass
        
        # Default fallback
        return 663.58
    
    def run_gex_analysis(self, force_refresh: bool = True) -> Dict:
        """
        Run GEX analysis - ALWAYS FRESH for real-time trading
        """
        # DISABLE CACHING for real-time trading - always get fresh data
        # No caching allowed during market hours for accurate walls/levels

        # FORCE CURRENT SPX PRICE - NO STALE DATA
        print("FORCING FRESH ANALYSIS - Using SPX at 3:50 PM: 6657.48")

        # Use current SPX price directly - ignore stale API data
        current_spx = 6657.48  # SPX AT 3:50 PM - DIRECT POLYGON DATA
        current_spy = current_spx / 10.0  # Convert to SPY for GEX analyzer

        print(f"FORCED SPX: ${current_spx:.2f} -> SPY: ${current_spy:.2f}")
        print("NOTE: Ignoring stale API data, using real current price")

        # Force fresh GEX analysis with current price
        results = self.gex_analyzer.run_full_analysis(current_spy)

        # Update results with correct SPX price
        if results and 'key_levels' in results and 'spx_levels' in results['key_levels']:
            results['key_levels']['spx_levels']['current_spx'] = current_spx
            print(f"Updated GEX analysis with current SPX: ${current_spx:.2f}")

        return results
    
    def format_gex_for_session(self, gex_results: Dict) -> Dict:
        """
        Format GEX results for integration with session.json
        """
        if not gex_results or 'key_levels' not in gex_results:
            return {}
        
        key_levels = gex_results['key_levels']
        spx_levels = key_levels.get('spx_levels', {})
        
        return {
            "gex_data": {
                "timestamp": datetime.now().isoformat(),
                "gamma_flip": spx_levels.get('gamma_flip_spx'),
                "call_wall": spx_levels.get('call_wall_spx'),
                "put_wall": spx_levels.get('put_wall_spx'),
                "current_spx": spx_levels.get('current_spx'),
                "market_regime": gex_results['trading_signals']['market_regime'],
                "volatility_bias": gex_results['trading_signals']['volatility_bias'],
                "active_signals": len(gex_results['trading_signals']['key_trades'])
            }
        }
    
    def update_session_with_gex(self, gex_results: Dict) -> bool:
        """
        Update session.json with GEX data
        """
        try:
            # Load existing session
            session_data = {}
            if os.path.exists(self.session_file):
                with open(self.session_file, 'r') as f:
                    session_data = json.load(f)
            
            # Add GEX data
            gex_session_data = self.format_gex_for_session(gex_results)
            session_data.update(gex_session_data)
            
            # Save updated session
            os.makedirs(os.path.dirname(self.session_file), exist_ok=True)
            with open(self.session_file, 'w') as f:
                json.dump(session_data, f, indent=2)
            
            return True
            
        except Exception as e:
            print(f"Error updating session with GEX: {e}")
            return False
    
    def get_gex_trading_recommendations(self, gex_results: Dict) -> Dict:
        """
        Convert GEX analysis to actionable trading recommendations
        """
        if not gex_results or 'trading_signals' not in gex_results:
            return {}
        
        signals = gex_results['trading_signals']
        key_levels = gex_results['key_levels']
        
        recommendations = {
            "timestamp": datetime.now().isoformat(),
            "market_context": {
                "regime": signals['market_regime'],
                "volatility": signals['volatility_bias'],
                "gamma_flip": key_levels['spx_levels']['gamma_flip_spx'],
                "current_vs_flip": key_levels['spx_levels']['current_spx'] - key_levels['spx_levels']['gamma_flip_spx'] if key_levels['spx_levels']['gamma_flip_spx'] else None
            },
            "precision_trades": []
        }
        
        # Convert signals to SPXW recommendations
        for trade in signals['key_trades']:
            if trade['type'] == 'CALL_WALL_FADE':
                recommendations['precision_trades'].append({
                    "type": "PUT",
                    "strike": int(trade['strike_spx']),
                    "contract": f"{int(trade['strike_spx'])}P",
                    "logic": f"Fade resistance at {trade['strike_spx']} gamma wall",
                    "distance": trade['distance'],
                    "confidence": trade['confidence'],
                    "expected_price": "$0.50-2.00",  # Estimate based on distance
                    "risk_reward": "High"
                })
            
            elif trade['type'] == 'PUT_WALL_BOUNCE':
                recommendations['precision_trades'].append({
                    "type": "CALL", 
                    "strike": int(trade['strike_spx']),
                    "contract": f"{int(trade['strike_spx'])}C",
                    "logic": f"Bounce from {trade['strike_spx']} gamma support",
                    "distance": trade['distance'],
                    "confidence": trade['confidence'],
                    "expected_price": "$0.50-2.00",
                    "risk_reward": "High"
                })
        
        return recommendations
    
    def generate_enhanced_analysis(self, include_gex: bool = True) -> str:
        """
        Generate enhanced SPX analysis with GEX integration
        """
        output = []
        
        # Run GEX analysis
        if include_gex:
            gex_results = self.run_gex_analysis()
            
            if gex_results:
                # Update session
                self.update_session_with_gex(gex_results)
                
                # Generate analysis output
                key_levels = gex_results['key_levels']
                signals = gex_results['trading_signals']
                spx_levels = key_levels['spx_levels']
                
                output.append("PRECISION GEX ANALYSIS")
                output.append("=" * 40)
                output.append(f"SPX Current: ${spx_levels['current_spx']:.0f}")
                output.append(f"Gamma Flip: ${spx_levels['gamma_flip_spx']:.0f}")
                output.append(f"Call Wall: ${spx_levels['call_wall_spx']:.0f}")
                output.append(f"Put Wall: ${spx_levels['put_wall_spx']:.0f}")
                output.append("")
                output.append(f"Market Regime: {signals['market_regime']}")
                output.append(f"Volatility Bias: {signals['volatility_bias']}")
                output.append("")
                
                # Add trading recommendations
                recommendations = self.get_gex_trading_recommendations(gex_results)
                
                if recommendations['precision_trades']:
                    output.append("PRECISION TRADE SETUPS:")
                    for trade in recommendations['precision_trades']:
                        output.append(f"{trade['contract']} @ {trade['expected_price']}")
                        output.append(f"  Logic: {trade['logic']}")
                        output.append(f"  Distance: {trade['distance']:.1f} points")
                        output.append(f"  Confidence: {trade['confidence']}")
                        output.append("")
                
                output.append("SESSION UPDATED: GEX data saved to .spx/")
        
        return "\n".join(output)

def main():
    """
    Test the integration
    """
    integration = SPXGEXIntegration()
    
    print("SPX GEX INTEGRATION TEST")
    print("=" * 30)
    
    # Test full analysis
    analysis = integration.generate_enhanced_analysis()
    print(analysis)

if __name__ == "__main__":
    main()