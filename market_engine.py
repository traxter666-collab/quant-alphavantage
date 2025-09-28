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

def analyze_multi_strikes(symbol, start_strike, end_strike, option_type):
    """Analyze multiple strikes in a range"""
    if symbol.upper() != 'SPX':
        return "Multi-strike analysis currently supports SPX only"

    current_data = get_spx_price()
    if not current_data['success']:
        return "Failed to get SPX price"

    current_price = current_data['price']
    results = []

    print(f"\nMULTI-STRIKE ANALYSIS - SPX: ${current_price:.2f}")
    print("=" * 60)

    # Generate strikes in 5-point increments
    strikes = list(range(int(start_strike), int(end_strike) + 5, 5))

    for strike in strikes:
        if option_type.upper() == 'C':
            distance = current_price - strike
            itm = distance > 0
            status = "ITM" if itm else "OTM"
        else:  # Put
            distance = strike - current_price
            itm = distance > 0
            status = "ITM" if itm else "OTM"

        intrinsic = max(0, distance)
        move_needed = abs(distance) if not itm else 0
        move_pct = (move_needed / current_price) * 100 if move_needed > 0 else 0

        # Probability assessment
        if move_pct < 0.05:
            probability = "EXCELLENT"
        elif move_pct < 0.15:
            probability = "VERY GOOD"
        elif move_pct < 0.3:
            probability = "GOOD"
        elif move_pct < 0.5:
            probability = "MODERATE"
        else:
            probability = "LOW"

        results.append({
            'strike': strike,
            'distance': distance,
            'status': status,
            'intrinsic': intrinsic,
            'move_needed': move_needed,
            'move_pct': move_pct,
            'probability': probability
        })

        print(f"{strike}{option_type.upper()}: {status} by ${abs(distance):.1f} | "
              f"Move: {move_needed:.1f}pts ({move_pct:.2f}%) | {probability}")

    # Find best opportunities
    if option_type.upper() == 'C':
        best = min([r for r in results if not r['status'] == 'ITM'],
                  key=lambda x: x['move_needed'], default=None)
    else:
        best = min([r for r in results if not r['status'] == 'ITM'],
                  key=lambda x: x['move_needed'], default=None)

    if best:
        print(f"\n🎯 BEST OPPORTUNITY: {best['strike']}{option_type.upper()}")
        print(f"   Distance: {best['move_needed']:.1f} points ({best['move_pct']:.2f}%)")
        print(f"   Probability: {best['probability']}")

    return results

def detect_put_walls():
    """Detect potential put/call walls from SPXW options data"""
    try:
        url = f"https://www.alphavantage.co/query?function=REALTIME_OPTIONS&symbol=SPXW&entitlement=realtime&apikey={API_KEY}"
        response = requests.get(url, timeout=10)
        data = response.json()

        if "data" not in data:
            return "Unable to get options data for wall detection"

        options = data["data"]
        today = datetime.now().strftime("%Y-%m-%d")

        # Aggregate open interest by strike
        strike_oi = {}

        for option in options:
            if option.get("expiration") == today:
                strike = float(option.get("strike", 0))
                oi = int(option.get("open_interest", 0))
                option_type = option.get("type", "")

                if 6500 <= strike <= 6700:  # Focus on relevant range
                    key = f"{int(strike)}"
                    if key not in strike_oi:
                        strike_oi[key] = {"calls": 0, "puts": 0, "strike": strike}

                    if option_type == "call":
                        strike_oi[key]["calls"] += oi
                    elif option_type == "put":
                        strike_oi[key]["puts"] += oi

        if not strike_oi:
            return "No options data found for wall detection"

        # Calculate potential walls
        print(f"\nPUT/CALL WALL DETECTION")
        print("=" * 40)

        walls = []
        for strike_key, data in strike_oi.items():
            strike = data["strike"]
            calls = data["calls"]
            puts = data["puts"]
            total_oi = calls + puts

            if total_oi > 1000:  # Significant open interest
                wall_type = "CALL WALL" if calls > puts * 2 else "PUT WALL" if puts > calls * 2 else "MIXED"

                walls.append({
                    "strike": strike,
                    "calls": calls,
                    "puts": puts,
                    "total": total_oi,
                    "type": wall_type
                })

        # Sort by total open interest
        walls.sort(key=lambda x: x["total"], reverse=True)

        current_spx = get_spx_price()["price"]

        for wall in walls[:10]:  # Top 10 walls
            distance = current_spx - wall["strike"]
            print(f"{int(wall['strike'])}: {wall['type']} | "
                  f"C:{wall['calls']:,} P:{wall['puts']:,} | "
                  f"Total:{wall['total']:,} | {distance:+.0f}pts")

        # Identify critical walls
        critical_walls = [w for w in walls if w["total"] > 5000]

        if critical_walls:
            print(f"\n🚨 CRITICAL WALLS (>5K OI):")
            for wall in critical_walls:
                distance = current_spx - wall["strike"]
                print(f"   {int(wall['strike'])}: {wall['type']} - {wall['total']:,} contracts ({distance:+.0f}pts)")

        return walls

    except Exception as e:
        return f"Wall detection failed: {e}"

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

def get_news_sentiment(symbol=None, search_terms=None, limit=50):
    """Get news sentiment for stocks - enhanced for NAK/Northern Dynasty"""
    try:
        # Try multiple approaches for NAK
        if symbol and symbol.upper() == 'NAK':
            print("Searching for Northern Dynasty Minerals (NAK) news...")
            # Try mining/financial sector news first
            urls_to_try = [
                f"https://www.alphavantage.co/query?function=NEWS_SENTIMENT&topics=financial_markets&limit={limit}&apikey={API_KEY}",
                f"https://www.alphavantage.co/query?function=NEWS_SENTIMENT&topics=energy_transportation&limit={limit}&apikey={API_KEY}",
                f"https://www.alphavantage.co/query?function=NEWS_SENTIMENT&limit={limit}&apikey={API_KEY}"
            ]
        else:
            # Standard approach for other stocks
            if search_terms:
                urls_to_try = [f"https://www.alphavantage.co/query?function=NEWS_SENTIMENT&keywords={search_terms}&limit={limit}&apikey={API_KEY}"]
            else:
                urls_to_try = [f"https://www.alphavantage.co/query?function=NEWS_SENTIMENT&topics=financial_markets&limit={limit}&apikey={API_KEY}"]

        all_relevant_news = []

        for url in urls_to_try:
            try:
                response = requests.get(url, timeout=15)
                data = response.json()

                if "Error Message" in data or "Note" in data:
                    print(f"API Issue with this search: {data}")
                    continue

                if "feed" in data:
                    all_news = data["feed"]

                    if symbol:
                        # Enhanced filtering for NAK/Northern Dynasty
                        if symbol.upper() == 'NAK':
                            search_keywords = ['NAK', 'NORTHERN DYNASTY', 'PEBBLE', 'ALASKA', 'MINING', 'COPPER', 'GOLD']
                        else:
                            search_keywords = [symbol.upper()]

                        for article in all_news:
                            title_text = article.get("title", "").upper()
                            summary_text = article.get("summary", "").upper()

                            # Check if any keyword appears in title or summary
                            if any(keyword in title_text or keyword in summary_text
                                  for keyword in search_keywords):
                                all_relevant_news.append(article)
                    else:
                        all_relevant_news.extend(all_news[:limit])

                    # If we found relevant news, we can break
                    if all_relevant_news and symbol:
                        break

            except Exception as e:
                print(f"Error with one search attempt: {e}")
                continue

        if all_relevant_news:
            print(f"Found {len(all_relevant_news)} relevant articles for {symbol}")
            # Remove duplicates based on title
            seen_titles = set()
            unique_articles = []
            for article in all_relevant_news:
                title = article.get('title', '')
                if title not in seen_titles:
                    seen_titles.add(title)
                    unique_articles.append(article)

            return unique_articles[:10]  # Return top 10
        else:
            print(f"No specific news found for {symbol}. Trying general market news...")
            # Fallback to general news
            url = f"https://www.alphavantage.co/query?function=NEWS_SENTIMENT&topics=financial_markets&limit=10&apikey={API_KEY}"
            response = requests.get(url, timeout=15)
            data = response.json()

            if "feed" in data:
                return data["feed"][:5]

            return None

    except Exception as e:
        print(f"NEWS_SENTIMENT error: {e}")
        return None

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
        print("Usage: python market_engine.py [COMMAND]")
        print("Examples:")
        print("  python market_engine.py SPX                    # Current SPX level")
        print("  python market_engine.py SPX 6635C 2.50         # Single option")
        print("  python market_engine.py range 6600-6650 C      # Multi-strike calls")
        print("  python market_engine.py range 6580-6620 P      # Multi-strike puts")
        print("  python market_engine.py walls                  # Put/call wall detection")
        print("  python market_engine.py news NAK               # News analysis for NAK")
        print("  python market_engine.py AAPL                   # Any stock")
        return

    command = sys.argv[1].upper()

    # Get market status
    market_status, status_msg = get_market_status()
    print(f"Market Status: {market_status} - {status_msg}")
    print()

    # Handle special commands
    if command == "NEWS" and len(sys.argv) >= 3:
        # News sentiment analysis: news NAK
        symbol = sys.argv[2].upper()
        print(f"\nNEWS SENTIMENT ANALYSIS - {symbol}")
        print("=" * 50)

        news_articles = get_news_sentiment(symbol)
        if news_articles:
            for i, article in enumerate(news_articles[:10], 1):
                title = article.get('title', 'No title')
                summary = article.get('summary', 'No summary')[:200] + "..."
                time_published = article.get('time_published', 'Unknown time')

                # Get sentiment scores
                sentiment = article.get('overall_sentiment_score', 0)
                sentiment_label = article.get('overall_sentiment_label', 'NEUTRAL')

                print(f"\n{i}. {title}")
                print(f"   Time: {time_published}")
                print(f"   Sentiment: {sentiment_label} ({sentiment:.3f})")
                print(f"   Summary: {summary}")

                # Show ticker-specific sentiment if available
                if 'ticker_sentiment' in article:
                    for ticker in article['ticker_sentiment']:
                        if ticker.get('ticker', '').upper() == symbol:
                            ticker_sentiment = ticker.get('relevance_score', 'N/A')
                            ticker_label = ticker.get('ticker_sentiment_label', 'N/A')
                            print(f"   {symbol} Relevance: {ticker_sentiment} ({ticker_label})")
        else:
            print("No recent news found or API issue")
        return

    if command == "RANGE" and len(sys.argv) >= 4:
        # Multi-strike analysis: range 6600-6650 C
        try:
            strike_range = sys.argv[2]
            start_strike, end_strike = map(float, strike_range.split('-'))
            option_type = sys.argv[3].upper()
            analyze_multi_strikes("SPX", start_strike, end_strike, option_type)
        except:
            print("Usage: python market_engine.py range 6600-6650 C")
        return

    if command == "WALLS":
        # Put/call wall detection
        detect_put_walls()
        return

    symbol = command

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