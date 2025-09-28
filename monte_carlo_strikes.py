import numpy as np
import os
import requests
from datetime import datetime

def get_current_spx():
    """Get current SPX price"""
    try:
        url = "https://query1.finance.yahoo.com/v8/finance/chart/%5EGSPC"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=8)
        data = response.json()
        
        if 'chart' in data and data['chart']['result']:
            meta = data['chart']['result'][0]['meta']
            return meta.get('regularMarketPrice', 6542.15)
    except:
        pass
    return 6542.15  # fallback

def monte_carlo_0dte_analysis(current_price, hours_to_expiry=4.5):
    """Monte Carlo analysis for 0DTE SPX options"""
    
    print("SPX 0DTE MONTE CARLO ANALYSIS")
    print("=" * 40)
    print(f"Current SPX: ${current_price:.2f}")
    print(f"Hours to expiry: {hours_to_expiry}")
    
    # Market parameters
    annual_vol = 0.18  # 18% annual volatility
    daily_vol = annual_vol / np.sqrt(252)
    hourly_vol = daily_vol / np.sqrt(6.5)  # 6.5 trading hours per day
    vol_for_period = hourly_vol * np.sqrt(hours_to_expiry)
    
    print(f"Implied volatility for period: {vol_for_period*100:.2f}%")
    
    # Monte Carlo simulation
    n_simulations = 100000
    np.random.seed(42)  # For reproducible results
    
    # Generate random price movements
    random_moves = np.random.normal(0, vol_for_period, n_simulations)
    final_prices = current_price * np.exp(random_moves)
    
    # Calculate statistics
    mean_price = np.mean(final_prices)
    std_price = np.std(final_prices)
    
    print(f"\nMONTE CARLO RESULTS ({n_simulations:,} simulations):")
    print(f"Expected price: ${mean_price:.2f}")
    print(f"Standard deviation: ${std_price:.2f}")
    print(f"1-sigma range: ${mean_price - std_price:.2f} - ${mean_price + std_price:.2f}")
    
    # Key probability levels
    prob_levels = [
        (6545, "Above 6545"),
        (6540, "Above 6540"), 
        (6535, "Above 6535"),
        (6530, "Above 6530"),
        (6525, "Above 6525"),
        (6520, "Above 6520"),
        (6515, "Above 6515")
    ]
    
    print(f"\nPROBABILITY ANALYSIS:")
    probabilities = {}
    for level, desc in prob_levels:
        prob_above = (final_prices > level).mean() * 100
        prob_below = 100 - prob_above
        probabilities[level] = {'above': prob_above, 'below': prob_below}
        print(f"{desc}: {prob_above:.1f}% | Below {level}: {prob_below:.1f}%")
    
    return final_prices, probabilities

def analyze_top_strikes(current_price, final_prices, probabilities):
    """Analyze top 5 strike opportunities"""
    
    print(f"\nTOP 5 STRIKE ANALYSIS:")
    print("=" * 30)
    
    strike_analysis = []
    
    # Analyze potential strikes around current price
    strikes_to_analyze = [6545, 6540, 6535, 6530, 6525, 6520, 6515, 6510, 6505, 6500]
    
    for strike in strikes_to_analyze:
        if strike in probabilities:
            # CALL analysis
            call_itm_prob = probabilities[strike]['above']
            call_distance = strike - current_price
            call_premium_est = max(0.25, 5.0 * np.exp(-0.5 * (call_distance/10)**2))  # Rough estimate
            
            if call_itm_prob > 15:  # Only if reasonable probability
                call_ev = call_itm_prob/100 * max(0, np.mean(final_prices[final_prices > strike]) - strike) - (100-call_itm_prob)/100 * call_premium_est
                strike_analysis.append({
                    'strike': f"SPXW250910C{strike}.0",
                    'type': 'CALL',
                    'strike_level': strike,
                    'distance': call_distance,
                    'probability': call_itm_prob,
                    'premium_est': call_premium_est,
                    'expected_value': call_ev,
                    'risk_reward': call_ev / call_premium_est if call_premium_est > 0 else 0
                })
            
            # PUT analysis
            put_itm_prob = probabilities[strike]['below']
            put_distance = current_price - strike
            put_premium_est = max(0.25, 5.0 * np.exp(-0.5 * (put_distance/10)**2))
            
            if put_itm_prob > 15:  # Only if reasonable probability
                put_ev = put_itm_prob/100 * max(0, strike - np.mean(final_prices[final_prices < strike])) - (100-put_itm_prob)/100 * put_premium_est
                strike_analysis.append({
                    'strike': f"SPXW250910P{strike}.0",
                    'type': 'PUT',
                    'strike_level': strike,
                    'distance': put_distance,
                    'probability': put_itm_prob,
                    'premium_est': put_premium_est,
                    'expected_value': put_ev,
                    'risk_reward': put_ev / put_premium_est if put_premium_est > 0 else 0
                })
    
    # Sort by expected value
    strike_analysis.sort(key=lambda x: x['expected_value'], reverse=True)
    
    # Display top 5
    print(f"TOP 5 BEST EXPECTED VALUE STRIKES:")
    print(f"{'Rank':<4} {'Strike':<20} {'Type':<4} {'Prob%':<6} {'Premium':<8} {'ExpVal':<6} {'R/R':<5}")
    print("-" * 65)
    
    for i, strike_data in enumerate(strike_analysis[:5], 1):
        print(f"{i:<4} {strike_data['strike']:<20} {strike_data['type']:<4} "
              f"{strike_data['probability']:<6.1f} ${strike_data['premium_est']:<7.2f} "
              f"{strike_data['expected_value']:<6.2f} {strike_data['risk_reward']:<5.2f}")
    
    # Detailed analysis of top 3
    print(f"\nDETAILED ANALYSIS - TOP 3:")
    for i, strike_data in enumerate(strike_analysis[:3], 1):
        print(f"\n{i}. {strike_data['strike']} ({strike_data['type']})")
        print(f"   Probability ITM: {strike_data['probability']:.1f}%")
        print(f"   Distance: {strike_data['distance']:+.2f} points")
        print(f"   Est. Premium: ${strike_data['premium_est']:.2f}")
        print(f"   Expected Value: ${strike_data['expected_value']:.2f}")
        print(f"   Risk/Reward: {strike_data['risk_reward']:.2f}")
        
        # Strategy recommendation
        if strike_data['type'] == 'PUT' and strike_data['probability'] > 50:
            print(f"   Strategy: HIGH PROBABILITY bearish play")
        elif strike_data['type'] == 'CALL' and strike_data['probability'] > 50:
            print(f"   Strategy: HIGH PROBABILITY bullish play")
        else:
            print(f"   Strategy: Moderate probability swing play")
    
    return strike_analysis[:5]

def run_full_monte_carlo():
    """Run complete Monte Carlo analysis"""
    
    # Get current SPX
    current_spx = get_current_spx()
    
    # Run Monte Carlo
    final_prices, probabilities = monte_carlo_0dte_analysis(current_spx)
    
    # Analyze best strikes
    top_strikes = analyze_top_strikes(current_spx, final_prices, probabilities)
    
    # Market context
    print(f"\nMARKET CONTEXT:")
    print(f"Current SPX: ${current_spx:.2f}")
    
    if current_spx <= 6542:
        print(f"⚠️  AT/BELOW 6542 quant support - bearish bias")
        print(f"   Best plays likely: PUT strikes")
        print(f"   Target: 6530-6535 breakdown")
    elif current_spx >= 6560:
        print(f"⚠️  AT/ABOVE 6560 reversal zone - fade rallies")  
        print(f"   Best plays likely: PUT strikes")
        print(f"   Target: Back to 6545-6550")
    else:
        print(f"📊 In 6542-6560 resistance zone")
        print(f"   Direction depends on key level breaks")
    
    print(f"\nRECOMMENDATION:")
    if top_strikes:
        best_strike = top_strikes[0]
        print(f"Primary: {best_strike['strike']}")
        print(f"Probability: {best_strike['probability']:.1f}%")
        print(f"Expected Value: ${best_strike['expected_value']:.2f}")
    
    return top_strikes

if __name__ == "__main__":
    top_strikes = run_full_monte_carlo()