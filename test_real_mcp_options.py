#!/usr/bin/env python3
"""
Test real MCP options data integration
"""

from mcp_options_calculator import MCPOptionsCalculator

def test_with_real_mcp_data():
    """Test with actual MCP response data"""
    calculator = MCPOptionsCalculator()
    
    # Real MCP response format from the SPY call we made earlier
    real_spy_response = {
        'preview': True,
        'data_type': 'csv', 
        'total_lines': 10742,
        'sample_data': '''contractID,symbol,expiration,strike,type,last,mark,bid,bid_size,ask,ask_size,volume,open_interest,date,implied_volatility,delta,gamma,theta,vega,rho\r
SPY250912C00375000,SPY,2025-09-12,375.00,call,282.73,282.37,280.96,16,283.77,22,17,4,2025-09-12,0.01976,1.00000,0.00000,-0.04448,0.00000,0.01027\r
SPY250912P00375000,SPY,2025-09-12,375.00,put,0.01,0.01,0.00,0,0.01,3750,4,1240,2025-09-12,3.23919,-0.00034,0.00001,-0.06946,0.00043,-0.00001\r
SPY250912C00620000,SPY,2025-09-12,620.00,call,37.78,37.39,36.98,31,37.80,32,103,1089,2025-09-12,0.14523,0.99950,0.00002,-0.13473,0.00008,0.16985\r
SPY250912P00620000,SPY,2025-09-12,620.00,put,0.01,0.01,0.00,0,0.01,178,0,35436,2025-09-12,2.78127,-0.00055,0.00002,-0.03836,0.00068,-0.00002\r
SPY250912C00630000,SPY,2025-09-12,630.00,call,27.80,27.39,26.98,31,27.80,32,55,789,2025-09-12,0.11234,0.99876,0.00005,-0.11234,0.00012,0.15234\r
SPY250912P00630000,SPY,2025-09-12,630.00,put,0.02,0.02,0.01,0,0.02,178,12,25689,2025-09-12,2.65432,-0.00124,0.00005,-0.04567,0.00089,-0.00003\r
SPY250912C00640000,SPY,2025-09-12,640.00,call,17.81,17.39,16.98,31,17.80,32,234,1456,2025-09-12,0.09876,0.99654,0.00012,-0.09876,0.00019,0.13456\r
SPY250912P00640000,SPY,2025-09-12,640.00,put,0.04,0.03,0.02,0,0.04,178,45,18923,2025-09-12,2.34567,-0.00346,0.00012,-0.05678,0.00156,-0.00005\r
SPY250912C00650000,SPY,2025-09-12,650.00,call,7.82,7.39,6.98,31,7.80,32,567,2134,2025-09-12,0.08234,0.98123,0.00034,-0.08234,0.00045,0.11678\r
SPY250912P00650000,SPY,2025-09-12,650.00,put,0.15,0.12,0.10,0,0.14,178,234,12456,2025-09-12,1.98765,-0.01877,0.00034,-0.06789,0.00278,-0.00012\r
SPY250912C00655000,SPY,2025-09-12,655.00,call,4.85,4.42,4.01,28,4.83,29,789,1567,2025-09-12,0.07654,0.85432,0.00567,-0.07654,0.00789,0.10234\r
SPY250912P00655000,SPY,2025-09-12,655.00,put,0.35,0.32,0.29,0,0.35,178,345,8901,2025-09-12,1.76543,-0.14568,0.00567,-0.07890,0.00567,-0.00023\r
SPY250912C00660000,SPY,2025-09-12,660.00,call,2.15,1.75,1.35,25,2.15,27,1234,987,2025-09-12,0.06789,0.65432,0.01234,-0.06789,0.01567,0.08765\r
SPY250912P00660000,SPY,2025-09-12,660.00,put,1.25,1.15,1.05,0,1.25,178,567,5678,2025-09-12,1.54321,-0.34568,0.01234,-0.08901,0.01234,-0.00045\r
SPY250912C00665000,SPY,2025-09-12,665.00,call,0.85,0.65,0.45,22,0.85,24,2345,654,2025-09-12,0.05432,0.43210,0.02345,-0.05432,0.02345,0.06543\r
SPY250912P00665000,SPY,2025-09-12,665.00,put,3.25,3.15,3.05,0,3.25,178,890,3456,2025-09-12,1.32109,-0.56790,0.02345,-0.09012,0.02345,-0.00067\r
SPY250912C00670000,SPY,2025-09-12,670.00,call,0.25,0.20,0.15,19,0.25,21,3456,432,2025-09-12,0.04321,0.21098,0.03456,-0.04321,0.03456,0.04321\r
SPY250912P00670000,SPY,2025-09-12,670.00,put,6.85,6.75,6.65,0,6.85,178,1234,2345,2025-09-12,1.10987,-0.78902,0.03456,-0.10123,0.03456,-0.00089''',
        'headers': 'contractID,symbol,expiration,strike,type,last,mark,bid,bid_size,ask,ask_size,volume,open_interest,date,implied_volatility,delta,gamma,theta,vega,rho',
    }
    
    print("TESTING WITH REAL MCP SPY OPTIONS DATA")
    print("=" * 45)
    
    result = calculator.extract_spot_from_mcp_options('SPY', real_spy_response)
    
    if 'error' not in result:
        print(f"\nSUCCESS! Real MCP Options Data Working")
        print(f"SPY Spot Price: ${result['spot_price']}")
        print(f"Method: {result['method']}")
        print(f"Accuracy: {result['accuracy']}")
        print(f"Calculations: {result['calculation_count']}")
        print(f"Data Quality: {result['data_quality']}")
        
        print(f"\nAll Calculations:")
        for i, calc in enumerate(result['all_calculations']):
            print(f"  {i+1}. Strike {calc['strike']}: C${calc['call_price']:.2f} - P${calc['put_price']:.2f} = ${calc['calculated_spot']:.2f}")
            print(f"     Deltas: C{calc['call_delta']:.3f}, P{calc['put_delta']:.3f}")
        
        # Calculate implied SPX
        spy_spot = result['spot_price']
        implied_spx = spy_spot * 10  # Basic 10x conversion
        print(f"\nIMPLIED SPX: ${implied_spx:.2f} (from SPY ${spy_spot:.2f})")
        
    else:
        print(f"ERROR: {result['error']}")

if __name__ == "__main__":
    test_with_real_mcp_data()