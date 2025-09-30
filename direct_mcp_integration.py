#!/usr/bin/env python3
"""
Direct MCP Integration for Options Spot Calculation
Uses Claude's MCP functions directly for real-time options data
"""

from mcp_options_calculator import MCPOptionsCalculator
from typing import Dict, Optional

class DirectMCPIntegration:
    def __init__(self):
        self.mcp_calculator = MCPOptionsCalculator()
    
    def get_spot_from_mcp_options(self, symbol: str) -> Dict:
        """
        Get spot price using MCP options data
        This function would be called with the actual MCP response
        """
        print(f"Getting {symbol} spot price via MCP options...")
        
        # In actual usage, this would receive the MCP response directly
        # For now, we simulate what the MCP call would return
        
        if symbol.upper() == 'SPY':
            # This simulates the actual mcp__alphavantage__REALTIME_OPTIONS("SPY") response
            return self._simulate_spy_mcp_response()
        elif symbol.upper() in ['SPXW', 'SPX']:
            # This simulates the actual mcp__alphavantage__REALTIME_OPTIONS("SPXW") response
            return self._simulate_spxw_mcp_response()
        else:
            return {'error': f'Symbol {symbol} not supported in simulation'}
    
    def _simulate_spy_mcp_response(self) -> Dict:
        """Simulate SPY MCP response for testing"""
        # This data structure matches what we get from the actual MCP call
        mcp_response = {
            'preview': True,
            'data_type': 'csv',
            'sample_data': '''contractID,symbol,expiration,strike,type,last,mark,bid,bid_size,ask,ask_size,volume,open_interest,date,implied_volatility,delta,gamma,theta,vega,rho\r
SPY250912C00650000,SPY,2025-09-12,650.00,call,7.82,7.39,6.98,31,7.80,32,567,2134,2025-09-12,0.08234,0.98123,0.00034,-0.08234,0.00045,0.11678\r
SPY250912P00650000,SPY,2025-09-12,650.00,put,0.15,0.12,0.10,0,0.14,178,234,12456,2025-09-12,1.98765,-0.01877,0.00034,-0.06789,0.00278,-0.00012\r
SPY250912C00655000,SPY,2025-09-12,655.00,call,4.85,4.42,4.01,28,4.83,29,789,1567,2025-09-12,0.07654,0.85432,0.00567,-0.07654,0.00789,0.10234\r
SPY250912P00655000,SPY,2025-09-12,655.00,put,0.35,0.32,0.29,0,0.35,178,345,8901,2025-09-12,1.76543,-0.14568,0.00567,-0.07890,0.00567,-0.00023\r
SPY250912C00660000,SPY,2025-09-12,660.00,call,2.15,1.75,1.35,25,2.15,27,1234,987,2025-09-12,0.06789,0.65432,0.01234,-0.06789,0.01567,0.08765\r
SPY250912P00660000,SPY,2025-09-12,660.00,put,1.25,1.15,1.05,0,1.25,178,567,5678,2025-09-12,1.54321,-0.34568,0.01234,-0.08901,0.01234,-0.00045\r
SPY250912C00665000,SPY,2025-09-12,665.00,call,0.85,0.65,0.45,22,0.85,24,2345,654,2025-09-12,0.05432,0.43210,0.02345,-0.05432,0.02345,0.06543\r
SPY250912P00665000,SPY,2025-09-12,665.00,put,3.25,3.15,3.05,0,3.25,178,890,3456,2025-09-12,1.32109,-0.56790,0.02345,-0.09012,0.02345,-0.00067'''
        }
        
        result = self.mcp_calculator.extract_spot_from_mcp_options('SPY', mcp_response)
        
        if 'error' not in result:
            # Convert SPY to SPX equivalent
            spy_spot = result['spot_price']
            implied_spx = spy_spot * 10.0  # Basic 10x conversion
            
            return {
                'symbol': 'SPX',
                'price': implied_spx,
                'source': 'spy_options_mcp',
                'method': 'spy_to_spx_conversion',
                'original_spy_price': spy_spot,
                'spy_calculation_count': result['calculation_count'],
                'accuracy': 'high',
                'timestamp': result['timestamp']
            }
        
        return result
    
    def _simulate_spxw_mcp_response(self) -> Dict:
        """Simulate SPXW MCP response for testing"""
        # SPXW options would have much higher strikes (6500+ range)
        mcp_response = {
            'preview': True,
            'data_type': 'csv',
            'sample_data': '''contractID,symbol,expiration,strike,type,last,mark,bid,bid_size,ask,ask_size,volume,open_interest,date,implied_volatility,delta,gamma,theta,vega,rho\r
SPXW250912C06500000,SPXW,2025-09-12,6500.00,call,84.50,82.25,81.00,5,83.50,8,123,456,2025-09-12,0.08234,0.85432,0.00012,-0.25678,0.02345,0.65432\r
SPXW250912P06500000,SPXW,2025-09-12,6500.00,put,1.25,1.15,1.05,0,1.25,15,67,890,2025-09-12,1.54321,-0.14568,0.00012,-0.18901,0.02345,-0.02345\r
SPXW250912C06550000,SPXW,2025-09-12,6550.00,call,42.50,40.25,39.00,3,41.50,5,89,234,2025-09-12,0.07654,0.65432,0.00034,-0.23456,0.03456,0.54321\r
SPXW250912P06550000,SPXW,2025-09-12,6550.00,put,8.75,8.25,7.75,0,8.75,12,34,567,2025-09-12,1.32109,-0.34568,0.00034,-0.21234,0.03456,-0.03456\r
SPXW250912C06600000,SPXW,2025-09-12,6600.00,call,18.50,16.25,15.00,2,17.50,3,45,123,2025-09-12,0.06789,0.43210,0.00067,-0.21234,0.04567,0.43210\r
SPXW250912P06600000,SPXW,2025-09-12,6600.00,put,24.75,22.25,21.00,0,23.75,8,23,345,2025-09-12,1.10987,-0.56790,0.00067,-0.23456,0.04567,-0.04567'''
        }
        
        result = self.mcp_calculator.extract_spot_from_mcp_options('SPXW', mcp_response)
        
        if 'error' not in result:
            return {
                'symbol': 'SPX',
                'price': result['spot_price'],
                'source': 'spxw_options_mcp',
                'method': 'spxw_put_call_parity',
                'calculation_count': result['calculation_count'],
                'accuracy': 'highest',
                'timestamp': result['timestamp']
            }
        
        return result

def test_direct_mcp():
    """Test the direct MCP integration"""
    integration = DirectMCPIntegration()
    
    print("TESTING DIRECT MCP INTEGRATION")
    print("=" * 35)
    
    # Test SPY -> SPX conversion
    print("\n1. Testing SPY Options -> SPX Conversion:")
    spy_result = integration.get_spot_from_mcp_options('SPY')
    
    if 'error' not in spy_result:
        print(f"   SPX Price: ${spy_result['price']:.2f}")
        print(f"   Source: {spy_result['source']}")
        print(f"   Original SPY: ${spy_result['original_spy_price']:.2f}")
        print(f"   Calculations: {spy_result['spy_calculation_count']}")
        print(f"   Accuracy: {spy_result['accuracy']}")
    else:
        print(f"   Error: {spy_result['error']}")
    
    # Test SPXW direct
    print("\n2. Testing SPXW Options Direct:")
    spxw_result = integration.get_spot_from_mcp_options('SPXW')
    
    if 'error' not in spxw_result:
        print(f"   SPX Price: ${spxw_result['price']:.2f}")
        print(f"   Source: {spxw_result['source']}")
        print(f"   Method: {spxw_result['method']}")
        print(f"   Calculations: {spxw_result['calculation_count']}")
        print(f"   Accuracy: {spxw_result['accuracy']}")
    else:
        print(f"   Error: {spxw_result['error']}")
    
    print(f"\n3. Comparison:")
    if 'error' not in spy_result and 'error' not in spxw_result:
        diff = abs(spy_result['price'] - spxw_result['price'])
        diff_pct = (diff / spxw_result['price']) * 100
        print(f"   SPY->SPX: ${spy_result['price']:.2f}")
        print(f"   SPXW Direct: ${spxw_result['price']:.2f}")
        print(f"   Difference: ${diff:.2f} ({diff_pct:.3f}%)")
        
        if diff_pct < 0.1:
            print("   EXCELLENT: Difference < 0.1%")
        elif diff_pct < 0.5:
            print("   GOOD: Difference < 0.5%")
        else:
            print("   REVIEW: Difference > 0.5%")

if __name__ == "__main__":
    test_direct_mcp()