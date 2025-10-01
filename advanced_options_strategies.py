#!/usr/bin/env python3
"""
ADVANCED OPTIONS STRATEGIES
Multiple strategies with profit analysis for each alert
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from simple_options_premium import calculate_simple_premium

def calculate_vertical_spread(symbol, current_price, long_strike, short_strike,
                              option_type='CALL', contracts=1):
    """Calculate vertical spread (debit spread)"""

    # Long option (buy)
    long = calculate_simple_premium(symbol, current_price, long_strike, option_type, contracts)
    # Short option (sell)
    short = calculate_simple_premium(symbol, current_price, short_strike, option_type, contracts)

    # Net debit (cost)
    net_debit = long['total_cost'] - short['total_cost']

    # Max profit = (spread width - net debit) * 100 * contracts
    spread_width = abs(long_strike - short_strike)
    max_profit = (spread_width * 100 * contracts) - net_debit

    return {
        'strategy': f'{option_type} Vertical Spread',
        'long_strike': long_strike,
        'short_strike': short_strike,
        'net_cost': abs(net_debit),
        'max_loss': abs(net_debit),
        'max_profit': max_profit,
        'profit_potential': (max_profit / abs(net_debit) * 100) if net_debit != 0 else 0,
        'risk_reward': (max_profit / abs(net_debit)) if net_debit != 0 else 0,
        'contracts': contracts,
        'description': f'Buy {long_strike} / Sell {short_strike}'
    }

def generate_strategy_comparison(symbol, current_price, pattern, target, stop):
    """Generate comparison of multiple strategies"""

    # Determine strikes based on pattern
    if 'BOUNCE' in pattern or 'BULLISH' in pattern or 'BREAK' in pattern:
        # Bullish strategies
        atm = round(current_price)

        strategies = []

        # 1. Simple CALL
        simple_call = calculate_simple_premium(symbol, current_price, atm, 'CALL', 1)
        profit_at_target = ((target - atm) * 100) - simple_call['total_cost'] if target > atm else 0
        strategies.append({
            'name': '💰 Simple Call (Beginner)',
            'type': 'DIRECTIONAL',
            'cost': simple_call['total_cost'],
            'max_loss': simple_call['total_cost'],
            'max_profit': 'Unlimited',
            'profit_at_target': max(0, profit_at_target),
            'complexity': 'EASY',
            'description': f'Buy {atm} CALL',
            'contract': f'{symbol}{atm}C'
        })

        # 2. OTM Call (Lower cost)
        otm = atm + 5
        otm_call = calculate_simple_premium(symbol, current_price, otm, 'CALL', 1)
        profit_otm = ((target - otm) * 100) - otm_call['total_cost'] if target > otm else -otm_call['total_cost']
        strategies.append({
            'name': '💸 OTM Call (Lower Risk)',
            'type': 'DIRECTIONAL',
            'cost': otm_call['total_cost'],
            'max_loss': otm_call['total_cost'],
            'max_profit': 'Unlimited',
            'profit_at_target': max(0, profit_otm),
            'complexity': 'EASY',
            'description': f'Buy {otm} CALL (cheaper)',
            'contract': f'{symbol}{otm}C'
        })

        # 3. Bull Call Spread (Defined risk)
        spread = calculate_vertical_spread(symbol, current_price, atm, atm + 5, 'CALL', 1)
        strategies.append({
            'name': '📊 Bull Call Spread (Defined Risk)',
            'type': 'DEFINED_RISK',
            'cost': spread['net_cost'],
            'max_loss': spread['max_loss'],
            'max_profit': spread['max_profit'],
            'profit_at_target': spread['max_profit'] if target >= atm + 5 else max(0, ((target - atm) * 100) - spread['net_cost']),
            'complexity': 'MODERATE',
            'description': spread['description'],
            'contract': f'{symbol}{atm}C/{symbol}{atm+5}C'
        })

    else:
        # Bearish strategies
        atm = round(current_price)

        strategies = []

        # Simple PUT
        simple_put = calculate_simple_premium(symbol, current_price, atm, 'PUT', 1)
        profit_put = (atm - target) * 100 - simple_put['total_cost'] if target < atm else 0
        strategies.append({
            'name': '💰 Simple Put (Beginner)',
            'type': 'DIRECTIONAL',
            'cost': simple_put['total_cost'],
            'max_loss': simple_put['total_cost'],
            'max_profit': atm * 100,
            'profit_at_target': max(0, profit_put),
            'complexity': 'EASY',
            'description': f'Buy {atm} PUT',
            'contract': f'{symbol}{atm}P'
        })

        # Bear Put Spread
        spread = calculate_vertical_spread(symbol, current_price, atm, atm - 5, 'PUT', 1)
        strategies.append({
            'name': '📊 Bear Put Spread (Defined Risk)',
            'type': 'DEFINED_RISK',
            'cost': spread['net_cost'],
            'max_loss': spread['max_loss'],
            'max_profit': spread['max_profit'],
            'profit_at_target': spread['max_profit'] if target <= atm - 5 else max(0, ((atm - target) * 100) - spread['net_cost']),
            'complexity': 'MODERATE',
            'description': spread['description'],
            'contract': f'{symbol}{atm}P/{symbol}{atm-5}P'
        })

    return strategies

if __name__ == '__main__':
    print('Advanced Options Strategies module loaded')
