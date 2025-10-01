#!/usr/bin/env python3
"""
SEAMLESS OPTIONS FLOW ANALYZER
One command: Parse PDF → Analyze → Format → Send to Discord
Usage: python flow.py "path/to/flow.pdf" [--send] [--channel alerts]
"""
import sys
import subprocess
from pathlib import Path
from flow_pdf_parser import FlowPDFParser

def calculate_win_rate(premium_value, percent_otm):
    """Estimate win rate based on premium and distance"""
    # Higher premium + closer to money = higher win rate
    pct = int(percent_otm.replace('%', '').replace('+', '').replace('-', ''))

    if premium_value > 5_000_000:  # >$5M
        if abs(pct) < 10:
            return 75
        elif abs(pct) < 20:
            return 70
        else:
            return 65
    elif premium_value > 2_000_000:  # >$2M
        if abs(pct) < 10:
            return 70
        elif abs(pct) < 20:
            return 65
        else:
            return 60
    else:  # <$2M
        if abs(pct) < 10:
            return 65
        elif abs(pct) < 20:
            return 60
        else:
            return 55

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

def format_for_discord(parser_data):
    """Format parsed data for Discord using mobile template"""

    parser = FlowPDFParser("")  # Create instance for sorting
    parser.data = parser_data
    top_plays = parser.get_top_plays(5)

    calls_count = len(parser_data['calls_bought'])
    puts_sold_count = len(parser_data['puts_sold'])
    puts_bought_count = len(parser_data['puts_bought'])
    calls_sold_count = len(parser_data['calls_sold'])

    message = f"""📊 INSTITUTIONAL OPTIONS FLOW

**{calls_count} CALLS BOUGHT | {puts_sold_count} PUTS SOLD | {puts_bought_count} PUTS BOUGHT | {calls_sold_count} CALLS SOLD**

━━━━━━━━━━━━━━━━━━━━━━━━━━━
🟢 **TOP BULLISH PLAYS**
━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""

    # Add top 5 calls bought
    for i, trade in enumerate(top_plays['calls_bought'][:5], 1):
        win_rate = calculate_win_rate(trade['premium_value'], trade['percent_otm'])
        strategy = generate_strategy(trade['ticker'], trade['strike'], trade['percent_otm'])

        descriptor = "HIGHEST CONVICTION" if i == 1 else "HIGH PREMIUM" if i == 2 else "INSTITUTIONAL BET"

        message += f"""**#{i} {trade['ticker']} - {descriptor}**
Calls Bought: ${trade['strike']} strike
Expiration: {trade['expiration']}
Premium: ${trade['premium']}
Distance: {trade['percent_otm']}% OTM
Strategy: {strategy}
Win Rate: {win_rate}%

"""

    # Add top 3 puts sold (bullish support)
    if top_plays['puts_sold']:
        message += """━━━━━━━━━━━━━━━━━━━━━━━━━━━
🛡️ **BULLISH PUTS SOLD**
━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""
        for i, trade in enumerate(top_plays['puts_sold'][:3], 1):
            descriptor = "FLOOR PROTECTION" if i == 1 else "SUPPORT LEVEL"

            message += f"""**#{i} {trade['ticker']} - {descriptor}**
Puts Sold: ${trade['strike']} strike
Expiration: {trade['expiration']}
Premium: ${trade['premium']}
Implication: ${trade['strike']} is institutional floor
Action: STAY BULLISH above ${trade['strike']}

"""

    # Add top 3 puts bought (bearish warnings)
    if top_plays['puts_bought']:
        message += """━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔴 **BEARISH WARNINGS**
━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""
        for i, trade in enumerate(top_plays['puts_bought'][:3], 1):
            warning_type = "MASSIVE HEDGING 🚨" if i == 1 else "BEARISH POSITIONING"

            message += f"""**#{i} {trade['ticker']} - {warning_type}**
Puts Bought: ${trade['strike']} strike
Expiration: {trade['expiration']}
Premium: ${trade['premium']}
Warning: AVOID BULLISH {trade['ticker']} TRADES
Risk: Institutional downside protection

"""

    # Add quick reference
    message += """━━━━━━━━━━━━━━━━━━━━━━━━━━━
💡 **POSITION SIZING**
━━━━━━━━━━━━━━━━━━━━━━━━━━━

1-2% per trade
Enter on pullbacks
Exit at 50-100% profit
30 days before expiration

🤖 Powered by TraxterAI"""

    return message

def send_to_discord(message, channel='alerts'):
    """Send formatted message to Discord"""
    try:
        result = subprocess.run(
            ['python', 'send_discord_multi.py', '🔥 Options Flow Analysis', message, channel],
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
        print("SEAMLESS OPTIONS FLOW ANALYZER")
        print("="*60)
        print("\nUsage:")
        print('  python flow.py "path/to/flow.pdf"')
        print('  python flow.py "path/to/flow.pdf" --send')
        print('  python flow.py "path/to/flow.pdf" --send --channel research')
        print("\nExamples:")
        print('  python flow.py "Downloads/Flow-9-30-25.pdf.pdf"')
        print('  python flow.py "Downloads/Flow.pdf" --send')
        sys.exit(1)

    pdf_path = sys.argv[1]
    send = '--send' in sys.argv
    channel = 'alerts'

    # Get channel if specified
    if '--channel' in sys.argv:
        idx = sys.argv.index('--channel')
        if idx + 1 < len(sys.argv):
            channel = sys.argv[idx + 1]

    # Verify file exists
    if not Path(pdf_path).exists():
        print(f"❌ File not found: {pdf_path}")
        sys.exit(1)

    print("🚀 SEAMLESS FLOW ANALYZER")
    print("="*60)
    print(f"📄 Input: {pdf_path}")
    print(f"📱 Channel: {channel}")
    print(f"🔄 Auto-send: {'Yes' if send else 'No'}")
    print()

    # Step 1: Parse PDF
    print("STEP 1: Parsing PDF...")
    parser = FlowPDFParser(pdf_path)
    data = parser.parse()

    if not data:
        print("❌ Failed to parse PDF")
        sys.exit(1)

    # Step 2: Format for Discord
    print("\nSTEP 2: Formatting for Discord...")
    message = format_for_discord(data)
    print(f"✅ Message formatted ({len(message)} characters)")

    # Step 3: Display or send
    if send:
        print("\nSTEP 3: Sending to Discord...")
        success = send_to_discord(message, channel)
        if success:
            print("\n✅ COMPLETE! Flow analysis sent to Discord")
        else:
            print("\n❌ Failed to send to Discord")
            print("\n📋 Preview:")
            print(message[:500] + "...")
    else:
        print("\nSTEP 3: Preview (not sending)")
        print("\n" + "="*60)
        print(message)
        print("="*60)
        print("\n💡 To send to Discord, add --send flag:")
        print(f'   python flow.py "{pdf_path}" --send')

if __name__ == "__main__":
    main()
