import os
import requests
import json
from datetime import datetime

def get_spx_open_range_analysis():
    """Get SPX open range analysis using Alphavantage data"""
    
    api_key = os.getenv('ALPHAVANTAGE_API_KEY', 'ZFL38ZY98GSN7E1S')
    base_url = "https://www.alphavantage.co/query"
    
    print("SPX 0DTE OPEN RANGE ANALYSIS - September 10, 2025")
    print("=" * 60)
    
    # Get SPY current quote
    print("Getting real-time SPY data...")
    spy_response = requests.get(f"{base_url}?function=GLOBAL_QUOTE&symbol=SPY&apikey={api_key}")
    spy_data = spy_response.json()
    
    if "Global Quote" not in spy_data:
        print(f"Error getting SPY data: {spy_data}")
        return
    
    spy_quote = spy_data["Global Quote"]
    spy_price = float(spy_quote["05. price"])
    spy_open = float(spy_quote["02. open"])
    spy_high = float(spy_quote["03. high"])
    spy_low = float(spy_quote["04. low"])
    spy_change = float(spy_quote["09. change"])
    spy_change_pct = float(spy_quote["10. change percent"].replace('%', ''))
    
    # Calculate SPX estimates
    spx_current = spy_price * 10
    spx_open = spy_open * 10
    spx_high = spy_high * 10
    spx_low = spy_low * 10
    
    # Get intraday 5min data for open range
    print("Getting 5-minute intraday data...")
    intraday_response = requests.get(f"{base_url}?function=TIME_SERIES_INTRADAY&symbol=SPY&interval=5min&apikey={api_key}")
    intraday_data = intraday_response.json()
    
    if "Time Series (5min)" not in intraday_data:
        print(f"Error getting intraday data: {intraday_data}")
        return
    
    time_series = intraday_data["Time Series (5min)"]
    timestamps = list(time_series.keys())[:12]  # First hour (12 x 5min bars)
    
    # Calculate open range (first 30-60 minutes)
    open_range_high = spx_open
    open_range_low = spx_open
    
    for timestamp in timestamps:
        bar = time_series[timestamp]
        high = float(bar["2. high"]) * 10
        low = float(bar["3. low"]) * 10
        
        if high > open_range_high:
            open_range_high = high
        if low < open_range_low:
            open_range_low = low
    
    open_range_size = open_range_high - open_range_low
    
    # Get RSI data
    print("Getting RSI indicators...")
    rsi_response = requests.get(f"{base_url}?function=RSI&symbol=SPY&interval=5min&time_period=14&series_type=close&apikey={api_key}")
    rsi_data = rsi_response.json()
    
    current_rsi = "N/A"
    if "Technical Analysis: RSI" in rsi_data:
        rsi_series = rsi_data["Technical Analysis: RSI"]
        latest_rsi_timestamp = list(rsi_series.keys())[0]
        current_rsi = float(rsi_series[latest_rsi_timestamp]["RSI"])
    
    # Display analysis
    print(f"\nCURRENT MARKET DATA (as of {datetime.now().strftime('%H:%M:%S')} PT):")
    print(f"SPY: ${spy_price:.2f} ({spy_change:+.2f}, {spy_change_pct:+.2f}%)")
    print(f"SPX Estimate: ${spx_current:.2f}")
    print(f"SPY Range: ${spy_low:.2f} - ${spy_high:.2f}")
    print(f"SPX Range: ${spx_low:.2f} - ${spx_high:.2f}")
    
    print(f"\nOPEN RANGE ANALYSIS:")
    print(f"SPX Open: ${spx_open:.2f}")
    print(f"Open Range High: ${spx_high:.2f}")
    print(f"Open Range Low: ${spx_low:.2f}")
    print(f"Open Range Size: {open_range_size:.2f} points")
    print(f"Current vs Open: {spx_current - spx_open:+.2f} points")
    
    if current_rsi != "N/A":
        print(f"RSI (5min): {current_rsi:.1f}")
        if current_rsi > 70:
            rsi_signal = "OVERBOUGHT - Consider puts"
        elif current_rsi < 30:
            rsi_signal = "OVERSOLD - Consider calls"
        else:
            rsi_signal = "NEUTRAL"
        print(f"RSI Signal: {rsi_signal}")
    
    # Generate trading opportunities
    print(f"\n0DTE SCALP OPPORTUNITIES:")
    
    # Breakout levels
    or_high_break = spx_high + 5
    or_low_break = spx_low - 5
    
    print(f"\nBREAKOUT PLAYS:")
    if spx_current > spx_open:
        # Bullish bias
        call_strike = int((spx_current + 10) / 5) * 5  # Round to nearest 5
        put_strike = int((spx_current - 10) / 5) * 5
        
        print(f"CALLS - Bullish continuation above {or_high_break:.0f}")
        print(f"Strike: {call_strike} calls @ est. $2.50-4.00")
        print(f"Target: +50-100% if breaks {or_high_break:.0f}")
        print(f"Stop: -50% or below {spx_current - 8:.0f}")
        
        print(f"\nPUTS - Reversal play below {or_low_break:.0f}")
        print(f"Strike: {put_strike} puts @ est. $1.50-3.00")
        print(f"Target: +100-200% if breaks {or_low_break:.0f}")
        print(f"Stop: -50% or above {spx_current + 5:.0f}")
        
    else:
        # Bearish bias
        put_strike = int((spx_current - 10) / 5) * 5
        call_strike = int((spx_current + 10) / 5) * 5
        
        print(f"PUTS - Bearish continuation below {or_low_break:.0f}")
        print(f"Strike: {put_strike} puts @ est. $2.50-4.00")
        print(f"Target: +50-100% if breaks {or_low_break:.0f}")
        print(f"Stop: -50% or above {spx_current + 8:.0f}")
        
        print(f"\nCALLS - Reversal play above {or_high_break:.0f}")
        print(f"Strike: {call_strike} calls @ est. $1.50-3.00") 
        print(f"Target: +100-200% if breaks {or_high_break:.0f}")
        print(f"Stop: -50% or below {spx_current - 5:.0f}")
    
    # Generate TradingView codes
    print(f"\nTRADINGVIEW CODES:")
    date_str = "250910"  # September 10, 2025
    if spx_current > spx_open:
        print(f"Primary: SPXW{date_str}C{call_strike:.0f}.0")
        print(f"Alt: SPXW{date_str}P{put_strike:.0f}.0")
    else:
        print(f"Primary: SPXW{date_str}P{put_strike:.0f}.0")
        print(f"Alt: SPXW{date_str}C{call_strike:.0f}.0")
    
    print(f"\nKEY LEVELS TO WATCH:")
    print(f"Open Range Breakout: {or_high_break:.0f}")
    print(f"Open Range Breakdown: {or_low_break:.0f}")
    print(f"VWAP: ~{(spx_high + spx_low) / 2:.0f} (estimated)")
    print(f"Session High: {spx_high:.2f}")
    print(f"Session Low: {spx_low:.2f}")

if __name__ == "__main__":
    get_spx_open_range_analysis()