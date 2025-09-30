#!/usr/bin/env python3
"""
QUICK ANALYSIS - Single Command, Instant Results
Usage: python quick.py SYMBOL STRIKE TYPE ENTRY
Example: python quick.py ORCL 320 P 12.50
"""

import sys
import requests
import os
from datetime import datetime

def quick_analysis(symbol, strike, opt_type, entry):
    """Ultra-fast option analysis - one command, instant results"""
    api_key = "ZFL38ZY98GSN7E1S"
    
    print(f"QUICK ANALYSIS: {symbol} {strike}{opt_type} @ ${entry}")
    print("-" * 40)
    
    # Get current price
    try:
        url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&entitlement=realtime&apikey={api_key}"
        response = requests.get(url, timeout=8)
        data = response.json()
        current = float(data['Global Quote']['05. price'])
    except:
        print("Error getting market data")
        return
    
    # Quick calculations
    strike = float(strike)
    entry = float(entry)
    
    if opt_type.upper() == 'P':
        distance = current - strike
        breakeven = strike - entry
        itm_condition = f"below {strike}"
    else:
        distance = strike - current
        breakeven = strike + entry  
        itm_condition = f"above {strike}"
    
    # Probability estimate
    prob = max(5, min(95, 50 - (distance * 1.5)))
    
    # Risk/Reward
    target_1 = entry * 2
    target_2 = entry * 3
    max_loss = entry
    
    # Recommendation
    if prob > 65 and abs(distance) < 15:
        rec = "BUY"
        confidence = "HIGH"
    elif prob > 45 and abs(distance) < 25:
        rec = "CONSIDER" 
        confidence = "MEDIUM"
    elif prob > 25:
        rec = "RISKY"
        confidence = "LOW"
    else:
        rec = "AVOID"
        confidence = "VERY LOW"
    
    # Results
    print(f"Current Price: ${current:.2f}")
    print(f"Strike Distance: {distance:.1f} points")
    print(f"Breakeven: ${breakeven:.2f}")
    print(f"ITM if {symbol} {itm_condition}")
    print(f"Probability: {prob:.0f}%")
    print(f"")
    print(f"TARGETS:")
    print(f"  Target 1: ${target_1:.2f} (100% gain)")
    print(f"  Target 2: ${target_2:.2f} (200% gain)")
    print(f"  Max Loss: ${max_loss:.2f}")
    print(f"")
    print(f"RECOMMENDATION: {rec} ({confidence} confidence)")
    
    # Auto-save
    os.makedirs(".spx", exist_ok=True)
    with open(".spx/quick_log.txt", "a") as f:
        timestamp = datetime.now().strftime("%H:%M:%S")
        f.write(f"{timestamp}: {symbol} {strike}{opt_type} @ ${entry} - {rec} ({prob:.0f}%)\n")
    
    return rec

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: python quick.py SYMBOL STRIKE TYPE ENTRY")
        print("Example: python quick.py ORCL 320 P 12.50")
        sys.exit(1)
    
    symbol = sys.argv[1].upper()
    strike = sys.argv[2]
    opt_type = sys.argv[3].upper()
    entry = sys.argv[4]
    
    quick_analysis(symbol, strike, opt_type, entry)