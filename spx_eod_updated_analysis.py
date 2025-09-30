#!/usr/bin/env python3
"""
SPX End of Day Contract Analysis - CORRECTED with actual close 6,584.28
Calculate actual returns using real closing price
"""

def calculate_actual_returns():
    """Calculate actual returns with correct SPX close price"""
    
    # CORRECTED DATA
    spx_actual_close = 6584.28  # User provided actual close
    spx_estimated_close = 6574.10  # Our estimate from SPY
    
    # Our recommended contract
    recommended_strike = 6580
    estimated_premium = 2.00
    
    print("SPX EOD CONTRACT - ACTUAL RESULTS")
    print("=" * 45)
    print(f"Estimated SPX Close: ${spx_estimated_close:.2f}")
    print(f"ACTUAL SPX Close:    ${spx_actual_close:.2f}")
    print(f"Difference: +${spx_actual_close - spx_estimated_close:.2f}")
    print()
    
    # Calculate actual option value at close
    actual_intrinsic = max(0, spx_actual_close - recommended_strike)
    
    print("SPXW6580C ACTUAL PERFORMANCE:")
    print("-" * 35)
    print(f"Strike Price: ${recommended_strike}")
    print(f"Estimated Entry: ${estimated_premium:.2f}")
    print(f"SPX Actual Close: ${spx_actual_close:.2f}")
    print(f"Intrinsic Value: ${actual_intrinsic:.2f}")
    print()
    
    if actual_intrinsic > 0:
        actual_return = (actual_intrinsic - estimated_premium) / estimated_premium * 100
        print(f"ACTUAL RETURN: {actual_return:.1f}%")
        
        if actual_return > 0:
            print(f"PROFITABLE TRADE: ${actual_intrinsic:.2f} vs ${estimated_premium:.2f} entry")
            multiplier = actual_intrinsic / estimated_premium
            print(f"Return Multiple: {multiplier:.1f}x")
        else:
            print(f"Loss: {actual_return:.1f}%")
    else:
        print(f"EXPIRED WORTHLESS - 100% loss")
        print(f"   SPX needed to reach ${recommended_strike} but closed at ${spx_actual_close:.2f}")
    
    # Analysis of our prediction accuracy
    points_itm = spx_actual_close - recommended_strike
    print()
    print("PREDICTION ACCURACY:")
    print("-" * 25)
    print(f"Contract was: {points_itm:.2f} points ITM")
    print(f"Strike Selection: {'EXCELLENT' if points_itm > 2 else 'GOOD' if points_itm > 0 else 'POOR'}")
    
    # What if analysis - other strikes
    print()
    print("OTHER STRIKE PERFORMANCE:")
    print("-" * 30)
    
    other_strikes = [6575, 6585, 6590]
    for strike in other_strikes:
        intrinsic = max(0, spx_actual_close - strike)
        if intrinsic > 0:
            return_pct = (intrinsic - 2.0) / 2.0 * 100
            print(f"SPXW{strike}C: ${intrinsic:.2f} intrinsic ({return_pct:+.1f}%)")
        else:
            print(f"SPXW{strike}C: $0.00 intrinsic (-100%)")
    
    print()
    print("CONCLUSION:")
    if actual_intrinsic > estimated_premium:
        print(f"Recommended SPXW6580C was PROFITABLE")
        print(f"System successfully identified winning EOD contract")
    else:
        print(f"Recommended contract would have lost money")
    
    return {
        'actual_close': spx_actual_close,
        'strike': recommended_strike,
        'intrinsic': actual_intrinsic,
        'estimated_entry': estimated_premium,
        'actual_return': (actual_intrinsic - estimated_premium) / estimated_premium * 100 if estimated_premium > 0 else -100,
        'profitable': actual_intrinsic > estimated_premium
    }

if __name__ == "__main__":
    result = calculate_actual_returns()
    print(f"\nFinal Result: {'WINNER' if result['profitable'] else 'LOSER'}")