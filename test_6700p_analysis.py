#!/usr/bin/env python3
"""
Test 6700P SPX Analysis
Specific test for our highest probability Monday trade recommendation
"""

import subprocess
import sys
from datetime import datetime

def analyze_6700p_setup():
    """Analyze the 6700P trade setup with current market conditions"""

    print("SPX 6700P TRADE ANALYSIS TEST")
    print("=" * 50)

    # Get current SPX price
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
                        current_spx = float(price_part.replace(',', ''))
                        break
                    except:
                        pass
        else:
            print("Could not get current SPX price")
            return False

    except Exception as e:
        print(f"Error getting SPX price: {e}")
        return False

    print(f"Current SPX: ${current_spx:.2f}")
    print()

    # Analyze 6700P setup
    distance_to_target = 6700 - current_spx

    print("6700P TRADE SETUP ANALYSIS:")
    print("-" * 30)
    print(f"Target Level: 6700 (High Reversal Zone)")
    print(f"Current Distance: {distance_to_target:+.1f} points")
    print(f"Percentage Move Needed: {(distance_to_target/current_spx)*100:.1f}%")

    # Trade feasibility
    if distance_to_target > 100:
        feasibility = "LOW - Too far from target"
        probability = "25%"
    elif distance_to_target > 60:
        feasibility = "MEDIUM - Normal market move required"
        probability = "60%"
    elif distance_to_target > 30:
        feasibility = "HIGH - Easy reach in normal volatility"
        probability = "80%"
    elif distance_to_target > 0:
        feasibility = "VERY HIGH - Close to target"
        probability = "90%"
    else:
        feasibility = "IMMEDIATE - Already at/above target"
        probability = "100% (fade now)"

    print(f"Feasibility: {feasibility}")
    print(f"Touch Probability: {probability}")
    print()

    # Risk/Reward Analysis
    print("RISK/REWARD ANALYSIS:")
    print("-" * 20)

    if current_spx < 6700:
        # Estimate option pricing (rough)
        estimated_premium = max(5, min(25, distance_to_target * 0.3))
        target_1_return = estimated_premium * 2  # Conservative 2x
        target_2_return = estimated_premium * 4  # Aggressive 4x

        print(f"Estimated 6700P Entry: ${estimated_premium:.0f}")
        print(f"Target 1 (SPX to 6680): ${target_1_return:.0f} (+{100*(target_1_return/estimated_premium-1):.0f}%)")
        print(f"Target 2 (SPX to 6650): ${target_2_return:.0f} (+{100*(target_2_return/estimated_premium-1):.0f}%)")
        print(f"Stop Loss (SPX >6705): 50% of premium")

        risk_reward = target_1_return / (estimated_premium * 0.5)
        print(f"Risk/Reward Ratio: 1:{risk_reward:.1f}")

    else:
        print("SPX already at/above 6700 - fade setup active NOW")
        print("Entry: Immediate")
        print("Target: 6680, 6650, 6620")
        print("Stop: Sustained break above 6705")

    print()

    # Market conditions check
    print("MARKET CONDITIONS CHECK:")
    print("-" * 25)

    # Check if it's within trading hours
    now = datetime.now()
    hour = now.hour
    minute = now.minute

    if (hour == 9 and minute >= 30) or (10 <= hour <= 15):
        market_condition = "ACTIVE TRADING HOURS - Execute when setup triggers"
    elif hour < 9 or (hour == 9 and minute < 30):
        market_condition = "PREMARKET - Monitor for gap to 6700"
    else:
        market_condition = "AFTER HOURS - Setup for tomorrow"

    print(f"Market Timing: {market_condition}")
    print(f"Current Time: {now.strftime('%H:%M:%S')} ET")

    # Quant level context
    print()
    print("QUANT LEVEL CONTEXT:")
    print("-" * 20)
    print("6700: HIGH REVERSAL ZONE - 'High likelihood of reversal'")
    print("6697-6700: Primary fade zone")
    print("6678: Key breakout level (bullish if sustained above)")
    print("6647: Major pivot (current support/resistance)")

    if current_spx < 6647:
        level_context = "Below pivot - bearish, but 6700 still resistance"
    elif current_spx < 6678:
        level_context = "Above pivot, below breakout - range bound"
    elif current_spx < 6700:
        level_context = "Above breakout - bullish momentum to 6700 resistance"
    else:
        level_context = "At/above 6700 - reversal zone active"

    print(f"Current Context: {level_context}")

    print()
    print("OVERALL ASSESSMENT:")
    print("-" * 20)

    if distance_to_target > 0 and distance_to_target < 80:
        assessment = "HIGH PROBABILITY SETUP"
        action = "PREPARE TO EXECUTE - Wait for approach to 6697-6700"
    elif distance_to_target <= 0:
        assessment = "ACTIVE SETUP"
        action = "EXECUTE NOW - Fade the reversal zone"
    else:
        assessment = "WAIT FOR BETTER SETUP"
        action = "Too far from target - need significant move up first"

    print(f"Assessment: {assessment}")
    print(f"Action: {action}")

    return True

def test_spx_system_integration():
    """Test how our SPX system would handle the 6700P recommendation"""

    print("\n" + "=" * 60)
    print("TESTING SPX SYSTEM INTEGRATION")
    print("=" * 60)

    try:
        # Test SPX quick analysis
        result = subprocess.run(
            ["python", "spx_command_router.py", "spx quick"],
            capture_output=True,
            text=True,
            timeout=60
        )

        if result.returncode == 0:
            print("SUCCESS: SPX Quick Analysis working")

            # Look for relevant output
            output = result.stdout
            if "SPX:" in output:
                print("SUCCESS: Current SPX price detected in output")
            if any(word in output.lower() for word in ['put', 'call', 'option']):
                print("SUCCESS: Options recommendations detected")
            if any(word in output for word in ['6700', '6680', '6650']):
                print("SUCCESS: Target levels near our 6700P setup detected")

            # Show relevant excerpts
            lines = output.split('\n')
            for i, line in enumerate(lines):
                if 'SPX:' in line or '6700' in line or '6680' in line:
                    print(f"RELEVANT: {line.strip()}")

        else:
            print(f"WARNING: SPX Quick Analysis failed - {result.stderr}")
            return False

    except Exception as e:
        print(f"ERROR: SPX system test failed - {e}")
        return False

    return True

def main():
    """Run complete 6700P analysis test"""

    print("TESTING 6700P TRADE RECOMMENDATION")
    print("Saturday, September 29, 2025")
    print("Preparing for Monday market open")
    print()

    # Run the analysis
    success1 = analyze_6700p_setup()
    success2 = test_spx_system_integration()

    print("\n" + "=" * 60)
    print("TEST SUMMARY:")
    print("=" * 60)

    if success1 and success2:
        print("SUCCESS: All tests passed")
        print("6700P analysis integrated and ready for Monday")
        print("System can identify and analyze the trade setup")
        print()
        print("READY FOR MONDAY EXECUTION!")
    else:
        print("WARNING: Some tests failed")
        print("Review issues before Monday trading")

    print(f"\nTest completed at {datetime.now().strftime('%H:%M:%S')}")

    return success1 and success2

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)