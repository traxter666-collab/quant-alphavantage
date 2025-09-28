import os
import requests
from datetime import datetime

def analyze_optimal_spx_strikes():
    """Analyze optimal SPX 0DTE strike prices based on current market conditions"""
    
    api_key = os.getenv('ALPHAVANTAGE_API_KEY', 'ZFL38ZY98GSN7E1S')
    base_url = "https://www.alphavantage.co/query"
    
    print("SPX OPTIMAL STRIKE ANALYSIS - 0DTE")
    print("=" * 45)
    
    # Get current market data
    spy_response = requests.get(f"{base_url}?function=GLOBAL_QUOTE&symbol=SPY&entitlement=realtime&apikey={api_key}")
    spy_data = spy_response.json()
    
    if "Global Quote" not in spy_data:
        print("Error getting market data")
        return
    
    spy_quote = spy_data["Global Quote"]
    spy_price = float(spy_quote["05. price"])
    spy_high = float(spy_quote["03. high"])
    spy_low = float(spy_quote["04. low"])
    spy_change = float(spy_quote["09. change"])
    
    spx_current = spy_price * 10
    spx_high = spy_high * 10
    spx_low = spy_low * 10
    
    # Get RSI for momentum context
    rsi_response = requests.get(f"{base_url}?function=RSI&symbol=SPY&interval=5min&time_period=14&series_type=close&entitlement=realtime&apikey={api_key}")
    current_rsi = 50  # Default
    if "Technical Analysis: RSI" in rsi_response.json():
        rsi_data = rsi_response.json()["Technical Analysis: RSI"]
        if rsi_data:
            latest_rsi_timestamp = list(rsi_data.keys())[0]
            current_rsi = float(rsi_data[latest_rsi_timestamp]["RSI"])
    
    print(f"SPX Current: ${spx_current:.2f}")
    print(f"Today's Range: ${spx_low:.2f} - ${spx_high:.2f}")
    print(f"RSI (5min): {current_rsi:.1f}")
    
    # Quant levels for reference
    key_levels = {
        'resistance': [6510, 6538, 6542, 6560, 6567, 6578],
        'support': [6498, 6488, 6482, 6470, 6465, 6455, 6430]
    }
    
    # Find nearest strikes (SPX strikes are in 5-point increments)
    current_strike = int(spx_current / 5) * 5
    
    print(f"\nSTRIKE EFFICIENCY ANALYSIS:")
    print(f"Current Strike (ATM): {current_strike}")
    
    # Analyze different strike strategies
    strikes_analysis = []
    
    # CALLS Analysis
    print(f"\nCALL STRIKES (Bullish Plays):")
    
    # ATM Calls (highest gamma, most sensitive)
    atm_call = current_strike
    atm_distance = abs(spx_current - atm_call)
    atm_probability = calculate_itm_probability(spx_current, atm_call, "CALL", current_rsi)
    
    strikes_analysis.append({
        'strike': atm_call,
        'type': 'CALL',
        'strategy': 'ATM - High Gamma',
        'distance': atm_distance,
        'probability': atm_probability,
        'premium_est': estimate_premium(atm_distance, "ATM"),
        'risk_reward': '1:1 to 1:2',
        'best_for': 'Quick scalps, momentum plays'
    })
    
    # OTM Calls (cheaper, higher return potential)
    otm_call_1 = current_strike + 10  # 10 points OTM
    otm_call_2 = current_strike + 15  # 15 points OTM
    
    for otm_strike in [otm_call_1, otm_call_2]:
        distance = otm_strike - spx_current
        probability = calculate_itm_probability(spx_current, otm_strike, "CALL", current_rsi)
        premium = estimate_premium(distance, "OTM_CALL")
        
        strikes_analysis.append({
            'strike': otm_strike,
            'type': 'CALL',
            'strategy': f'OTM +{distance:.0f}pts',
            'distance': distance,
            'probability': probability,
            'premium_est': premium,
            'risk_reward': '1:2 to 1:5',
            'best_for': 'Breakout plays, lotto tickets'
        })
    
    # PUTS Analysis
    print(f"\nPUT STRIKES (Bearish Plays):")
    
    # ATM Puts
    atm_put = current_strike
    atm_put_distance = abs(spx_current - atm_put)
    atm_put_probability = calculate_itm_probability(spx_current, atm_put, "PUT", current_rsi)
    
    strikes_analysis.append({
        'strike': atm_put,
        'type': 'PUT',
        'strategy': 'ATM - High Gamma',
        'distance': atm_put_distance,
        'probability': atm_put_probability,
        'premium_est': estimate_premium(atm_put_distance, "ATM"),
        'risk_reward': '1:1 to 1:2',
        'best_for': 'Quick scalps, momentum plays'
    })
    
    # OTM Puts
    otm_put_1 = current_strike - 10  # 10 points OTM
    otm_put_2 = current_strike - 15  # 15 points OTM
    
    for otm_strike in [otm_put_1, otm_put_2]:
        distance = spx_current - otm_strike
        probability = calculate_itm_probability(spx_current, otm_strike, "PUT", current_rsi)
        premium = estimate_premium(distance, "OTM_PUT")
        
        strikes_analysis.append({
            'strike': otm_strike,
            'type': 'PUT',
            'strategy': f'OTM -{distance:.0f}pts',
            'distance': distance,
            'probability': probability,
            'premium_est': premium,
            'risk_reward': '1:2 to 1:5',
            'best_for': 'Breakdown plays, lotto tickets'
        })
    
    # Display analysis with recommendations
    print(f"\nSTRIKE RECOMMENDATIONS BY SCENARIO:")
    
    # Scenario 1: Break above 6510 (bullish)
    print(f"\nSCENARIO 1: BREAK ABOVE 6510 (Bullish)")
    best_bullish_strikes = [6510, 6515, 6520]
    for strike in best_bullish_strikes:
        distance = strike - spx_current
        if strike <= spx_current + 5:  # ATM/ITM
            premium = "$3.00-5.00"
            probability = "60-70%"
        elif strike <= spx_current + 15:  # Moderate OTM
            premium = "$1.50-3.00"
            probability = "35-45%"
        else:  # Far OTM
            premium = "$0.50-1.50"
            probability = "15-25%"
        
        print(f"  {strike} calls: {premium} | Prob: {probability} | +{distance:.0f}pts move needed")
    
    # Scenario 2: Fail at 6510, fall to support (bearish)
    print(f"\nSCENARIO 2: FAIL AT 6510, FALL TO SUPPORT (Bearish)")
    best_bearish_strikes = [6500, 6495, 6490]
    for strike in best_bearish_strikes:
        distance = spx_current - strike
        if distance <= 5:  # ATM/ITM
            premium = "$3.00-5.00"
            probability = "60-70%"
        elif distance <= 15:  # Moderate OTM
            premium = "$1.50-3.00"
            probability = "35-45%"
        else:  # Far OTM
            premium = "$0.50-1.50"
            probability = "15-25%"
        
        print(f"  {strike} puts: {premium} | Prob: {probability} | -{distance:.0f}pts move needed")
    
    # Scenario 3: Range-bound (straddle/strangle)
    print(f"\nSCENARIO 3: RANGE-BOUND TRADING")
    print(f"  Straddle: {current_strike} calls + {current_strike} puts")
    print(f"  Strangle: {current_strike + 5} calls + {current_strike - 5} puts")
    print(f"  Iron Condor: Sell {current_strike - 10}/{current_strike + 10}, Buy {current_strike - 20}/{current_strike + 20}")
    
    # Best strikes based on current market conditions
    print(f"\nCURRENT MARKET OPTIMAL STRIKES:")
    
    # Based on being below 6510 resistance
    if spx_current < 6510:
        print(f"BEARISH BIAS (Below 6510 resistance):")
        print(f"  1. 6500 puts - High probability, close to ATM")
        print(f"  2. 6495 puts - Moderate risk, targeting 6498 support break")
        print(f"  3. 6490 puts - Higher risk/reward, targeting support zone")
        print(f"  UPSIDE: 6510 calls if reclaim with volume")
        
        recommended_strikes = ["SPXW250910P6500.0", "SPXW250910P6495.0", "SPXW250910C6510.0"]
    else:
        print(f"BULLISH BIAS (Above 6510 resistance):")
        print(f"  1. 6515 calls - Momentum continuation")
        print(f"  2. 6520 calls - Breakout target")
        print(f"  3. 6500 puts - Reversal hedge")
        
        recommended_strikes = ["SPXW250910C6515.0", "SPXW250910C6520.0", "SPXW250910P6500.0"]
    
    print(f"\nTRADINGVIEW CODES:")
    for code in recommended_strikes:
        print(f"  {code}")

def calculate_itm_probability(current, strike, option_type, rsi):
    """Estimate ITM probability based on distance and RSI"""
    if option_type == "CALL":
        distance = strike - current
        base_prob = max(10, 60 - (distance * 2))  # 60% at ATM, decreases 2% per point OTM
        rsi_adjustment = (rsi - 50) * 0.5  # RSI above 50 helps calls
    else:  # PUT
        distance = current - strike
        base_prob = max(10, 60 - (distance * 2))  # 60% at ATM, decreases 2% per point OTM
        rsi_adjustment = (50 - rsi) * 0.5  # RSI below 50 helps puts
    
    return max(10, min(80, base_prob + rsi_adjustment))

def estimate_premium(distance, option_type):
    """Rough premium estimates based on distance from current price"""
    if option_type == "ATM":
        return "$3.00-5.00"
    elif distance <= 5:
        return "$2.00-4.00"
    elif distance <= 10:
        return "$1.00-3.00"
    elif distance <= 15:
        return "$0.50-2.00"
    else:
        return "$0.25-1.00"

if __name__ == "__main__":
    analyze_optimal_spx_strikes()