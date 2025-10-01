#!/usr/bin/env python3
"""
MULTI-STRATEGY ALERT SYSTEM
Shows simple + advanced strategies for every alert
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from advanced_options_strategies import generate_strategy_comparison

def create_multi_strategy_alert(symbol, current_price, pattern, confidence,
                               entry_zone, target, stop):
    """Create comprehensive alert with multiple strategy options"""
    
    # Generate all strategies
    strategies = generate_strategy_comparison(symbol, current_price, pattern, target, stop)
    
    # Potential move
    move = target - current_price
    move_pct = (move / current_price) * 100
    
    alert = f"""🎯 {symbol} - {pattern}
Confidence: {confidence}% | Target: ${target:.2f} (+{move_pct:.1f}%)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 MULTIPLE STRATEGY OPTIONS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    
    for i, strat in enumerate(strategies, 1):
        roi = (strat['profit_at_target'] / strat['cost'] * 100) if strat['cost'] > 0 else 0
        
        alert += f"""
{i}. {strat['name']}
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   💵 Cost: ${strat['cost']:.2f}
   🛡️ Max Loss: ${strat['max_loss']:.2f}
   📈 Max Profit: {strat['max_profit'] if isinstance(strat['max_profit'], str) else f"${strat['max_profit']:.2f}"}
   
   🎯 AT TARGET (${target:.2f}):
   Profit: ${strat['profit_at_target']:.2f}
   Return: {roi:.0f}%
   
   📋 Setup: {strat['description']}
   🎫 Contract: {strat['contract']}
   🎓 Level: {strat['complexity']}
"""
    
    # Add recommendation
    best_roi = max(strategies, key=lambda x: (x['profit_at_target'] / x['cost']) if x['cost'] > 0 else 0)
    lowest_risk = min(strategies, key=lambda x: x['max_loss'])
    
    alert += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💡 RECOMMENDATIONS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🏆 BEST ROI: {best_roi['name']}
   Cost: ${best_roi['cost']:.2f} → Profit: ${best_roi['profit_at_target']:.2f}
   Return: {(best_roi['profit_at_target']/best_roi['cost']*100):.0f}%

🛡️ LOWEST RISK: {lowest_risk['name']}
   Max Loss: ${lowest_risk['max_loss']:.2f}
   Conservative choice for smaller accounts

✅ CHOOSE BASED ON:
• Account size (lower cost = less capital)
• Risk tolerance (defined risk vs unlimited)
• Experience level (easy vs advanced)
• Profit goal (higher ROI vs safer return)"""
    
    return alert

if __name__ == '__main__':
    alert = create_multi_strategy_alert(
        symbol='SPY',
        current_price=662.25,
        pattern='SUPPORT_BOUNCE',
        confidence=75,
        entry_zone='$662.00-$662.60',
        target=668.00,
        stop=661.00
    )
    
    print('🧪 MULTI-STRATEGY ALERT TEST')
    print('=' * 70)
    print()
    print(alert)
    print()
    print('=' * 70)
    print('✅ Multi-strategy alerts ready')
