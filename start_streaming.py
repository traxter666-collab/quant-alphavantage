#!/usr/bin/env python3
"""
Streaming Launcher - Quick Start for Monday Trading
Choose your streaming preference instantly
"""

import subprocess
import sys

def main():
    print("LIVE STREAMING LAUNCHER FOR MONDAY TRADING")
    print("=" * 60)
    print()
    print("STREAMING OPTIONS:")
    print("1. Basic Live Updates (30-second refresh)")
    print("   - Simple and reliable")
    print("   - Perfect for monitoring positions")
    print("   - Low resource usage")
    print()
    print("2. Enhanced Streaming (1-10 second refresh)")
    print("   - High-frequency updates")
    print("   - Real-time price monitoring")
    print("   - Active trading focused")
    print()
    print("3. Manual Refresh (On-demand)")
    print("   - Run commands when needed")
    print("   - Most reliable option")
    print("   - Full control over timing")
    print()
    print("4. Quick Test (Single update)")
    print("   - Test system before streaming")
    print("   - Verify data accuracy")
    print()

    choice = input("Select option (1-4): ").strip()

    if choice == "1":
        print("\nStarting Basic Live Updates...")
        subprocess.run([sys.executable, "basic_live_stream.py"])

    elif choice == "2":
        print("\nStarting Enhanced Streaming...")
        subprocess.run([sys.executable, "enhanced_live_stream.py"])

    elif choice == "3":
        print("\nMANUAL REFRESH COMMANDS:")
        print("=" * 40)
        print("ES Futures:    python trading_shortcuts.py smart_es")
        print("NQ Futures:    python trading_shortcuts.py smart_nq")
        print("SPX Options:   python spx_command_router.py \"spx quick\"")
        print("Multi-Asset:   python trading_shortcuts.py multi")
        print("Portfolio:     python trading_shortcuts.py portfolio")
        print()
        print("TIP: Copy and paste these commands as needed!")

    elif choice == "4":
        print("\nRunning Quick Test...")
        print("Testing ES futures analysis...")
        try:
            result = subprocess.run(
                [sys.executable, "trading_shortcuts.py", "smart_es"],
                timeout=60
            )
            if result.returncode == 0:
                print("SUCCESS: System test successful!")
                print("Ready for Monday trading!")
            else:
                print("ERROR: Test failed - check system status")
        except Exception as e:
            print(f"ERROR: Test error: {e}")

    else:
        print("Invalid choice. Please run again.")

if __name__ == "__main__":
    main()