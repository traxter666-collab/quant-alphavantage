#!/usr/bin/env python3
"""
MCP Options Calculator
Extract spot prices using AlphaVantage MCP options data
"""

from typing import Dict, List, Optional
from datetime import datetime
import json

class MCPOptionsCalculator:
    def __init__(self):
        pass
    
    def parse_mcp_options_response(self, mcp_response: Dict) -> List[Dict]:
        """Parse MCP options response format"""
        options = []
        
        if 'sample_data' not in mcp_response:
            return options
            
        csv_data = mcp_response['sample_data']
        # Handle different line endings
        lines = csv_data.strip().replace('\r\n', '\n').replace('\r', '\n').split('\n')
        
        if len(lines) < 2:
            return options
            
        # Parse header to get field positions
        header = lines[0].split(',')
        
        # Find key field indices
        field_indices = {}
        for i, field in enumerate(header):
            field_indices[field.strip()] = i
            
        # Parse data lines
        for line in lines[1:]:
            try:
                fields = line.split(',')
                if len(fields) >= len(header):
                    option = {
                        'contractID': fields[field_indices.get('contractID', 0)],
                        'symbol': fields[field_indices.get('symbol', 1)],
                        'expiration': fields[field_indices.get('expiration', 2)],
                        'strike': float(fields[field_indices.get('strike', 3)]),
                        'type': fields[field_indices.get('type', 4)],
                        'last': float(fields[field_indices.get('last', 5)]) if fields[field_indices.get('last', 5)] not in ['0.00', ''] else 0,
                        'mark': float(fields[field_indices.get('mark', 6)]) if fields[field_indices.get('mark', 6)] else 0,
                        'bid': float(fields[field_indices.get('bid', 7)]) if fields[field_indices.get('bid', 7)] else 0,
                        'ask': float(fields[field_indices.get('ask', 9)]) if fields[field_indices.get('ask', 9)] else 0,
                        'volume': int(fields[field_indices.get('volume', 11)]) if fields[field_indices.get('volume', 11)] else 0,
                        'open_interest': int(fields[field_indices.get('open_interest', 12)]) if fields[field_indices.get('open_interest', 12)] else 0,
                        'delta': float(fields[field_indices.get('delta', 15)]) if fields[field_indices.get('delta', 15)] else 0,
                        'gamma': float(fields[field_indices.get('gamma', 16)]) if fields[field_indices.get('gamma', 16)] else 0,
                        'theta': float(fields[field_indices.get('theta', 17)]) if fields[field_indices.get('theta', 17)] else 0
                    }
                    options.append(option)
            except (ValueError, IndexError, KeyError) as e:
                continue  # Skip malformed lines
                
        return options
    
    def extract_spot_from_mcp_options(self, symbol: str, mcp_response: Dict) -> Dict:
        """Extract spot price from MCP options response using put-call parity"""
        
        print(f"Extracting {symbol} spot from MCP options data...")
        
        # Parse the MCP response
        options = self.parse_mcp_options_response(mcp_response)
        
        if not options:
            return {'error': 'No options data parsed from MCP response'}
        
        print(f"Parsed {len(options)} options contracts")
        
        # Separate calls and puts
        calls = [opt for opt in options if opt['type'] == 'call']
        puts = [opt for opt in options if opt['type'] == 'put']
        
        if not calls or not puts:
            return {'error': f'Insufficient options: {len(calls)} calls, {len(puts)} puts'}
        
        print(f"Found {len(calls)} calls and {len(puts)} puts")
        
        # Find ATM pairs (closest to delta ±0.5)
        atm_pairs = self.find_atm_pairs(calls, puts)
        
        if not atm_pairs:
            return {'error': 'No ATM option pairs found for put-call parity'}
        
        print(f"Found {len(atm_pairs)} ATM pairs")
        
        # Calculate spot prices using put-call parity
        spot_calculations = []
        
        for call, put in atm_pairs[:5]:  # Use top 5 ATM pairs
            try:
                # Use mark price if available, otherwise bid/ask midpoint
                call_price = call['mark'] if call['mark'] > 0 else (call['bid'] + call['ask']) / 2 if call['ask'] > 0 else call['last']
                put_price = put['mark'] if put['mark'] > 0 else (put['bid'] + put['ask']) / 2 if put['ask'] > 0 else put['last']
                strike = call['strike']
                
                if call_price > 0 and put_price >= 0 and strike > 0:
                    # Put-Call Parity: Spot = Call - Put + Strike
                    calculated_spot = call_price - put_price + strike
                    
                    spot_calculations.append({
                        'strike': strike,
                        'call_price': call_price,
                        'put_price': put_price,
                        'calculated_spot': calculated_spot,
                        'call_delta': call['delta'],
                        'put_delta': put['delta'],
                        'delta_quality': abs(abs(call['delta']) - 0.5) + abs(abs(put['delta']) - 0.5)
                    })
                    
                    print(f"  Strike {strike}: C${call_price:.2f} - P${put_price:.2f} + {strike} = ${calculated_spot:.2f}")
                    
            except (ValueError, TypeError) as e:
                continue
        
        if not spot_calculations:
            return {'error': 'Put-call parity calculation failed - no valid price data'}
        
        # Sort by delta quality (closest to ATM) and average the best ones
        spot_calculations.sort(key=lambda x: x['delta_quality'])
        best_calculations = spot_calculations[:3]  # Use best 3 calculations
        
        avg_spot = sum(calc['calculated_spot'] for calc in best_calculations) / len(best_calculations)
        best_calc = best_calculations[0]  # Highest quality calculation
        
        return {
            'symbol': symbol,
            'spot_price': round(avg_spot, 2),
            'best_calculation': best_calc,
            'all_calculations': spot_calculations,
            'calculation_count': len(spot_calculations),
            'method': 'mcp_put_call_parity',
            'timestamp': datetime.now().isoformat(),
            'accuracy': 'high' if len(best_calculations) >= 3 else 'medium',
            'data_quality': f"{len(options)} total options, {len(atm_pairs)} ATM pairs"
        }
    
    def find_atm_pairs(self, calls: List[Dict], puts: List[Dict]) -> List[tuple]:
        """Find ATM call/put pairs with deltas closest to ±0.5"""
        atm_pairs = []
        
        # Group by strike price
        strikes = {}
        
        for call in calls:
            strike = call['strike']
            if strike not in strikes:
                strikes[strike] = {'calls': [], 'puts': []}
            strikes[strike]['calls'].append(call)
        
        for put in puts:
            strike = put['strike']
            if strike not in strikes:
                strikes[strike] = {'calls': [], 'puts': []}
            strikes[strike]['puts'].append(put)
        
        # Find pairs with both calls and puts
        for strike, options in strikes.items():
            if options['calls'] and options['puts']:
                # Find closest to ATM (delta ±0.5)
                best_call = min(options['calls'], 
                              key=lambda x: abs(abs(x['delta']) - 0.5))
                best_put = min(options['puts'], 
                             key=lambda x: abs(abs(x['delta']) - 0.5))
                
                # Check if reasonably close to ATM and have pricing data
                call_delta = abs(best_call['delta'])
                put_delta = abs(best_put['delta'])
                
                # More lenient delta requirements
                if (0.2 <= call_delta <= 0.8 and 0.2 <= put_delta <= 0.8 and
                    (best_call['mark'] > 0 or best_call['bid'] > 0 or best_call['last'] > 0) and
                    (best_put['mark'] >= 0 or best_put['bid'] >= 0 or best_put['last'] >= 0)):
                    
                    atm_pairs.append((best_call, best_put))
        
        # Sort by how close deltas are to 0.5 (best ATM first)
        atm_pairs.sort(key=lambda pair: abs(abs(pair[0]['delta']) - 0.5) + abs(abs(pair[1]['delta']) - 0.5))
        
        return atm_pairs

def test_mcp_calculator_with_spy_data():
    """Test with the SPY data we know is available"""
    calculator = MCPOptionsCalculator()
    
    # This simulates what we'd get from the MCP call
    # In real usage, we'd get this from mcp__alphavantage__REALTIME_OPTIONS
    spy_sample_response = {
        'sample_data': '''contractID,symbol,expiration,strike,type,last,mark,bid,bid_size,ask,ask_size,volume,open_interest,date,implied_volatility,delta,gamma,theta,vega,rho
SPY250912C00650000,SPY,2025-09-12,650.00,call,7.48,7.41,7.41,100,7.41,100,50,500,2025-09-12,0.1234,0.52000,0.01234,-0.05678,0.12345,0.01234
SPY250912P00650000,SPY,2025-09-12,650.00,put,0.28,0.25,0.24,100,0.26,100,25,750,2025-09-12,0.1234,-0.48000,0.01234,-0.05678,0.12345,-0.01234
SPY250912C00655000,SPY,2025-09-12,655.00,call,4.25,4.18,4.16,100,4.20,100,30,300,2025-09-12,0.1234,0.35000,0.01234,-0.05678,0.12345,0.01234
SPY250912P00655000,SPY,2025-09-12,655.00,put,1.85,1.82,1.80,100,1.84,100,15,400,2025-09-12,0.1234,-0.35000,0.01234,-0.05678,0.12345,-0.01234
SPY250912C00660000,SPY,2025-09-12,660.00,call,2.15,2.10,2.08,100,2.12,100,20,200,2025-09-12,0.1234,0.22000,0.01234,-0.05678,0.12345,0.01234
SPY250912P00660000,SPY,2025-09-12,660.00,put,4.85,4.80,4.78,100,4.82,100,10,600,2025-09-12,0.1234,-0.78000,0.01234,-0.05678,0.12345,-0.01234'''
    }
    
    print("TESTING MCP OPTIONS CALCULATOR")
    print("=" * 40)
    
    result = calculator.extract_spot_from_mcp_options('SPY', spy_sample_response)
    
    if 'error' not in result:
        print(f"\nSUCCESS!")
        print(f"SPY Spot Price: ${result['spot_price']}")
        print(f"Method: {result['method']}")
        print(f"Accuracy: {result['accuracy']}")
        print(f"Calculations: {result['calculation_count']}")
        print(f"Data Quality: {result['data_quality']}")
        print(f"\nBest Calculation:")
        best = result['best_calculation']
        print(f"  Strike: {best['strike']}")
        print(f"  Call: ${best['call_price']:.2f}, Put: ${best['put_price']:.2f}")
        print(f"  Calculated Spot: ${best['calculated_spot']:.2f}")
        print(f"  Call Delta: {best['call_delta']:.3f}, Put Delta: {best['put_delta']:.3f}")
    else:
        print(f"ERROR: {result['error']}")

if __name__ == "__main__":
    test_mcp_calculator_with_spy_data()