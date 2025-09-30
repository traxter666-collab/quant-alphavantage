#!/usr/bin/env python3
"""
Trading Shortcuts - Quick Access Commands
Simple shortcuts for common trading operations
"""

import sys
import subprocess
from unified_trading_interface import UnifiedTradingInterface

def run_shortcut(command: str):
    """Run shortcut command through unified interface"""
    interface = UnifiedTradingInterface()
    response = interface.process_command(command)
    interface.display_unified_response(response)

def main():
    """Handle shortcut commands"""

    if len(sys.argv) < 2:
        print("Trading Shortcuts Available:")
        print("python trading_shortcuts.py es          # Quick ES analysis")
        print("python trading_shortcuts.py nq          # Quick NQ analysis")
        print("python trading_shortcuts.py gc          # Quick GC analysis")
        print("python trading_shortcuts.py portfolio   # Portfolio analysis")
        print("python trading_shortcuts.py smart_es    # Smart ES analysis")
        print("python trading_shortcuts.py smart_nq    # Smart NQ analysis")
        print("python trading_shortcuts.py multi       # Multi-asset analysis")
        return

    shortcut = sys.argv[1].lower()

    # Define shortcut mappings
    shortcuts = {
        'es': 'ES analysis',
        'nq': 'NQ analysis',
        'gc': 'GC analysis',
        'portfolio': 'portfolio analysis',
        'smart_es': 'smart ES analysis',
        'smart_nq': 'smart NQ analysis',
        'smart_gc': 'smart GC analysis',
        'multi': 'multi asset analysis',
        'ndx': 'NDX analysis',
        'spy': 'SPY analysis',
        'qqq': 'QQQ analysis'
    }

    if shortcut in shortcuts:
        command = shortcuts[shortcut]
        print(f"Running: {command}")
        run_shortcut(command)
    else:
        print(f"Unknown shortcut: {shortcut}")
        print("Available shortcuts:", list(shortcuts.keys()))

if __name__ == "__main__":
    main()