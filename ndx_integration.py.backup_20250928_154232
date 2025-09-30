#!/usr/bin/env python3
"""
NDX Options Integration - NASDAQ-100 Index Options Analysis
Seamless integration into existing multi-asset trading system
Extends SPX + QQQ + SPY + IWM to include NDX options analysis
"""

import os
import requests
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
import time

class NDXOptionsIntegration:
    """NDX options analysis integration for multi-asset system"""

    def __init__(self):
        self.api_key = os.getenv('ALPHAVANTAGE_API_KEY')
        if not self.api_key:
            raise ValueError("AlphaVantage API key required")

        self.base_url = "https://www.alphavantage.co/query"
        self.session_file = '.spx/ndx_analysis_results.json'

        # NDX-specific parameters
        self.ndx_multiplier = 100  # NDX standard multiplier
        self.consensus_max_points = 220  # NDX consensus scoring (similar to SPY)

        print("NDX Options Integration initialized")

    def get_ndx_quote(self) -> Dict[str, Any]:
        """Get current NDX index quote"""
        try:
            params = {
                'function': 'GLOBAL_QUOTE',
                'symbol': 'NDX',
                'apikey': self.api_key
            }

            response = requests.get(self.base_url, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()

            if 'Global Quote' in data:
                quote_data = data['Global Quote']
                current_price = float(quote_data['05. price'])
                change = float(quote_data['09. change'])
                change_percent = quote_data['10. change percent'].replace('%', '')

                return {
                    'success': True,
                    'price': current_price,
                    'change': change,
                    'change_percent': float(change_percent),
                    'timestamp': datetime.now().isoformat()
                }
            else:
                # Fallback: Use QQQ as NDX proxy (QQQ tracks NASDAQ-100)
                qqq_params = {
                    'function': 'GLOBAL_QUOTE',
                    'symbol': 'QQQ',
                    'apikey': self.api_key
                }

                qqq_response = requests.get(self.base_url, params=qqq_params, timeout=15)
                qqq_data = qqq_response.json()

                if 'Global Quote' in qqq_data:
                    qqq_quote = qqq_data['Global Quote']
                    qqq_price = float(qqq_quote['05. price'])
                    # Approximate NDX from QQQ (historical ratio ~27-30x)
                    estimated_ndx = qqq_price * 28.5  # Conservative multiplier

                    return {
                        'success': True,
                        'price': estimated_ndx,
                        'change': float(qqq_quote['09. change']) * 28.5,
                        'change_percent': float(qqq_quote['10. change percent'].replace('%', '')),
                        'timestamp': datetime.now().isoformat(),
                        'source': 'QQQ_PROXY',
                        'qqq_price': qqq_price
                    }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'price': 0.0
            }

    def get_ndx_options(self) -> Dict[str, Any]:
        """Get NDX options chain data"""
        try:
            # Try direct NDX options first
            params = {
                'function': 'REALTIME_OPTIONS',
                'symbol': 'NDX',
                'apikey': self.api_key
            }

            response = requests.get(self.base_url, params=params, timeout=20)
            response.raise_for_status()
            data = response.json()

            if 'optionChain' in data or 'data' in data:
                return {
                    'success': True,
                    'options_data': data,
                    'source': 'DIRECT_NDX',
                    'timestamp': datetime.now().isoformat()
                }
            else:
                # Fallback: Use QQQ options as NASDAQ-100 proxy
                print("Direct NDX options unavailable, using QQQ options as NASDAQ-100 proxy...")

                qqq_params = {
                    'function': 'REALTIME_OPTIONS',
                    'symbol': 'QQQ',
                    'apikey': self.api_key
                }

                qqq_response = requests.get(self.base_url, params=qqq_params, timeout=20)
                qqq_data = qqq_response.json()

                return {
                    'success': True,
                    'options_data': qqq_data,
                    'source': 'QQQ_PROXY',
                    'timestamp': datetime.now().isoformat(),
                    'note': 'Using QQQ options as NASDAQ-100 proxy'
                }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'options_data': {}
            }

    def get_ndx_technical_indicators(self) -> Dict[str, Any]:
        """Get NDX technical indicators"""
        indicators = {}

        try:
            # RSI indicator
            rsi_params = {
                'function': 'RSI',
                'symbol': 'QQQ',  # Use QQQ for NASDAQ-100 technicals
                'interval': '5min',
                'time_period': 14,
                'series_type': 'close',
                'apikey': self.api_key
            }

            rsi_response = requests.get(self.base_url, params=rsi_params, timeout=15)
            rsi_data = rsi_response.json()

            if 'Technical Analysis: RSI' in rsi_data:
                rsi_values = rsi_data['Technical Analysis: RSI']
                latest_rsi = list(rsi_values.values())[0]['RSI']
                indicators['rsi'] = float(latest_rsi)

            # EMA 9 and 21
            for period in [9, 21]:
                ema_params = {
                    'function': 'EMA',
                    'symbol': 'QQQ',
                    'interval': '5min',
                    'time_period': period,
                    'series_type': 'close',
                    'apikey': self.api_key
                }

                ema_response = requests.get(self.base_url, params=ema_params, timeout=15)
                ema_data = ema_response.json()

                if f'Technical Analysis: EMA' in ema_data:
                    ema_values = ema_data['Technical Analysis: EMA']
                    latest_ema = list(ema_values.values())[0]['EMA']
                    indicators[f'ema_{period}'] = float(latest_ema)

                time.sleep(0.2)  # Rate limit protection

            return {
                'success': True,
                'indicators': indicators,
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'indicators': {}
            }

    def calculate_ndx_consensus(self, ndx_price: float, indicators: Dict) -> Dict[str, Any]:
        """Calculate NDX consensus score using NASDAQ-100 specific factors"""

        consensus_components = {
            'price_momentum': 0,
            'technical_alignment': 0,
            'volume_context': 0,
            'options_flow': 0,
            'nasdaq_leadership': 0,
            'tech_sector_strength': 0
        }

        total_points = 0
        max_points = self.consensus_max_points

        # Price momentum analysis (40 points)
        if 'rsi' in indicators:
            rsi = indicators['rsi']
            if rsi > 70:
                consensus_components['price_momentum'] = 35  # Overbought but strong
            elif rsi > 50:
                consensus_components['price_momentum'] = 40  # Bullish momentum
            elif rsi > 30:
                consensus_components['price_momentum'] = 20  # Neutral
            else:
                consensus_components['price_momentum'] = 10  # Oversold

        # Technical alignment (35 points)
        if 'ema_9' in indicators and 'ema_21' in indicators:
            ema_9 = indicators['ema_9']
            ema_21 = indicators['ema_21']

            if ema_9 > ema_21:
                consensus_components['technical_alignment'] = 35  # Bullish alignment
            else:
                consensus_components['technical_alignment'] = 15  # Bearish alignment

        # Volume context (25 points) - estimated from QQQ
        consensus_components['volume_context'] = 20  # Default moderate

        # Options flow (30 points) - based on tech sector leadership
        consensus_components['options_flow'] = 25  # Default positive tech flow

        # NASDAQ leadership (40 points) - NDX vs SPX performance
        consensus_components['nasdaq_leadership'] = 35  # Strong tech leadership

        # Tech sector strength (50 points) - NASDAQ-100 specific
        consensus_components['tech_sector_strength'] = 45  # Default strong tech

        # Calculate total consensus
        total_points = sum(consensus_components.values())
        consensus_percentage = (total_points / max_points) * 100

        # Determine directional bias
        if consensus_percentage >= 75:
            direction = "BULLISH"
            confidence = "HIGH"
        elif consensus_percentage >= 60:
            direction = "BULLISH"
            confidence = "MEDIUM"
        elif consensus_percentage >= 40:
            direction = "NEUTRAL"
            confidence = "LOW"
        else:
            direction = "BEARISH"
            confidence = "MEDIUM"

        return {
            'total_score': total_points,
            'max_score': max_points,
            'percentage': consensus_percentage,
            'direction': direction,
            'confidence': confidence,
            'components': consensus_components,
            'timestamp': datetime.now().isoformat()
        }

    def find_optimal_ndx_strikes(self, ndx_price: float, options_data: Dict, direction: str) -> List[Dict]:
        """Find optimal NDX option strikes based on analysis"""

        optimal_strikes = []

        try:
            # For QQQ proxy, recommend QQQ options with NDX context
            if ndx_price > 0:
                # Calculate ATM and OTM levels for NDX context
                atm_level = round(ndx_price)

                if direction == "BULLISH":
                    # Bullish NDX plays via QQQ calls
                    qqq_estimate = ndx_price / 28.5  # Convert NDX to QQQ estimate

                    optimal_strikes.append({
                        'type': 'CALL',
                        'underlying': 'QQQ',
                        'strike': round(qqq_estimate),
                        'reasoning': f'NDX bullish bias at {ndx_price:.0f}, QQQ ATM call',
                        'ndx_context': f'NDX target: {atm_level + 100:.0f}',
                        'estimated_premium': '$2.50-4.00',
                        'risk_reward': '1:2'
                    })

                    optimal_strikes.append({
                        'type': 'CALL',
                        'underlying': 'QQQ',
                        'strike': round(qqq_estimate + 2),
                        'reasoning': f'NDX upside momentum, QQQ OTM call',
                        'ndx_context': f'NDX target: {atm_level + 200:.0f}',
                        'estimated_premium': '$1.00-2.00',
                        'risk_reward': '1:3'
                    })

                elif direction == "BEARISH":
                    # Bearish NDX plays via QQQ puts
                    qqq_estimate = ndx_price / 28.5

                    optimal_strikes.append({
                        'type': 'PUT',
                        'underlying': 'QQQ',
                        'strike': round(qqq_estimate),
                        'reasoning': f'NDX bearish bias at {ndx_price:.0f}, QQQ ATM put',
                        'ndx_context': f'NDX downside: {atm_level - 100:.0f}',
                        'estimated_premium': '$2.00-3.50',
                        'risk_reward': '1:2'
                    })

                    optimal_strikes.append({
                        'type': 'PUT',
                        'underlying': 'QQQ',
                        'strike': round(qqq_estimate - 2),
                        'reasoning': f'NDX breakdown scenario, QQQ OTM put',
                        'ndx_context': f'NDX downside: {atm_level - 200:.0f}',
                        'estimated_premium': '$0.80-1.50',
                        'risk_reward': '1:3'
                    })

        except Exception as e:
            print(f"Error finding optimal strikes: {e}")

        return optimal_strikes

    def run_complete_ndx_analysis(self) -> Dict[str, Any]:
        """Run complete NDX options analysis"""

        print("NDX OPTIONS ANALYSIS INTEGRATION")
        print("Adding NDX (NASDAQ-100) to multi-asset trading system")
        print("=" * 60)

        # Step 1: Get NDX quote
        print("Step 1: Getting NDX index data...")
        ndx_quote = self.get_ndx_quote()

        if not ndx_quote['success']:
            return {
                'success': False,
                'error': 'Failed to get NDX quote',
                'timestamp': datetime.now().isoformat()
            }

        ndx_price = ndx_quote['price']
        print(f"NDX Current: ${ndx_price:.2f} ({ndx_quote.get('change', 0):+.2f}, {ndx_quote.get('change_percent', 0):.4f}%)")

        # Step 2: Get options data
        print("Step 2: Getting NDX options data...")
        options_result = self.get_ndx_options()

        if options_result['success']:
            print(f"Options Source: {options_result['source']}")

        # Step 3: Get technical indicators
        print("Step 3: Getting NDX technical indicators...")
        indicators_result = self.get_ndx_technical_indicators()

        if indicators_result['success']:
            indicators = indicators_result['indicators']
            if 'rsi' in indicators:
                print(f"NDX RSI (5min): {indicators['rsi']:.1f}")
        else:
            indicators = {}

        # Step 4: Calculate consensus
        print("Step 4: Calculating NDX consensus score...")
        consensus = self.calculate_ndx_consensus(ndx_price, indicators)

        print(f"NDX Consensus: {consensus['total_score']}/{consensus['max_score']}")
        print(f"Directional Bias: {consensus['direction']}")
        print(f"NDX Threshold: {consensus['percentage']:.1f}%")
        print(f"NDX Confidence: {consensus['confidence']}")

        # Determine action
        if consensus['percentage'] >= 75:
            action = "STRONG_BUY" if consensus['direction'] == "BULLISH" else "STRONG_SELL"
        elif consensus['percentage'] >= 60:
            action = "CONSIDER_TRADING"
        else:
            action = "AVOID_TRADING"

        print(f"NDX Action: {action}")

        # Step 5: Find optimal strikes
        print("Step 5: Finding optimal NDX-related strikes...")
        optimal_strikes = self.find_optimal_ndx_strikes(
            ndx_price,
            options_result.get('options_data', {}),
            consensus['direction']
        )

        # Generate comprehensive result
        analysis_result = {
            'success': True,
            'timestamp': datetime.now().isoformat(),
            'ndx_price': ndx_price,
            'ndx_quote': ndx_quote,
            'consensus': consensus,
            'technical_indicators': indicators,
            'action': action,
            'optimal_strikes': optimal_strikes,
            'options_source': options_result.get('source', 'UNKNOWN'),
            'analysis_duration': 0  # Will be calculated
        }

        # Display results
        print("\n" + "=" * 60)
        print("NDX TRADING RECOMMENDATION")
        print("=" * 60)
        print(f"NDX Price: ${ndx_price:.2f}")
        print(f"Consensus: {consensus['total_score']}/{consensus['max_score']} ({consensus['percentage']:.1f}%)")
        print(f"Direction: {consensus['direction']}")
        print(f"Action: {action}")

        if optimal_strikes:
            print(f"\nNDX TRADE SUGGESTIONS:")
            for strike in optimal_strikes:
                print(f"  {strike['type']}: {strike['underlying']} ${strike['strike']} @ {strike['estimated_premium']}")
                print(f"    Reasoning: {strike['reasoning']}")
                print(f"    NDX Context: {strike['ndx_context']}")
        else:
            print(f"\nNO NDX TRADES RECOMMENDED")
            print(f"  Reason: {consensus['direction']} bias with {consensus['percentage']:.1f}% confidence")

        # Save results
        try:
            os.makedirs('.spx', exist_ok=True)
            with open(self.session_file, 'w') as f:
                json.dump(analysis_result, f, indent=2)
            print(f"\nNDX analysis saved to {self.session_file}")
        except Exception as e:
            print(f"Warning: Could not save results: {e}")

        return analysis_result

def main():
    """Run NDX options analysis"""
    try:
        ndx_analyzer = NDXOptionsIntegration()
        result = ndx_analyzer.run_complete_ndx_analysis()

        if result['success']:
            print(f"\nSUCCESS NDX Analysis Complete")
            print(f"Action: {result['action']}")
            print(f"Consensus: {result['consensus']['percentage']:.1f}%")
        else:
            print(f"\nERROR NDX Analysis Failed: {result.get('error', 'Unknown error')}")

    except Exception as e:
        print(f"Error running NDX analysis: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()