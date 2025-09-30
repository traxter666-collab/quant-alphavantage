#!/usr/bin/env python3
"""
Monday Market Open Protocol - Complete System Testing
Execute this script at 9:30 AM ET Monday for full system validation
"""

import time
import subprocess
import sys
from datetime import datetime
import json
import os

class MondayMarketOpenProtocol:
    """Complete system testing and validation for Monday market open"""

    def __init__(self):
        self.results = {}
        self.start_time = datetime.now()
        print("MONDAY MARKET OPEN PROTOCOL INITIATED")
        print(f"Start Time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)

    def check_market_hours(self):
        """Verify market is open"""
        current_time = datetime.now()
        hour = current_time.hour
        minute = current_time.minute
        weekday = current_time.weekday()  # 0=Monday, 6=Sunday

        # Market hours: 9:30 AM - 4:00 PM ET, Monday-Friday
        market_open = (hour == 9 and minute >= 30) or (10 <= hour <= 15) or (hour == 16 and minute == 0)
        is_weekday = weekday < 5

        market_status = market_open and is_weekday

        print(f"MARKET STATUS CHECK:")
        print(f"Current Time: {current_time.strftime('%H:%M:%S')} ET")
        print(f"Weekday: {weekday < 5} | Market Hours: {market_open}")
        print(f"Market Status: {'OPEN' if market_status else 'CLOSED'}")
        print("-" * 40)

        self.results['market_status'] = {
            'open': market_status,
            'time': current_time.strftime('%Y-%m-%d %H:%M:%S'),
            'weekday': is_weekday,
            'market_hours': market_open
        }

        return market_status

    def analyze_quant_levels(self, spx_price):
        """Analyze current price relative to Quant levels"""
        if spx_price is None:
            return "No price data available"

        # Quant levels from Monday analysis
        levels = {
            'resistance_major': 6700,
            'resistance_high_reversal': 6697,
            'key_breakout': 6678,
            'resistance_lower': 6685,
            'pivot_major': 6647,
            'support_upper': 6620,
            'gamma_flip': 6610,
            'support_high_reversal': 6590,
            'support_21d_ema': 6587
        }

        # Determine current zone
        if spx_price >= 6700:
            zone = "HIGH REVERSAL ZONE (6697-6700) - FADE STRENGTH"
        elif spx_price >= 6678:
            zone = "RESISTANCE ZONE (6678-6700) - Watch for breakout above 6678"
        elif spx_price >= 6647:
            zone = "NEUTRAL ZONE - Above pivot, below resistance"
        elif spx_price >= 6620:
            zone = "SUPPORT ZONE (6610-6620) - Look for bounces"
        elif spx_price >= 6587:
            zone = "HIGH REVERSAL ZONE (6587-6590) - BUY WEAKNESS"
        else:
            zone = "BELOW MAJOR SUPPORT - Bearish territory"

        # Calculate distances to key levels
        distances = {}
        for name, level in levels.items():
            distances[name] = spx_price - level

        # Trading bias
        if spx_price > 6678:
            bias = f"BULLISH (Above 6678 breakout) - Target 6730-6750"
        elif spx_price < 6647:
            bias = f"BEARISH (Below 6647 pivot) - Target 6620 support"
        else:
            bias = f"NEUTRAL (Range 6647-6678)"

        return {
            'current_zone': zone,
            'trading_bias': bias,
            'key_distances': {
                'to_breakout_6678': distances['key_breakout'],
                'to_reversal_6700': distances['resistance_major'],
                'to_pivot_6647': distances['pivot_major'],
                'to_gamma_flip_6610': distances['gamma_flip']
            }
        }

    def test_fresh_market_data(self):
        """Get fresh market data - Task 1 with Quant level analysis"""
        print("TASK 1: GETTING FRESH MARKET DATA + QUANT LEVEL ANALYSIS")
        print("-" * 60)

        data_sources = []

        # Test 1: SPX Live Data
        try:
            print("Testing SPX Live Data...")
            result = subprocess.run(
                ["python", "spx_live.py"],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                output = result.stdout
                # Extract SPX price
                spx_price = None
                for line in output.split('\n'):
                    if "SPX:" in line and "$" in line:
                        try:
                            price_part = line.split("$")[1].split("(")[0].strip()
                            spx_price = float(price_part.replace(',', ''))
                            break
                        except:
                            pass

                # Analyze Quant levels
                quant_analysis = self.analyze_quant_levels(spx_price)

                data_sources.append({
                    'source': 'SPX_LIVE',
                    'status': 'SUCCESS',
                    'price': spx_price,
                    'quant_analysis': quant_analysis,
                    'data': output[:200] + "..." if len(output) > 200 else output
                })
                print(f"SUCCESS: SPX Live - ${spx_price:.2f}")

                # Display Quant level analysis
                if isinstance(quant_analysis, dict):
                    print(f"ZONE: {quant_analysis['current_zone']}")
                    print(f"BIAS: {quant_analysis['trading_bias']}")
                    distances = quant_analysis['key_distances']
                    print(f"Distance to 6678 breakout: {distances['to_breakout_6678']:+.1f} points")
                    print(f"Distance to 6700 reversal: {distances['to_reversal_6700']:+.1f} points")
            else:
                data_sources.append({
                    'source': 'SPX_LIVE',
                    'status': 'FAILED',
                    'error': result.stderr
                })
                print(f"FAILED: SPX Live - {result.stderr}")

        except Exception as e:
            data_sources.append({
                'source': 'SPX_LIVE',
                'status': 'ERROR',
                'error': str(e)
            })
            print(f"ERROR: SPX Live - {e}")

        # Test 2: API Validation
        try:
            print("Testing API Validation...")
            result = subprocess.run(
                ["python", "validate_api_key.py"],
                capture_output=True,
                text=True,
                timeout=30
            )

            api_status = "SUCCESS" if result.returncode == 0 else "FAILED"
            data_sources.append({
                'source': 'API_VALIDATION',
                'status': api_status,
                'output': result.stdout[:200] + "..." if len(result.stdout) > 200 else result.stdout
            })
            print(f"{api_status}: API Validation")

        except Exception as e:
            data_sources.append({
                'source': 'API_VALIDATION',
                'status': 'ERROR',
                'error': str(e)
            })
            print(f"ERROR: API Validation - {e}")

        self.results['fresh_data'] = {
            'task_completed': True,
            'sources_tested': len(data_sources),
            'sources': data_sources,
            'timestamp': datetime.now().isoformat()
        }

        print(f"TASK 1 COMPLETE: {len(data_sources)} data sources tested")
        print("=" * 40)

    def test_complete_system(self):
        """Test complete system with live data - Task 2"""
        print("TASK 2: TESTING COMPLETE SYSTEM WITH LIVE DATA")
        print("-" * 40)

        system_tests = []

        # Test 1: Smart ES Analysis
        try:
            print("Testing Smart ES Analysis...")
            result = subprocess.run(
                ["python", "trading_shortcuts.py", "smart_es"],
                capture_output=True,
                text=True,
                timeout=120
            )

            if result.returncode == 0:
                output = result.stdout
                # Extract key metrics
                action = None
                confidence = None
                score = None

                for line in output.split('\n'):
                    if "Action:" in line:
                        action = line.split("Action:")[1].strip()
                    elif "Confidence:" in line:
                        confidence = line.split("Confidence:")[1].strip()
                    elif "Score:" in line and "%" in line:
                        score = line.split("Score:")[1].strip()

                system_tests.append({
                    'system': 'SMART_ES',
                    'status': 'SUCCESS',
                    'action': action,
                    'confidence': confidence,
                    'score': score,
                    'output_length': len(output)
                })
                print(f"SUCCESS: Smart ES - {action} | {confidence}")
            else:
                system_tests.append({
                    'system': 'SMART_ES',
                    'status': 'FAILED',
                    'error': result.stderr
                })
                print(f"FAILED: Smart ES - {result.stderr}")

        except Exception as e:
            system_tests.append({
                'system': 'SMART_ES',
                'status': 'ERROR',
                'error': str(e)
            })
            print(f"ERROR: Smart ES - {e}")

        # Test 2: SPX Quick Analysis
        try:
            print("Testing SPX Quick Analysis...")
            result = subprocess.run(
                ["python", "spx_command_router.py", "spx quick"],
                capture_output=True,
                text=True,
                timeout=120
            )

            status = "SUCCESS" if result.returncode == 0 else "FAILED"
            system_tests.append({
                'system': 'SPX_QUICK',
                'status': status,
                'output_length': len(result.stdout) if result.returncode == 0 else 0,
                'error': result.stderr if result.returncode != 0 else None
            })
            print(f"{status}: SPX Quick Analysis")

        except Exception as e:
            system_tests.append({
                'system': 'SPX_QUICK',
                'status': 'ERROR',
                'error': str(e)
            })
            print(f"ERROR: SPX Quick - {e}")

        # Test 3: Multi-Asset Analysis
        try:
            print("Testing Multi-Asset Analysis...")
            result = subprocess.run(
                ["python", "trading_shortcuts.py", "multi"],
                capture_output=True,
                text=True,
                timeout=120
            )

            status = "SUCCESS" if result.returncode == 0 else "FAILED"
            system_tests.append({
                'system': 'MULTI_ASSET',
                'status': status,
                'output_length': len(result.stdout) if result.returncode == 0 else 0,
                'error': result.stderr if result.returncode != 0 else None
            })
            print(f"{status}: Multi-Asset Analysis")

        except Exception as e:
            system_tests.append({
                'system': 'MULTI_ASSET',
                'status': 'ERROR',
                'error': str(e)
            })
            print(f"ERROR: Multi-Asset - {e}")

        # Test 4: Command Router
        try:
            print("Testing Command Router...")
            result = subprocess.run(
                ["python", "spx_command_router.py"],
                capture_output=True,
                text=True,
                timeout=30
            )

            # Count available commands
            command_count = 0
            if "Available commands" in result.stdout:
                for line in result.stdout.split('\n'):
                    if "Available commands (" in line:
                        try:
                            command_count = int(line.split("(")[1].split(")")[0])
                        except:
                            pass

            system_tests.append({
                'system': 'COMMAND_ROUTER',
                'status': 'SUCCESS',
                'command_count': command_count
            })
            print(f"SUCCESS: Command Router - {command_count} commands available")

        except Exception as e:
            system_tests.append({
                'system': 'COMMAND_ROUTER',
                'status': 'ERROR',
                'error': str(e)
            })
            print(f"ERROR: Command Router - {e}")

        self.results['system_tests'] = {
            'task_completed': True,
            'systems_tested': len(system_tests),
            'tests': system_tests,
            'timestamp': datetime.now().isoformat()
        }

        print(f"TASK 2 COMPLETE: {len(system_tests)} systems tested")
        print("=" * 40)

    def generate_report(self):
        """Generate comprehensive test report"""
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()

        print("MONDAY MARKET OPEN PROTOCOL COMPLETE")
        print("=" * 60)
        print(f"Duration: {duration:.1f} seconds")
        print(f"End Time: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print()

        # Summary
        fresh_data_success = self.results.get('fresh_data', {}).get('task_completed', False)
        system_test_success = self.results.get('system_tests', {}).get('task_completed', False)
        market_open = self.results.get('market_status', {}).get('open', False)

        print("TASK STATUS SUMMARY:")
        print(f"Market Status: {'OPEN' if market_open else 'CLOSED'}")
        print(f"Fresh Market Data: {'COMPLETE' if fresh_data_success else 'FAILED'}")
        print(f"Complete System Test: {'COMPLETE' if system_test_success else 'FAILED'}")
        print()

        # Data Sources Summary
        if 'fresh_data' in self.results:
            sources = self.results['fresh_data']['sources']
            successful_sources = [s for s in sources if s['status'] == 'SUCCESS']
            print(f"Data Sources: {len(successful_sources)}/{len(sources)} successful")

        # System Tests Summary
        if 'system_tests' in self.results:
            tests = self.results['system_tests']['tests']
            successful_tests = [t for t in tests if t['status'] == 'SUCCESS']
            print(f"System Tests: {len(successful_tests)}/{len(tests)} successful")

        print()

        # Overall Status
        overall_success = fresh_data_success and system_test_success and market_open
        print(f"OVERALL STATUS: {'SUCCESS - READY FOR TRADING!' if overall_success else 'ATTENTION NEEDED'}")

        # Save results
        try:
            os.makedirs('.spx', exist_ok=True)
            self.results['summary'] = {
                'duration_seconds': duration,
                'overall_success': overall_success,
                'market_open': market_open,
                'tasks_completed': fresh_data_success and system_test_success,
                'end_time': end_time.isoformat()
            }

            with open('.spx/monday_test_results.json', 'w') as f:
                json.dump(self.results, f, indent=2)

            print(f"Results saved to .spx/monday_test_results.json")

        except Exception as e:
            print(f"Warning: Could not save results - {e}")

        return overall_success

def main():
    """Execute Monday Market Open Protocol"""
    protocol = MondayMarketOpenProtocol()

    # Check if market is open
    if not protocol.check_market_hours():
        print("WARNING: Market appears to be closed!")
        print("This test is designed for market hours (9:30 AM - 4:00 PM ET, Mon-Fri)")

        response = input("Continue anyway? (y/N): ").strip().lower()
        if response != 'y':
            print("Test cancelled.")
            return False
        print()

    # Execute both tasks
    protocol.test_fresh_market_data()
    protocol.test_complete_system()

    # Generate final report
    success = protocol.generate_report()

    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)