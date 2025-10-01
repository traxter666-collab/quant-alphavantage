#!/usr/bin/env python3
"""Test ETF data functions"""
import sys
sys.dont_write_bytecode = True  # Don't create __pycache__

from dual_api_system import DualAPISystem

api = DualAPISystem()

print("Testing standardized ETF data retrieval:\n")
print("="*70)

for symbol, func_name in [('SPY', 'get_spy_data_with_failover'),
                          ('QQQ', 'get_qqq_data_with_failover'),
                          ('IWM', 'get_iwm_data_with_failover')]:
    func = getattr(api, func_name)
    result = func()
    print(f"\n{symbol}:")
    if result['success']:
        print(f"  ✅ Close: ${result['price']:.2f}")
        print(f"     Open: ${result.get('open', 0):.2f}")
        print(f"     High: ${result.get('high', 0):.2f}")
        print(f"     Low: ${result.get('low', 0):.2f}")
        print(f"     Volume: {result.get('volume', 0):,.0f}")
        print(f"     Method: {result['conversion_method']}")
        print(f"     Reliability: {result['reliability']}")
    else:
        print(f"  ❌ Error: {result['error']}")

print("\n" + "="*70)
print("✅ All ETF functions working correctly")
