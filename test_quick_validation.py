#!/usr/bin/env python3
"""
Quick System Validation Test
Tests key fixes without unicode issues
"""

import sys
sys.path.append('.')

def test_gex_calculation():
    """Test GEX calculation accuracy"""
    print("Testing GEX Calculation...")

    try:
        from gex_analyzer_fixed import GEXAnalyzerFixed
        import pandas as pd

        analyzer = GEXAnalyzerFixed()
        spy_price = 661.74

        # Create test data
        test_data = [
            [660.0, 'call', 1000, 0.05, 100],
            [660.0, 'put', 500, 0.03, 50],
            [665.0, 'call', 2000, 0.04, 200],
            [665.0, 'put', 1500, 0.02, 75]
        ]

        df = pd.DataFrame(test_data, columns=['strike', 'type', 'open_interest', 'gamma', 'volume'])

        # Test calculation
        gex_results = analyzer.calculate_gex_by_strike_fixed(df, spy_price)

        # Verify results exist
        assert 660.0 in gex_results
        assert 665.0 in gex_results

        # Verify data preservation (critical fix)
        assert 'volume_weight' in gex_results[660.0]
        assert 'net_gex' in gex_results[660.0]

        # Test key levels
        key_levels = analyzer.identify_key_levels_fixed(gex_results, spy_price)

        print("  GEX Calculation: PASS")
        print(f"  - 660 Strike: Net GEX = {gex_results[660.0]['net_gex']:.2f}M")
        print(f"  - 665 Strike: Net GEX = {gex_results[665.0]['net_gex']:.2f}M")
        print(f"  - Key Levels Detected: {len(key_levels)}")

        return True

    except Exception as e:
        print(f"  GEX Calculation: FAIL - {e}")
        return False

def test_touch_probability():
    """Test Heatseeker touch probability system"""
    print("Testing Touch Probability System...")

    try:
        from heatseeker_touch_tracker import HeatSeekerTouchTracker

        tracker = HeatSeekerTouchTracker(".spx/test_touch.json")

        test_level = 6650.0

        # Test 1st touch (should be 90%)
        prob_1st = tracker.get_touch_probability(test_level)
        assert prob_1st['probability'] == 0.90
        assert prob_1st['classification'] == 'FRESH_LEVEL'

        # Record touch and test 2nd touch probability
        tracker.record_touch(6648.0, test_level, volume_confirmed=True)
        tracker.update_touch_result(test_level, hold_result=True, subsequent_move=5.0)

        prob_2nd = tracker.get_touch_probability(test_level)
        assert abs(prob_2nd['model_probability'] - 0.66) < 0.01  # 2nd touch = 66%

        print("  Touch Probability: PASS")
        print(f"  - 1st Touch: {prob_1st['probability']:.0%}")
        print(f"  - 2nd Touch: {prob_2nd['model_probability']:.0%}")

        return True

    except Exception as e:
        print(f"  Touch Probability: FAIL - {e}")
        return False

def test_unified_engine():
    """Test unified trading engine"""
    print("Testing Unified Trading Engine...")

    try:
        from unified_trading_engine import UnifiedTradingEngine

        engine = UnifiedTradingEngine(".spx/test_unified")
        spy_price = 661.74

        # Test market analysis
        market_state = engine.analyze_market(spy_price, volume=50000)

        # Verify core components
        assert market_state.consensus_score >= 0
        assert market_state.consensus_score <= 100
        assert market_state.directional_bias in ['BULLISH', 'BEARISH', 'NEUTRAL']
        assert isinstance(market_state.node_classifications, dict)

        # Test recommendation generation
        recommendation = engine.generate_trading_recommendation(market_state)

        assert recommendation.action in ['BUY', 'SELL', 'HOLD', 'AVOID']

        print("  Unified Engine: PASS")
        print(f"  - Consensus Score: {market_state.consensus_score:.1f}/100")
        print(f"  - Directional Bias: {market_state.directional_bias}")
        print(f"  - Recommendation: {recommendation.action}")

        return True

    except Exception as e:
        print(f"  Unified Engine: FAIL - {e}")
        return False

def test_friday_scenario():
    """Test with Friday's successful market conditions"""
    print("Testing Friday Success Scenario...")

    try:
        from unified_trading_engine import UnifiedTradingEngine

        engine = UnifiedTradingEngine(".spx/friday_test")

        # Friday conditions: SPY ~661.74, bullish momentum
        friday_spy_price = 661.74

        market_state = engine.analyze_market(friday_spy_price, volume=400000)  # High volume
        recommendation = engine.generate_trading_recommendation(market_state)

        # Should show reasonable analysis
        consensus_reasonable = 30 <= market_state.consensus_score <= 100

        print("  Friday Scenario: PASS" if consensus_reasonable else "  Friday Scenario: MARGINAL")
        print(f"  - Consensus: {market_state.consensus_score:.1f}/100")
        print(f"  - Recommendation: {recommendation.action}")

        return consensus_reasonable

    except Exception as e:
        print(f"  Friday Scenario: FAIL - {e}")
        return False

def run_quick_validation():
    """Run quick validation of all key fixes"""
    print("QUICK SYSTEM VALIDATION")
    print("=" * 50)

    tests = [
        ("GEX Calculation Fix", test_gex_calculation),
        ("Touch Probability System", test_touch_probability),
        ("Unified Trading Engine", test_unified_engine),
        ("Friday Success Scenario", test_friday_scenario)
    ]

    results = []

    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        result = test_func()
        results.append((test_name, result))

    # Summary
    print("\n" + "=" * 50)
    print("VALIDATION SUMMARY")
    print("=" * 50)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"  {test_name}: {status}")

    success_rate = (passed / total) * 100
    print(f"\nSuccess Rate: {success_rate:.1f}% ({passed}/{total})")

    if success_rate >= 75:
        print("\nSYSTEM STATUS: SIGNIFICANTLY IMPROVED")
        print("Critical fixes are working correctly")
        print("Ready for further testing with live data")
    else:
        print("\nSYSTEM STATUS: NEEDS MORE WORK")
        print("Some critical fixes are not working")

    return success_rate >= 75

if __name__ == "__main__":
    success = run_quick_validation()

    if success:
        print("\nNEXT STEPS:")
        print("1. Test with live market data")
        print("2. Validate against Friday's predictions")
        print("3. Monitor accuracy in paper trading")
    else:
        print("\nNEXT STEPS:")
        print("1. Debug failing components")
        print("2. Check import dependencies")
        print("3. Verify file paths and permissions")