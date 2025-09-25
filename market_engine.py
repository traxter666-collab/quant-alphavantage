#!/usr/bin/env python3
"""
Simplified Market Analysis Engine - Fresh data, zero context loss
Usage: python market_engine.py [SYMBOL] [STRIKE][C/P] [ENTRY]
Examples:
  python market_engine.py SPY 663C 2.50
  python market_engine.py AAPL 230P 3.20
  python market_engine.py spx 6635C
"""

import os
import sys
import requests
import json
from datetime import datetime

API_KEY = os.getenv('ALPHAVANTAGE_API_KEY', 'ZFL38ZY98GSN7E1S')

def get_fresh_price(symbol):
    """Get fresh real-time price from AlphaVantage"""
    try:
        url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&entitlement=realtime&apikey={API_KEY}"
        response = requests.get(url, timeout=10)
        data = response.json()

        if "Global Quote" in data:
            price = float(data["Global Quote"]["05. price"])
            change = float(data["Global Quote"]["09. change"])
            change_pct = data["Global Quote"]["10. change percent"].rstrip('%')

            return {
                'symbol': symbol,
                'price': price,
                'change': change,
                'change_pct': change_pct,
                'timestamp': datetime.now().isoformat(),
                'success': True
            }
    except Exception as e:
        print(f"ERROR getting {symbol}: {e}")

    return {'success': False}

def get_spx_price():
    """Get accurate SPX price from SPXW real-time options using put-call parity"""
    try:
        # Get SPXW options data
        url = f"https://www.alphavantage.co/query?function=REALTIME_OPTIONS&symbol=SPXW&entitlement=realtime&apikey={API_KEY}"
        response = requests.get(url, timeout=10)
        data = response.json()

        if "data" in data and data["data"]:
            options = data["data"]

            # Find ATM options around current market level for accuracy
            target_strikes = [6625, 6630, 6635, 6640, 6645]

            for strike in target_strikes:
                call_data = None
                put_data = None

                # Find matching call and put for this strike (today's date)
                today = datetime.now().strftime("%Y-%m-%d")
                for option in options:
                    if option.get("expiration") == today and float(option.get("strike", 0)) == strike:
                        if option.get("type") == "call":
                            call_data = option
                        elif option.get("type") == "put":
                            put_data = option

                # If we have both call and put, calculate SPX via put-call parity
                if call_data and put_data:
                    try:
                        call_bid = float(call_data.get("bid", 0))
                        put_bid = float(put_data.get("bid", 0))

                        if call_bid > 0 and put_bid >= 0:
                            # SPX = Call_bid - Put_bid + Strike
                            spx_price = call_bid - put_bid + strike

                            return {
                                'symbol': 'SPX',
                                'price': spx_price,
                                'change': 0,  # Will calculate separately if needed
                                'change_pct': "0.00%",
                                'timestamp': datetime.now().isoformat(),
                                'source': f'SPXW {strike} options put-call parity',
                                'success': True
                            }
                    except (ValueError, TypeError):
                        continue

        print("SPXW options parsing failed, using fallback")
    except Exception as e:
        print(f"SPXW options failed: {e}")

    # Fallback to SPY conversion if SPXW fails
    spy_data = get_fresh_price('SPY')
    if spy_data['success']:
        spx_price = spy_data['price'] * 10
        return {
            'symbol': 'SPX',
            'price': spx_price,
            'change': spy_data['change'] * 10,
            'change_pct': spy_data['change_pct'],
            'timestamp': spy_data['timestamp'],
            'source': 'SPY conversion fallback',
            'success': True
        }
    return {'success': False}

def analyze_option(symbol, strike, option_type, entry_price=None):
    """Analyze option position"""
    # Get current price
    if symbol.upper() == 'SPX':
        current_data = get_spx_price()
        current_price = current_data['price']
    else:
        current_data = get_fresh_price(symbol)
        current_price = current_data['price']

    if not current_data['success']:
        return f"Failed to get {symbol} price"

    # Calculate distance
    if option_type.upper() == 'C':
        distance = current_price - strike
        itm = distance > 0
        status = "ITM" if itm else "OTM"
    else:  # Put
        distance = strike - current_price
        itm = distance > 0
        status = "ITM" if itm else "OTM"

    # Calculate intrinsic value
    intrinsic = max(0, distance)

    result = f"""
{symbol.upper()} OPTION ANALYSIS - {datetime.now().strftime('%H:%M:%S')}
{'='*50}
Current {symbol.upper()}: ${current_price:.2f} ({current_data['change']:+.2f}, {current_data['change_pct']}%)

{strike}{option_type.upper()} Analysis:
Strike: ${strike:.2f}
Status: {status}
Distance: {distance:+.2f} points
Intrinsic: ${intrinsic:.2f}
"""

    if entry_price:
        pnl = intrinsic - entry_price
        pnl_pct = (pnl / entry_price) * 100 if entry_price > 0 else 0
        result += f"""
Entry Price: ${entry_price:.2f}
Current Value: ${intrinsic:.2f}
P&L: ${pnl:+.2f} ({pnl_pct:+.1f}%)
"""

    # Quick recommendation
    if symbol.upper() == 'SPX':
        move_pct = abs(distance) / current_price * 100
        if move_pct < 0.2:
            rec = "EXCELLENT - Very close to money"
        elif move_pct < 0.5:
            rec = "GOOD - Reasonable move needed"
        elif move_pct < 1.0:
            rec = "MODERATE - Significant move required"
        else:
            rec = "CHALLENGING - Large move needed"

        result += f"\nMove needed: {abs(distance):.0f} points ({move_pct:.2f}%)\nRecommendation: {rec}"

    return result

def analyze_stock(symbol):
    """Simple stock analysis with key levels"""
    data = get_fresh_price(symbol)
    if not data['success']:
        return f"Failed to get {symbol} data"

    result = f"""
{symbol.upper()} STOCK ANALYSIS - {datetime.now().strftime('%H:%M:%S')}
{'='*40}
Price: ${data['price']:.2f}
Change: {data['change']:+.2f} ({data['change_pct']}%)

Key Levels:
Support: ${data['price'] * 0.98:.2f} (-2%)
Resistance: ${data['price'] * 1.02:.2f} (+2%)

Status: {"BULLISH" if float(data['change']) > 0 else "BEARISH" if float(data['change']) < 0 else "FLAT"}
"""
    return result

def parse_option_string(option_str):
    """Parse option string like '663C' or '230P'"""
    option_str = option_str.upper()
    if option_str.endswith('C') or option_str.endswith('P'):
        option_type = option_str[-1]
        strike = float(option_str[:-1])
        return strike, option_type
    return None, None

def get_market_status():
    """Get current market status and time to close"""
    from datetime import datetime, time

    now = datetime.now()
    current_time = now.time()

    # Market hours: 9:30 AM - 4:00 PM ET
    market_open = time(9, 30)
    market_close = time(16, 0)  # 4:00 PM ET

    if current_time < market_open:
        return "PRE_MARKET", f"Opens at 9:30 AM ET"
    elif current_time > market_close:
        return "CLOSED", f"Closed at 4:00 PM ET"
    else:
        # Calculate time to close
        close_datetime = now.replace(hour=16, minute=0, second=0, microsecond=0)
        time_remaining = close_datetime - now
        minutes_left = int(time_remaining.total_seconds() / 60)
        return "OPEN", f"{minutes_left} minutes to close (4:00 PM ET)"

def main():
    if len(sys.argv) < 2:
        print("Usage: python market_engine.py [SYMBOL] [STRIKE][C/P] [ENTRY]")
        print("Examples:")
        print("  python market_engine.py AAPL")
        print("  python market_engine.py SPY 663C")
        print("  python market_engine.py SPX 6635C 2.50")
        return

    symbol = sys.argv[1].upper()

    # Get market status
    market_status, status_msg = get_market_status()
    print(f"Market Status: {market_status} - {status_msg}")
    print()

    # If only symbol provided, do stock analysis
    if len(sys.argv) == 2:
        if symbol == 'SPX':
            spx_data = get_spx_price()
            if spx_data['success']:
                print(f"""
SPX ANALYSIS - {datetime.now().strftime('%H:%M:%S')}
{'='*40}
SPX: ${spx_data['price']:.2f}
Change: {spx_data['change']:+.2f} ({spx_data['change_pct']})

Key SPX Levels:
Support: ${spx_data['price'] - 50:.0f}
Resistance: ${spx_data['price'] + 50:.0f}
""")
        else:
            print(analyze_stock(symbol))
        return

    # Parse option
    option_str = sys.argv[2]
    strike, option_type = parse_option_string(option_str)

    if not strike or not option_type:
        print(f"Invalid option format: {option_str}")
        print("Use format like: 663C or 230P")
        return

    # Get entry price if provided
    entry_price = None
    if len(sys.argv) > 3:
        try:
            entry_price = float(sys.argv[3])
        except:
            print(f"Invalid entry price: {sys.argv[3]}")
            return

    # Analyze option
    result = analyze_option(symbol, strike, option_type, entry_price)
    print(result)

    # Save to cache for context
    try:
        os.makedirs('.spx', exist_ok=True)
        with open('.spx/last_analysis.json', 'w') as f:
            json.dump({
                'symbol': symbol,
                'strike': strike,
                'option_type': option_type,
                'entry_price': entry_price,
                'timestamp': datetime.now().isoformat(),
                'analysis': result
            }, f)
    except:
        pass  # Don't fail on cache issues

if __name__ == "__main__":
    main()