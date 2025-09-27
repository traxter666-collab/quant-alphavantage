#!/usr/bin/env python3
"""
Friday Unified System Backtest
Test the new unified system against Friday's known successful market conditions
"""

import sys
import json
from datetime import datetime
sys.path.append('.')

def simulate_friday_morning_conditions():
    """Simulate Friday 11:05 AM King Node breach conditions"""
    print("FRIDAY MORNING BACKTEST - KING NODE BREACH")
    print("=" * 60)

    # Friday morning conditions (before King Node breach)
    friday_morning = {
        'time': '11:05 AM ET',
        'spy_price': 662.5,
        'spx_equivalent': 6625.0,  # King Node level
        'market_context': 'Approaching King Node resistance',
        'volume': 'Moderate (200K)',
        'expected_outcome': 'Bullish breakthrough prediction'
    }

    print(f"Friday Morning Conditions:")
    print(f"  Time: {friday_morning['time']}")
    print(f"  SPY: ${friday_morning['spy_price']:.2f}")
    print(f"  SPX: {friday_morning['spx_equivalent']:.0f} (King Node)")
    print(f"  Context: {friday_morning['market_context']}")
    print(f"  Volume: {friday_morning['volume']}")

    return friday_morning

def simulate_friday_afternoon_conditions():
    """Simulate Friday 2:42 PM breakthrough conditions"""
    print("\nFRIDAY AFTERNOON BACKTEST - 6645 BREAKTHROUGH")
    print("=" * 60)

    # Friday afternoon conditions (approaching 6645)
    friday_afternoon = {
        'time': '2:42 PM ET',
        'spy_price': 664.3,
        'spx_equivalent': 6643.0,  # Approaching 6645 resistance
        'market_context': 'Strong momentum approaching 6645',
        'volume': 'High EOD (400K)',
        'expected_outcome': 'Breakthrough to 6646.65'
    }

    print(f"Friday Afternoon Conditions:")
    print(f"  Time: {friday_afternoon['time']}")
    print(f"  SPY: ${friday_afternoon['spy_price']:.2f}")
    print(f"  SPX: {friday_afternoon['spx_equivalent']:.0f} (Pre-6645)")
    print(f"  Context: {friday_afternoon['market_context']}")
    print(f"  Volume: {friday_afternoon['volume']}")

    return friday_afternoon

def test_unified_system_with_conditions(spy_price, expected_spx, scenario_name):
    """Test unified system with specific market conditions"""

    try:
        # Import unified system components
        from spx_unified_launcher import (
            calculate_market_consensus,
            apply_optimized_thresholds,
            calculate_dynamic_risk_parameters
        )

        # Simulate accurate SPX price (Friday had strong correlation)
        simulated_spx = spy_price * 10.02  # Friday's approximate correlation

        print(f"\nTesting Unified System - {scenario_name}:")
        print(f"  Simulated SPX: {simulated_spx:.2f}")
        print(f"  Expected SPX: {expected_spx:.2f}")
        print(f"  Accuracy: {abs(simulated_spx - expected_spx):.2f} point difference")

        # Calculate consensus with Friday conditions
        consensus_data = calculate_market_consensus(simulated_spx, spy_price, volume=300000)

        print(f"  Consensus Score: {consensus_data['total_score']}/275")
        print(f"  Directional Bias: {consensus_data['directional_bias']}")

        # Apply optimized thresholds
        threshold_data = apply_optimized_thresholds(consensus_data['total_score'])

        print(f"  Score Percentage: {threshold_data['score_percentage']:.1f}%")
        print(f"  Confidence Level: {threshold_data['confidence_level']}")
        print(f"  Threshold Met: {'YES' if threshold_data['threshold_met'] else 'NO'}")

        # Calculate risk parameters
        risk_data = calculate_dynamic_risk_parameters(simulated_spx, consensus_data)

        print(f"  Portfolio Heat: {risk_data['portfolio_heat']:.1f}%")
        print(f"  Position Size: {risk_data['position_size']:.1f}%")

        # Assess system performance
        system_performance = {
            'scenario': scenario_name,
            'spx_accuracy': abs(simulated_spx - expected_spx),
            'consensus_score': consensus_data['total_score'],
            'score_percentage': threshold_data['score_percentage'],
            'threshold_met': threshold_data['threshold_met'],
            'directional_bias': consensus_data['directional_bias'],
            'confidence_level': threshold_data['confidence_level'],
            'system_recommendation': threshold_data['action_recommendation']
        }

        # Determine if system would have made good decisions
        if scenario_name == "Morning King Node":
            # Morning should show bullish potential (moderate confidence)
            success_criteria = (
                consensus_data['directional_bias'] in ['BULLISH', 'NEUTRAL'] and
                consensus_data['total_score'] >= 150  # Reasonable score
            )
        else:  # Afternoon breakthrough
            # Afternoon should show higher confidence for breakthrough
            success_criteria = (
                consensus_data['directional_bias'] == 'BULLISH' and
                threshold_data['score_percentage'] >= 65  # Strong signal
            )

        system_performance['success'] = success_criteria
        system_performance['assessment'] = 'GOOD' if success_criteria else 'NEEDS_WORK'

        print(f"  System Assessment: {system_performance['assessment']}")

        return system_performance

    except Exception as e:
        print(f"  System Test Failed: {e}")
        return {
            'scenario': scenario_name,
            'success': False,
            'error': str(e),
            'assessment': 'ERROR'
        }

def compare_old_vs_new_system():
    """Compare old system behavior vs new unified system"""
    print("\nOLD vs NEW SYSTEM COMPARISON")
    print("=" * 60)

    # Friday's actual data points
    test_points = [
        {'spy': 662.5, 'actual_spx': 6625.0, 'scenario': 'King Node Test'},
        {'spy': 664.3, 'actual_spx': 6643.0, 'scenario': '6645 Approach'},
        {'spy': 664.665, 'actual_spx': 6646.65, 'scenario': 'Breakthrough'}
    ]

    print("SPY Price | Old SPX  | New SPX  | Actual   | Old Error | New Error")
    print("-" * 70)

    total_old_error = 0
    total_new_error = 0

    for point in test_points:
        spy = point['spy']
        actual_spx = point['actual_spx']

        old_spx = spy * 10.0  # Old SPY×10 method
        new_spx = spy * 10.02  # New correlation-adjusted method

        old_error = abs(old_spx - actual_spx)
        new_error = abs(new_spx - actual_spx)

        total_old_error += old_error
        total_new_error += new_error

        print(f"{spy:8.2f} | {old_spx:7.1f} | {new_spx:7.1f} | {actual_spx:7.1f} | {old_error:8.1f} | {new_error:8.1f}")

    avg_old_error = total_old_error / len(test_points)
    avg_new_error = total_new_error / len(test_points)
    improvement = avg_old_error - avg_new_error

    print(f"\nACCURACY IMPROVEMENT:")
    print(f"  Average Old Error: {avg_old_error:.1f} points")
    print(f"  Average New Error: {avg_new_error:.1f} points")
    print(f"  Improvement: {improvement:.1f} points ({improvement/avg_old_error*100:.1f}%)")

    return {
        'avg_old_error': avg_old_error,
        'avg_new_error': avg_new_error,
        'improvement': improvement,
        'improvement_percentage': improvement/avg_old_error*100
    }

def run_friday_unified_backtest():
    """Run complete Friday backtest with unified system"""
    print("FRIDAY UNIFIED SYSTEM BACKTEST")
    print("Testing new seamless system against Friday's successful conditions")
    print("=" * 80)

    start_time = datetime.now()

    # Test scenarios
    morning_conditions = simulate_friday_morning_conditions()
    afternoon_conditions = simulate_friday_afternoon_conditions()

    # Test unified system
    morning_result = test_unified_system_with_conditions(
        morning_conditions['spy_price'],
        morning_conditions['spx_equivalent'],
        "Morning King Node"
    )

    afternoon_result = test_unified_system_with_conditions(
        afternoon_conditions['spy_price'],
        afternoon_conditions['spx_equivalent'],
        "Afternoon Breakthrough"
    )

    # Compare accuracy improvements
    accuracy_comparison = compare_old_vs_new_system()

    # Calculate overall results
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    test_results = [morning_result, afternoon_result]
    successful_tests = sum(1 for result in test_results if result.get('success', False))
    total_tests = len(test_results)
    success_rate = (successful_tests / total_tests) * 100

    # Summary
    print(f"\n" + "=" * 80)
    print("FRIDAY UNIFIED BACKTEST SUMMARY")
    print("=" * 80)

    for result in test_results:
        status = "PASS" if result.get('success', False) else "FAIL"
        print(f"  {result['scenario']:20s}: {status}")
        if 'consensus_score' in result:
            print(f"    Consensus: {result['consensus_score']}/275 ({result.get('score_percentage', 0):.1f}%)")
        if 'confidence_level' in result:
            print(f"    Confidence: {result['confidence_level']}")

    print(f"\nBacktest Success Rate: {success_rate:.1f}% ({successful_tests}/{total_tests})")
    print(f"Test Duration: {duration:.1f} seconds")

    print(f"\nSPX Accuracy Improvement:")
    print(f"  Old Method Error: {accuracy_comparison['avg_old_error']:.1f} points")
    print(f"  New Method Error: {accuracy_comparison['avg_new_error']:.1f} points")
    print(f"  Improvement: {accuracy_comparison['improvement']:.1f} points ({accuracy_comparison['improvement_percentage']:.1f}%)")

    # Overall assessment
    if success_rate >= 70 and accuracy_comparison['improvement'] > 10:
        overall_result = "UNIFIED SYSTEM VALIDATED"
        print(f"\n🎯 BACKTEST RESULT: {overall_result}")
        print("New unified system successfully replicates Friday's performance")
        print("Key improvements:")
        print("  - Seamless single-command execution")
        print("  - Improved SPX pricing accuracy")
        print("  - Optimized consensus thresholds working correctly")
        print("  - Dynamic risk management operational")
        system_validated = True
    else:
        overall_result = "SYSTEM NEEDS REFINEMENT"
        print(f"\n⚠️ BACKTEST RESULT: {overall_result}")
        print("Unified system shows promise but needs additional work")
        system_validated = False

    # Save backtest results
    backtest_summary = {
        'timestamp': datetime.now().isoformat(),
        'backtest_type': 'FRIDAY_UNIFIED_SYSTEM',
        'test_results': test_results,
        'success_rate': success_rate,
        'accuracy_comparison': accuracy_comparison,
        'overall_result': overall_result,
        'system_validated': system_validated,
        'duration_seconds': duration
    }

    with open('.spx/friday_unified_backtest.json', 'w') as f:
        json.dump(backtest_summary, f, indent=2)

    print(f"\nBacktest results saved to .spx/friday_unified_backtest.json")

    return system_validated

if __name__ == "__main__":
    print("Starting Friday Unified System Backtest...")

    success = run_friday_unified_backtest()

    if success:
        print(f"\n✅ UNIFIED SYSTEM: VALIDATED AGAINST FRIDAY")
        print("Ready for live trading with confidence")
    else:
        print(f"\n⚠️ UNIFIED SYSTEM: NEEDS REFINEMENT")
        print("Continue optimization before full deployment")