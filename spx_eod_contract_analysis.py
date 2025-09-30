#!/usr/bin/env python3
"""
SPX End of Day Best Contract Return Analysis - 9/12/2025 Data
Calculate optimal SPXW contract returns for end-of-day trading
"""

import math
from datetime import datetime

def analyze_spx_eod_contracts():
    """Analyze SPX end of day best contract opportunities using 9/12 data"""
    
    # SPX derived from SPY data (SPY * 10 approximation)
    spy_close = 657.41
    spx_close = spy_close * 10  # Approximate SPX price: 6,574.10
    
    # Market data from 9/12/2025
    spy_high = 659.11
    spy_low = 656.90
    spx_high = spy_high * 10  # 6,591.10
    spx_low = spy_low * 10    # 6,569.00
    
    # Volume analysis
    spy_volume = 72.78  # 72.78M shares
    volume_vs_avg = 72.78 / 50.0  # Assume 50M avg = 1.46x normal
    
    print(f"SPX EOD CONTRACT ANALYSIS - 9/12/2025")
    print(f"=" * 50)
    print(f"SPX Close: ${spx_close:.2f}")
    print(f"SPX Range: ${spx_low:.2f} - ${spx_high:.2f}")
    print(f"SPY Volume: {spy_volume:.1f}M ({volume_vs_avg:.1f}x avg)")
    print()
    
    # Calculate optimal strikes for 0DTE contracts
    # End of day = limited time, need close-to-money strikes
    
    strikes_calls = [
        (spx_close + 5, "6580"),   # 5 points OTM
        (spx_close + 10, "6585"),  # 10 points OTM
        (spx_close + 15, "6590"),  # 15 points OTM
        (spx_close + 20, "6595"),  # 20 points OTM
    ]
    
    strikes_puts = [
        (spx_close - 5, "6570"),   # 5 points OTM
        (spx_close - 10, "6565"),  # 10 points OTM
        (spx_close - 15, "6560"),  # 15 points OTM
        (spx_close - 20, "6555"),  # 20 points OTM
    ]
    
    # Calculate theoretical option values for EOD (1-2 hours to expiry)
    time_to_expiry = 1.5 / 24  # 1.5 hours as fraction of day
    volatility = 0.15  # Assume 15% annualized volatility
    
    def black_scholes_approx(S, K, T, is_call=True):
        """Simplified BS approximation for very short time"""
        intrinsic = max(0, S - K) if is_call else max(0, K - S)
        
        if T <= 0:
            return intrinsic
        
        # Time value diminishes rapidly near expiry
        time_value = min(2.0, math.sqrt(T) * volatility * S * 0.4)
        
        if intrinsic > 0:
            return intrinsic + time_value * 0.3  # Reduced time value for ITM
        else:
            distance = abs(S - K) / S
            if distance < 0.005:  # Very close to money
                return time_value
            elif distance < 0.01:  # Close to money
                return time_value * 0.6
            else:  # Further OTM
                return time_value * 0.3 * math.exp(-distance * 50)
    
    print("OPTIMAL EOD CALL CONTRACTS:")
    print("-" * 40)
    
    best_call_return = 0
    best_call_strike = ""
    
    for strike_price, strike_name in strikes_calls:
        option_price = black_scholes_approx(spx_close, strike_price, time_to_expiry, True)
        
        # Calculate potential return scenarios
        # Scenario: SPX moves to daily high (6591.10)
        target_price = spx_high
        target_option_value = max(0, target_price - strike_price)
        
        if option_price > 0.1:  # Minimum viable premium
            potential_return = (target_option_value - option_price) / option_price * 100
        else:
            potential_return = -100
        
        distance = (strike_price - spx_close) / spx_close * 100
        
        print(f"SPXW{strike_name}C @ ${option_price:.2f}")
        print(f"  Distance: +{distance:.1f}% | Target: ${target_option_value:.2f}")
        print(f"  Potential Return: {potential_return:.1f}%")
        print()
        
        if potential_return > best_call_return and option_price > 0.5:
            best_call_return = potential_return
            best_call_strike = f"SPXW{strike_name}C"
    
    print("OPTIMAL EOD PUT CONTRACTS:")
    print("-" * 40)
    
    best_put_return = 0
    best_put_strike = ""
    
    for strike_price, strike_name in strikes_puts:
        option_price = black_scholes_approx(spx_close, strike_price, time_to_expiry, False)
        
        # Scenario: SPX moves to daily low (6569.00)
        target_price = spx_low
        target_option_value = max(0, strike_price - target_price)
        
        if option_price > 0.1:
            potential_return = (target_option_value - option_price) / option_price * 100
        else:
            potential_return = -100
        
        distance = (spx_close - strike_price) / spx_close * 100
        
        print(f"SPXW{strike_name}P @ ${option_price:.2f}")
        print(f"  Distance: -{distance:.1f}% | Target: ${target_option_value:.2f}")
        print(f"  Potential Return: {potential_return:.1f}%")
        print()
        
        if potential_return > best_put_return and option_price > 0.5:
            best_put_return = potential_return
            best_put_strike = f"SPXW{strike_name}P"
    
    # Determine best overall contract
    if best_call_return > best_put_return:
        best_contract = best_call_strike
        best_return = best_call_return
        bias = "BULLISH"
        scenario = f"SPX move to daily high ${spx_high:.0f}"
    else:
        best_contract = best_put_strike
        best_return = best_put_return
        bias = "BEARISH"
        scenario = f"SPX move to daily low ${spx_low:.0f}"
    
    # Risk analysis
    risk_assessment = "HIGH" if time_to_expiry < 2/24 else "EXTREME"
    
    print("=" * 50)
    print("BEST EOD CONTRACT RECOMMENDATION:")
    print("=" * 50)
    print(f"Contract: {best_contract}")
    print(f"Expected Return: {best_return:.1f}%")
    print(f"Market Bias: {bias}")
    print(f"Scenario: {scenario}")
    print(f"Risk Level: {risk_assessment}")
    print(f"Time Remaining: {time_to_expiry * 24:.1f} hours")
    print()
    
    return {
        'contract': best_contract,
        'return': best_return,
        'bias': bias,
        'scenario': scenario,
        'risk': risk_assessment,
        'spx_close': spx_close,
        'spx_range': f"${spx_low:.0f}-${spx_high:.0f}"
    }

if __name__ == "__main__":
    result = analyze_spx_eod_contracts()
    print("Analysis complete!")