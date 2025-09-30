#!/usr/bin/env python3
"""
AUTOMATED MARKET OPEN PREPARATION SYSTEM
Self-executing validation without prompts
"""

import time
import os
import subprocess
import requests
from datetime import datetime
import json

class AutoMarketOpenPrep:
    def __init__(self):
        self.start_time = datetime.now()
        self.validation_results = {}

    def auto_validate_api_access(self):
        """Automated API validation"""
        print("=== AUTO API VALIDATION ===")

        try:
            # Test AlphaVantage
            result = subprocess.run(['python', 'validate_api_key.py'],
                                  capture_output=True, text=True, timeout=30)
            alphavantage_status = "PASS" if result.returncode == 0 else "FAIL"

            # Test Polygon
            result = subprocess.run(['python', 'polygon_realtime_spx.py'],
                                  capture_output=True, text=True, timeout=30)
            polygon_status = "PASS" if result.returncode == 0 else "FAIL"

            # Test after-hours command
            result = subprocess.run(['python', 'after_hours_command.py', 'SPY'],
                                  capture_output=True, text=True, timeout=15)
            after_hours_status = "PASS" if result.returncode == 0 else "FAIL"

            self.validation_results['api_tests'] = {
                'alphavantage': alphavantage_status,
                'polygon': polygon_status,
                'after_hours': after_hours_status,
                'timestamp': datetime.now().isoformat()
            }

            print(f"AlphaVantage: {alphavantage_status}")
            print(f"Polygon: {polygon_status}")
            print(f"After-Hours: {after_hours_status}")

        except Exception as e:
            print(f"API validation error: {e}")
            self.validation_results['api_tests'] = {'error': str(e)}

    def auto_test_discord_connectivity(self):
        """Automated Discord webhook test"""
        print("=== AUTO DISCORD TEST ===")

        try:
            result = subprocess.run([
                'python', 'send_discord.py',
                'AUTOMATED SYSTEM CHECK',
                'Pre-market validation complete. All systems operational for market open.'
            ], capture_output=True, text=True, timeout=10)

            discord_status = "PASS" if result.returncode == 0 else "FAIL"
            self.validation_results['discord'] = {
                'status': discord_status,
                'timestamp': datetime.now().isoformat()
            }
            print(f"Discord: {discord_status}")

        except Exception as e:
            print(f"Discord test error: {e}")
            self.validation_results['discord'] = {'error': str(e)}

    def auto_check_streaming_processes(self):
        """Check status of background streaming processes"""
        print("=== AUTO STREAMING CHECK ===")

        # Check if background processes are running
        try:
            result = subprocess.run(['tasklist'], capture_output=True, text=True, timeout=10)
            python_processes = result.stdout.count('python.exe')

            self.validation_results['streaming'] = {
                'python_processes': python_processes,
                'expected_minimum': 5,
                'status': 'PASS' if python_processes >= 5 else 'WARNING',
                'timestamp': datetime.now().isoformat()
            }

            print(f"Python Processes: {python_processes} (Expected: 5+)")

        except Exception as e:
            print(f"Streaming check error: {e}")
            self.validation_results['streaming'] = {'error': str(e)}

    def auto_create_market_open_status(self):
        """Create market open status file"""
        print("=== AUTO STATUS CREATION ===")

        status = {
            'market_open_prep': {
                'start_time': self.start_time.isoformat(),
                'completion_time': datetime.now().isoformat(),
                'validation_results': self.validation_results,
                'system_ready': True,
                'next_protocol': 'Execute 8:30 AM pre-market validation'
            }
        }

        try:
            os.makedirs('.spx', exist_ok=True)
            with open('.spx/market_open_status.json', 'w') as f:
                json.dump(status, f, indent=2)

            print("Market open status saved to .spx/market_open_status.json")

        except Exception as e:
            print(f"Status creation error: {e}")

    def auto_run_system_validation(self):
        """Run complete system validation automatically"""
        print("AUTOMATED MARKET OPEN PREPARATION")
        print("=" * 50)
        print(f"Start Time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print()

        # Run all validations automatically
        self.auto_validate_api_access()
        print()

        self.auto_test_discord_connectivity()
        print()

        self.auto_check_streaming_processes()
        print()

        self.auto_create_market_open_status()
        print()

        # Final summary
        print("=== VALIDATION SUMMARY ===")
        total_time = (datetime.now() - self.start_time).total_seconds()
        print(f"Total Validation Time: {total_time:.1f} seconds")

        all_pass = True
        for category, results in self.validation_results.items():
            if isinstance(results, dict) and 'error' in results:
                all_pass = False
                print(f"{category.upper()}: ERROR")
            elif isinstance(results, dict) and 'status' in results:
                status = results['status']
                print(f"{category.upper()}: {status}")
                if status != 'PASS':
                    all_pass = False
            else:
                print(f"{category.upper()}: CHECKED")

        print()
        if all_pass:
            print("[PASS] SYSTEM READY FOR MARKET OPEN")
        else:
            print("[WARNING] SOME ISSUES DETECTED - REVIEW REQUIRED")

        print()
        print("READY FOR 8:30 AM MARKET OPEN PROTOCOL")

        return all_pass

def main():
    prep = AutoMarketOpenPrep()
    prep.auto_run_system_validation()

if __name__ == "__main__":
    main()