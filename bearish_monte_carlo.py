import numpy as np
import os
import requests

def get_current_spx():
    """Get current SPX price"""
    try:
        url = "https://query1.finance.yahoo.com/v8/finance/chart/%5EGSPC"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=8)
        data = response.json()
        
        if 'chart' in data and data['chart']['result']:
            meta = data['chart']['result'][0]['meta']
            return meta.get('regularMarketPrice', 6541.54)
    except:
        pass
    return 6541.54

def bearish_monte_carlo_analysis(current_price, hours_to_expiry=4.5):
    """Monte Carlo with bearish bias for support breakdown scenario"""
    
    print("BEARISH BIAS MONTE CARLO - SPX 0DTE")
    print("=" * 45)
    print(f"Current SPX: ${current_price:.2f}")
    print(f"Critical Support: 6542 (BROKEN/BREAKING)")
    
    # Enhanced volatility for breakdown scenario
    base_vol = 0.18  # 18% annual
    breakdown_vol_multiplier = 1.5  # 50% higher vol on breakdown
    annual_vol = base_vol * breakdown_vol_multiplier
    
    daily_vol = annual_vol / np.sqrt(252)
    hourly_vol = daily_vol / np.sqrt(6.5)
    vol_for_period = hourly_vol * np.sqrt(hours_to_expiry)
    
    # Bearish drift adjustment
    bearish_drift = -0.003  # -0.3% negative drift for support breakdown
    
    print(f"Enhanced volatility: {annual_vol*100:.1f}% (breakdown scenario)")
    print(f"Bearish drift: {bearish_drift*100:.1f}%")
    
    # Monte Carlo simulation
    n_simulations = 100000
    np.random.seed(42)
    
    # Generate bearish-biased price movements
    random_moves = np.random.normal(bearish_drift, vol_for_period, n_simulations)
    final_prices = current_price * np.exp(random_moves)
    
    # Calculate statistics
    mean_price = np.mean(final_prices)
    std_price = np.std(final_prices)
    
    print(f"\nBEARISH MONTE CARLO RESULTS ({n_simulations:,} simulations):")
    print(f"Expected price: ${mean_price:.2f}")
    print(f"Expected move: {mean_price - current_price:+.2f} points")
    print(f"Standard deviation: ${std_price:.2f}")
    
    # Key bearish probability levels
    bearish_levels = [
        (6540, "Below 6540"),
        (6535, "Below 6535"), 
        (6530, "Below 6530"),
        (6525, "Below 6525"),
        (6520, "Below 6520"),
        (6515, "Below 6515"),
        (6510, "Below 6510"),
        (6500, "Below 6500"),
        (6498, "Below 6498 (strong support)")
    ]
    
    print(f"\nBEARISH PROBABILITY ANALYSIS:")
    probabilities = {}
    for level, desc in bearish_levels:
        prob_below = (final_prices < level).mean() * 100
        prob_above = 100 - prob_below
        probabilities[level] = {'above': prob_above, 'below': prob_below}
        print(f"{desc}: {prob_below:.1f}% | Above {level}: {prob_above:.1f}%")
    
    return final_prices, probabilities

def analyze_top_bearish_strikes(current_price, probabilities):
    """Analyze top 5 BEARISH strike opportunities"""
    
    print(f"\nTOP 5 BEARISH PUT STRIKES:")
    print("=" * 35)
    
    put_analysis = []
    
    # Focus on PUT strikes for bearish plays
    strikes_to_analyze = [6540, 6535, 6530, 6525, 6520, 6515, 6510, 6505, 6500, 6498]
    
    for strike in strikes_to_analyze:
        if strike in probabilities:
            # PUT analysis (bearish)
            put_itm_prob = probabilities[strike]['below']
            put_distance = current_price - strike
            
            # Premium estimation based on distance and probability
            if put_distance <= 0:  # OTM puts
                put_premium_est = max(0.5, 3.0 - abs(put_distance) * 0.2)
            else:  # ITM puts
                put_premium_est = put_distance + max(1.0, 3.0 - put_distance * 0.1)
            
            # Expected value calculation
            if put_itm_prob > 20:  # Reasonable probability threshold
                avg_itm_value = max(0, strike - np.mean([p for p in np.random.normal(current_price - 10, 15, 10000) if p < strike]))
                put_ev = (put_itm_prob/100 * avg_itm_value) - ((100-put_itm_prob)/100 * put_premium_est)
                
                put_analysis.append({
                    'strike': f"SPXW250910P{strike}.0",
                    'strike_level': strike,
                    'distance': put_distance,
                    'probability': put_itm_prob,
                    'premium_est': put_premium_est,
                    'expected_value': put_ev,
                    'risk_reward': put_ev / put_premium_est if put_premium_est > 0 else 0
                })
    
    # Sort by probability ITM (bearish bias)
    put_analysis.sort(key=lambda x: x['probability'], reverse=True)
    
    # Display top 5
    print(f"{'Rank':<4} {'Strike':<18} {'Prob%':<6} {'Dist':<6} {'Premium':<8} {'ExpVal':<6} {'R/R':<5}")
    print("-" * 60)
    
    for i, strike_data in enumerate(put_analysis[:5], 1):
        print(f"{i:<4} {strike_data['strike']:<18} {strike_data['probability']:<6.1f} "
              f"{strike_data['distance']:<6.1f} ${strike_data['premium_est']:<7.2f} "
              f"{strike_data['expected_value']:<6.2f} {strike_data['risk_reward']:<5.2f}")
    
    # Detailed analysis
    print(f"\nDETAILED BEARISH ANALYSIS:")
    for i, strike_data in enumerate(put_analysis[:3], 1):
        print(f"\n{i}. {strike_data['strike']}")
        print(f"   Probability ITM: {strike_data['probability']:.1f}%")
        print(f"   Distance: {strike_data['distance']:+.1f} points from current")
        print(f"   Est. Premium: ${strike_data['premium_est']:.2f}")
        print(f"   Expected Value: ${strike_data['expected_value']:.2f}")
        
        # Strategy context
        if strike_data['probability'] > 60:
            strategy = "HIGH CONVICTION bearish play"
        elif strike_data['probability'] > 45:
            strategy = "SOLID bearish probability"  
        else:
            strategy = "Speculative bearish play"
        print(f"   Strategy: {strategy}")
        
        # Target analysis
        if strike_data['strike_level'] == 6540:
            print(f"   Context: First support break target")
        elif strike_data['strike_level'] == 6535:
            print(f"   Context: Next technical support level")
        elif strike_data['strike_level'] == 6530:
            print(f"   Context: Major breakdown continuation")
        elif strike_data['strike_level'] == 6498:
            print(f"   Context: Strong quant support test")
    
    return put_analysis[:5]

def run_bearish_analysis():
    """Run complete bearish Monte Carlo analysis"""
    
    current_spx = get_current_spx()
    
    # Bearish context
    print(f"BEARISH SETUP CONTEXT:")
    print(f"- SPX at/below 6542 quant support")
    print(f"- Multiple support tests = eventual break")  
    print(f"- 0DTE momentum accelerates moves")
    print(f"- Next targets: 6535 → 6530 → 6520 → 6498")
    print()
    
    # Run bearish Monte Carlo
    final_prices, probabilities = bearish_monte_carlo_analysis(current_spx)
    
    # Analyze best bearish strikes
    top_puts = analyze_top_bearish_strikes(current_spx, probabilities)
    
    print(f"\nBEARISH TRADE PLAN:")
    if top_puts:
        best_put = top_puts[0]
        print(f"Primary: {best_put['strike']}")
        print(f"Probability: {best_put['probability']:.1f}%")
        print(f"Expected Value: ${best_put['expected_value']:.2f}")
        
        print(f"\nEXECUTION PLAN:")
        print(f"Entry: On any bounce toward 6543-6545")
        print(f"Target 1: 6535 ({6535 - current_spx:.0f} point move)")
        print(f"Target 2: 6530 ({6530 - current_spx:.0f} point move)")
        print(f"Stop: Above 6545 (failed breakdown)")
        print(f"Time: Exit by 2:30 PM if not moving")
    
    return top_puts

if __name__ == "__main__":
    top_puts = run_bearish_analysis()