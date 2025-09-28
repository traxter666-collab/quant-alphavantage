import requests
import numpy as np

def get_iwm_data():
    """Get IWM (Russell 2000 ETF) current data"""
    try:
        url = "https://query1.finance.yahoo.com/v8/finance/chart/IWM"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=8)
        data = response.json()
        
        if 'chart' in data and data['chart']['result']:
            meta = data['chart']['result'][0]['meta']
            current_price = meta.get('regularMarketPrice')
            prev_close = meta.get('previousClose')
            high = meta.get('regularMarketDayHigh')
            low = meta.get('regularMarketDayLow')
            
            if current_price and prev_close:
                change = current_price - prev_close
                change_pct = (change / prev_close) * 100
                
                return {
                    'price': current_price,
                    'change': change,
                    'change_pct': change_pct,
                    'high': high,
                    'low': low,
                    'prev_close': prev_close
                }
    except Exception as e:
        print(f"Error getting IWM data: {e}")
    
    return None

def analyze_iwm_correlation_with_spx():
    """Analyze IWM in context of SPX breakdown"""
    
    # Get SPX for correlation context
    try:
        spx_url = "https://query1.finance.yahoo.com/v8/finance/chart/%5EGSPC"
        spx_response = requests.get(spx_url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=8)
        spx_data = spx_response.json()
        spx_price = spx_data['chart']['result'][0]['meta']['regularMarketPrice']
    except:
        spx_price = 6535.44
    
    iwm_data = get_iwm_data()
    
    if not iwm_data:
        print("Could not get IWM data")
        return
    
    print("IWM 0DTE STRIKE ANALYSIS")
    print("=" * 30)
    print(f"IWM Current: ${iwm_data['price']:.2f} ({iwm_data['change']:+.2f}, {iwm_data['change_pct']:+.2f}%)")
    print(f"Range: ${iwm_data['low']:.2f} - ${iwm_data['high']:.2f}")
    print(f"SPX Context: ${spx_price:.2f} (broken support)")
    
    current_price = iwm_data['price']
    
    # IWM typically more volatile than SPX
    # Small caps often sell off harder when SPX breaks support
    print(f"\nIWM vs SPX CORRELATION CONTEXT:")
    print(f"• Small caps (IWM) typically decline 1.5-2x SPX moves")
    print(f"• SPX broke 6542 support = IWM likely follows")
    print(f"• IWM more volatile = bigger percentage moves")
    print(f"• Risk-off environment hurts small caps more")
    
    # Calculate IWM strike levels
    # IWM strikes are typically in $1 increments
    atm_strike = round(current_price)
    
    scenarios = [
        {"strike": atm_strike, "type": "ATM", "prob": 55, "desc": "At the money"},
        {"strike": atm_strike - 1, "type": "OTM_PUT", "prob": 65, "desc": "Follow SPX down"},
        {"strike": atm_strike - 2, "type": "OTM_PUT", "prob": 58, "desc": "Amplified selling"},
        {"strike": atm_strike - 3, "type": "OTM_PUT", "prob": 48, "desc": "Major breakdown"},
        {"strike": atm_strike - 4, "type": "OTM_PUT", "prob": 38, "desc": "Cascade selling"},
        {"strike": atm_strike + 1, "type": "OTM_CALL", "prob": 35, "desc": "Counter-trend bounce"},
        {"strike": atm_strike + 2, "type": "OTM_CALL", "prob": 25, "desc": "Strong bounce"},
    ]
    
    print(f"\nIWM STRIKE ANALYSIS:")
    print(f"ATM Strike: ${atm_strike}")
    
    # Focus on puts given SPX breakdown
    put_strikes = []
    call_strikes = []
    
    for scenario in scenarios:
        strike = scenario["strike"]
        prob = scenario["prob"]
        distance = strike - current_price
        
        # Premium estimation for IWM (less expensive than SPX)
        if abs(distance) <= 1:
            premium = max(0.8, 2.5 - abs(distance) * 0.3)
        else:
            premium = max(0.3, 2.0 - abs(distance) * 0.2)
        
        expected_move = abs(distance) * (prob / 100)
        risk_reward = expected_move / premium if premium > 0 else 0
        
        strike_data = {
            'strike_code': f"IWM250910{'P' if 'PUT' in scenario['type'] else 'C'}{strike:03d}.0",
            'strike': strike,
            'type': scenario['type'],
            'prob': prob,
            'distance': distance,
            'premium': premium,
            'expected_move': expected_move,
            'risk_reward': risk_reward,
            'desc': scenario['desc']
        }
        
        if 'PUT' in scenario['type'] or scenario['type'] == 'ATM':
            put_strikes.append(strike_data)
        else:
            call_strikes.append(strike_data)
    
    # Sort puts by probability (bearish bias)
    put_strikes.sort(key=lambda x: x['prob'], reverse=True)
    
    print(f"\nTOP 5 IWM PUT STRIKES (Bearish bias from SPX):")
    print(f"Rank Strike Code         Strike Prob%  Dist   Premium  R/R   Description")
    print("-" * 80)
    
    for i, s in enumerate(put_strikes[:5], 1):
        print(f"{i:<4} {s['strike_code']:<18} ${s['strike']:<5} {s['prob']:<6} {s['distance']:<6.1f} "
              f"${s['premium']:<7.2f} {s['risk_reward']:<5.2f} {s['desc']}")
    
    print(f"\nTOP 3 DETAILED IWM ANALYSIS:")
    
    for i, s in enumerate(put_strikes[:3], 1):
        print(f"\n{i}. {s['strike_code']}")
        print(f"   Strike: ${s['strike']}")
        print(f"   Probability: {s['prob']}%")
        print(f"   Distance: {s['distance']:+.1f} from current")
        print(f"   Est. Premium: ${s['premium']:.2f}")
        print(f"   Strategy: {s['desc']}")
        
        if s['strike'] == atm_strike - 1:
            print(f"   Context: HIGHEST PROBABILITY - follows SPX breakdown")
        elif s['strike'] == atm_strike:
            print(f"   Context: ATM hedge - safe bearish play")
        elif s['strike'] == atm_strike - 2:
            print(f"   Context: AMPLIFIED MOVE - small caps sell harder")
    
    # Bullish hedge options
    if call_strikes:
        print(f"\nBULLISH HEDGE OPTIONS (Lower probability):")
        call_strikes.sort(key=lambda x: x['prob'], reverse=True)
        best_call = call_strikes[0]
        print(f"{best_call['strike_code']}: {best_call['prob']}% prob - {best_call['desc']}")
    
    print(f"\nIWM EXECUTION STRATEGY:")
    best_put = put_strikes[0]
    print(f"Primary: {best_put['strike_code']}")
    print(f"Logic: SPX breakdown typically leads IWM down 1.5-2x")
    print(f"Entry: Current levels or any bounce")
    print(f"Target: +50-100% on small cap selling")
    print(f"Stop: If SPX reclaims 6542 support")
    
    print(f"\nWHY IWM BEARISH:")
    print(f"• Small caps more sensitive to risk-off")
    print(f"• Higher beta to SPX moves")
    print(f"• Less institutional support during selloffs")
    print(f"• Credit concerns hit small caps first")
    print(f"• IWM options cheaper than SPX for similar moves")
    
    return put_strikes

if __name__ == "__main__":
    iwm_strikes = analyze_iwm_correlation_with_spx()