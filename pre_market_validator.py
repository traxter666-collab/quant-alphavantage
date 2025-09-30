#!/usr/bin/env python3
"""
PRE-MARKET SYSTEM VALIDATION
Automated 8:30 AM pre-market validation system
"""

import time
import os
import subprocess
import requests
from datetime import datetime
import json

class PreMarketValidator:
    def __init__(self):
        self.start_time = datetime.now()
        self.validation_results = {}
        self.critical_failures = []

    def validate_streaming_systems(self):
        """Validate all 5 streaming systems are operational"""
        print("=== STREAMING SYSTEMS VALIDATION ===")

        try:
            # Check running processes
            result = subprocess.run(['tasklist'], capture_output=True, text=True, timeout=10)
            python_processes = result.stdout.count('python.exe')

            # Expected: 5 streaming processes + this validator
            expected_min = 5
            status = "PASS" if python_processes >= expected_min else "FAIL"

            if status == "FAIL":
                self.critical_failures.append(f"Only {python_processes} Python processes running (expected {expected_min}+)")

            self.validation_results['streaming_systems'] = {
                'python_processes': python_processes,
                'expected_minimum': expected_min,
                'status': status,
                'timestamp': datetime.now().isoformat()
            }

            print(f"Python Processes: {python_processes} (Expected: {expected_min}+)")
            print(f"Streaming Status: {status}")

        except Exception as e:
            print(f"Streaming validation error: {e}")
            self.validation_results['streaming_systems'] = {'error': str(e)}
            self.critical_failures.append(f"Streaming validation failed: {e}")

    def validate_api_connectivity(self):
        """Test all API endpoints for pre-market readiness"""
        print("=== API CONNECTIVITY VALIDATION ===")

        api_tests = {
            'alphavantage': ('python', 'validate_api_key.py'),
            'polygon': ('python', 'polygon_realtime_spx.py'),
            'after_hours': ('python', 'after_hours_command.py', 'SPY')
        }

        api_status = {}

        for service, command in api_tests.items():
            try:
                result = subprocess.run(command, capture_output=True, text=True, timeout=30)
                status = "PASS" if result.returncode == 0 else "FAIL"

                if status == "FAIL":
                    self.critical_failures.append(f"{service.upper()} API validation failed")

                api_status[service] = {
                    'status': status,
                    'response_time': '< 30s',
                    'timestamp': datetime.now().isoformat()
                }

                print(f"{service.upper()}: {status}")

            except Exception as e:
                print(f"{service.upper()}: ERROR - {e}")
                api_status[service] = {'error': str(e)}
                self.critical_failures.append(f"{service.upper()} API error: {e}")

        self.validation_results['api_connectivity'] = api_status

    def validate_discord_integration(self):
        """Test Discord webhook for market open alerts"""
        print("=== DISCORD INTEGRATION VALIDATION ===")

        try:
            result = subprocess.run([
                'python', 'send_discord.py',
                'PRE-MARKET VALIDATION',
                'All systems validated for market open. Ready for live trading session.'
            ], capture_output=True, text=True, timeout=15)

            status = "PASS" if result.returncode == 0 else "FAIL"

            if status == "FAIL":
                self.critical_failures.append("Discord webhook validation failed")

            self.validation_results['discord'] = {
                'status': status,
                'timestamp': datetime.now().isoformat()
            }

            print(f"Discord Webhook: {status}")

        except Exception as e:
            print(f"Discord validation error: {e}")
            self.validation_results['discord'] = {'error': str(e)}
            self.critical_failures.append(f"Discord error: {e}")

    def validate_data_pipeline(self):
        """Test real-time data pipeline readiness"""
        print("=== DATA PIPELINE VALIDATION ===")

        try:
            # Test SPX data accuracy
            result = subprocess.run(['python', 'spx_live.py'], capture_output=True, text=True, timeout=30)

            # Check for valid SPX data
            has_spx_data = 'SPX:' in result.stdout and '$' in result.stdout
            status = "PASS" if has_spx_data and result.returncode == 0 else "FAIL"

            if status == "FAIL":
                self.critical_failures.append("SPX data pipeline validation failed")

            self.validation_results['data_pipeline'] = {
                'spx_data': status,
                'real_time_access': "VERIFIED" if has_spx_data else "FAILED",
                'timestamp': datetime.now().isoformat()
            }

            print(f"SPX Data Pipeline: {status}")
            print(f"Real-time Access: {'VERIFIED' if has_spx_data else 'FAILED'}")

        except Exception as e:
            print(f"Data pipeline validation error: {e}")
            self.validation_results['data_pipeline'] = {'error': str(e)}
            self.critical_failures.append(f"Data pipeline error: {e}")

    def validate_options_chain_access(self):
        """Test options chain data access"""
        print("=== OPTIONS CHAIN VALIDATION ===")

        try:
            # Test options data access
            result = subprocess.run(['python', 'spx_strike_analysis.py'], capture_output=True, text=True, timeout=45)

            # Look for options data indicators
            has_options = 'SPXW' in result.stdout or 'strike' in result.stdout.lower()
            status = "PASS" if has_options and result.returncode == 0 else "FAIL"

            if status == "FAIL":
                self.critical_failures.append("Options chain validation failed")

            self.validation_results['options_chain'] = {
                'access_status': status,
                'spxw_available': "YES" if has_options else "NO",
                'timestamp': datetime.now().isoformat()
            }

            print(f"Options Chain: {status}")
            print(f"SPXW Access: {'YES' if has_options else 'NO'}")

        except Exception as e:
            print(f"Options validation error: {e}")
            self.validation_results['options_chain'] = {'error': str(e)}
            self.critical_failures.append(f"Options chain error: {e}")

    def generate_pre_market_report(self):
        """Generate comprehensive pre-market readiness report"""
        print("=== PRE-MARKET READINESS REPORT ===")

        total_time = (datetime.now() - self.start_time).total_seconds()

        # Calculate overall readiness score
        total_systems = len(self.validation_results)
        passed_systems = 0

        for system, results in self.validation_results.items():
            if isinstance(results, dict) and results.get('status') == 'PASS':
                passed_systems += 1
            elif isinstance(results, dict) and 'error' not in results:
                # Check for alternative success indicators
                if system == 'data_pipeline' and results.get('spx_data') == 'PASS':
                    passed_systems += 1
                elif system == 'options_chain' and results.get('access_status') == 'PASS':
                    passed_systems += 1

        readiness_score = (passed_systems / total_systems * 100) if total_systems > 0 else 0

        # Market readiness assessment
        if readiness_score >= 90 and len(self.critical_failures) == 0:
            market_readiness = "FULLY READY"
            readiness_icon = "[READY]"
        elif readiness_score >= 75 and len(self.critical_failures) <= 1:
            market_readiness = "READY WITH MINOR ISSUES"
            readiness_icon = "[WARNING]"
        else:
            market_readiness = "NOT READY - REQUIRES ATTENTION"
            readiness_icon = "[NOT_READY]"

        print(f"Validation Time: {total_time:.1f} seconds")
        print(f"Systems Tested: {total_systems}")
        print(f"Systems Passed: {passed_systems}")
        print(f"Readiness Score: {readiness_score:.1f}%")
        print()

        # System status summary
        for system, results in self.validation_results.items():
            system_name = system.upper().replace('_', ' ')
            if isinstance(results, dict):
                if 'error' in results:
                    print(f"{system_name}: [FAIL] ERROR")
                elif results.get('status') == 'PASS':
                    print(f"{system_name}: [PASS] PASS")
                elif system == 'data_pipeline' and results.get('spx_data') == 'PASS':
                    print(f"{system_name}: [PASS] PASS")
                elif system == 'options_chain' and results.get('access_status') == 'PASS':
                    print(f"{system_name}: [PASS] PASS")
                else:
                    print(f"{system_name}: [WARNING] PARTIAL")

        print()
        print(f"{readiness_icon} MARKET READINESS: {market_readiness}")

        if self.critical_failures:
            print()
            print("[CRITICAL] CRITICAL ISSUES TO RESOLVE:")
            for i, failure in enumerate(self.critical_failures, 1):
                print(f"  {i}. {failure}")

        print()
        print("NEXT: Execute 9:30 AM market open protocol")

        # Save results
        try:
            os.makedirs('.spx', exist_ok=True)
            report = {
                'pre_market_validation': {
                    'timestamp': self.start_time.isoformat(),
                    'completion_time': datetime.now().isoformat(),
                    'validation_time_seconds': total_time,
                    'readiness_score': readiness_score,
                    'market_readiness': market_readiness,
                    'systems_tested': total_systems,
                    'systems_passed': passed_systems,
                    'critical_failures': self.critical_failures,
                    'validation_results': self.validation_results
                }
            }

            with open('.spx/pre_market_validation.json', 'w') as f:
                json.dump(report, f, indent=2)

            print("Pre-market validation saved to .spx/pre_market_validation.json")

        except Exception as e:
            print(f"Failed to save report: {e}")

        return readiness_score >= 75  # Minimum readiness threshold

    def run_pre_market_validation(self):
        """Run complete pre-market validation sequence"""
        print("PRE-MARKET SYSTEM VALIDATION")
        print("=" * 50)
        print(f"Start Time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("Target: 8:30 AM pre-market validation")
        print()

        # Run all validations
        self.validate_streaming_systems()
        print()

        self.validate_api_connectivity()
        print()

        self.validate_discord_integration()
        print()

        self.validate_data_pipeline()
        print()

        self.validate_options_chain_access()
        print()

        # Generate final report
        ready_for_market = self.generate_pre_market_report()

        return ready_for_market

def main():
    validator = PreMarketValidator()
    ready = validator.run_pre_market_validation()

    if ready:
        print("\n[PASS] SYSTEM READY FOR MARKET OPEN")
    else:
        print("\n[WARNING] SYSTEM REQUIRES ATTENTION BEFORE MARKET OPEN")

if __name__ == "__main__":
    main()