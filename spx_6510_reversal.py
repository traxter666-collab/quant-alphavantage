import os
import requests
from datetime import datetime

def analyze_spx_6510_reversal():
    """Analyze SPX 6510 level for potential reversal signals"""
    
    api_key = os.getenv('ALPHAVANTAGE_API_KEY', 'ZFL38ZY98GSN7E1S')
    base_url = "https://www.alphavantage.co/query"
    
    print("SPX 6510 REVERSAL ANALYSIS")
    print("=" * 40)
    
    # Get current SPY data
    spy_response = requests.get(f"{base_url}?function=GLOBAL_QUOTE&symbol=SPY&apikey={api_key}")
    spy_data = spy_response.json()
    
    if "Global Quote" not in spy_data:
        print("Error getting data")
        return
    
    spy_quote = spy_data["Global Quote"]
    spy_price = float(spy_quote["05. price"])
    spy_high = float(spy_quote["03. high"])
    spy_change = float(spy_quote["09. change"])
    
    spx_current = spy_price * 10
    spx_high = spy_high * 10
    
    # Distance from 6510
    distance_to_6510 = 6510 - spx_current
    
    print(f"SPX Current: ${spx_current:.2f}")
    print(f"Distance to 6510: {distance_to_6510:+.2f} points")
    print(f"Session High: ${spx_high:.2f}")
    
    # Get recent 1min bars for momentum
    intraday_response = requests.get(f"{base_url}?function=TIME_SERIES_INTRADAY&symbol=SPY&interval=1min&apikey={api_key}")
    intraday_data = intraday_response.json()
    
    momentum = "UNKNOWN"
    if "Time Series (1min)" in intraday_data:
        time_series = intraday_data["Time Series (1min)"]
        recent_bars = list(time_series.keys())[:5]  # Last 5 minutes
        
        prices = []
        for timestamp in recent_bars:
            close = float(time_series[timestamp]["4. close"]) * 10
            prices.append(close)
        
        if len(prices) >= 3:
            if prices[0] > prices[1] > prices[2]:  # Recent decline
                momentum = "DECLINING"
            elif prices[0] < prices[1] < prices[2]:  # Recent rally
                momentum = "RALLYING" 
            else:
                momentum = "CHOPPY"
    
    print(f"Recent Momentum: {momentum}")
    
    # Reversal analysis
    print(f"\n6510 REVERSAL SCENARIOS:")
    
    if spx_current >= 6505:  # Near 6510
        print("BEARISH REVERSAL SETUP (Near 6510):")
        print(f"Entry: 6505-6510 puts if rejected at 6510")
        print(f"Target 1: 6495 (-15 pts)")
        print(f"Target 2: 6485 (-25 pts)") 
        print(f"Stop: Above 6515 (+5 pts)")
        print(f"Risk/Reward: 1:3 to 1:5")
        
        # Put options
        put_strike_1 = 6500
        put_strike_2 = 6495
        
        print(f"\nPUT OPTIONS:")
        print(f"SPXW250910P{put_strike_1}.0 - Conservative")
        print(f"SPXW250910P{put_strike_2}.0 - Aggressive")
        
    elif spx_current < 6505:  # Below 6510
        print("FAILED BREAKOUT SETUP:")
        print(f"Scenario: SPX failed to hold above 6505-6510")
        print(f"Bearish continuation expected")
        print(f"Target 1: 6490 (-{6490-spx_current:.0f} pts)")
        print(f"Target 2: 6475 (-{6475-spx_current:.0f} pts)")
        
        put_strike = int((spx_current - 5) / 5) * 5
        print(f"\nPUT ENTRY:")
        print(f"SPXW250910P{put_strike}.0 - Failed breakout play")
    
    # Reversal signals to watch
    print(f"\nREVERSAL SIGNALS TO WATCH:")
    print(f"• Rejection at 6510 with long upper wick")
    print(f"• Volume spike on approach to 6510")
    print(f"• RSI divergence if making new highs")
    print(f"• Failed to hold above 6505 after touching 6510")
    
    # Risk management
    print(f"\nRISK MANAGEMENT:")
    print(f"• Position size: 1-2% max (high volatility)")
    print(f"• Stop loss: Tight (5-8 points above entry)")
    print(f"• Time decay: Exit by 2:30 PM if flat")
    print(f"• Take profits: 50% at first target, let rest run")

if __name__ == "__main__":
    analyze_spx_6510_reversal()