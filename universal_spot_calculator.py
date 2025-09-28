#!/usr/bin/env python3
"""
Universal Spot Price Calculator
Extract accurate spot prices from options chains for any stock or index
"""

from options_spot_calculator import OptionsSpotCalculator
from enhanced_spx_data import EnhancedSPXData
import requests
from typing import Dict, Optional

class UniversalSpotCalculator:
    def __init__(self):
        self.options_calc = OptionsSpotCalculator()
        self.spx_data = EnhancedSPXData()
        self.alphavantage_key = "ZFL38ZY98GSN7E1S"
    
    def get_spot_price(self, symbol: str, method: str = "auto") -> Dict:
        """
        Get spot price for any symbol using best available method
        
        Args:
            symbol: Stock/index symbol (e.g., "SPY", "SPXW", "AAPL", "TSLA")
            method: "options", "quote", "auto" (tries options first, falls back to quote)
        
        Returns:
            Dict with price, source, accuracy, and metadata
        """
        symbol = symbol.upper().strip()
        
        print(f"Getting spot price for {symbol} using method: {method}")
        
        # Special handling for SPX-related symbols
        if symbol in ['SPX', 'SPXW', 'SPX.X']:
            return self._get_spx_spot()
        
        # Auto method: Try options first, fallback to quote
        if method in ["auto", "options"]:
            options_result = self._get_options_spot(symbol)
            if options_result and 'error' not in options_result:
                return options_result
            
            if method == "options":
                return options_result or {'error': f'No options data for {symbol}'}
        
        # Fallback to direct quote
        if method in ["auto", "quote"]:
            return self._get_quote_spot(symbol)
        
        return {'error': f'Invalid method: {method}'}
    
    def _get_spx_spot(self) -> Dict:
        """Get SPX spot using enhanced multi-source system"""
        result = self.spx_data.get_best_spx_price()
        
        if 'error' not in result:
            return {
                'symbol': 'SPX',
                'price': result['price'],
                'source': result['source'],
                'method': 'enhanced_spx',
                'accuracy': 'high' if 'options' in result['source'] else 'medium',
                'consensus_sources': result.get('consensus', {}).get('sources_count', 1),
                'timestamp': result.get('timestamp')
            }
        
        return result
    
    def _get_options_spot(self, symbol: str) -> Optional[Dict]:
        """Get spot price using options put-call parity"""
        try:
            result = self.options_calc.extract_spot_from_options(symbol)
            
            if 'error' not in result:
                return {
                    'symbol': symbol,
                    'price': result['spot_price'],
                    'source': 'options_parity',
                    'method': 'put_call_parity',
                    'accuracy': result['accuracy'],
                    'calculation_count': result['calculation_count'],
                    'timestamp': result['timestamp']
                }
            else:
                print(f"Options failed for {symbol}: {result['error']}")
                return None
                
        except Exception as e:
            print(f"Options extraction error for {symbol}: {e}")
            return None
    
    def _get_quote_spot(self, symbol: str) -> Dict:
        """Get spot price using direct quote API"""
        try:
            url = "https://www.alphavantage.co/query"
            params = {
                'function': 'GLOBAL_QUOTE',
                'symbol': symbol,
                'apikey': self.alphavantage_key,
                'entitlement': 'realtime'
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if 'Global Quote' in data:
                    quote = data['Global Quote']
                    
                    return {
                        'symbol': symbol,
                        'price': float(quote['05. price']),
                        'source': 'alphavantage_quote',
                        'method': 'global_quote',
                        'accuracy': 'medium',
                        'change': float(quote['09. change']),
                        'change_percent': quote['10. change percent'].rstrip('%'),
                        'volume': int(quote['06. volume']),
                        'timestamp': quote['07. latest trading day']
                    }
                else:
                    return {'error': f'No quote data for {symbol}'}
            else:
                return {'error': f'API error {response.status_code} for {symbol}'}
                
        except Exception as e:
            return {'error': f'Quote fetch error for {symbol}: {e}'}
    
    def calculate_option_metrics(self, symbol: str, spot_price: float, strike: float, 
                                option_type: str, expiry_hours: float = 1.0) -> Dict:
        """
        Calculate option metrics for given parameters
        
        Args:
            symbol: Underlying symbol
            spot_price: Current spot price
            strike: Option strike price
            option_type: "call" or "put"
            expiry_hours: Hours to expiry
        
        Returns:
            Dict with delta, gamma, theta estimates and moneyness
        """
        moneyness = spot_price / strike if option_type.lower() == "call" else strike / spot_price
        
        # Distance metrics
        distance = abs(spot_price - strike)
        distance_pct = distance / spot_price * 100
        
        # Simple Black-Scholes approximations for 0DTE
        if option_type.lower() == "call":
            itm = spot_price > strike
            delta_estimate = 0.8 if itm else (0.5 if abs(spot_price - strike) < 5 else 0.2)
        else:  # put
            itm = spot_price < strike
            delta_estimate = -0.8 if itm else (-0.5 if abs(spot_price - strike) < 5 else -0.2)
        
        # Gamma highest at ATM
        gamma_estimate = max(0.01, 0.1 * (1 - min(1.0, distance_pct / 2)))
        
        # Theta acceleration near expiry
        theta_estimate = -max(0.05, 0.5 / max(0.1, expiry_hours))
        
        return {
            'symbol': symbol,
            'spot_price': spot_price,
            'strike': strike,
            'option_type': option_type,
            'moneyness': round(moneyness, 4),
            'distance': round(distance, 2),
            'distance_pct': round(distance_pct, 2),
            'delta_estimate': round(delta_estimate, 3),
            'gamma_estimate': round(gamma_estimate, 3),
            'theta_estimate': round(theta_estimate, 3),
            'in_the_money': itm,
            'expiry_hours': expiry_hours
        }

def test_universal_calculator():
    """Test the universal spot calculator with multiple symbols"""
    calc = UniversalSpotCalculator()
    
    test_symbols = ['SPX', 'SPY', 'AAPL', 'TSLA', 'NVDA']
    
    print("UNIVERSAL SPOT PRICE CALCULATOR TEST")
    print("=" * 50)
    
    for symbol in test_symbols:
        print(f"\nTesting {symbol}:")
        result = calc.get_spot_price(symbol, method="auto")
        
        if 'error' not in result:
            print(f"  Price: ${result['price']:.2f}")
            print(f"  Source: {result['source']}")
            print(f"  Method: {result['method']}")
            print(f"  Accuracy: {result['accuracy']}")
            
            # Test option metrics calculation
            if symbol != 'SPX':  # Skip complex SPX option calculations for test
                spot = result['price']
                strike = round(spot * 1.01)  # 1% OTM call
                
                option_metrics = calc.calculate_option_metrics(symbol, spot, strike, "call", 1.0)
                print(f"  Call ${strike} Delta: {option_metrics['delta_estimate']}")
                print(f"  Distance: {option_metrics['distance_pct']:.1f}%")
        else:
            print(f"  Error: {result['error']}")

if __name__ == "__main__":
    test_universal_calculator()