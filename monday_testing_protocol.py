#!/usr/bin/env python3
"""
Monday Testing Protocol - Comprehensive Live Market Validation
Complete testing framework for live market deployment validation
"""

import os
import json
import time
import subprocess
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

class MondayTestingProtocol:
    """Comprehensive Monday market testing protocol"""

    def __init__(self):
        self.test_results = {}
        self.start_time = None
        self.session_file = '.spx/monday_testing_results.json'

        # Test configuration
        self.critical_tests = [
            'api_connectivity',
            'real_time_data',
            'multi_asset_analysis',
            'ndx_integration',
            'performance_metrics',
            'error_handling',
            'discord_integration'
        ]

        self.performance_benchmarks = {
            'api_response_time': 2.0,  # seconds
            'analysis_completion': 30.0,  # seconds
            'system_health': 95.0,  # percentage
            'data_accuracy': 99.0  # percentage
        }

        print("Monday Testing Protocol initialized")
        print("Ready for comprehensive live market validation")

    def create_test_schedule(self) -> Dict[str, Any]:
        """Create comprehensive testing schedule for Monday"""

        # Market hours: 9:30 AM - 4:00 PM ET
        market_open = datetime.now().replace(hour=9, minute=30, second=0, microsecond=0)
        market_close = datetime.now().replace(hour=16, minute=0, second=0, microsecond=0)

        schedule = {
            'pre_market_tests': {
                'start_time': market_open - timedelta(hours=1),
                'duration': 30,  # minutes
                'tests': [
                    'system_health_check',
                    'api_connectivity_validation',
                    'data_source_verification',
                    'performance_baseline'
                ]
            },
            'market_open_tests': {
                'start_time': market_open,
                'duration': 30,  # minutes
                'tests': [
                    'live_data_validation',
                    'high_frequency_performance',
                    'multi_asset_coordination',
                    'real_time_analysis'
                ]
            },
            'mid_session_tests': {
                'start_time': market_open + timedelta(hours=2),
                'duration': 15,  # minutes
                'tests': [
                    'sustained_performance',
                    'accuracy_validation',
                    'system_stability'
                ]
            },
            'end_of_day_tests': {
                'start_time': market_close - timedelta(minutes=30),
                'duration': 30,  # minutes
                'tests': [
                    'session_persistence',
                    'data_integrity',
                    'comprehensive_report'
                ]
            }
        }

        return schedule

    def run_pre_market_validation(self) -> Dict[str, Any]:
        """Run pre-market system validation"""

        print("PRE-MARKET VALIDATION")
        print("=" * 40)
        print("Testing system readiness before market open...")

        validation_results = {
            'timestamp': datetime.now().isoformat(),
            'tests': {},
            'overall_status': 'UNKNOWN'
        }

        # Test 1: System Health Check
        print("\n1. System Health Check...")
        try:
            result = subprocess.run(
                ['python', 'market_open_protocol.py'],
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode == 0 and "READY FOR LIVE TRADING" in result.stdout:
                validation_results['tests']['system_health'] = {
                    'status': 'PASS',
                    'details': 'System health check passed'
                }
                print("   SUCCESS - System health optimal")
            else:
                validation_results['tests']['system_health'] = {
                    'status': 'FAIL',
                    'details': result.stderr or 'Health check failed'
                }
                print("   WARNING - System health issues detected")

        except Exception as e:
            validation_results['tests']['system_health'] = {
                'status': 'ERROR',
                'details': str(e)
            }
            print(f"   ERROR - Health check failed: {e}")

        # Test 2: API Connectivity
        print("\n2. API Connectivity Validation...")
        try:
            result = subprocess.run(
                ['python', 'validate_api_key.py'],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                validation_results['tests']['api_connectivity'] = {
                    'status': 'PASS',
                    'details': 'API connectivity verified'
                }
                print("   SUCCESS - API connectivity confirmed")
            else:
                validation_results['tests']['api_connectivity'] = {
                    'status': 'FAIL',
                    'details': 'API connectivity issues'
                }
                print("   WARNING - API connectivity problems")

        except Exception as e:
            validation_results['tests']['api_connectivity'] = {
                'status': 'ERROR',
                'details': str(e)
            }
            print(f"   ERROR - API test failed: {e}")

        # Test 3: Performance Baseline
        print("\n3. Performance Baseline...")
        try:
            result = subprocess.run(
                ['python', 'performance_optimizer.py'],
                capture_output=True,
                text=True,
                timeout=45
            )

            if result.returncode == 0:
                validation_results['tests']['performance_baseline'] = {
                    'status': 'PASS',
                    'details': 'Performance baseline established'
                }
                print("   SUCCESS - Performance baseline set")
            else:
                validation_results['tests']['performance_baseline'] = {
                    'status': 'FAIL',
                    'details': 'Performance baseline issues'
                }
                print("   WARNING - Performance concerns")

        except Exception as e:
            validation_results['tests']['performance_baseline'] = {
                'status': 'ERROR',
                'details': str(e)
            }
            print(f"   ERROR - Performance test failed: {e}")

        # Calculate overall status
        passed_tests = sum(1 for test in validation_results['tests'].values() if test['status'] == 'PASS')
        total_tests = len(validation_results['tests'])

        if passed_tests == total_tests:
            validation_results['overall_status'] = 'READY'
        elif passed_tests >= total_tests * 0.8:
            validation_results['overall_status'] = 'CAUTION'
        else:
            validation_results['overall_status'] = 'NOT_READY'

        print(f"\nPRE-MARKET VALIDATION COMPLETE")
        print(f"Status: {validation_results['overall_status']}")
        print(f"Tests Passed: {passed_tests}/{total_tests}")

        return validation_results

    def run_live_market_validation(self) -> Dict[str, Any]:
        """Run live market validation during trading hours"""

        print("\nLIVE MARKET VALIDATION")
        print("=" * 40)
        print("Testing with live market data...")

        live_results = {
            'timestamp': datetime.now().isoformat(),
            'tests': {},
            'performance_metrics': {},
            'data_samples': {}
        }

        # Test 1: Real-time Data Accuracy
        print("\n1. Real-time Data Accuracy...")
        start_time = time.time()

        try:
            # Test SPX analysis
            result = subprocess.run(
                ['python', 'spx_command_router.py', 'spx now'],
                capture_output=True,
                text=True,
                timeout=30
            )

            response_time = time.time() - start_time

            if result.returncode == 0:
                live_results['tests']['spx_analysis'] = {
                    'status': 'PASS',
                    'response_time': response_time,
                    'details': 'SPX analysis completed successfully'
                }
                print(f"   SUCCESS - SPX analysis ({response_time:.2f}s)")
            else:
                live_results['tests']['spx_analysis'] = {
                    'status': 'FAIL',
                    'response_time': response_time,
                    'details': result.stderr or 'SPX analysis failed'
                }
                print(f"   FAIL - SPX analysis failed ({response_time:.2f}s)")

        except Exception as e:
            live_results['tests']['spx_analysis'] = {
                'status': 'ERROR',
                'details': str(e)
            }
            print(f"   ERROR - SPX analysis: {e}")

        # Test 2: NDX Integration
        print("\n2. NDX Integration...")
        start_time = time.time()

        try:
            result = subprocess.run(
                ['python', 'spx_command_router.py', 'ndx analysis'],
                capture_output=True,
                text=True,
                timeout=30
            )

            response_time = time.time() - start_time

            if result.returncode == 0 and "NDX TRADING RECOMMENDATION" in result.stdout:
                live_results['tests']['ndx_integration'] = {
                    'status': 'PASS',
                    'response_time': response_time,
                    'details': 'NDX integration working'
                }
                print(f"   SUCCESS - NDX integration ({response_time:.2f}s)")
            else:
                live_results['tests']['ndx_integration'] = {
                    'status': 'FAIL',
                    'response_time': response_time,
                    'details': 'NDX integration issues'
                }
                print(f"   FAIL - NDX integration problems ({response_time:.2f}s)")

        except Exception as e:
            live_results['tests']['ndx_integration'] = {
                'status': 'ERROR',
                'details': str(e)
            }
            print(f"   ERROR - NDX integration: {e}")

        # Test 3: Multi-Asset Performance
        print("\n3. Multi-Asset System...")
        start_time = time.time()

        try:
            result = subprocess.run(
                ['python', 'spx_command_router.py', 'spx systems check'],
                capture_output=True,
                text=True,
                timeout=60
            )

            response_time = time.time() - start_time

            if result.returncode == 0 and "100.0%" in result.stdout:
                live_results['tests']['multi_asset'] = {
                    'status': 'PASS',
                    'response_time': response_time,
                    'details': 'Multi-asset system operational'
                }
                print(f"   SUCCESS - Multi-asset system ({response_time:.2f}s)")
            else:
                live_results['tests']['multi_asset'] = {
                    'status': 'FAIL',
                    'response_time': response_time,
                    'details': 'Multi-asset system issues'
                }
                print(f"   FAIL - Multi-asset problems ({response_time:.2f}s)")

        except Exception as e:
            live_results['tests']['multi_asset'] = {
                'status': 'ERROR',
                'details': str(e)
            }
            print(f"   ERROR - Multi-asset system: {e}")

        # Test 4: Performance Under Load
        print("\n4. Performance Under Load...")
        start_time = time.time()

        try:
            # Run multiple commands quickly
            commands = [
                'spx quick',
                'ndx analysis',
                'spx consensus score'
            ]

            total_start = time.time()
            command_times = []

            for cmd in commands:
                cmd_start = time.time()
                result = subprocess.run(
                    ['python', 'spx_command_router.py', cmd],
                    capture_output=True,
                    text=True,
                    timeout=20
                )
                cmd_time = time.time() - cmd_start
                command_times.append(cmd_time)

            total_time = time.time() - total_start
            avg_time = sum(command_times) / len(command_times)

            live_results['performance_metrics'] = {
                'total_time': total_time,
                'average_command_time': avg_time,
                'commands_tested': len(commands),
                'throughput': len(commands) / total_time
            }

            if avg_time < self.performance_benchmarks['api_response_time']:
                live_results['tests']['performance_load'] = {
                    'status': 'PASS',
                    'details': f'Average response: {avg_time:.2f}s'
                }
                print(f"   SUCCESS - Performance acceptable ({avg_time:.2f}s avg)")
            else:
                live_results['tests']['performance_load'] = {
                    'status': 'WARN',
                    'details': f'Slow response: {avg_time:.2f}s'
                }
                print(f"   WARNING - Performance slow ({avg_time:.2f}s avg)")

        except Exception as e:
            live_results['tests']['performance_load'] = {
                'status': 'ERROR',
                'details': str(e)
            }
            print(f"   ERROR - Performance test: {e}")

        return live_results

    def run_comprehensive_validation(self) -> Dict[str, Any]:
        """Run complete Monday testing protocol"""

        print("MONDAY COMPREHENSIVE TESTING PROTOCOL")
        print("=" * 50)
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        self.start_time = time.time()

        # Initialize results
        comprehensive_results = {
            'test_session': {
                'start_time': datetime.now().isoformat(),
                'protocol_version': '1.0',
                'test_type': 'COMPREHENSIVE_MONDAY_VALIDATION'
            },
            'pre_market': {},
            'live_market': {},
            'summary': {}
        }

        # Run pre-market validation
        print(f"\nPhase 1: Pre-Market Validation")
        comprehensive_results['pre_market'] = self.run_pre_market_validation()

        # Check if system is ready for live testing
        if comprehensive_results['pre_market']['overall_status'] in ['READY', 'CAUTION']:
            print(f"\nPhase 2: Live Market Validation")
            comprehensive_results['live_market'] = self.run_live_market_validation()
        else:
            print(f"\nSKIPPING LIVE MARKET TESTS - System not ready")
            comprehensive_results['live_market'] = {
                'status': 'SKIPPED',
                'reason': 'Pre-market validation failed'
            }

        # Generate summary
        comprehensive_results['summary'] = self.generate_test_summary(comprehensive_results)

        # Save results
        try:
            os.makedirs('.spx', exist_ok=True)
            with open(self.session_file, 'w') as f:
                json.dump(comprehensive_results, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save results: {e}")

        return comprehensive_results

    def generate_test_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive test summary"""

        summary = {
            'overall_status': 'UNKNOWN',
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'error_tests': 0,
            'test_duration': time.time() - self.start_time if self.start_time else 0,
            'recommendations': [],
            'critical_issues': [],
            'performance_assessment': 'UNKNOWN'
        }

        # Count tests from pre-market
        if 'tests' in results.get('pre_market', {}):
            for test_name, test_result in results['pre_market']['tests'].items():
                summary['total_tests'] += 1
                if test_result['status'] == 'PASS':
                    summary['passed_tests'] += 1
                elif test_result['status'] == 'FAIL':
                    summary['failed_tests'] += 1
                elif test_result['status'] == 'ERROR':
                    summary['error_tests'] += 1

        # Count tests from live market
        if 'tests' in results.get('live_market', {}):
            for test_name, test_result in results['live_market']['tests'].items():
                summary['total_tests'] += 1
                if test_result['status'] == 'PASS':
                    summary['passed_tests'] += 1
                elif test_result['status'] == 'FAIL':
                    summary['failed_tests'] += 1
                elif test_result['status'] == 'ERROR':
                    summary['error_tests'] += 1

        # Calculate overall status
        if summary['total_tests'] > 0:
            pass_rate = summary['passed_tests'] / summary['total_tests']
            if pass_rate >= 0.9:
                summary['overall_status'] = 'EXCELLENT'
            elif pass_rate >= 0.8:
                summary['overall_status'] = 'GOOD'
            elif pass_rate >= 0.7:
                summary['overall_status'] = 'FAIR'
            else:
                summary['overall_status'] = 'POOR'

        # Performance assessment
        if 'performance_metrics' in results.get('live_market', {}):
            metrics = results['live_market']['performance_metrics']
            avg_time = metrics.get('average_command_time', 999)
            if avg_time < 1.0:
                summary['performance_assessment'] = 'EXCELLENT'
            elif avg_time < 2.0:
                summary['performance_assessment'] = 'GOOD'
            elif avg_time < 5.0:
                summary['performance_assessment'] = 'FAIR'
            else:
                summary['performance_assessment'] = 'POOR'

        # Generate recommendations
        if summary['failed_tests'] > 0:
            summary['recommendations'].append("Review failed tests and address issues")
        if summary['error_tests'] > 0:
            summary['recommendations'].append("Investigate error conditions")
        if summary['performance_assessment'] in ['FAIR', 'POOR']:
            summary['recommendations'].append("Optimize system performance")

        return summary

def main():
    """Run Monday testing protocol"""
    testing_protocol = MondayTestingProtocol()

    # Show test schedule
    schedule = testing_protocol.create_test_schedule()
    print("MONDAY TESTING SCHEDULE:")
    print("=" * 30)
    for phase, config in schedule.items():
        start_time = config['start_time'].strftime('%H:%M')
        duration = config['duration']
        print(f"{phase.replace('_', ' ').title()}: {start_time} ({duration}min)")
        for test in config['tests']:
            print(f"  - {test.replace('_', ' ').title()}")
        print()

    # Run comprehensive validation
    results = testing_protocol.run_comprehensive_validation()

    # Display final summary
    summary = results['summary']
    print(f"\n{'='*50}")
    print("MONDAY TESTING PROTOCOL COMPLETE")
    print(f"{'='*50}")
    print(f"Overall Status: {summary['overall_status']}")
    print(f"Tests Passed: {summary['passed_tests']}/{summary['total_tests']}")
    print(f"Performance: {summary['performance_assessment']}")
    print(f"Duration: {summary['test_duration']:.1f} seconds")

    if summary['recommendations']:
        print(f"\nRecommendations:")
        for rec in summary['recommendations']:
            print(f"- {rec}")

    print(f"\nResults saved to: .spx/monday_testing_results.json")

if __name__ == "__main__":
    main()