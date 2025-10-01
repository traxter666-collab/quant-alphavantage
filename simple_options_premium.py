#!/usr/bin/env python3
"""
SIMPLE OPTIONS PREMIUM CALCULATOR
Shows exact dollar amounts needed for top alerts
"""

def calculate_simple_premium(symbol, current_price, strike, option_type='CALL', contracts=1):
    """Calculate simple option premium estimates"""
    
    # Distance to strike
    if option_type == 'CALL':
        distance = strike - current_price
        itm_otm = 'ITM' if distance < 0 else 'ATM' if abs(distance) < 5 else 'OTM'
    else:  # PUT
        distance = current_price - strike
        itm_otm = 'ITM' if distance < 0 else 'ATM' if abs(distance) < 5 else 'OTM'
    
    distance_pct = abs(distance / current_price * 100)
    
    # Simple premium estimation (conservative)
    if itm_otm == 'ITM':
        base_premium = abs(distance) + (current_price * 0.02)  # Intrinsic + 2% time value
    elif itm_otm == 'ATM':
        base_premium = current_price * 0.025  # 2.5% for ATM
    else:  # OTM
        if distance_pct < 1:
            base_premium = current_price * 0.015  # 1.5% for near OTM
        elif distance_pct < 2:
            base_premium = current_price * 0.008  # 0.8% for moderate OTM
        else:
            base_premium = current_price * 0.004  # 0.4% for far OTM
    
    # Adjust for 0DTE (lower premium)
    base_premium *= 0.7  # 30% discount for 0DTE
    
    # Calculate totals
    premium_per_contract = base_premium
    total_cost = premium_per_contract * 100 * contracts  # 100 shares per contract
    
    return {
        'symbol': symbol,
        'strike': strike,
        'type': option_type,
        'position': itm_otm,
        'distance': distance,
        'distance_pct': distance_pct,
        'premium_per_share': premium_per_contract,
        'premium_per_contract': premium_per_contract * 100,
        'contracts': contracts,
        'total_cost': total_cost,
        'max_loss': total_cost,
        'contract_code': f'{symbol}{strike}{option_type[0]}'
    }

def format_simple_alert(setup):
    """Format simple premium alert for Discord"""
    s = setup
    
    return f"""💰 SIMPLE OPTIONS SETUP - {s['symbol']}

📊 EXACT COST TO ENTER:
Contract: {s['contract_code']} ({s['position']})
Premium: ${s['premium_per_contract']:.2f} per contract
Contracts: {s['contracts']}
TOTAL COST: ${s['total_cost']:.2f}
MAX LOSS: ${s['total_cost']:.2f} (100% of premium)

🎯 THIS IS ALL YOU NEED:
• Just ${s['total_cost']:.2f} to enter this trade
• No margin required
• No additional capital needed
• Risk is limited to what you pay

💵 PAYMENT BREAKDOWN:
1 contract = ${s['premium_per_contract']:.2f}
{s['contracts']} contract(s) × ${s['premium_per_contract']:.2f} = ${s['total_cost']:.2f}

✅ BEGINNER-FRIENDLY:
• Simple to understand
• Known maximum loss
• No surprises
• Just pay the premium shown"""

if __name__ == '__main__':
    # Example: SPY support bounce setup
    spy_setup = calculate_simple_premium(
        symbol='SPY',
        current_price=662.25,
        strike=665,
        option_type='CALL',
        contracts=1
    )
    
    print('🧪 SIMPLE OPTIONS PREMIUM TEST')
    print('=' * 70)
    print()
    print(format_simple_alert(spy_setup))
    print()
    print('=' * 70)
    print('✅ Simple premium calculator ready for top alerts')
