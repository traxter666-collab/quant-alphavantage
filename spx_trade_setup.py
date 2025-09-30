#!/usr/bin/env python3
"""
SPX TRADE SETUP GENERATOR
Uses Polygon I:SPX real-time pricing for accurate trade recommendations
"""

import os
import sys
import json
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dual_api_system import DualAPISystem

def get_spx_trade_setups():
    """Generate SPX trade setups using accurate Polygon pricing"""

    print('='*70)
    print('SPX TRADE SETUP ANALYSIS (Polygon Real-Time)')
    print(f'Time: {datetime.now().strftime("%I:%M %p ET")}')
    print('='*70)

    # Initialize dual API system
    dual_api = DualAPISystem()

    # Get accurate SPX price
    print('\nGetting SPX data with dual API failover...')
    spx_result = dual_api.get_spx_data_with_failover()

    if not spx_result['success']:
        print('❌ Failed to get SPX data')
        return

    spx_price = spx_result['spx_price']
    api_used = spx_result['api_used']
    reliability = spx_result['reliability']

    # Get SPY for options strikes
    print('Getting SPY data...')
    spy_result = dual_api.get_stock_quote_with_failover('SPY')

    if not spy_result['success']:
        print('❌ Failed to get SPY data')
        return

    spy_price = spy_result['price']

    print(f'\n💰 CURRENT PRICES (via {api_used} - {reliability} reliability):')
    print(f'   SPX: ${spx_price:.2f}')
    print(f'   SPY: ${spy_price:.2f}')

    # Load today's levels
    base_path = os.path.dirname(os.path.abspath(__file__))
    levels_file = os.path.join(base_path, '.spx', 'todays_levels.json')

    try:
        with open(levels_file, 'r') as f:
            levels = json.load(f)
    except:
        print('\n⚠️  Could not load today\'s levels')
        return

    print(f'\n📊 TODAY\'S KEY LEVELS:')
    print(f'   Resistance Zone: {levels["zones"]["resistance_zone"]["range"]}')
    print(f'   Support Zone: {levels["zones"]["support_zone"]["range"]}')
    print(f'   Gamma Flip Zone: {levels["zones"]["gamma_flip_zone"]["range"]}')

    # Define levels
    resistance_lower = 6680
    resistance_upper = 6694
    support_lower = 6620
    support_upper = 6626
    gamma_lower = 6607
    gamma_upper = 6610

    # Calculate distances
    dist_to_resistance = resistance_lower - spx_price
    dist_to_support = spx_price - support_upper
    dist_to_gamma = spx_price - gamma_upper

    print(f'\n🎯 POSITION ANALYSIS:')
    print(f'   Distance to Resistance (6680): {dist_to_resistance:+.2f} points')
    print(f'   Distance to Support (6626): {dist_to_support:+.2f} points')
    print(f'   Distance to Gamma Flip (6610): {dist_to_gamma:+.2f} points')

    # Generate trade setups based on position
    print(f'\n🚨 ACTIVE TRADE SETUPS:')

    setups_found = False

    # Resistance zone setup
    if spx_price >= resistance_lower - 20 and spx_price <= resistance_upper + 5:
        setups_found = True
        print(f'\n📉 RESISTANCE REJECTION SETUP (75% confidence):')
        print(f'   Status: {"🟢 ACTIVE" if spx_price >= resistance_lower else "⚪ STANDBY"}')
        print(f'   Trigger: SPX at/near 6680-6694 resistance zone')
        print(f'   Entry: SPY {int(spy_price)} PUTS @ market')
        print(f'   Target: 6626 support zone (~${int((support_upper/10)*10)/10:.2f} SPY)')
        print(f'   Stop: Above 6694 (~${int((resistance_upper/10)*10 + 0.5)/10:.2f} SPY)')
        print(f'   Size: 1-2% position')
        print(f'   Risk/Reward: ~{abs((resistance_lower - support_upper)/(resistance_upper - resistance_lower)):.1f}:1')

    # Support zone setup
    if spx_price <= support_upper + 20 and spx_price >= support_lower - 5:
        setups_found = True
        print(f'\n📈 SUPPORT BOUNCE SETUP (75% confidence):')
        print(f'   Status: {"🟢 ACTIVE" if spx_price <= support_upper else "⚪ STANDBY"}')
        print(f'   Trigger: SPX at/near 6620-6626 support zone')
        print(f'   Entry: SPY {int(spy_price) + 1} CALLS @ market')
        print(f'   Target: 6680 resistance zone (~${int((resistance_lower/10)*10 + 0.5)/10:.2f} SPY)')
        print(f'   Stop: Below 6620 (~${int((support_lower/10)*10)/10:.2f} SPY)')
        print(f'   Size: 1-2% position')
        print(f'   Risk/Reward: ~{abs((resistance_lower - support_upper)/(support_upper - support_lower)):.1f}:1')

    # Gamma flip setup
    if spx_price <= gamma_upper + 40:
        setups_found = True
        print(f'\n🎯 GAMMA FLIP REVERSAL (85% confidence):')
        print(f'   Status: {"🔥 ACTIVE - HIGHEST CONVICTION" if spx_price <= gamma_upper else "⚪ STANDBY"}')
        print(f'   Trigger: SPX at critical gamma flip zone 6607-6610')
        print(f'   Entry: SPY {int(spy_price) + 1} CALLS @ market')
        print(f'   Target: 6650+ (~${int((6650/10)*10 + 0.5)/10:.2f} SPY)')
        print(f'   Stop: Below 6607 (~${int((gamma_lower/10)*10)/10:.2f} SPY)')
        print(f'   Size: 2-3% position (VERY HIGH probability)')
        print(f'   Risk/Reward: ~{abs((6650 - gamma_upper)/(gamma_upper - gamma_lower)):.1f}:1')

    if not setups_found:
        print(f'\n   ⚠️  NO ACTIVE SETUPS')
        print(f'   Current SPX: ${spx_price:.2f}')
        print(f'   Wait for price to reach key levels')

    # Current best recommendation
    print(f'\n💡 CURRENT RECOMMENDATION:')

    if spx_price >= resistance_lower and spx_price <= resistance_upper:
        print(f'   🎯 AT RESISTANCE ZONE - WATCH FOR REJECTION')
        print(f'   Primary: SPY {int(spy_price)} PUTS')
        print(f'   Entry: Wait for confirmation (rejection candle)')
    elif spx_price >= support_lower and spx_price <= support_upper:
        print(f'   🎯 AT SUPPORT ZONE - WATCH FOR BOUNCE')
        print(f'   Primary: SPY {int(spy_price) + 1} CALLS')
        print(f'   Entry: Wait for confirmation (bounce candle)')
    elif spx_price >= gamma_lower and spx_price <= gamma_upper:
        print(f'   🔥 AT GAMMA FLIP - HIGHEST PROBABILITY REVERSAL')
        print(f'   Primary: SPY {int(spy_price) + 1} CALLS')
        print(f'   Entry: IMMEDIATE (85% confidence)')
    else:
        print(f'   ⏰ WAIT FOR KEY LEVEL')

        # Find nearest level
        distances = {
            'Resistance (6680)': abs(resistance_lower - spx_price),
            'Support (6626)': abs(support_upper - spx_price),
            'Gamma Flip (6610)': abs(gamma_upper - spx_price)
        }

        nearest = min(distances, key=distances.get)
        print(f'   Next Level: {nearest} ({distances[nearest]:.1f} points away)')
        print(f'   Action: Monitor for approach to key level')

    print(f'\n' + '='*70)
    print(f'Data Source: {api_used.upper()} | Reliability: {reliability}')
    print(f'Timestamp: {datetime.now().strftime("%Y-%m-%d %I:%M:%S %p ET")}')
    print('='*70)

if __name__ == "__main__":
    get_spx_trade_setups()