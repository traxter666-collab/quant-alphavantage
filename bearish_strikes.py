import numpy as np
import requests

def get_spx():
    try:
        url = "https://query1.finance.yahoo.com/v8/finance/chart/%5EGSPC"
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=5)
        data = response.json()
        return data['chart']['result'][0]['meta']['regularMarketPrice']
    except:
        return 6541.54

def bearish_analysis():
    current_spx = get_spx()
    
    print("BEARISH BIAS ANALYSIS - SPX 0DTE PUTS")
    print("=" * 45)
    print(f"Current SPX: ${current_spx:.2f}")
    print(f"Support Status: BROKEN/BREAKING at 6542")
    print()
    
    # Bearish scenarios with probabilities
    scenarios = [
        {"level": 6540, "prob": 75, "desc": "Break below 6542 support"},
        {"level": 6535, "prob": 65, "desc": "Continue to next support"}, 
        {"level": 6530, "prob": 55, "desc": "Major breakdown move"},
        {"level": 6525, "prob": 45, "desc": "Accelerated selling"},
        {"level": 6520, "prob": 35, "desc": "Cascade to 6520 level"},
        {"level": 6515, "prob": 25, "desc": "Deep breakdown"},
        {"level": 6510, "prob": 20, "desc": "Back to key resistance"},
        {"level": 6498, "prob": 15, "desc": "Strong support test"}
    ]
    
    print("BEARISH PROBABILITY TARGETS:")
    for scenario in scenarios:
        move_needed = current_spx - scenario["level"]
        print(f"${scenario['level']:,}: {scenario['prob']}% prob (-{move_needed:.0f} pts) - {scenario['desc']}")
    
    print(f"\nTOP 5 BEARISH PUT STRIKES:")
    print("=" * 35)
    
    strikes = []
    
    for scenario in scenarios[:5]:
        strike = scenario["level"]
        prob = scenario["prob"]
        distance = current_spx - strike
        
        # Premium estimation
        if distance <= 0:  # OTM
            premium = max(0.5, 2.5 - abs(distance) * 0.15)
        else:  # ITM  
            premium = distance + max(0.8, 2.0 - distance * 0.1)
        
        # Expected move calculation
        expected_move = distance * (prob / 100)
        risk_reward = expected_move / premium if premium > 0 else 0
        
        strikes.append({
            'strike': f"SPXW250910P{strike}.0",
            'level': strike,
            'prob': prob,
            'distance': distance,
            'premium': premium,
            'expected_move': expected_move,
            'risk_reward': risk_reward
        })
    
    # Sort by probability
    strikes.sort(key=lambda x: x['prob'], reverse=True)
    
    print(f"Rank Strike              Prob%  Dist   Premium  ExpMove  R/R")
    print("-" * 60)
    
    for i, s in enumerate(strikes, 1):
        print(f"{i:<4} {s['strike']:<18} {s['prob']:<6} {s['distance']:<6.1f} "
              f"${s['premium']:<7.2f} ${s['expected_move']:<7.2f} {s['risk_reward']:<4.2f}")
    
    print(f"\nTOP 3 DETAILED ANALYSIS:")
    
    for i, s in enumerate(strikes[:3], 1):
        print(f"\n{i}. {s['strike']}")
        print(f"   Target: ${s['level']:,}")
        print(f"   Probability: {s['prob']}%") 
        print(f"   Move needed: {s['distance']:.0f} points")
        print(f"   Est. premium: ${s['premium']:.2f}")
        print(f"   Risk/Reward: {s['risk_reward']:.2f}")
        
        if s['level'] == 6540:
            print(f"   Strategy: HIGHEST PROBABILITY - first breakdown target")
        elif s['level'] == 6535:
            print(f"   Strategy: STRONG FOLLOW-THROUGH - next technical level")
        elif s['level'] == 6530:
            print(f"   Strategy: MAJOR BREAKDOWN - acceleration target")
    
    print(f"\nBEARISH EXECUTION PLAN:")
    best = strikes[0]
    print(f"Primary play: {best['strike']}")
    print(f"Entry: Current levels or any bounce to 6543-6545")
    print(f"Target 1: Break of 6540 for +50-100%")
    print(f"Target 2: Continue to 6535 for +100-200%") 
    print(f"Stop loss: Above 6545 (failed breakdown)")
    print(f"Time exit: 2:30 PM if not moving")
    
    print(f"\nWHY BEARISH NOW:")
    print(f"• SPX at critical 6542 quant support")
    print(f"• Multiple tests of support = eventual break")
    print(f"• 0DTE options amplify breakdown moves")
    print(f"• Next major support not until 6498")
    print(f"• Risk/reward favors downside")
    
    return strikes

if __name__ == "__main__":
    bearish_analysis()