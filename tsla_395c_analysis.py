import requests
import os
from datetime import datetime

def tsla_395c_performance():
    """TSLA 395C 9/12 performance analysis"""
    
    # Get current TSLA data
    api_key = 'ZFL38ZY98GSN7E1S'
    response = requests.get(f'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=TSLA&entitlement=realtime&apikey={api_key}')
    data = response.json()

    if 'Global Quote' in data:
        quote = data['Global Quote']
        current_price = float(quote['05. price'])
        change = float(quote['09. change'])
        change_pct = float(quote['10. change percent'].rstrip('%'))
        high = float(quote['03. high'])
        low = float(quote['04. low'])
        
        print(f'TSLA 395C 9/12 PERFORMANCE ANALYSIS')
        print(f'=' * 40)
        print(f'Current TSLA Price: ${current_price:.2f} ({change:+.2f}, {change_pct:+.1f}%)')
        print(f'Session Range: ${low:.2f} - ${high:.2f}')
        print()
        
        # 395 Call analysis
        strike = 395.0
        intrinsic_value = max(0, current_price - strike)
        
        print(f'395C CONTRACT STATUS:')
        print(f'Strike Price: ${strike}')
        print(f'Current Price: ${current_price:.2f}')
        print(f'Intrinsic Value: ${intrinsic_value:.2f}')
        
        if current_price > strike:
            print(f'Status: IN THE MONEY by ${current_price - strike:.2f}')
            profit_pct = ((current_price - strike) / strike) * 100
            print(f'Profit from Strike: {profit_pct:.1f}%')
        else:
            print(f'Status: OUT OF THE MONEY by ${strike - current_price:.2f}')
            print(f'Needs +${strike - current_price:.2f} to reach breakeven')
        
        print()
        print(f'PERFORMANCE METRICS:')
        print(f'Distance from Strike: {((current_price - strike) / strike * 100):+.1f}%')
        print(f'Moneyness: {current_price / strike:.3f}')
        
        # Time decay consideration (0DTE)
        print()
        print(f'0DTE CONSIDERATIONS:')
        print(f'Time Value: Minimal (expiring today)')
        print(f'Theta Decay: Maximum impact')
        print(f'Gamma Risk: Extreme near strike')
        
        if current_price > strike:
            print(f'Recommendation: PROFITABLE - Exercise or sell immediately')
            # Calculate expected profit for typical option premium
            print(f'Expected Value: ${intrinsic_value:.2f} per contract')
        else:
            print(f'Recommendation: WORTHLESS - Will expire OTM')
    else:
        print('Error retrieving TSLA data')

if __name__ == "__main__":
    tsla_395c_performance()