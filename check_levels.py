#!/usr/bin/env python3
"""
Quick Quant Level Checker
Instantly see where SPX is relative to key Monday levels
"""

import subprocess
import sys

def get_current_spx():
    """Get current SPX price"""
    try:
        result = subprocess.run(
            ["python", "spx_live.py"],
            capture_output=True,
            text=True,
            timeout=15
        )

        if result.returncode == 0:
            for line in result.stdout.split('\n'):
                if "SPX:" in line and "$" in line:
                    try:
                        price_part = line.split("$")[1].split("(")[0].strip()
                        return float(price_part.replace(',', ''))
                    except:
                        pass
    except:
        pass

    return None

def analyze_levels(spx_price):
    """Analyze current position vs Quant levels"""

    if spx_price is None:
        print("ERROR: Could not get SPX price")
        return

    print(f"CURRENT SPX: ${spx_price:.2f}")
    print("=" * 50)

    # Key levels
    levels = [
        (6750, "Target 2 (Extended)"),
        (6730, "Target 1 (Breakout)"),
        (6700, "HIGH REVERSAL - FADE"),
        (6697, "Reversal Zone Start"),
        (6685, "Resistance Upper"),
        (6678, "KEY BREAKOUT LEVEL"),
        (6647, "MAJOR PIVOT"),
        (6620, "Support Zone Upper"),
        (6610, "GAMMA FLIP"),
        (6590, "HIGH REVERSAL - BUY"),
        (6587, "21d EMA Support"),
        (6570, "Lower Support"),
        (6557, "Support Floor")
    ]

    print("LEVEL ANALYSIS:")
    print("-" * 30)

    for level, description in levels:
        distance = spx_price - level
        status = "ABOVE" if distance > 0 else "BELOW"

        # Highlight key levels
        if level == 6678:  # Key breakout
            marker = "***" if distance > 0 else ">>>"
        elif level in [6700, 6590]:  # High reversal zones
            marker = "[R]" if level == 6700 else "[B]"
        elif level == 6647:  # Major pivot
            marker = "[P]"
        elif level == 6610:  # Gamma flip
            marker = "[G]"
        else:
            marker = "   "

        print(f"{marker} {level}: {description}")
        print(f"     {status} by {abs(distance):+.1f} points")
        print()

    # Trading zone
    if spx_price >= 6700:
        zone = "[R] HIGH REVERSAL ZONE - Consider fading strength"
        strategy = "Look for 6697-6700 reversal, puts on strength"
    elif spx_price >= 6678:
        zone = "[!] RESISTANCE ZONE - Watch for 6678 breakout"
        strategy = "Above 6678 = bullish to 6730-6750, below = range"
    elif spx_price >= 6647:
        zone = "[N] NEUTRAL ZONE - Above pivot"
        strategy = "Range trading, watch pivot hold/break"
    elif spx_price >= 6620:
        zone = "[S] APPROACH SUPPORT - Watch for bounces"
        strategy = "Look for support zone bounces 6610-6620"
    elif spx_price >= 6587:
        zone = "[B] HIGH REVERSAL ZONE - Buy weakness"
        strategy = "Strong buy zone at 21d EMA + major support"
    else:
        zone = "[!] BELOW MAJOR SUPPORT - Bearish"
        strategy = "Bearish territory, look for continuation lower"

    print("CURRENT ZONE:")
    print(f"{zone}")
    print()
    print("STRATEGY:")
    print(f"{strategy}")
    print()

    # Key distances
    print("KEY DISTANCES:")
    print(f"To 6678 breakout: {spx_price - 6678:+.1f} points")
    print(f"To 6700 reversal: {spx_price - 6700:+.1f} points")
    print(f"To 6647 pivot: {spx_price - 6647:+.1f} points")
    print(f"To 6610 gamma flip: {spx_price - 6610:+.1f} points")

def main():
    print("MONDAY QUANT LEVEL CHECKER")
    print("=" * 40)

    print("Getting current SPX price...")
    spx_price = get_current_spx()

    analyze_levels(spx_price)

if __name__ == "__main__":
    main()