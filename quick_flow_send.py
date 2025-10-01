#!/usr/bin/env python3
"""
Quick Options Flow Sender
Simplified script for rapid Discord posting
Usage: python quick_flow_send.py
"""
import subprocess

# Quick template for manual entry
TEMPLATE = """📊 INSTITUTIONAL OPTIONS FLOW

**66 CALLS BOUGHT | 23 PUTS SOLD | 13 PUTS BOUGHT | 3 CALLS SOLD**

━━━━━━━━━━━━━━━━━━━━━━━━━━━
🟢 **TOP BULLISH PLAYS**
━━━━━━━━━━━━━━━━━━━━━━━━━━━

**#1 TICKER - DESCRIPTOR**
Calls Bought: $XXX strike
Expiration: MM/DD/YY
Premium: $X.XM
Distance: +X% OTM
Strategy: $XXX/$XXX call spread
Win Rate: XX%

━━━━━━━━━━━━━━━━━━━━━━━━━━━
🛡️ **BULLISH PUTS SOLD**
━━━━━━━━━━━━━━━━━━━━━━━━━━━

**#X TICKER - FLOOR PROTECTION**
Puts Sold: $XXX strike
Expiration: MM/DD/YY
Premium: $X.XM
Implication: $XXX is institutional floor
Action: STAY BULLISH above $XXX

━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔴 **BEARISH WARNINGS**
━━━━━━━━━━━━━━━━━━━━━━━━━━━

**#X TICKER - WARNING 🚨**
Puts Bought: $XXX strike
Expiration: MM/DD/YY
Premium: $X.XM
Warning: ACTION TO AVOID
Risk: RISK DESCRIPTION

━━━━━━━━━━━━━━━━━━━━━━━━━━━
💡 **POSITION SIZING**
━━━━━━━━━━━━━━━━━━━━━━━━━━━

1-2% per trade
Enter on pullbacks
Exit at 50-100% profit
30 days before expiration

🤖 Powered by TraxterAI"""

def quick_send(title="🔥 Options Flow Update"):
    """Quick send template to Discord"""

    print("📱 Quick Flow Sender")
    print("=" * 50)
    print("\n📋 Using template format...")
    print("\n💡 Edit the message content in the script or:")
    print("   1. Copy template to clipboard")
    print("   2. Paste into Discord manually")
    print("   3. OR: Update quick_flow_send.py with your data")

    # Uncomment to auto-send template
    # subprocess.run(['python', 'send_discord.py', title, TEMPLATE])

    print("\n✅ Template ready!")
    print("\n" + TEMPLATE)

if __name__ == "__main__":
    quick_send()
