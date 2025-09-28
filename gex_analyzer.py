#!/usr/bin/env python3
"""
GEX (Gamma Exposure) Analyzer for SPY/SPXW Options
Calculates precise gamma exposure by strike for institutional-grade analysis
"""

import requests
import json
import pandas as pd
from typing import Dict, List, Tuple
from datetime import datetime

class GEXAnalyzer:
    def __init__(self):
        self.spy_multiplier = 100  # Standard options multiplier
        self.spx_conversion = 10   # SPY to SPX conversion
        
    def fetch_spy_options_data(self) -> str:
        """
        Fetch full SPY options chain with Greeks
        Returns the data URL for full dataset
        """
        # This would use the MCP function result URL
        # For now, return the URL from the previous call
        return "https://cdn.yovy.ai/alphavantage-responses/1758494354-ba5d3b66.json"
    
    def parse_options_data(self, data_url: str) -> pd.DataFrame:
        """
        Parse options data from AlphaVantage response
        Returns DataFrame with strikes, OI, gamma, etc.
        """
        try:
            response = requests.get(data_url, timeout=30)
            lines = response.text.strip().split('\n')
            
            # Parse CSV data
            header = lines[0].split(',')
            data_rows = []
            
            for line in lines[1:]:
                if line.strip():
                    row = line.split(',')
                    if len(row) == len(header):
                        data_rows.append(row)
            
            df = pd.DataFrame(data_rows, columns=header)
            
            # Convert numeric columns
            numeric_cols = ['strike', 'last', 'mark', 'bid', 'ask', 'volume', 
                          'open_interest', 'delta', 'gamma', 'theta', 'vega']
            
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            return df
            
        except Exception as e:
            print(f"Error parsing options data: {e}")
            return pd.DataFrame()
    
    def calculate_gex_by_strike(self, df: pd.DataFrame) -> Dict[float, float]:
        """
        Calculate Net Gamma Exposure by strike
        Formula: Net GEX = (Call OI × Call Gamma) - (Put OI × Put Gamma) × 100
        """
        gex_by_strike = {}
        
        # Group by strike and type
        strikes = df['strike'].unique()
        
        for strike in strikes:
            strike_data = df[df['strike'] == strike]
            
            call_data = strike_data[strike_data['type'] == 'call']
            put_data = strike_data[strike_data['type'] == 'put']
            
            # Calculate call GEX contribution
            call_gex = 0
            if not call_data.empty:
                call_oi = call_data['open_interest'].iloc[0] if not pd.isna(call_data['open_interest'].iloc[0]) else 0
                call_gamma = call_data['gamma'].iloc[0] if not pd.isna(call_data['gamma'].iloc[0]) else 0
                call_gex = call_oi * call_gamma * self.spy_multiplier
            
            # Calculate put GEX contribution  
            put_gex = 0
            if not put_data.empty:
                put_oi = put_data['open_interest'].iloc[0] if not pd.isna(put_data['open_interest'].iloc[0]) else 0
                put_gamma = put_data['gamma'].iloc[0] if not pd.isna(put_data['gamma'].iloc[0]) else 0
                put_gex = put_oi * put_gamma * self.spy_multiplier
            
            # Net GEX = Call GEX - Put GEX (market maker perspective)
            net_gex = call_gex - put_gex
            
            if abs(net_gex) > 0:  # Only include strikes with meaningful GEX
                gex_by_strike[float(strike)] = net_gex
        
        return gex_by_strike
    
    def identify_key_levels(self, gex_data: Dict[float, float], current_spy_price: float) -> Dict:
        """
        Identify key gamma levels for trading
        """
        if not gex_data:
            return {}
        
        # Sort by strike
        sorted_strikes = sorted(gex_data.keys())
        
        # Find gamma flip level (where net GEX crosses zero)
        gamma_flip = None
        for i in range(len(sorted_strikes) - 1):
            current_gex = gex_data[sorted_strikes[i]]
            next_gex = gex_data[sorted_strikes[i + 1]]
            
            if current_gex * next_gex < 0:  # Sign change
                gamma_flip = (sorted_strikes[i] + sorted_strikes[i + 1]) / 2
                break
        
        # Find largest positive and negative GEX levels
        max_positive_gex = max([gex for gex in gex_data.values() if gex > 0], default=0)
        max_negative_gex = min([gex for gex in gex_data.values() if gex < 0], default=0)
        
        # Find strikes with max GEX
        call_wall = None
        put_wall = None
        
        for strike, gex in gex_data.items():
            if gex == max_positive_gex and max_positive_gex > 0:
                call_wall = strike
            if gex == max_negative_gex and max_negative_gex < 0:
                put_wall = strike
        
        # Find nearest significant levels to current price
        near_strikes = [s for s in sorted_strikes if abs(s - current_spy_price) <= 5]
        
        return {
            'gamma_flip': gamma_flip,
            'call_wall': call_wall,
            'put_wall': put_wall,
            'max_positive_gex': max_positive_gex,
            'max_negative_gex': max_negative_gex,
            'near_strikes': near_strikes,
            'current_spy': current_spy_price,
            'spx_levels': {
                'current_spx': current_spy_price * self.spx_conversion,
                'call_wall_spx': call_wall * self.spx_conversion if call_wall else None,
                'put_wall_spx': put_wall * self.spx_conversion if put_wall else None,
                'gamma_flip_spx': gamma_flip * self.spx_conversion if gamma_flip else None
            }
        }
    
    def generate_trading_signals(self, key_levels: Dict, gex_data: Dict[float, float]) -> Dict:
        """
        Generate actionable trading signals based on GEX analysis
        """
        if not key_levels or not gex_data:
            return {}
        
        current_spy = key_levels['current_spy']
        gamma_flip = key_levels['gamma_flip']
        call_wall = key_levels['call_wall']
        put_wall = key_levels['put_wall']
        
        signals = {
            'timestamp': datetime.now().isoformat(),
            'market_regime': 'UNKNOWN',
            'volatility_bias': 'NEUTRAL',
            'key_trades': [],
            'risk_levels': [],
            'summary': ''
        }
        
        # Determine market regime
        if gamma_flip:
            if current_spy > gamma_flip:
                signals['market_regime'] = 'POSITIVE_GAMMA'
                signals['volatility_bias'] = 'SUPPRESSED'
            else:
                signals['market_regime'] = 'NEGATIVE_GAMMA'
                signals['volatility_bias'] = 'AMPLIFIED'
        
        # Generate specific trade signals
        if call_wall and current_spy < call_wall:
            distance = call_wall - current_spy
            if distance <= 2:
                signals['key_trades'].append({
                    'type': 'CALL_WALL_FADE',
                    'strike_spy': call_wall,
                    'strike_spx': call_wall * self.spx_conversion,
                    'distance': distance,
                    'setup': f"SPY {call_wall}P for resistance at gamma wall",
                    'confidence': 'HIGH' if distance <= 1 else 'MEDIUM'
                })
        
        if put_wall and current_spy > put_wall:
            distance = current_spy - put_wall
            if distance <= 2:
                signals['key_trades'].append({
                    'type': 'PUT_WALL_BOUNCE',
                    'strike_spy': put_wall,
                    'strike_spx': put_wall * self.spx_conversion,
                    'distance': distance,
                    'setup': f"SPY {put_wall}C for support at gamma wall",
                    'confidence': 'HIGH' if distance <= 1 else 'MEDIUM'
                })
        
        # Add risk levels
        for strike, gex in gex_data.items():
            if abs(gex) > abs(key_levels['max_positive_gex']) * 0.5:  # Significant GEX levels
                signals['risk_levels'].append({
                    'strike_spy': strike,
                    'strike_spx': strike * self.spx_conversion,
                    'gex_value': gex,
                    'type': 'RESISTANCE' if gex > 0 else 'SUPPORT'
                })
        
        return signals
    
    def run_full_analysis(self, current_spy_price: float) -> Dict:
        """
        Run complete GEX analysis and return results
        """
        print("Starting GEX Analysis...")
        
        # Fetch options data
        data_url = self.fetch_spy_options_data()
        print(f"Fetching options data from: {data_url[:50]}...")
        
        # Parse data
        df = self.parse_options_data(data_url)
        if df.empty:
            print("Failed to parse options data")
            return {}
        
        print(f"Parsed {len(df)} option contracts")
        
        # Calculate GEX by strike
        gex_data = self.calculate_gex_by_strike(df)
        print(f"Calculated GEX for {len(gex_data)} strikes")
        
        # Identify key levels
        key_levels = self.identify_key_levels(gex_data, current_spy_price)
        print("Identified key gamma levels")
        
        # Generate trading signals
        signals = self.generate_trading_signals(key_levels, gex_data)
        print("Generated trading signals")
        
        return {
            'gex_by_strike': gex_data,
            'key_levels': key_levels,
            'trading_signals': signals,
            'analysis_timestamp': datetime.now().isoformat()
        }

def main():
    """
    Main execution function
    """
    analyzer = GEXAnalyzer()
    
    # Current SPY price (you would get this from real-time data)
    current_spy = 663.58
    
    print(f"GEX ANALYSIS - SPY @ ${current_spy}")
    print("=" * 50)
    
    results = analyzer.run_full_analysis(current_spy)
    
    if results:
        print("\nKEY LEVELS:")
        key_levels = results['key_levels']
        
        if key_levels.get('gamma_flip'):
            print(f"Gamma Flip: SPY ${key_levels['gamma_flip']:.2f} | SPX {key_levels['spx_levels']['gamma_flip_spx']:.0f}")
        
        if key_levels.get('call_wall'):
            print(f"Call Wall: SPY ${key_levels['call_wall']:.2f} | SPX {key_levels['spx_levels']['call_wall_spx']:.0f}")
            
        if key_levels.get('put_wall'):
            print(f"Put Wall: SPY ${key_levels['put_wall']:.2f} | SPX {key_levels['spx_levels']['put_wall_spx']:.0f}")
        
        print(f"\nTRADING SIGNALS:")
        signals = results['trading_signals']
        print(f"Market Regime: {signals['market_regime']}")
        print(f"Volatility Bias: {signals['volatility_bias']}")
        
        for trade in signals['key_trades']:
            print(f"{trade['type']}: {trade['setup']} (Confidence: {trade['confidence']})")
        
        # Save results
        with open('.spx/gex_analysis.json', 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\nResults saved to .spx/gex_analysis.json")
    
    else:
        print("❌ Analysis failed")

if __name__ == "__main__":
    main()