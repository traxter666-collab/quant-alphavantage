#!/usr/bin/env python3
"""
ENHANCED ALERTS WITH SIMPLE PREMIUM CALCULATOR
Adds exact dollar amounts to all top alerts
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from simple_options_premium import calculate_simple_premium, format_simple_alert

def create_enhanced_alert(symbol, current_price, pattern, confidence, 
                         entry_zone, target, stop, strike, option_type='CALL'):
    """Create alert with premium calculation"""
    
    # Calculate premium for 1 contract
    premium_calc = calculate_simple_premium(
        symbol=symbol,
        current_price=current_price,
        strike=strike,
        option_type=option_type,
        contracts=1
    )
    
    # Calculate potential gains
    potential_move = target - current_price
    potential_move_pct = (potential_move / current_price) * 100
    
    # Estimate option value at target (conservative)
    if option_type == 'CALL':
        option_profit = (target - strike) * 100 - premium_calc['premium_per_contract']
    else:  # PUT
        option_profit = (strike - target) * 100 - premium_calc['premium_per_contract']
    
    option_profit = max(0, option_profit)  # Can't be negative
    profit_pct = (option_profit / premium_calc['premium_per_contract']) * 100 if premium_calc['premium_per_contract'] > 0 else 0
    
    alert = f"""🚨 {symbol} - {pattern}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 SETUP DETAILS:
Current Price: ${current_price:.2f}
Entry Zone: {entry_zone}
Target: ${target:.2f} (+{potential_move_pct:.1f}%)
Stop: ${stop:.2f}
Confidence: {confidence}%

💰 SIMPLE OPTIONS TRADE:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 CONTRACT: {premium_calc['contract_code']}
Strike: ${strike} {option_type}
Position: {premium_calc['position']}

💵 EXACT COST TO ENTER (1 CONTRACT):
Premium: ${premium_calc['premium_per_contract']:.2f}
TOTAL NEEDED: ${premium_calc['total_cost']:.2f}
MAX LOSS: ${premium_calc['total_cost']:.2f}

📈 POTENTIAL AT TARGET:
If {symbol} hits ${target:.2f}:
Option Value: ~${option_profit + premium_calc['premium_per_contract']:.2f}
Your Profit: ~${option_profit:.2f}
Return: ~{profit_pct:.0f}%

✅ THIS IS ALL YOU NEED:
• ${premium_calc['total_cost']:.2f} to enter
• No margin required
• Risk is ONLY the ${premium_calc['total_cost']:.2f} you pay
• Maximum loss is known upfront

🎓 BEGINNER-FRIENDLY:
• Simple premium payment
• No complicated calculations
• Known maximum risk
• Easy to understand"""
    
    return alert

if __name__ == '__main__':
    # Test with current SPY setup
    alert = create_enhanced_alert(
        symbol='SPY',
        current_price=662.25,
        pattern='SUPPORT_BOUNCE',
        confidence=75,
        entry_zone='$662.00-$662.60',
        target=668.00,
        stop=661.00,
        strike=665,
        option_type='CALL'
    )
    
    print('🧪 ENHANCED ALERT WITH PREMIUM TEST')
    print('=' * 70)
    print()
    print(alert)
    print()
    print('=' * 70)
    print('✅ Enhanced alerts ready with exact premium amounts')
