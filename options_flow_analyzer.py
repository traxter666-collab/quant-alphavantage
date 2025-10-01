#!/usr/bin/env python3
"""
Seamless Options Flow Analyzer
Automatically processes options flow data and sends formatted Discord alerts
Usage: python options_flow_analyzer.py [pdf_path]
"""
import sys
import re
import subprocess
from pathlib import Path

def parse_options_flow(data):
    """Parse options flow data and return structured analysis"""

    # Extract calls bought
    calls_bought = []
    puts_sold = []
    puts_bought = []
    calls_sold = []

    # Parse the data (simplified - would need PDF parsing in production)
    # For now, accepting formatted text input

    analysis = {
        'calls_bought': calls_bought,
        'puts_sold': puts_sold,
        'puts_bought': puts_bought,
        'calls_sold': calls_sold
    }

    return analysis

def format_discord_message(analysis):
    """Format analysis using mobile-optimized template"""

    calls_count = len(analysis.get('calls_bought', []))
    puts_sold_count = len(analysis.get('puts_sold', []))
    puts_bought_count = len(analysis.get('puts_bought', []))
    calls_sold_count = len(analysis.get('calls_sold', []))

    message = f"""📊 INSTITUTIONAL OPTIONS FLOW

**{calls_count} CALLS BOUGHT | {puts_sold_count} PUTS SOLD | {puts_bought_count} PUTS BOUGHT | {calls_sold_count} CALLS SOLD**

━━━━━━━━━━━━━━━━━━━━━━━━━━━
🟢 **TOP BULLISH PLAYS**
━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""

    # Add top bullish plays
    for i, trade in enumerate(analysis.get('calls_bought', [])[:5], 1):
        message += f"""**#{i} {trade['ticker']} - {trade['descriptor']}**
Calls Bought: ${trade['strike']} strike
Expiration: {trade['expiration']}
Premium: ${trade['premium']}
Distance: {trade['distance']}
Strategy: {trade['strategy']}
Win Rate: {trade['win_rate']}

"""

    # Add puts sold (bullish)
    if analysis.get('puts_sold'):
        message += """━━━━━━━━━━━━━━━━━━━━━━━━━━━
🛡️ **BULLISH PUTS SOLD**
━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""
        for i, trade in enumerate(analysis.get('puts_sold', [])[:3], 1):
            message += f"""**#{i} {trade['ticker']} - {trade['descriptor']}**
Puts Sold: ${trade['strike']} strike
Expiration: {trade['expiration']}
Premium: ${trade['premium']}
Implication: ${trade['floor_level']} is institutional floor
Action: {trade['action']}

"""

    # Add bearish warnings
    if analysis.get('puts_bought'):
        message += """━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔴 **BEARISH WARNINGS**
━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""
        for i, trade in enumerate(analysis.get('puts_bought', [])[:3], 1):
            message += f"""**#{i} {trade['ticker']} - {trade['warning_type']} 🚨**
Puts Bought: ${trade['strike']} strike
Expiration: {trade['expiration']}
Premium: ${trade['premium']}
Warning: {trade['warning']}
Risk: {trade['risk']}

"""

    message += """━━━━━━━━━━━━━━━━━━━━━━━━━━━
💡 **POSITION SIZING**
━━━━━━━━━━━━━━━━━━━━━━━━━━━

1-2% per trade
Enter on pullbacks
Exit at 50-100% profit
30 days before expiration

🤖 Powered by TraxterAI"""

    return message

def send_to_discord(title, message, channel='alerts'):
    """Send formatted message to Discord"""
    try:
        result = subprocess.run(
            ['python', 'send_discord_multi.py', title, message, channel],
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode == 0:
            print(f"✅ Sent to Discord channel '{channel}'")
            return True
        else:
            print(f"❌ Failed to send to Discord: {result.stderr}")
            return False

    except Exception as e:
        print(f"❌ Error sending to Discord: {e}")
        return False

def main():
    """Main execution flow"""

    print("🔄 Options Flow Analyzer - Seamless Mode")
    print("=" * 50)

    # Example: Auto-process if PDF path provided
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
        print(f"📄 Processing: {pdf_path}")

        # TODO: Add PDF parsing logic here
        # For now, using manual data entry
        print("⚠️  PDF parsing not yet implemented")
        print("💡 Use manual entry mode for now")

    # For seamless operation, would integrate with:
    # 1. PDF parser (PyPDF2 or similar)
    # 2. Automated file monitoring (watchdog)
    # 3. Scheduled runs (cron/Task Scheduler)

    print("\n✅ Ready for seamless processing")
    print("💡 Next: Add PDF to Downloads folder and run:")
    print('   python options_flow_analyzer.py "path/to/flow.pdf"')

if __name__ == "__main__":
    main()
