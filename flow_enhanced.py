#!/usr/bin/env python3
"""
ENHANCED OPTIONS FLOW ANALYZER WITH TECHNICAL ANALYSIS
Combines: PDF parsing + TA engine + Level 2/3 data + Intelligent filtering
Usage: python flow_enhanced.py "path/to/flow.pdf" [--send] [--channel alerts] [--min-score 60]
"""
import sys
import subprocess
from pathlib import Path
from flow_pdf_parser import FlowPDFParser
from flow_ta_engine import FlowTechnicalAnalyzer

def calculate_win_rate(premium_value, percent_otm, ta_score):
    """Enhanced win rate calculation including TA score"""
    pct = int(percent_otm.replace('%', '').replace('+', '').replace('-', ''))

    # Base win rate from premium/OTM
    if premium_value > 5_000_000:  # >$5M
        if abs(pct) < 10:
            base_rate = 75
        elif abs(pct) < 20:
            base_rate = 70
        else:
            base_rate = 65
    elif premium_value > 2_000_000:  # >$2M
        if abs(pct) < 10:
            base_rate = 70
        elif abs(pct) < 20:
            base_rate = 65
        else:
            base_rate = 60
    else:  # <$2M
        if abs(pct) < 10:
            base_rate = 65
        elif abs(pct) < 20:
            base_rate = 60
        else:
            base_rate = 55

    # TA enhancement (can add up to +15% or subtract -10%)
    ta_adjustment = (ta_score - 50) / 100 * 25  # Scale TA score to +/-12.5%

    final_rate = min(95, max(30, base_rate + ta_adjustment))
    return int(final_rate)

def generate_strategy(ticker, strike, percent_otm):
    """Generate call spread strategy"""
    strike_num = float(strike)
    pct = int(percent_otm.replace('%', '').replace('+', '').replace('-', ''))

    if pct > 0:  # OTM calls
        lower = int(strike_num * 0.95)
        upper = int(strike_num)
        return f"${lower}/${upper} call spread"
    else:  # Near/ITM
        lower = int(strike_num)
        upper = int(strike_num * 1.05)
        return f"${lower}/${upper} call spread"

def format_for_discord_enhanced(parser_data, ta_results, min_ta_score=0):
    """
    Enhanced Discord formatting with TA analysis
    Only includes plays with TA score >= min_ta_score
    """
    parser = FlowPDFParser("")
    parser.data = parser_data
    top_plays = parser.get_top_plays(10)  # Get top 10 for filtering

    # Filter plays by TA score
    filtered_calls = [
        (trade, ta_results.get(trade['ticker'], {}))
        for trade in top_plays['calls_bought']
        if ta_results.get(trade['ticker'], {}).get('ta_score', 0) >= min_ta_score
    ][:5]  # Keep top 5 after filtering

    filtered_puts_sold = [
        (trade, ta_results.get(trade['ticker'], {}))
        for trade in top_plays['puts_sold']
        if ta_results.get(trade['ticker'], {}).get('ta_score', 0) >= min_ta_score
    ][:3]

    filtered_puts_bought = [
        (trade, ta_results.get(trade['ticker'], {}))
        for trade in top_plays['puts_bought']
        if ta_results.get(trade['ticker'], {}).get('ta_score', 0) >= min_ta_score
    ][:3]

    calls_count = len(parser_data['calls_bought'])
    puts_sold_count = len(parser_data['puts_sold'])
    puts_bought_count = len(parser_data['puts_bought'])
    calls_sold_count = len(parser_data['calls_sold'])

    ta_filtered = len(filtered_calls)

    message = f"""📊 INSTITUTIONAL OPTIONS FLOW (TA ENHANCED)

**{calls_count} CALLS BOUGHT | {puts_sold_count} PUTS SOLD | {puts_bought_count} PUTS BOUGHT | {calls_sold_count} CALLS SOLD**
**{ta_filtered} High-Quality Setups** (TA Score ≥{min_ta_score})

━━━━━━━━━━━━━━━━━━━━━━━━━━━
🟢 **TOP BULLISH PLAYS (TA FILTERED)**
━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""

    # Add filtered calls bought with TA analysis
    for i, (trade, ta_data) in enumerate(filtered_calls, 1):
        ta_score = ta_data.get('ta_score', 0)
        setup_quality = ta_data.get('setup_quality', 'UNKNOWN')
        recommendation = ta_data.get('recommendation', 'ANALYZE')

        win_rate = calculate_win_rate(
            trade['premium_value'],
            trade['percent_otm'],
            ta_score
        )
        strategy = generate_strategy(trade['ticker'], trade['strike'], trade['percent_otm'])

        descriptor = "HIGHEST CONVICTION" if i == 1 else "HIGH PREMIUM" if i == 2 else "INSTITUTIONAL BET"

        # Get key TA signals (top 3)
        signals = ta_data.get('signals', [])[:3]
        signal_text = "\n".join([f"  • {s}" for s in signals]) if signals else "  • TA analysis pending"

        message += f"""**#{i} {trade['ticker']} - {descriptor} ({setup_quality})**
Calls Bought: ${trade['strike']} strike
Expiration: {trade['expiration']}
Premium: ${trade['premium']}
Distance: {trade['percent_otm']}% OTM
Strategy: {strategy}

📊 **TA Analysis:**
TA Score: {ta_score:.0f}/100 | Win Rate: {win_rate}% | Rec: {recommendation}
{signal_text}

"""

    # Add filtered puts sold with TA
    if filtered_puts_sold:
        message += """━━━━━━━━━━━━━━━━━━━━━━━━━━━
🛡️ **BULLISH PUTS SOLD (TA FILTERED)**
━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""
        for i, (trade, ta_data) in enumerate(filtered_puts_sold, 1):
            ta_score = ta_data.get('ta_score', 0)
            setup_quality = ta_data.get('setup_quality', 'UNKNOWN')

            descriptor = "FLOOR PROTECTION" if i == 1 else "SUPPORT LEVEL"

            signals = ta_data.get('signals', [])[:2]
            signal_text = "\n".join([f"  • {s}" for s in signals]) if signals else ""

            message += f"""**#{i} {trade['ticker']} - {descriptor} ({setup_quality})**
Puts Sold: ${trade['strike']} strike
Expiration: {trade['expiration']}
Premium: ${trade['premium']}
Implication: ${trade['strike']} is institutional floor
TA Score: {ta_score:.0f}/100
{signal_text}

"""

    # Add filtered puts bought (warnings)
    if filtered_puts_bought:
        message += """━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔴 **BEARISH WARNINGS (TA FILTERED)**
━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""
        for i, (trade, ta_data) in enumerate(filtered_puts_bought, 1):
            ta_score = ta_data.get('ta_score', 0)

            warning_type = "MASSIVE HEDGING 🚨" if i == 1 else "BEARISH POSITIONING"

            message += f"""**#{i} {trade['ticker']} - {warning_type}**
Puts Bought: ${trade['strike']} strike
Expiration: {trade['expiration']}
Premium: ${trade['premium']}
Warning: AVOID BULLISH {trade['ticker']} TRADES
TA Score: {ta_score:.0f}/100 - Confirm bearish setup

"""

    message += """━━━━━━━━━━━━━━━━━━━━━━━━━━━
💡 **POSITION SIZING**
━━━━━━━━━━━━━━━━━━━━━━━━━━━

1-2% per trade
Enter on pullbacks
Exit at 50-100% profit
30 days before expiration

🤖 Powered by TraxterAI + TA Engine"""

    return message

def send_to_discord(message, channel='alerts'):
    """Send formatted message to Discord"""
    try:
        result = subprocess.run(
            ['python', 'send_discord_multi.py', '🔥 Options Flow Analysis (TA Enhanced)', message, channel],
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode == 0:
            print(f"✅ Sent to Discord channel '{channel}'")
            return True
        else:
            print(f"❌ Failed to send: {result.stderr}")
            return False

    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    if len(sys.argv) < 2:
        print("ENHANCED OPTIONS FLOW ANALYZER WITH TECHNICAL ANALYSIS")
        print("="*60)
        print("\nUsage:")
        print('  python flow_enhanced.py "path/to/flow.pdf"')
        print('  python flow_enhanced.py "path/to/flow.pdf" --send')
        print('  python flow_enhanced.py "path/to/flow.pdf" --send --min-score 60')
        print('  python flow_enhanced.py "path/to/flow.pdf" --send --channel research')
        print("\nOptions:")
        print("  --send              Auto-send to Discord")
        print("  --channel NAME      Discord channel (default: alerts)")
        print("  --min-score X       Minimum TA score (0-100, default: 60)")
        print("\nExamples:")
        print('  python flow_enhanced.py "Downloads/Flow.pdf" --min-score 70')
        print('  python flow_enhanced.py "Downloads/Flow.pdf" --send --min-score 75')
        sys.exit(1)

    pdf_path = sys.argv[1]
    send = '--send' in sys.argv
    channel = 'alerts'
    min_score = 60  # Default minimum TA score

    # Get channel if specified
    if '--channel' in sys.argv:
        idx = sys.argv.index('--channel')
        if idx + 1 < len(sys.argv):
            channel = sys.argv[idx + 1]

    # Get minimum score if specified
    if '--min-score' in sys.argv:
        idx = sys.argv.index('--min-score')
        if idx + 1 < len(sys.argv):
            try:
                min_score = int(sys.argv[idx + 1])
            except:
                print("⚠️ Invalid min-score, using default 60")

    # Verify file exists
    if not Path(pdf_path).exists():
        print(f"❌ File not found: {pdf_path}")
        sys.exit(1)

    print("🚀 ENHANCED FLOW ANALYZER (WITH TA ENGINE)")
    print("="*60)
    print(f"📄 Input: {pdf_path}")
    print(f"📱 Channel: {channel}")
    print(f"🔄 Auto-send: {'Yes' if send else 'No'}")
    print(f"📊 Min TA Score: {min_score}")
    print()

    # Step 1: Parse PDF
    print("STEP 1: Parsing PDF...")
    parser = FlowPDFParser(pdf_path)
    data = parser.parse()

    if not data:
        print("❌ Failed to parse PDF")
        sys.exit(1)

    # Step 2: Run TA analysis on all tickers
    print("\nSTEP 2: Running Technical Analysis...")
    analyzer = FlowTechnicalAnalyzer()
    ta_results = {}

    # Get unique tickers from all plays
    all_trades = (
        data['calls_bought'][:10] +
        data['puts_sold'][:5] +
        data['puts_bought'][:5]
    )

    unique_tickers = list(set(trade['ticker'] for trade in all_trades))

    print(f"Analyzing {len(unique_tickers)} unique tickers...")
    for ticker in unique_tickers:
        # Find the trade with highest premium for this ticker
        ticker_trades = [t for t in all_trades if t['ticker'] == ticker]
        if ticker_trades:
            best_trade = max(ticker_trades, key=lambda x: x['premium_value'])

            # Determine option type
            if best_trade in data['calls_bought']:
                option_type = 'calls_bought'
            elif best_trade in data['puts_sold']:
                option_type = 'puts_sold'
            else:
                option_type = 'puts_bought'

            # Run TA analysis
            ta_result = analyzer.analyze_ticker(
                ticker,
                option_type,
                best_trade['strike'],
                best_trade['premium_value']
            )
            ta_results[ticker] = ta_result

    # Step 3: Format for Discord with TA filtering
    print(f"\nSTEP 3: Formatting with TA filter (min score: {min_score})...")
    message = format_for_discord_enhanced(data, ta_results, min_score)
    print(f"✅ Message formatted ({len(message)} characters)")

    # Show TA summary
    print(f"\n📊 TA SUMMARY:")
    excellent = sum(1 for ta in ta_results.values() if ta['ta_score'] >= 75)
    good = sum(1 for ta in ta_results.values() if 60 <= ta['ta_score'] < 75)
    fair = sum(1 for ta in ta_results.values() if 45 <= ta['ta_score'] < 60)
    poor = sum(1 for ta in ta_results.values() if ta['ta_score'] < 45)

    print(f"  Excellent (≥75): {excellent}")
    print(f"  Good (60-74): {good}")
    print(f"  Fair (45-59): {fair}")
    print(f"  Poor (<45): {poor}")

    # Step 4: Display or send
    if send:
        print("\nSTEP 4: Sending to Discord...")
        success = send_to_discord(message, channel)
        if success:
            print("\n✅ COMPLETE! Enhanced flow analysis sent to Discord")
        else:
            print("\n❌ Failed to send to Discord")
            print("\n📋 Preview:")
            print(message[:500] + "...")
    else:
        print("\nSTEP 4: Preview (not sending)")
        print("\n" + "="*60)
        print(message)
        print("="*60)
        print("\n💡 To send to Discord, add --send flag:")
        print(f'   python flow_enhanced.py "{pdf_path}" --send --min-score {min_score}')

if __name__ == "__main__":
    main()
