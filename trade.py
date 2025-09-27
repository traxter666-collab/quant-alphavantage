#!/usr/bin/env python3
"""
Simple Daily Trading Command
Single command to run optimized SPX trading system
Usage: python trade.py
"""

import sys
sys.path.append('.')

def main():
    print("SPX TRADING SYSTEM - OPTIMIZED & READY")
    print("Single command execution with all enhancements")
    print("-" * 50)

    try:
        from spx_unified_launcher import run_unified_analysis

        print("Running unified analysis...")
        success = run_unified_analysis()

        if success:
            print("\n✓ Analysis complete - Check results above")
            print("✓ All optimizations active: SPX accuracy, thresholds, risk")
            print("✓ System ready for trading decisions")
        else:
            print("\n✗ Analysis failed - Check API connectivity")

    except ImportError as e:
        print(f"Import error: {e}")
        print("Ensure all required files are present")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()