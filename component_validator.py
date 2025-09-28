#!/usr/bin/env python3
"""
Component Validator - Specific Feature Testing
Validates individual system components and features
"""

import os
import json
import subprocess
import time
from datetime import datetime
from typing import Dict, List, Any, Optional

class ComponentValidator:
    """Validates specific system components and features"""

    def __init__(self):
        self.validation_results = {}
        self.session_file = '.spx/component_validation_results.json'

        # Component test definitions
        self.component_tests = {
            'api_integration': {
                'description': 'AlphaVantage API integration and data quality',
                'critical': True,
                'timeout': 30
            },
            'ndx_analysis': {
                'description': 'NDX (NASDAQ-100) analysis integration',
                'critical': True,
                'timeout': 45
            },
            'multi_asset_coordination': {
                'description': 'Five-asset system coordination (SPX+QQQ+SPY+IWM+NDX)',
                'critical': True,
                'timeout': 60
            },
            'volatility_intelligence': {
                'description': 'VIX regime analysis and position sizing',
                'critical': False,
                'timeout': 30
            },
            'news_sentiment': {
                'description': 'Real-time news sentiment analysis',
                'critical': False,
                'timeout': 30
            },
            'market_microstructure': {
                'description': 'Order flow and institutional detection',
                'critical': False,
                'timeout': 30
            },
            'dealer_positioning': {
                'description': 'Heatseeker dealer positioning analysis',
                'critical': False,
                'timeout': 45
            },
            'performance_optimization': {
                'description': 'High-frequency trading performance',
                'critical': True,
                'timeout': 60
            },
            'discord_integration': {
                'description': 'Discord webhook integration',
                'critical': False,
                'timeout': 20
            },
            'error_handling': {
                'description': 'System error handling and recovery',
                'critical': True,
                'timeout': 120
            }
        }

        print("Component Validator initialized")
        print(f"Configured to test {len(self.component_tests)} components")

    def validate_api_integration(self) -> Dict[str, Any]:
        """Validate AlphaVantage API integration"""

        print("Testing API Integration...")

        test_result = {
            'component': 'api_integration',
            'status': 'UNKNOWN',
            'details': {},
            'timestamp': datetime.now().isoformat()
        }

        try:
            # Test API key validation
            result = subprocess.run(
                ['python', 'validate_api_key.py'],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                test_result['details']['api_key_validation'] = 'PASS'
                print("  SUCCESS - API key validation")
            else:
                test_result['details']['api_key_validation'] = 'FAIL'
                print("  FAIL - API key validation")

            # Test real-time data access
            result = subprocess.run(
                ['python', 'simple_api_test.py'],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                test_result['details']['real_time_access'] = 'PASS'
                print("  SUCCESS - Real-time data access")
            else:
                test_result['details']['real_time_access'] = 'FAIL'
                print("  FAIL - Real-time data access")

            # Overall status
            if all(status == 'PASS' for status in test_result['details'].values()):
                test_result['status'] = 'PASS'
            else:
                test_result['status'] = 'FAIL'

        except Exception as e:
            test_result['status'] = 'ERROR'
            test_result['error'] = str(e)
            print(f"  ERROR - API integration test: {e}")

        return test_result

    def validate_ndx_analysis(self) -> Dict[str, Any]:
        """Validate NDX analysis integration"""

        print("Testing NDX Analysis...")

        test_result = {
            'component': 'ndx_analysis',
            'status': 'UNKNOWN',
            'details': {},
            'timestamp': datetime.now().isoformat()
        }

        try:
            start_time = time.time()

            # Test NDX analysis
            result = subprocess.run(
                ['python', 'ndx_integration.py'],
                capture_output=True,
                text=True,
                timeout=45
            )

            response_time = time.time() - start_time

            if result.returncode == 0:
                if "NDX TRADING RECOMMENDATION" in result.stdout:
                    test_result['status'] = 'PASS'
                    test_result['details']['analysis_output'] = 'COMPLETE'
                    print(f"  SUCCESS - NDX analysis ({response_time:.2f}s)")
                else:
                    test_result['status'] = 'FAIL'
                    test_result['details']['analysis_output'] = 'INCOMPLETE'
                    print(f"  FAIL - NDX analysis incomplete")
            else:
                test_result['status'] = 'FAIL'
                test_result['details']['error_output'] = result.stderr
                print(f"  FAIL - NDX analysis failed")

            test_result['details']['response_time'] = response_time

        except Exception as e:
            test_result['status'] = 'ERROR'
            test_result['error'] = str(e)
            print(f"  ERROR - NDX analysis test: {e}")

        return test_result

    def validate_multi_asset_coordination(self) -> Dict[str, Any]:
        """Validate multi-asset system coordination"""

        print("Testing Multi-Asset Coordination...")

        test_result = {
            'component': 'multi_asset_coordination',
            'status': 'UNKNOWN',
            'details': {},
            'timestamp': datetime.now().isoformat()
        }

        try:
            start_time = time.time()

            # Test five-asset integration
            result = subprocess.run(
                ['python', 'five_asset_integration.py'],
                capture_output=True,
                text=True,
                timeout=60
            )

            response_time = time.time() - start_time

            if result.returncode == 0:
                if "FIVE-ASSET SYSTEM ANALYSIS COMPLETE" in result.stdout:
                    test_result['status'] = 'PASS'
                    test_result['details']['integration_status'] = 'COMPLETE'

                    # Check for asset count in output
                    if "Total Assets:" in result.stdout:
                        asset_line = [line for line in result.stdout.split('\n') if 'Total Assets:' in line][0]
                        test_result['details']['assets_analyzed'] = asset_line.split(':')[1].strip()

                    print(f"  SUCCESS - Multi-asset coordination ({response_time:.2f}s)")
                else:
                    test_result['status'] = 'FAIL'
                    test_result['details']['integration_status'] = 'INCOMPLETE'
                    print(f"  FAIL - Multi-asset coordination incomplete")
            else:
                test_result['status'] = 'FAIL'
                test_result['details']['error_output'] = result.stderr
                print(f"  FAIL - Multi-asset coordination failed")

            test_result['details']['response_time'] = response_time

        except Exception as e:
            test_result['status'] = 'ERROR'
            test_result['error'] = str(e)
            print(f"  ERROR - Multi-asset coordination test: {e}")

        return test_result

    def validate_volatility_intelligence(self) -> Dict[str, Any]:
        """Validate volatility intelligence system"""

        print("Testing Volatility Intelligence...")

        test_result = {
            'component': 'volatility_intelligence',
            'status': 'UNKNOWN',
            'details': {},
            'timestamp': datetime.now().isoformat()
        }

        try:
            start_time = time.time()

            # Test volatility intelligence
            result = subprocess.run(
                ['python', 'volatility_intelligence.py'],
                capture_output=True,
                text=True,
                timeout=30
            )

            response_time = time.time() - start_time

            if result.returncode == 0:
                if "VOLATILITY INTELLIGENCE ANALYSIS" in result.stdout:
                    test_result['status'] = 'PASS'
                    test_result['details']['analysis_complete'] = True
                    print(f"  SUCCESS - Volatility intelligence ({response_time:.2f}s)")
                else:
                    test_result['status'] = 'FAIL'
                    test_result['details']['analysis_complete'] = False
                    print(f"  FAIL - Volatility intelligence incomplete")
            else:
                test_result['status'] = 'FAIL'
                test_result['details']['error_output'] = result.stderr
                print(f"  FAIL - Volatility intelligence failed")

            test_result['details']['response_time'] = response_time

        except Exception as e:
            test_result['status'] = 'ERROR'
            test_result['error'] = str(e)
            print(f"  ERROR - Volatility intelligence test: {e}")

        return test_result

    def validate_performance_optimization(self) -> Dict[str, Any]:
        """Validate performance optimization system"""

        print("Testing Performance Optimization...")

        test_result = {
            'component': 'performance_optimization',
            'status': 'UNKNOWN',
            'details': {},
            'timestamp': datetime.now().isoformat()
        }

        try:
            start_time = time.time()

            # Test performance optimization
            result = subprocess.run(
                ['python', 'performance_optimizer.py'],
                capture_output=True,
                text=True,
                timeout=60
            )

            response_time = time.time() - start_time

            if result.returncode == 0:
                if "PERFORMANCE OPTIMIZATION TEST" in result.stdout:
                    test_result['status'] = 'PASS'
                    test_result['details']['optimization_working'] = True

                    # Extract performance metrics if available
                    if "Average Response:" in result.stdout:
                        perf_line = [line for line in result.stdout.split('\n') if 'Average Response:' in line][0]
                        test_result['details']['avg_response_time'] = perf_line.split(':')[1].strip()

                    print(f"  SUCCESS - Performance optimization ({response_time:.2f}s)")
                else:
                    test_result['status'] = 'FAIL'
                    test_result['details']['optimization_working'] = False
                    print(f"  FAIL - Performance optimization incomplete")
            else:
                test_result['status'] = 'FAIL'
                test_result['details']['error_output'] = result.stderr
                print(f"  FAIL - Performance optimization failed")

            test_result['details']['response_time'] = response_time

        except Exception as e:
            test_result['status'] = 'ERROR'
            test_result['error'] = str(e)
            print(f"  ERROR - Performance optimization test: {e}")

        return test_result

    def validate_discord_integration(self) -> Dict[str, Any]:
        """Validate Discord integration"""

        print("Testing Discord Integration...")

        test_result = {
            'component': 'discord_integration',
            'status': 'UNKNOWN',
            'details': {},
            'timestamp': datetime.now().isoformat()
        }

        try:
            start_time = time.time()

            # Test Discord webhook
            result = subprocess.run(
                ['python', 'send_discord.py', 'Component Test', 'Testing Discord integration from component validator'],
                capture_output=True,
                text=True,
                timeout=20
            )

            response_time = time.time() - start_time

            if result.returncode == 0:
                if "SUCCESS" in result.stdout:
                    test_result['status'] = 'PASS'
                    test_result['details']['webhook_working'] = True
                    print(f"  SUCCESS - Discord integration ({response_time:.2f}s)")
                else:
                    test_result['status'] = 'FAIL'
                    test_result['details']['webhook_working'] = False
                    print(f"  FAIL - Discord webhook not responding")
            else:
                test_result['status'] = 'FAIL'
                test_result['details']['error_output'] = result.stderr
                print(f"  FAIL - Discord integration failed")

            test_result['details']['response_time'] = response_time

        except Exception as e:
            test_result['status'] = 'ERROR'
            test_result['error'] = str(e)
            print(f"  ERROR - Discord integration test: {e}")

        return test_result

    def validate_error_handling(self) -> Dict[str, Any]:
        """Validate error handling system"""

        print("Testing Error Handling...")

        test_result = {
            'component': 'error_handling',
            'status': 'UNKNOWN',
            'details': {},
            'timestamp': datetime.now().isoformat()
        }

        try:
            start_time = time.time()

            # Test error handling
            result = subprocess.run(
                ['python', 'error_handling_test.py'],
                capture_output=True,
                text=True,
                timeout=120
            )

            response_time = time.time() - start_time

            if result.returncode == 0:
                if "ERROR HANDLING TEST COMPLETE" in result.stdout:
                    test_result['status'] = 'PASS'
                    test_result['details']['error_handling_working'] = True

                    # Count SUCCESS vs WARNING/ERROR in output
                    success_count = result.stdout.count('SUCCESS')
                    warning_count = result.stdout.count('WARNING')
                    error_count = result.stdout.count('ERROR')

                    test_result['details']['test_summary'] = {
                        'success': success_count,
                        'warnings': warning_count,
                        'errors': error_count
                    }

                    print(f"  SUCCESS - Error handling ({response_time:.2f}s)")
                    print(f"    Results: {success_count} success, {warning_count} warnings, {error_count} errors")
                else:
                    test_result['status'] = 'FAIL'
                    test_result['details']['error_handling_working'] = False
                    print(f"  FAIL - Error handling incomplete")
            else:
                test_result['status'] = 'FAIL'
                test_result['details']['error_output'] = result.stderr
                print(f"  FAIL - Error handling failed")

            test_result['details']['response_time'] = response_time

        except Exception as e:
            test_result['status'] = 'ERROR'
            test_result['error'] = str(e)
            print(f"  ERROR - Error handling test: {e}")

        return test_result

    def run_selected_component_tests(self, components: List[str] = None) -> Dict[str, Any]:
        """Run validation tests for selected components"""

        if components is None:
            components = list(self.component_tests.keys())

        print("COMPONENT VALIDATION TESTING")
        print("=" * 40)
        print(f"Testing {len(components)} components...")
        print()

        validation_results = {
            'timestamp': datetime.now().isoformat(),
            'components_tested': len(components),
            'test_results': {},
            'summary': {}
        }

        # Define test methods
        test_methods = {
            'api_integration': self.validate_api_integration,
            'ndx_analysis': self.validate_ndx_analysis,
            'multi_asset_coordination': self.validate_multi_asset_coordination,
            'volatility_intelligence': self.validate_volatility_intelligence,
            'performance_optimization': self.validate_performance_optimization,
            'discord_integration': self.validate_discord_integration,
            'error_handling': self.validate_error_handling
        }

        # Run tests
        for component in components:
            if component in test_methods:
                print(f"\nTesting {component.replace('_', ' ').title()}...")
                test_result = test_methods[component]()
                validation_results['test_results'][component] = test_result
            else:
                print(f"\nSKIPPING {component} - Test method not implemented")
                validation_results['test_results'][component] = {
                    'status': 'SKIPPED',
                    'reason': 'Test method not implemented'
                }

        # Generate summary
        validation_results['summary'] = self.generate_validation_summary(validation_results['test_results'])

        # Save results
        try:
            os.makedirs('.spx', exist_ok=True)
            with open(self.session_file, 'w') as f:
                json.dump(validation_results, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save results: {e}")

        return validation_results

    def generate_validation_summary(self, test_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate validation summary"""

        summary = {
            'total_components': len(test_results),
            'passed': 0,
            'failed': 0,
            'errors': 0,
            'skipped': 0,
            'critical_issues': [],
            'recommendations': [],
            'overall_status': 'UNKNOWN'
        }

        for component, result in test_results.items():
            status = result.get('status', 'UNKNOWN')

            if status == 'PASS':
                summary['passed'] += 1
            elif status == 'FAIL':
                summary['failed'] += 1
                if self.component_tests.get(component, {}).get('critical', False):
                    summary['critical_issues'].append(f"Critical component {component} failed")
            elif status == 'ERROR':
                summary['errors'] += 1
                summary['critical_issues'].append(f"Component {component} had errors")
            elif status == 'SKIPPED':
                summary['skipped'] += 1

        # Calculate overall status
        if summary['critical_issues']:
            summary['overall_status'] = 'CRITICAL_ISSUES'
        elif summary['failed'] == 0 and summary['errors'] == 0:
            summary['overall_status'] = 'ALL_PASS'
        elif summary['passed'] > summary['failed'] + summary['errors']:
            summary['overall_status'] = 'MOSTLY_PASS'
        else:
            summary['overall_status'] = 'MULTIPLE_FAILURES'

        # Generate recommendations
        if summary['failed'] > 0:
            summary['recommendations'].append("Review and fix failed components")
        if summary['errors'] > 0:
            summary['recommendations'].append("Investigate error conditions")
        if summary['critical_issues']:
            summary['recommendations'].append("Address critical issues before deployment")

        return summary

def main():
    """Run component validation tests"""
    validator = ComponentValidator()

    print("Available components for testing:")
    for i, (component, config) in enumerate(validator.component_tests.items(), 1):
        critical = "CRITICAL" if config['critical'] else "optional"
        print(f"{i:2d}. {component.replace('_', ' ').title()} ({critical})")

    print(f"\nRunning validation on all components...")

    # Run all component tests
    results = validator.run_selected_component_tests()

    # Display summary
    summary = results['summary']
    print(f"\n{'='*50}")
    print("COMPONENT VALIDATION COMPLETE")
    print(f"{'='*50}")
    print(f"Overall Status: {summary['overall_status']}")
    print(f"Components Tested: {summary['total_components']}")
    print(f"Passed: {summary['passed']}")
    print(f"Failed: {summary['failed']}")
    print(f"Errors: {summary['errors']}")
    print(f"Skipped: {summary['skipped']}")

    if summary['critical_issues']:
        print(f"\nCRITICAL ISSUES:")
        for issue in summary['critical_issues']:
            print(f"- {issue}")

    if summary['recommendations']:
        print(f"\nRECOMMENDATIONS:")
        for rec in summary['recommendations']:
            print(f"- {rec}")

    print(f"\nDetailed results saved to: .spx/component_validation_results.json")

if __name__ == "__main__":
    main()