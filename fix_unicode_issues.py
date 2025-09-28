#!/usr/bin/env python3
"""
Unicode Issue Fixer for Windows Compatibility
Removes problematic Unicode characters from analysis engines
"""

import os
import re
import shutil
from datetime import datetime

def fix_unicode_in_file(file_path):
    """Fix Unicode issues in a single file"""
    print(f"Processing: {file_path}")

    # Create backup first
    backup_path = f"{file_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    try:
        # Read file with UTF-8 encoding
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        # Create backup
        shutil.copy2(file_path, backup_path)
        print(f"  Backup created: {backup_path}")

        # Define Unicode replacements
        unicode_replacements = {
            # Emojis to text
            '🚨': 'ALERT',
            '⚡': 'FAST',
            '📊': 'CHART',
            '🎯': 'TARGET',
            '✅': 'SUCCESS',
            '❌': 'ERROR',
            '🔥': 'HOT',
            '💰': 'MONEY',
            '📈': 'UP',
            '📉': 'DOWN',
            '🚀': 'ROCKET',
            '⚠️': 'WARNING',
            '🧲': 'MAGNET',
            '👑': 'KING',
            '🛡️': 'SHIELD',
            '🎪': 'CIRCUS',
            '🏆': 'TROPHY',
            '🔍': 'SEARCH',
            '🌐': 'GLOBAL',
            '🎮': 'GAME',
            '🔧': 'TOOL',
            '⭐': 'STAR',
            '🤖': 'ROBOT',
            '📱': 'PHONE',
            '💡': 'IDEA',
            '🧠': 'BRAIN',
            '🎲': 'DICE',
            '🔴': 'RED',
            '🟡': 'YELLOW',
            '🟢': 'GREEN',
            '🔵': 'BLUE',
            '🏛️': 'INSTITUTIONAL',
            '🎖️': 'MEDAL',
            # Special characters
            '•': '-',
            '→': '->',
            '←': '<-',
            '↑': '^',
            '↓': 'v',
            '"': '"',
            '"': '"',
            ''': "'",
            ''': "'",
            '…': '...',
            '–': '-',
            '—': '--',
            # Math symbols
            '≥': '>=',
            '≤': '<=',
            '≠': '!=',
            '×': '*',
            '÷': '/',
            # Currency
            '€': 'EUR',
            '£': 'GBP',
            '¥': 'JPY'
        }

        # Apply replacements
        original_content = content
        for unicode_char, replacement in unicode_replacements.items():
            content = content.replace(unicode_char, replacement)

        # Remove any remaining problematic Unicode characters
        # Keep only ASCII + common extended ASCII
        content = re.sub(r'[^\x00-\xFF]', '', content)

        # Write cleaned content
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        # Calculate changes
        changes_made = len(original_content) - len(content)
        print(f"  Fixed: {changes_made} characters changed/removed")

        return True

    except Exception as e:
        print(f"  ERROR: {e}")
        # Restore backup if something went wrong
        if os.path.exists(backup_path):
            shutil.copy2(backup_path, file_path)
            print(f"  Restored from backup")
        return False

def main():
    """Fix Unicode issues in all problematic files"""
    print("UNICODE ISSUE FIXER")
    print("=" * 40)
    print("Fixing Windows compatibility issues...")
    print("")

    # Files that need fixing based on test results
    problematic_files = [
        'smart_alerts.py',
        'trading_dashboard.py',
        'volatility_intelligence.py',
        'market_microstructure.py',
        'spx_auto.py',
        'error_handling_test.py',
        'unified_spx_data.py',
        'ndx_integration.py',
        'five_asset_integration.py',
        'news_sentiment_engine.py',
        'performance_analytics.py',
        'ml_pattern_engine.py',
        'dealer_positioning_engine.py',
        'dealer_positioning_integration.py'
    ]

    fixed_count = 0
    total_count = len(problematic_files)

    for file_path in problematic_files:
        if os.path.exists(file_path):
            if fix_unicode_in_file(file_path):
                fixed_count += 1
            print("")
        else:
            print(f"SKIPPING: {file_path} (not found)")
            print("")

    print("=" * 40)
    print(f"SUMMARY: {fixed_count}/{total_count} files fixed")

    if fixed_count == total_count:
        print("SUCCESS: All files fixed successfully")
        print("System should now be Windows compatible")
    else:
        print(f"WARNING: {total_count - fixed_count} files had issues")
        print("Manual review may be required")

    print("")
    print("Backups created with timestamp suffix")
    print("Test the system with: python market_open_protocol.py")

if __name__ == "__main__":
    main()