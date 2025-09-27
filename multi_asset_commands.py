#!/usr/bin/env python3
"""
Multi-Asset Trading Commands
Simple command interface for the complete three-asset system
"""

import sys
import subprocess

def run_spx_only():
    """Run SPX analysis only"""
    print("Running SPX analysis...")
    subprocess.run([sys.executable, "trade.py"])

def run_qqq_only():
    """Run QQQ analysis only"""
    print("Running QQQ analysis...")
    subprocess.run([sys.executable, "qqq_integration.py"])

def run_spy_only():
    """Run SPY analysis only"""
    print("Running SPY analysis...")
    subprocess.run([sys.executable, "spy_integration.py"])

def run_spx_qqq():
    """Run SPX + QQQ analysis"""
    print("Running SPX + QQQ analysis...")
    subprocess.run([sys.executable, "trade_both.py"])

def run_all_three():
    """Run SPX + QQQ + SPY analysis"""
    print("Running complete three-asset analysis...")
    subprocess.run([sys.executable, "trade_all.py"])

def show_menu():
    """Display command menu"""
    print("\nMULTI-ASSET TRADING SYSTEM")
    print("=" * 50)
    print("Available Commands:")
    print("1. SPX only          - python trade.py")
    print("2. QQQ only          - python qqq_integration.py")
    print("3. SPY only          - python spy_integration.py")
    print("4. SPX + QQQ         - python trade_both.py")
    print("5. All three assets  - python trade_all.py")
    print("")
    print("Quick Commands:")
    print("- spx     : SPX analysis")
    print("- qqq     : QQQ analysis")
    print("- spy     : SPY analysis")
    print("- both    : SPX + QQQ")
    print("- all     : SPX + QQQ + SPY")
    print("=" * 50)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()

        if command == "spx":
            run_spx_only()
        elif command == "qqq":
            run_qqq_only()
        elif command == "spy":
            run_spy_only()
        elif command == "both":
            run_spx_qqq()
        elif command == "all":
            run_all_three()
        elif command == "menu":
            show_menu()
        else:
            print(f"Unknown command: {command}")
            show_menu()
    else:
        show_menu()