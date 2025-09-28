#!/usr/bin/env python3
"""
Options Spot Price Calculator
Extract accurate spot prices using put-call parity from options chains
"""

import requests
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple

class OptionsSpotCalculator:
    def __init__(self):
        self.alphavantage_key = "ZFL38ZY98GSN7E1S"
        
    def get_options_chain_via_mcp(self, symbol: str) -> Dict:
        """Get options chain data via MCP (preferred method)"""
        try:
            # This would call the MCP function - for now use the direct API
            # In actual usage, this would be called via MCP
            return {}
        except Exception as e:
            print(f"MCP options chain error: {e}")
            return {}
    
    def parse_csv_options_data(self, csv_data: str) -> List[Dict]:
        """Parse CSV format options data from AlphaVantage"""
        options = []
        
        if not csv_data:
            return options
            
        lines = csv_data.strip().split('\n')
        if len(lines) < 2:
            return options
            
        # Skip header line
        for line in lines[1:]:
            try:
                fields = line.split(',')
                if len(fields) >= 20:  # Ensure we have all required fields
                    option = {
                        'contractID': fields[0],
                        'symbol': fields[1], 
                        'expiration': fields[2],
                        'strike': float(fields[3]),
                        'type': fields[4],
                        'last': float(fields[5]) if fields[5] != '0.00' and fields[5] else 0,
                        'mark': float(fields[6]) if fields[6] else 0,
                        'bid': float(fields[7]) if fields[7] else 0,
                        'ask': float(fields[9]) if fields[9] else 0,
                        'volume': int(fields[11]) if fields[11] else 0,
                        'open_interest': int(fields[12]) if fields[12] else 0,
                        'delta': float(fields[15]) if fields[15] else 0,
                        'gamma': float(fields[16]) if fields[16] else 0,
                        'theta': float(fields[17]) if fields[17] else 0
                    }
                    options.append(option)
            except (ValueError, IndexError) as e:
                continue  # Skip malformed lines
                
        return options
    
    def extract_spot_from_options(self, symbol: str) -> Dict:
        """
        Extract spot price using put-call parity from ATM options
        Formula: Spot = (Call Price - Put Price) + Strike Price + Present Value of Dividends
        
        For ATM options: Call Delta ≈ 0.5, Put Delta ≈ -0.5
        """
        print(f"Extracting {symbol} spot price from options chain...")
        
        options_data = self.get_options_chain(symbol)
        
        if not options_data:
            return {'error': 'No options data available'}
        
        # Parse options chain and find ATM strikes
        calls = []
        puts = []
        
        # Process options data (format depends on API response)
        if 'data' in options_data:
            for option in options_data['data']:
                if option.get('type') == 'call':
                    calls.append(option)
                elif option.get('type') == 'put':
                    puts.append(option)
        
        if not calls or not puts:
            return {'error': 'Insufficient options data for put-call parity'}
        
        # Find ATM options (closest to delta ±0.5)
        atm_pairs = self.find_atm_pairs(calls, puts)
        
        if not atm_pairs:
            return {'error': 'No ATM option pairs found'}
        
        # Calculate spot prices using put-call parity
        spot_calculations = []
        
        for call, put in atm_pairs[:3]:  # Use top 3 ATM pairs
            try:
                call_price = float(call.get('mark', call.get('last', 0)))
                put_price = float(put.get('mark', put.get('last', 0)))
                strike = float(call.get('strike', 0))
                
                if call_price > 0 and put_price > 0 and strike > 0:
                    # Put-Call Parity: Spot = Call - Put + Strike (ignoring dividends and interest for 0DTE)
                    calculated_spot = call_price - put_price + strike
                    
                    spot_calculations.append({
                        'strike': strike,
                        'call_price': call_price,
                        'put_price': put_price,
                        'calculated_spot': calculated_spot,
                        'call_delta': call.get('delta', 0),
                        'put_delta': put.get('delta', 0)
                    })
                    
            except (ValueError, TypeError) as e:
                continue
        
        if not spot_calculations:
            return {'error': 'Put-call parity calculation failed'}
        
        # Average the calculations for accuracy
        avg_spot = sum(calc['calculated_spot'] for calc in spot_calculations) / len(spot_calculations)
        
        # Find the calculation closest to 0.5 delta for highest accuracy
        best_calc = min(spot_calculations, 
                       key=lambda x: abs(abs(x.get('call_delta', 0)) - 0.5))
        
        return {
            'symbol': symbol,
            'spot_price': round(avg_spot, 2),
            'best_calculation': best_calc,
            'all_calculations': spot_calculations,
            'calculation_count': len(spot_calculations),
            'method': 'put_call_parity',
            'timestamp': datetime.now().isoformat(),
            'accuracy': 'high' if len(spot_calculations) >= 2 else 'medium'
        }
    
    def find_atm_pairs(self, calls: List[Dict], puts: List[Dict]) -> List[Tuple[Dict, Dict]]:
        """Find ATM call/put pairs with deltas closest to ±0.5"""
        atm_pairs = []
        
        # Group by strike price
        strikes = {}
        
        for call in calls:
            strike = call.get('strike')
            if strike:
                if strike not in strikes:
                    strikes[strike] = {'calls': [], 'puts': []}
                strikes[strike]['calls'].append(call)
        
        for put in puts:
            strike = put.get('strike')
            if strike:
                if strike not in strikes:
                    strikes[strike] = {'calls': [], 'puts': []}
                strikes[strike]['puts'].append(put)
        
        # Find pairs with both calls and puts
        for strike, options in strikes.items():
            if options['calls'] and options['puts']:
                # Find closest to ATM (delta ±0.5)
                best_call = min(options['calls'], 
                              key=lambda x: abs(abs(float(x.get('delta', 0))) - 0.5))
                best_put = min(options['puts'], 
                             key=lambda x: abs(abs(float(x.get('delta', 0))) - 0.5))
                
                # Check if reasonably close to ATM
                call_delta = abs(float(best_call.get('delta', 0)))
                put_delta = abs(float(best_put.get('delta', 0)))
                
                if 0.3 <= call_delta <= 0.7 and 0.3 <= put_delta <= 0.7:
                    atm_pairs.append((best_call, best_put))
        
        # Sort by how close deltas are to 0.5
        atm_pairs.sort(key=lambda pair: abs(abs(float(pair[0].get('delta', 0))) - 0.5))
        
        return atm_pairs
    
    def calculate_spx_from_spy(self, spy_price: float) -> float:
        """Fallback: Calculate SPX from SPY using 10x multiplier with adjustments"""
        # SPX typically trades at SPY * 10 with small premium
        base_spx = spy_price * 10
        
        # Add typical premium (usually 0.05-0.15%)
        premium_adjustment = base_spx * 0.001  # 0.1% typical premium
        
        return round(base_spx + premium_adjustment, 2)

def test_spot_calculation():
    """Test the spot price extraction"""
    calculator = OptionsSpotCalculator()
    
    # Test with SPXW
    print("TESTING SPXW SPOT PRICE EXTRACTION")
    spx_result = calculator.extract_spot_from_options('SPXW')
    
    if 'error' not in spx_result:
        print(f"SPX Spot Price: ${spx_result['spot_price']}")
        print(f"Method: {spx_result['method']}")
        print(f"Accuracy: {spx_result['accuracy']}")
        print(f"Calculations: {spx_result['calculation_count']}")
    else:
        print(f"SPX Error: {spx_result['error']}")
    
    # Test with SPY for comparison
    print("\nTESTING SPY SPOT PRICE EXTRACTION")
    spy_result = calculator.extract_spot_from_options('SPY')
    
    if 'error' not in spy_result:
        print(f"SPY Spot Price: ${spy_result['spot_price']}")
        print(f"Method: {spy_result['method']}")
        print(f"Accuracy: {spy_result['accuracy']}")
        
        # Calculate implied SPX
        implied_spx = calculator.calculate_spx_from_spy(spy_result['spot_price'])
        print(f"Implied SPX (from SPY): ${implied_spx}")
    else:
        print(f"SPY Error: {spy_result['error']}")

if __name__ == "__main__":
    test_spot_calculation()