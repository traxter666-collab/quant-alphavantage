#!/usr/bin/env python3
"""
Test the enhanced SPX data system with options priority
"""

from enhanced_spx_data import EnhancedSPXData

def test_enhanced_spx():
    print("Testing Enhanced SPX Data with Options Priority")
    print("=" * 50)
    
    spx = EnhancedSPXData()
    result = spx.get_best_spx_price()
    
    print("\nSPX PRICE RESULT:")
    print(f"Price: ${result.get('price', 'N/A')}")
    print(f"Source: {result.get('source', 'N/A')}")
    
    if 'error' in result:
        print(f"Error: {result['error']}")
    else:
        print(f"Change: {result.get('change', 'N/A')}")
        print(f"Timestamp: {result.get('timestamp', 'N/A')}")
        
        if 'consensus' in result:
            consensus = result['consensus']
            print(f"\nCONSENSUS DATA:")
            print(f"Sources: {consensus.get('sources_count', 'N/A')}")
            print(f"Average: ${consensus.get('average_price', 'N/A')}")
            print(f"Std Dev: {consensus.get('price_std', 'N/A')}")

if __name__ == "__main__":
    test_enhanced_spx()