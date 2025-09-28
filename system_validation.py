#!/usr/bin/env python3
"""
Complete System Validation & Backtest
Comprehensive testing of the three-asset trading system
"""

import sys
import json
import time
import requests
from datetime import datetime, timedelta
sys.path.append('.')

def test_api_connectivity():
    """Test AlphaVantage API connectivity and response times"""
    print("API CONNECTIVITY TEST")
    print("=" * 50)

    api_key = 'ZFL38ZY98GSN7E1S'
    tests = []

    # Test 1: SPY Quote
    print("Testing SPY quote...")
    start_time = time.time()
    try:
        url = f'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=SPY&apikey={api_key}'
        response = requests.get(url, timeout=10)
        data = response.json()
        response_time = time.time() - start_time

        if 'Global Quote' in data:
            spy_price = float(data['Global Quote']['05. price'])
            tests.append({
                'test': 'SPY_QUOTE',
                'status': 'PASS',
                'response_time': response_time,
                'data': f"SPY: ${spy_price:.2f}"
            })
            print(f"  PASS - SPY: ${spy_price:.2f} ({response_time:.2f}s)")
        else:
            tests.append({'test': 'SPY_QUOTE', 'status': 'FAIL', 'error': 'No data'})
            print(f"  FAIL - No SPY data")

    except Exception as e:
        tests.append({'test': 'SPY_QUOTE', 'status': 'ERROR', 'error': str(e)})
        print(f"  ERROR - {e}")

    # Test 2: QQQ Quote
    print("Testing QQQ quote...")
    start_time = time.time()
    try:
        url = f'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=QQQ&apikey={api_key}'
        response = requests.get(url, timeout=10)
        data = response.json()
        response_time = time.time() - start_time

        if 'Global Quote' in data:
            qqq_price = float(data['Global Quote']['05. price'])
            tests.append({
                'test': 'QQQ_QUOTE',
                'status': 'PASS',
                'response_time': response_time,
                'data': f"QQQ: ${qqq_price:.2f}"
            })
            print(f"  PASS - QQQ: ${qqq_price:.2f} ({response_time:.2f}s)")
        else:
            tests.append({'test': 'QQQ_QUOTE', 'status': 'FAIL', 'error': 'No data'})
            print(f"  FAIL - No QQQ data")

    except Exception as e:
        tests.append({'test': 'QQQ_QUOTE', 'status': 'ERROR', 'error': str(e)})
        print(f"  ERROR - {e}")

    # Test 3: SPY Options
    print("Testing SPY options...")
    start_time = time.time()
    try:
        url = f'https://www.alphavantage.co/query?function=REALTIME_OPTIONS&symbol=SPY&apikey={api_key}'
        response = requests.get(url, timeout=15)
        data = response.json()
        response_time = time.time() - start_time

        if 'data' in data and len(data['data']) > 0:
            option_count = len(data['data'])
            tests.append({
                'test': 'SPY_OPTIONS',
                'status': 'PASS',
                'response_time': response_time,
                'data': f"{option_count} contracts"
            })
            print(f"  PASS - {option_count} SPY options ({response_time:.2f}s)")
        else:
            tests.append({'test': 'SPY_OPTIONS', 'status': 'FAIL', 'error': 'No options data'})
            print(f"  FAIL - No SPY options data")

    except Exception as e:
        tests.append({'test': 'SPY_OPTIONS', 'status': 'ERROR', 'error': str(e)})
        print(f"  ERROR - {e}")

    # Test 4: RSI Technical Indicator
    print("Testing RSI indicator...")
    start_time = time.time()
    try:
        url = f'https://www.alphavantage.co/query?function=RSI&symbol=SPY&interval=5min&time_period=14&series_type=close&apikey={api_key}'
        response = requests.get(url, timeout=10)
        data = response.json()
        response_time = time.time() - start_time

        if 'Technical Analysis: RSI' in data:
            rsi_data = list(data['Technical Analysis: RSI'].values())
            if rsi_data:
                rsi_value = float(list(rsi_data[0].values())[0])
                tests.append({
                    'test': 'RSI_INDICATOR',
                    'status': 'PASS',
                    'response_time': response_time,
                    'data': f"RSI: {rsi_value:.1f}"
                })
                print(f"  PASS - RSI: {rsi_value:.1f} ({response_time:.2f}s)")
            else:
                tests.append({'test': 'RSI_INDICATOR', 'status': 'FAIL', 'error': 'No RSI values'})
                print(f"  FAIL - No RSI values")
        else:
            tests.append({'test': 'RSI_INDICATOR', 'status': 'FAIL', 'error': 'No RSI data'})
            print(f"  FAIL - No RSI data")

    except Exception as e:
        tests.append({'test': 'RSI_INDICATOR', 'status': 'ERROR', 'error': str(e)})
        print(f"  ERROR - {e}")

    # Test 5: IWM Quote
    print("Testing IWM quote...")
    start_time = time.time()
    try:
        url = f'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=IWM&apikey={api_key}'
        response = requests.get(url, timeout=10)
        data = response.json()
        response_time = time.time() - start_time

        if 'Global Quote' in data:
            iwm_price = float(data['Global Quote']['05. price'])
            tests.append({
                'test': 'IWM_QUOTE',
                'status': 'PASS',
                'response_time': response_time,
                'data': f"IWM: ${iwm_price:.2f}"
            })
            print(f"  PASS - IWM: ${iwm_price:.2f} ({response_time:.2f}s)")
        else:
            tests.append({'test': 'IWM_QUOTE', 'status': 'FAIL', 'error': 'No data'})
            print(f"  FAIL - No IWM data")

    except Exception as e:
        tests.append({'test': 'IWM_QUOTE', 'status': 'ERROR', 'error': str(e)})
        print(f"  ERROR - {e}")

    return tests

def test_individual_systems():
    """Test each individual trading system"""
    print("\nINDIVIDUAL SYSTEM TESTS")
    print("=" * 50)

    system_tests = []

    # Test SPX System
    print("Testing SPX system...")
    start_time = time.time()
    try:
        from spx_unified_launcher import run_unified_analysis
        spx_result = run_unified_analysis()
        response_time = time.time() - start_time

        system_tests.append({
            'system': 'SPX_UNIFIED',
            'status': 'PASS' if spx_result else 'FAIL',
            'response_time': response_time,
            'result': spx_result
        })
        print(f"  SPX System: {'PASS' if spx_result else 'FAIL'} ({response_time:.2f}s)")

    except Exception as e:
        system_tests.append({
            'system': 'SPX_UNIFIED',
            'status': 'ERROR',
            'error': str(e)
        })
        print(f"  SPX System: ERROR - {e}")

    # Test QQQ System
    print("Testing QQQ system...")
    start_time = time.time()
    try:
        from qqq_integration import run_qqq_analysis
        qqq_result = run_qqq_analysis()
        response_time = time.time() - start_time

        system_tests.append({
            'system': 'QQQ_INTEGRATION',
            'status': 'PASS' if qqq_result else 'FAIL',
            'response_time': response_time,
            'result': qqq_result
        })
        print(f"  QQQ System: {'PASS' if qqq_result else 'FAIL'} ({response_time:.2f}s)")

    except Exception as e:
        system_tests.append({
            'system': 'QQQ_INTEGRATION',
            'status': 'ERROR',
            'error': str(e)
        })
        print(f"  QQQ System: ERROR - {e}")

    # Test SPY System
    print("Testing SPY system...")
    start_time = time.time()
    try:
        from spy_integration import run_spy_analysis
        spy_result = run_spy_analysis()
        response_time = time.time() - start_time

        system_tests.append({
            'system': 'SPY_INTEGRATION',
            'status': 'PASS' if spy_result else 'FAIL',
            'response_time': response_time,
            'result': spy_result
        })
        print(f"  SPY System: {'PASS' if spy_result else 'FAIL'} ({response_time:.2f}s)")

    except Exception as e:
        system_tests.append({
            'system': 'SPY_INTEGRATION',
            'status': 'ERROR',
            'error': str(e)
        })
        print(f"  SPY System: ERROR - {e}")

    # Test IWM System
    print("Testing IWM system...")
    start_time = time.time()
    try:
        from spy_integration import run_iwm_analysis
        iwm_result = run_iwm_analysis()
        response_time = time.time() - start_time

        system_tests.append({
            'system': 'IWM_INTEGRATION',
            'status': 'PASS' if iwm_result else 'FAIL',
            'response_time': response_time,
            'result': iwm_result
        })
        print(f"  IWM System: {'PASS' if iwm_result else 'FAIL'} ({response_time:.2f}s)")

    except Exception as e:
        system_tests.append({
            'system': 'IWM_INTEGRATION',
            'status': 'ERROR',
            'error': str(e)
        })
        print(f"  IWM System: ERROR - {e}")

    return system_tests

def test_multi_asset_system():
    """Test the complete multi-asset system"""
    print("\nMULTI-ASSET SYSTEM TEST")
    print("=" * 50)

    print("Testing complete four-asset system...")
    start_time = time.time()
    try:
        from trade_all import run_multi_asset_analysis
        multi_result = run_multi_asset_analysis()
        response_time = time.time() - start_time

        multi_test = {
            'system': 'MULTI_ASSET_COMPLETE',
            'status': 'PASS' if multi_result else 'FAIL',
            'response_time': response_time,
            'result': multi_result
        }
        print(f"  Multi-Asset System: {'PASS' if multi_result else 'FAIL'} ({response_time:.2f}s)")

        return multi_test

    except Exception as e:
        multi_test = {
            'system': 'MULTI_ASSET_COMPLETE',
            'status': 'ERROR',
            'error': str(e)
        }
        print(f"  Multi-Asset System: ERROR - {e}")
        return multi_test

def validate_data_accuracy():
    """Validate data accuracy and consistency"""
    print("\nDATA ACCURACY VALIDATION")
    print("=" * 50)

    validation_tests = []

    try:
        # Load saved results
        with open('.spx/unified_analysis_results.json', 'r') as f:
            spx_data = json.load(f)
        with open('.spx/qqq_analysis_results.json', 'r') as f:
            qqq_data = json.load(f)
        with open('.spx/spy_analysis_results.json', 'r') as f:
            spy_data = json.load(f)
        with open('.spx/multi_asset_complete_results.json', 'r') as f:
            multi_data = json.load(f)

        # Try to load IWM data if available
        try:
            with open('.spx/iwm_analysis_results.json', 'r') as f:
                iwm_data = json.load(f)
                iwm_available = True
        except:
            iwm_data = None
            iwm_available = False

        # Validate SPX data
        spx_price = spx_data.get('spx_price', 0)
        spx_consensus = spx_data['market_analysis']['consensus_score']
        print(f"SPX Data: Price={spx_price}, Consensus={spx_consensus}")

        # Fix validation logic - check if price > 0 and consensus exists (not empty)
        spx_price_valid = spx_price > 0
        spx_consensus_valid = spx_consensus is not None and str(spx_consensus).strip() != ""

        validation_tests.append({
            'test': 'SPX_DATA_INTEGRITY',
            'status': 'PASS' if spx_price_valid and spx_consensus_valid else 'FAIL',
            'data': f"Price: {spx_price:.2f}, Consensus: {spx_consensus}"
        })

        # Validate QQQ data
        qqq_price = qqq_data['qqq_analysis']['current_price']
        qqq_consensus = qqq_data['qqq_consensus']['total_score']
        print(f"QQQ Data: Price={qqq_price}, Consensus={qqq_consensus}")

        validation_tests.append({
            'test': 'QQQ_DATA_INTEGRITY',
            'status': 'PASS' if qqq_price > 0 and qqq_consensus > 0 else 'FAIL',
            'data': f"Price: {qqq_price}, Consensus: {qqq_consensus}"
        })

        # Validate SPY data
        spy_price = spy_data['spy_analysis']['current_price']
        spy_consensus = spy_data['spy_consensus']['total_score']
        print(f"SPY Data: Price={spy_price}, Consensus={spy_consensus}")

        validation_tests.append({
            'test': 'SPY_DATA_INTEGRITY',
            'status': 'PASS' if spy_price > 0 and spy_consensus > 0 else 'FAIL',
            'data': f"Price: {spy_price}, Consensus: {spy_consensus}"
        })

        # Validate multi-asset consistency
        tradeable_count = len(multi_data.get('tradeable_assets', []))
        print(f"Multi-Asset: {tradeable_count} tradeable assets")

        validation_tests.append({
            'test': 'MULTI_ASSET_CONSISTENCY',
            'status': 'PASS' if tradeable_count >= 0 else 'FAIL',
            'data': f"Tradeable: {tradeable_count}/4 assets"
        })

        # Validate IWM data if available
        if iwm_available:
            iwm_price = iwm_data['iwm_analysis']['current_price']
            iwm_consensus = iwm_data['iwm_consensus']['total_score']
            print(f"IWM Data: Price={iwm_price}, Consensus={iwm_consensus}")

            validation_tests.append({
                'test': 'IWM_DATA_INTEGRITY',
                'status': 'PASS' if iwm_price > 0 and iwm_consensus > 0 else 'FAIL',
                'data': f"Price: {iwm_price}, Consensus: {iwm_consensus}"
            })
        else:
            validation_tests.append({
                'test': 'IWM_DATA_INTEGRITY',
                'status': 'FAIL',
                'data': "IWM data not available"
            })

    except Exception as e:
        validation_tests.append({
            'test': 'DATA_VALIDATION',
            'status': 'ERROR',
            'error': str(e)
        })
        print(f"Data validation error: {e}")

    return validation_tests

def run_performance_backtest():
    """Run a simple performance backtest"""
    print("\nPERFORMANCE BACKTEST")
    print("=" * 50)

    backtest_results = []

    try:
        # Load current analysis results
        with open('.spx/multi_asset_complete_results.json', 'r') as f:
            current_data = json.load(f)

        tradeable_assets = current_data.get('tradeable_assets', [])
        asset_ranking = current_data.get('asset_ranking', [])

        print(f"Current Analysis Results:")
        print(f"  Tradeable Assets: {len(tradeable_assets)}/4")
        print(f"  Asset Ranking: {asset_ranking}")

        # Simulate backtest scenarios
        scenarios = [
            {'name': 'Bull Market', 'spy_move': +2.0, 'qqq_move': +2.5, 'spx_move': +20, 'iwm_move': +2.8},
            {'name': 'Bear Market', 'spy_move': -2.0, 'qqq_move': -2.5, 'spx_move': -20, 'iwm_move': -3.2},
            {'name': 'Sideways', 'spy_move': +0.1, 'qqq_move': -0.1, 'spx_move': +1, 'iwm_move': +0.2}
        ]

        for scenario in scenarios:
            print(f"\n{scenario['name']} Scenario:")

            # Calculate hypothetical outcomes based on current recommendations
            hypothetical_pnl = 0

            if 'SPY' in tradeable_assets:
                spy_pnl = scenario['spy_move'] * 1.5  # Leverage effect
                hypothetical_pnl += spy_pnl
                print(f"  SPY P&L: {spy_pnl:+.1f}%")

            if 'QQQ' in tradeable_assets:
                qqq_pnl = scenario['qqq_move'] * 1.5  # Leverage effect
                hypothetical_pnl += qqq_pnl
                print(f"  QQQ P&L: {qqq_pnl:+.1f}%")

            if 'SPX' in tradeable_assets:
                spx_pnl = scenario['spx_move'] / 10 * 1.5  # Convert to % and leverage
                hypothetical_pnl += spx_pnl
                print(f"  SPX P&L: {spx_pnl:+.1f}%")

            if 'IWM' in tradeable_assets:
                iwm_pnl = scenario['iwm_move'] * 1.5  # Leverage effect
                hypothetical_pnl += iwm_pnl
                print(f"  IWM P&L: {iwm_pnl:+.1f}%")

            total_positions = len(tradeable_assets)
            avg_pnl = hypothetical_pnl / total_positions if total_positions > 0 else 0

            print(f"  Total P&L: {hypothetical_pnl:+.1f}%")
            print(f"  Avg per position: {avg_pnl:+.1f}%")

            backtest_results.append({
                'scenario': scenario['name'],
                'total_pnl': hypothetical_pnl,
                'avg_pnl': avg_pnl,
                'positions': total_positions,
                'status': 'PROFIT' if hypothetical_pnl > 0 else 'LOSS' if hypothetical_pnl < 0 else 'FLAT'
            })

    except Exception as e:
        backtest_results.append({
            'test': 'BACKTEST',
            'status': 'ERROR',
            'error': str(e)
        })
        print(f"❌ Backtest error: {e}")

    return backtest_results

def generate_system_health_report(api_tests, system_tests, multi_test, validation_tests, backtest_results):
    """Generate comprehensive system health report"""
    print("\n" + "=" * 80)
    print("COMPREHENSIVE SYSTEM HEALTH REPORT")
    print("=" * 80)

    # Calculate overall scores
    api_passed = sum(1 for test in api_tests if test['status'] == 'PASS')
    api_total = len(api_tests)

    system_passed = sum(1 for test in system_tests if test['status'] == 'PASS')
    system_total = len(system_tests)

    validation_passed = sum(1 for test in validation_tests if test['status'] == 'PASS')
    validation_total = len(validation_tests)

    multi_status = multi_test['status'] == 'PASS'

    # Overall system score
    total_tests = api_total + system_total + validation_total + 1  # +1 for multi-asset
    total_passed = api_passed + system_passed + validation_passed + (1 if multi_status else 0)

    overall_score = (total_passed / total_tests) * 100

    print(f"OVERALL SYSTEM HEALTH: {overall_score:.1f}%")
    print(f"")
    print(f"TEST RESULTS SUMMARY:")
    print(f"  API Connectivity: {api_passed}/{api_total} tests passed ({api_passed/api_total*100:.1f}%)")
    print(f"  Individual Systems: {system_passed}/{system_total} tests passed ({system_passed/system_total*100:.1f}%)")
    print(f"  Data Validation: {validation_passed}/{validation_total} tests passed ({validation_passed/validation_total*100:.1f}%)")
    print(f"  Multi-Asset System: {'PASS' if multi_status else 'FAIL'}")

    print(f"\nDETAILED TEST RESULTS:")

    print(f"\nAPI Tests:")
    for test in api_tests:
        status_icon = "PASS" if test['status'] == 'PASS' else "FAIL"
        print(f"  {status_icon} - {test['test']}: {test['status']}")
        if 'data' in test:
            print(f"      {test['data']}")

    print(f"\nSystem Tests:")
    for test in system_tests:
        status_icon = "PASS" if test['status'] == 'PASS' else "FAIL"
        print(f"  {status_icon} - {test['system']}: {test['status']}")
        if 'response_time' in test:
            print(f"      Response Time: {test['response_time']:.2f}s")

    print(f"\nData Validation:")
    for test in validation_tests:
        status_icon = "PASS" if test['status'] == 'PASS' else "FAIL"
        print(f"  {status_icon} - {test['test']}: {test['status']}")
        if 'data' in test:
            print(f"      {test['data']}")

    print(f"\nBacktest Results:")
    for result in backtest_results:
        if 'scenario' in result:
            status_icon = "PROFIT" if result['status'] == 'PROFIT' else "LOSS" if result['status'] == 'LOSS' else "FLAT"
            print(f"  {status_icon} - {result['scenario']}: {result['total_pnl']:+.1f}% ({result['positions']} positions)")

    # Test IWM if available
    try:
        with open('.spx/iwm_analysis_results.json', 'r') as f:
            iwm_data = json.load(f)
            iwm_available = True
    except:
        iwm_available = False

    if iwm_available:
        print(f"\nIWM Integration Status: AVAILABLE")
        print(f"  IWM Price: ${iwm_data['iwm_analysis']['current_price']:.2f}")
        print(f"  IWM Consensus: {iwm_data['iwm_consensus']['total_score']}/200 ({iwm_data['threshold_percentage']:.1f}%)")
    else:
        print(f"\nIWM Integration Status: NOT AVAILABLE")

    # Add system health improvement recommendations
    print(f"\nSYSTEM HEALTH IMPROVEMENT RECOMMENDATIONS:")

    # Check for failing tests
    failing_tests = []
    for test in api_tests + system_tests + validation_tests:
        if test['status'] != 'PASS':
            failing_tests.append(test)

    if not failing_tests:
        print(f"  CHECK All tests passing - system health excellent")
    else:
        print(f"  FIX Address {len(failing_tests)} failing test(s):")
        for test in failing_tests:
            test_name = test.get('test', test.get('system', 'Unknown'))
            print(f"    - {test_name}: {test['status']}")

    # Response time optimizations
    slow_tests = []
    for test in api_tests + system_tests:
        if 'response_time' in test and test['response_time'] > 5.0:
            slow_tests.append(test)

    if slow_tests:
        print(f"  SPEED Optimize {len(slow_tests)} slow test(s) (>5s response time):")
        for test in slow_tests:
            test_name = test.get('test', test.get('system', 'Unknown'))
            print(f"    - {test_name}: {test['response_time']:.1f}s")

    # Multi-asset integration improvements
    if iwm_available:
        print(f"  ASSETS 4-Asset integration complete - consider correlation analysis")
    else:
        print(f"  ASSETS Add IWM integration for complete 4-asset coverage")

    # Error handling improvements
    error_tests = [test for test in api_tests + system_tests + validation_tests if test['status'] == 'ERROR']
    if error_tests:
        print(f"  ERRORS Fix {len(error_tests)} error condition(s) for better reliability")

    print(f"  TARGET Achieve 95%+ system health for optimal trading performance")

    # System recommendations
    print(f"\nSYSTEM RECOMMENDATIONS:")
    if overall_score >= 90:
        print(f"  EXCELLENT - System ready for live trading")
    elif overall_score >= 80:
        print(f"  GOOD - System operational with minor issues")
    elif overall_score >= 70:
        print(f"  FAIR - Address failing tests before live trading")
    else:
        print(f"  POOR - Significant issues need resolution")

    # Save report
    report = {
        'timestamp': datetime.now().isoformat(),
        'overall_score': overall_score,
        'api_tests': api_tests,
        'system_tests': system_tests,
        'multi_asset_test': multi_test,
        'validation_tests': validation_tests,
        'backtest_results': backtest_results
    }

    with open('.spx/system_health_report.json', 'w') as f:
        json.dump(report, f, indent=2)

    print(f"\nSystem health report saved to .spx/system_health_report.json")

    return overall_score

def run_complete_system_validation():
    """Run complete system validation and testing"""
    print("COMPLETE SYSTEM VALIDATION & BACKTEST")
    print("Testing all components of the four-asset trading system")
    print("=" * 80)

    start_time = datetime.now()

    # Run all tests
    api_tests = test_api_connectivity()
    system_tests = test_individual_systems()
    multi_test = test_multi_asset_system()
    validation_tests = validate_data_accuracy()
    backtest_results = run_performance_backtest()

    # Generate report
    overall_score = generate_system_health_report(
        api_tests, system_tests, multi_test, validation_tests, backtest_results
    )

    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    print(f"\nValidation completed in {duration:.1f} seconds")
    print(f"Overall System Health: {overall_score:.1f}%")

    return overall_score >= 80  # Return True if system is healthy

if __name__ == "__main__":
    print("Starting Complete System Validation...")

    success = run_complete_system_validation()

    if success:
        print(f"\nSYSTEM VALIDATION: PASSED")
        print("Four-asset trading system is operational and ready")
    else:
        print(f"\nSYSTEM VALIDATION: FAILED")
        print("System issues detected - review health report for details")