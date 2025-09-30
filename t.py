#!/usr/bin/env python3
"""
T - Ultra-minimal trade analysis
Usage: python t.py SYMBOL STRIKE TYPE ENTRY
Example: python t.py SPXW 6525 P 4.30
"""

import sys
import requests
import json
import os
from datetime import datetime

def t(symbol, strike, opt_type, entry):
    """Minimal analysis - essential data only"""
    
    # Get price
    if symbol.upper() in ['SPXW', 'SPX']:
        url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=SPY&entitlement=realtime&apikey=ZFL38ZY98GSN7E1S"
        mult = 10
    else:
        url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&entitlement=realtime&apikey=ZFL38ZY98GSN7E1S"
        mult = 1
    
    try:
        response = requests.get(url, timeout=5)
        current = float(response.json()['Global Quote']['05. price']) * mult
    except:
        print("Error getting data")
        return
    
    # Calculate
    strike = float(strike)
    entry = float(entry)
    
    if opt_type.upper() == 'P':
        dist = current - strike
        itm = dist < 0
    else:
        dist = strike - current
        itm = dist < 0
    
    # Probability
    if itm:
        prob = min(85, 70 + abs(dist))
    else:
        prob = max(15, 55 - (dist * 1.5))
    
    # Action
    if itm and entry < abs(dist) * 0.8:
        action = "BUY"
    elif abs(dist) < 15 and entry < 8:
        action = "CONSIDER"  
    else:
        action = "AVOID"
    
    # Display
    print(f"{symbol} {strike}{opt_type} @ ${entry}")
    print(f"Current: ${current:.1f} | Dist: {dist:.1f} | Prob: {prob:.0f}% | {action}")
    
    # Save if useful
    if prob >= 70 or (itm and entry < abs(dist)):
        os.makedirs('.spx', exist_ok=True)
        trade = {
            'time': datetime.now().strftime("%H:%M"),
            'setup': f"{symbol} {strike}{opt_type}",
            'current': round(current, 1),
            'entry': entry,
            'dist': round(dist, 1),
            'prob': round(prob),
            'action': action
        }
        
        with open('.spx/trades.jsonl', 'a') as f:
            f.write(json.dumps(trade) + '\n')

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: python t.py SYMBOL STRIKE TYPE ENTRY")
        sys.exit(1)
    
    t(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])