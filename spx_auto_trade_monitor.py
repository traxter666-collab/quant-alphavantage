#!/usr/bin/env python3
"""
SPX AUTOMATED TRADE SETUP MONITOR
Continuously monitors SPX and alerts when trade setups appear
Uses Polygon I:SPX real-time pricing
"""

import os
import sys
import time
import json
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dual_api_system import DualAPISystem

def check_for_trade_setups(dual_api, silent=False):
    """Check for active trade setups"""

    # Get accurate SPX price
    spx_result = dual_api.get_spx_data_with_failover()

    if not spx_result['success']:
        if not silent:
            print('❌ Failed to get SPX data')
        return None

    spx_price = spx_result['spx_price']

    # Get SPY for options strikes
    spy_result = dual_api.get_stock_quote_with_failover('SPY')

    if not spy_result['success']:
        if not silent:
            print('❌ Failed to get SPY data')
        return None

    spy_price = spy_result['price']

    # Define levels
    resistance_lower = 6680
    resistance_upper = 6694
    support_lower = 6620
    support_upper = 6626
    gamma_lower = 6607
    gamma_upper = 6610

    # Check for active setups
    active_setups = []

    # Resistance zone (within 10 points)
    if spx_price >= resistance_lower - 10 and spx_price <= resistance_upper + 5:
        active_setups.append({
            'type': 'RESISTANCE_REJECTION',
            'confidence': 75,
            'active': spx_price >= resistance_lower,
            'direction': 'PUT',
            'strike': int(spy_price),
            'target': 6626,
            'stop': 6694,
            'size': '1-2%',
            'spx_price': spx_price,
            'spy_price': spy_price
        })

    # Support zone (within 10 points)
    if spx_price <= support_upper + 10 and spx_price >= support_lower - 5:
        active_setups.append({
            'type': 'SUPPORT_BOUNCE',
            'confidence': 75,
            'active': spx_price <= support_upper,
            'direction': 'CALL',
            'strike': int(spy_price) + 1,
            'target': 6680,
            'stop': 6620,
            'size': '1-2%',
            'spx_price': spx_price,
            'spy_price': spy_price
        })

    # Gamma flip (within 30 points)
    if spx_price <= gamma_upper + 30:
        active_setups.append({
            'type': 'GAMMA_FLIP_REVERSAL',
            'confidence': 85,
            'active': spx_price <= gamma_upper,
            'direction': 'CALL',
            'strike': int(spy_price) + 1,
            'target': 6650,
            'stop': 6607,
            'size': '2-3%',
            'spx_price': spx_price,
            'spy_price': spy_price
        })

    return {
        'timestamp': datetime.now(),
        'spx_price': spx_price,
        'spy_price': spy_price,
        'active_setups': active_setups
    }

def format_setup_alert(setup):
    """Format trade setup for display"""

    status = "🔥 ACTIVE" if setup['active'] else "⚪ STANDBY"

    output = f"""
{'='*70}
🚨 TRADE SETUP DETECTED: {setup['type']}
{'='*70}

Status: {status}
Confidence: {setup['confidence']}%
Direction: {setup['direction']}

💰 CURRENT PRICES:
   SPX: ${setup['spx_price']:.2f}
   SPY: ${setup['spy_price']:.2f}

💡 TRADE DETAILS:
   Entry: SPY {setup['strike']} {setup['direction']}S @ market
   Target: {setup['target']} (~${(setup['target']/10):.2f} SPY)
   Stop: {setup['stop']} (~${(setup['stop']/10):.2f} SPY)
   Size: {setup['size']} position

⏰ Time: {datetime.now().strftime('%I:%M:%S %p ET')}
{'='*70}
"""

    return output

def main():
    """Main monitoring loop"""

    print('='*70)
    print('SPX AUTOMATED TRADE SETUP MONITOR')
    print('Polygon I:SPX Real-Time Pricing')
    print('='*70)
    print()
    print('Monitoring for trade setups...')
    print('Press Ctrl+C to stop')
    print()

    dual_api = DualAPISystem()
    last_alert_type = None
    cycle = 0

    try:
        while True:
            cycle += 1

            # Check for setups
            result = check_for_trade_setups(dual_api, silent=True)

            if result is None:
                print(f"[{datetime.now().strftime('%I:%M:%S')}] ⚠️  API Error - Retrying in 30s...")
                time.sleep(30)
                continue

            # Print status update every cycle
            print(f"[{datetime.now().strftime('%I:%M:%S')}] 📊 SPX: ${result['spx_price']:.2f} | Active Setups: {len([s for s in result['active_setups'] if s['active']])}")

            # Alert on active setups
            for setup in result['active_setups']:
                if setup['active']:
                    # Only alert once per setup type
                    if last_alert_type != setup['type']:
                        print(format_setup_alert(setup))

                        # Send to Discord
                        try:
                            import subprocess
                            title = f"🚨 {setup['type']} - {setup['confidence']}% Confidence"
                            message = f"""SPX: ${setup['spx_price']:.2f}
SPY: ${setup['spy_price']:.2f}

Entry: SPY {setup['strike']} {setup['direction']}S
Target: {setup['target']}
Stop: {setup['stop']}
Size: {setup['size']}

Time: {datetime.now().strftime('%I:%M:%S %p ET')}"""

                            subprocess.run([
                                'python', 'send_discord.py', title, message
                            ], timeout=10)
                            print('✅ Alert sent to Discord')
                        except:
                            pass

                        last_alert_type = setup['type']

            # Reset alert if no active setups
            if not any(s['active'] for s in result['active_setups']):
                last_alert_type = None

            # Wait 30 seconds
            time.sleep(30)

    except KeyboardInterrupt:
        print('\n\n✅ Monitor stopped')
        print(f'Total cycles: {cycle}')

if __name__ == "__main__":
    main()