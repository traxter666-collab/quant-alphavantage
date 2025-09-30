#!/usr/bin/env python3
"""
FIXED GEX (Gamma Exposure) Analyzer for SPY/SPXW Options
Corrects critical data pipeline and calculation issues
"""

import requests
import json
import pandas as pd
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import numpy as np

class GEXAnalyzerFixed:
    def __init__(self):
        self.spy_multiplier = 100  # Standard options multiplier
        self.spx_conversion = 10   # SPY to SPX conversion
        self.notional_scaling = 1_000_000  # Scale to millions for readability

    def fetch_spy_options_data(self) -> str:
        """
        Fetch full SPY options chain with Greeks
        Returns the data URL for full dataset
        """
        return "https://cdn.yovy.ai/alphavantage-responses/1758494354-ba5d3b66.json"

    def parse_options_data(self, data_url: str) -> pd.DataFrame:
        """
        Parse options data from AlphaVantage response
        FIXED: Better error handling and data validation
        """
        try:
            response = requests.get(data_url, timeout=30)
            lines = response.text.strip().split('\n')

            if len(lines) < 2:
                print("ERROR: Insufficient data in response")
                return pd.DataFrame()

            # Parse CSV data
            header = lines[0].split(',')
            data_rows = []

            for line in lines[1:]:
                if line.strip():
                    row = line.split(',')
                    if len(row) == len(header):
                        data_rows.append(row)

            if not data_rows:
                print("ERROR: No valid data rows found")
                return pd.DataFrame()

            df = pd.DataFrame(data_rows, columns=header)

            # Convert numeric columns with better error handling
            numeric_cols = ['strike', 'last', 'mark', 'bid', 'ask', 'volume',
                          'open_interest', 'delta', 'gamma', 'theta', 'vega']

            for col in numeric_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                    # Fill NaN values with 0 for calculations
                    df[col] = df[col].fillna(0)

            # Validate essential columns exist
            required_cols = ['strike', 'type', 'open_interest', 'gamma']
            missing_cols = [col for col in required_cols if col not in df.columns]
            if missing_cols:
                print(f"ERROR: Missing required columns: {missing_cols}")
                return pd.DataFrame()

            return df

        except Exception as e:
            print(f"Error parsing options data: {e}")
            return pd.DataFrame()

    def calculate_gex_by_strike_fixed(self, df: pd.DataFrame, current_spy_price: float) -> Dict[float, Dict]:
        """
        FIXED: Calculate Net Gamma Exposure by strike with proper financial formula

        Corrected Issues:
        1. Added underlying price multiplication (notional exposure)
        2. Preserve ALL data including zero GEX (critical for gamma flip)
        3. Added volume weighting and dealer perspective
        4. Proper scaling to institutional standards
        """
        gex_by_strike = {}

        if df.empty:
            print("ERROR: Empty DataFrame provided")
            return gex_by_strike

        # Group by strike and type
        strikes = sorted(df['strike'].unique())

        for strike in strikes:
            strike_data = df[df['strike'] == strike]

            call_data = strike_data[strike_data['type'] == 'call']
            put_data = strike_data[strike_data['type'] == 'put']

            # FIXED: Calculate call GEX contribution with proper formula
            call_gex = 0
            call_volume_weight = 0
            if not call_data.empty:
                call_oi = call_data['open_interest'].iloc[0]
                call_gamma = call_data['gamma'].iloc[0]
                call_volume = call_data['volume'].iloc[0]

                # CORRECTED FORMULA: Include underlying price for notional exposure
                call_gex = call_oi * call_gamma * self.spy_multiplier * current_spy_price
                call_volume_weight = call_volume * call_oi if call_oi > 0 else 0

            # FIXED: Calculate put GEX contribution with proper formula
            put_gex = 0
            put_volume_weight = 0
            if not put_data.empty:
                put_oi = put_data['open_interest'].iloc[0]
                put_gamma = put_data['gamma'].iloc[0]
                put_volume = put_data['volume'].iloc[0]

                # CORRECTED FORMULA: Include underlying price for notional exposure
                # Put GEX is negative from dealer perspective (they're long puts)
                put_gex = put_oi * put_gamma * self.spy_multiplier * current_spy_price
                put_volume_weight = put_volume * put_oi if put_oi > 0 else 0

            # Net GEX = Call GEX - Put GEX (market maker perspective)
            # Positive = dealers short gamma (need to buy on up moves)
            # Negative = dealers long gamma (need to sell on up moves)
            net_gex = call_gex - put_gex

            # CRITICAL FIX: PRESERVE ALL DATA INCLUDING ZERO VALUES
            # Zero GEX levels are essential for gamma flip identification
            gex_by_strike[float(strike)] = {
                'net_gex': net_gex / self.notional_scaling,  # Scale to millions
                'call_gex': call_gex / self.notional_scaling,
                'put_gex': put_gex / self.notional_scaling,
                'call_oi': call_oi if not call_data.empty else 0,
                'put_oi': put_oi if not put_data.empty else 0,
                'total_oi': (call_oi if not call_data.empty else 0) + (put_oi if not put_data.empty else 0),
                'volume_weight': call_volume_weight + put_volume_weight,
                'distance_from_spot': abs(float(strike) - current_spy_price),
                'strike_type': 'ITM' if float(strike) < current_spy_price else 'OTM',
                # ADDED: Touch probability tracking for Heatseeker methodology
                'touch_count': 0,  # Will be updated with historical data
                'last_touch_date': None,
                'probability_score': self._calculate_strike_probability(float(strike), current_spy_price, net_gex)
            }

        return gex_by_strike

    def _calculate_strike_probability(self, strike: float, current_price: float, gex_value: float) -> float:
        """
        ADDED: Calculate probability score for Heatseeker touch probability system
        """
        distance_factor = abs(strike - current_price) / current_price
        gex_factor = min(abs(gex_value) / 100, 1.0)  # Cap at 1.0

        # Higher GEX and closer distance = higher probability of touch/reaction
        base_probability = (1 - distance_factor) * 0.7 + gex_factor * 0.3

        return max(0.1, min(0.9, base_probability))  # Keep between 10-90%

    def identify_key_levels_fixed(self, gex_data: Dict[float, Dict], current_spy_price: float) -> Dict:
        """
        FIXED: Identify key gamma levels with enhanced logic

        Fixed Issues:
        1. Better gamma flip detection using all data points
        2. Added volume weighting for level significance
        3. Enhanced classification logic
        4. Added Heatseeker node classification
        """
        if not gex_data:
            return {}

        # Sort by strike
        sorted_strikes = sorted(gex_data.keys())

        # IMPROVED: Find gamma flip level with better interpolation
        gamma_flip = None
        flip_confidence = 0

        for i in range(len(sorted_strikes) - 1):
            current_strike = sorted_strikes[i]
            next_strike = sorted_strikes[i + 1]
            current_gex = gex_data[current_strike]['net_gex']
            next_gex = gex_data[next_strike]['net_gex']

            # Check for sign change (zero crossing)
            if current_gex * next_gex < 0:  # Sign change detected
                # Linear interpolation to find exact flip point
                weight = abs(current_gex) / (abs(current_gex) + abs(next_gex))
                gamma_flip = current_strike + (next_strike - current_strike) * weight

                # Confidence based on GEX magnitude and volume
                total_volume = (gex_data[current_strike]['volume_weight'] +
                              gex_data[next_strike]['volume_weight'])
                flip_confidence = min(total_volume / 1000, 1.0)  # Normalize
                break

        # IMPROVED: Find walls with volume weighting
        call_wall_candidates = []
        put_wall_candidates = []

        for strike, data in gex_data.items():
            if data['net_gex'] > 0:  # Positive GEX (call wall candidate)
                call_wall_candidates.append((strike, data['net_gex'], data['volume_weight']))
            elif data['net_gex'] < 0:  # Negative GEX (put wall candidate)
                put_wall_candidates.append((strike, abs(data['net_gex']), data['volume_weight']))

        # Find strongest levels (GEX * volume weighting)
        call_wall = None
        call_wall_strength = 0
        if call_wall_candidates:
            call_wall_scored = [(strike, gex_val * (1 + vol_weight/10000))
                               for strike, gex_val, vol_weight in call_wall_candidates]
            call_wall, call_wall_strength = max(call_wall_scored, key=lambda x: x[1])

        put_wall = None
        put_wall_strength = 0
        if put_wall_candidates:
            put_wall_scored = [(strike, gex_val * (1 + vol_weight/10000))
                              for strike, gex_val, vol_weight in put_wall_candidates]
            put_wall, put_wall_strength = max(put_wall_scored, key=lambda x: x[1])

        # ADDED: Heatseeker node classification
        nodes_classified = self._classify_heatseeker_nodes(gex_data, current_spy_price,
                                                          call_wall, put_wall, gamma_flip)

        return {
            'gamma_flip': gamma_flip,
            'gamma_flip_confidence': flip_confidence,
            'call_wall': call_wall,
            'call_wall_strength': call_wall_strength,
            'put_wall': put_wall,
            'put_wall_strength': put_wall_strength,
            'current_spy': current_spy_price,
            'spx_levels': {
                'current_spx': current_spy_price * self.spx_conversion,
                'call_wall_spx': call_wall * self.spx_conversion if call_wall else None,
                'put_wall_spx': put_wall * self.spx_conversion if put_wall else None,
                'gamma_flip_spx': gamma_flip * self.spx_conversion if gamma_flip else None
            },
            'heatseeker_nodes': nodes_classified,
            'market_regime': self._determine_market_regime(current_spy_price, gamma_flip, call_wall, put_wall),
            'volatility_expectation': self._calculate_volatility_expectation(current_spy_price, gamma_flip)
        }

    def _classify_heatseeker_nodes(self, gex_data: Dict, current_price: float,
                                  call_wall: Optional[float], put_wall: Optional[float],
                                  gamma_flip: Optional[float]) -> Dict:
        """
        ADDED: Classify strikes according to Heatseeker methodology
        """
        nodes = {}

        # Find highest absolute GEX value for King Node
        max_absolute_gex = 0
        king_node = None

        for strike, data in gex_data.items():
            abs_gex = abs(data['net_gex'])
            if abs_gex > max_absolute_gex:
                max_absolute_gex = abs_gex
                king_node = strike

        # Classify major nodes
        if king_node:
            nodes['KING_NODE'] = {
                'strike': king_node,
                'spy_level': king_node,
                'spx_level': king_node * self.spx_conversion,
                'absolute_gex': max_absolute_gex,
                'node_type': 'KING_NODE',
                'description': 'Highest absolute GEX - dealer preferred settlement',
                'distance_from_current': abs(king_node - current_price)
            }

        if call_wall and call_wall != king_node:
            nodes['GATEKEEPER'] = {
                'strike': call_wall,
                'spy_level': call_wall,
                'spx_level': call_wall * self.spx_conversion,
                'gex_value': gex_data[call_wall]['net_gex'],
                'node_type': 'GATEKEEPER',
                'description': 'Major resistance - high deflection probability',
                'distance_from_current': abs(call_wall - current_price)
            }

        if gamma_flip:
            nodes['GAMMA_FLIP'] = {
                'strike': gamma_flip,
                'spy_level': gamma_flip,
                'spx_level': gamma_flip * self.spx_conversion,
                'node_type': 'GAMMA_FLIP',
                'description': 'Volatility regime change level',
                'distance_from_current': abs(gamma_flip - current_price)
            }

        return nodes

    def _determine_market_regime(self, current_price: float, gamma_flip: Optional[float],
                                call_wall: Optional[float], put_wall: Optional[float]) -> str:
        """
        ADDED: Determine current market regime for volatility expectations
        """
        if not gamma_flip:
            return "UNKNOWN"

        if current_price > gamma_flip:
            return "POSITIVE_GAMMA"  # Lower volatility expected
        else:
            return "NEGATIVE_GAMMA"  # Higher volatility expected

    def _calculate_volatility_expectation(self, current_price: float, gamma_flip: Optional[float]) -> str:
        """
        ADDED: Calculate volatility expectation based on position relative to gamma flip
        """
        if not gamma_flip:
            return "UNKNOWN"

        distance_to_flip = abs(current_price - gamma_flip) / current_price

        if distance_to_flip < 0.01:  # Within 1% of flip
            return "EXTREME_VOLATILITY"
        elif current_price > gamma_flip:
            return "SUPPRESSED_VOLATILITY"
        else:
            return "AMPLIFIED_VOLATILITY"

def run_fixed_gex_analysis():
    """
    Run the fixed GEX analysis with proper error handling
    """
    analyzer = GEXAnalyzerFixed()

    print("🔧 RUNNING FIXED GEX ANALYSIS")
    print("=" * 50)

    try:
        # Fetch data
        data_url = analyzer.fetch_spy_options_data()
        print(f"✅ Data URL: {data_url}")

        # Parse options chain
        df = analyzer.parse_options_data(data_url)
        if df.empty:
            print("❌ Failed to parse options data")
            return None

        print(f"✅ Parsed {len(df)} option contracts")

        # Assume current SPY price (would get from live data)
        current_spy_price = 661.74  # From latest data

        # Calculate GEX with fixes
        gex_data = analyzer.calculate_gex_by_strike_fixed(df, current_spy_price)
        print(f"✅ Calculated GEX for {len(gex_data)} strikes")

        # Identify key levels
        key_levels = analyzer.identify_key_levels_fixed(gex_data, current_spy_price)

        # Display results
        print("\n🎯 KEY LEVELS IDENTIFIED:")
        print(f"Current SPY: ${current_spy_price}")
        print(f"Current SPX: {current_spy_price * 10:.2f}")

        if key_levels.get('gamma_flip'):
            print(f"Gamma Flip: SPY ${key_levels['gamma_flip']:.2f} | SPX {key_levels['spx_levels']['gamma_flip_spx']:.2f}")
            print(f"Market Regime: {key_levels['market_regime']}")
            print(f"Volatility: {key_levels['volatility_expectation']}")

        if key_levels.get('call_wall'):
            print(f"Call Wall: SPY ${key_levels['call_wall']:.2f} | SPX {key_levels['spx_levels']['call_wall_spx']:.2f}")

        if key_levels.get('put_wall'):
            print(f"Put Wall: SPY ${key_levels['put_wall']:.2f} | SPX {key_levels['spx_levels']['put_wall_spx']:.2f}")

        # Heatseeker nodes
        print("\n🔥 HEATSEEKER NODE CLASSIFICATION:")
        for node_type, node_data in key_levels.get('heatseeker_nodes', {}).items():
            print(f"{node_type}: SPX {node_data['spx_level']:.2f} ({node_data['description']})")

        return key_levels

    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        return None

if __name__ == "__main__":
    result = run_fixed_gex_analysis()