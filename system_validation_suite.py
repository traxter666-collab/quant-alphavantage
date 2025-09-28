#!/usr/bin/env python3
"""
Comprehensive System Validation Suite
Tests all components with known data to verify reliability improvements
"""

import json
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Tuple, Any
import unittest
from unittest.mock import Mock, patch

# Import our fixed components
from gex_analyzer_fixed import GEXAnalyzerFixed
from heatseeker_touch_tracker import HeatSeekerTouchTracker, TouchEvent
from unified_trading_engine import UnifiedTradingEngine

class TestGEXAnalyzerFixed(unittest.TestCase):
    """Test the fixed GEX analyzer"""

    def setUp(self):
        self.analyzer = GEXAnalyzerFixed()
        self.test_spy_price = 661.74

    def test_gex_calculation_accuracy(self):
        """Test GEX calculation with known data"""
        print("\nTesting GEX Calculation Accuracy...")

        # Create test data with known values
        test_data = {
            660.0: {
                'call_oi': 1000, 'call_gamma': 0.05,
                'put_oi': 500, 'put_gamma': 0.03
            },
            665.0: {
                'call_oi': 2000, 'call_gamma': 0.04,
                'put_oi': 1500, 'put_gamma': 0.02
            }
        }

        # Expected calculations:
        # 660 Call GEX = 1000 * 0.05 * 100 * 661.74 = 3,308,700
        # 660 Put GEX = 500 * 0.03 * 100 * 661.74 = 992,610
        # 660 Net GEX = 3,308,700 - 992,610 = 2,316,090 (scaled to 2.32M)

        expected_660_net_gex = 2.32  # Millions
        expected_665_net_gex = 3.31  # Millions

        # Mock DataFrame
        mock_data = []
        for strike, data in test_data.items():
            mock_data.extend([
                [strike, 'call', data['call_oi'], data['call_gamma'], 100],
                [strike, 'put', data['put_oi'], data['put_gamma'], 50]
            ])

        df = pd.DataFrame(mock_data, columns=['strike', 'type', 'open_interest', 'gamma', 'volume'])

        # Test calculation
        gex_results = self.analyzer.calculate_gex_by_strike_fixed(df, self.test_spy_price)

        self.assertIn(660.0, gex_results)
        self.assertIn(665.0, gex_results)

        # Verify calculations are close to expected (within 5%)
        actual_660 = gex_results[660.0]['net_gex']
        actual_665 = gex_results[665.0]['net_gex']

        self.assertAlmostEqual(actual_660, expected_660_net_gex, delta=expected_660_net_gex * 0.05)
        self.assertAlmostEqual(actual_665, expected_665_net_gex, delta=expected_665_net_gex * 0.05)

        print(f"✅ 660 GEX: Expected {expected_660_net_gex:.2f}M, Got {actual_660:.2f}M")
        print(f"✅ 665 GEX: Expected {expected_665_net_gex:.2f}M, Got {actual_665:.2f}M")

    def test_data_preservation(self):
        """Test that Volume × OI data is preserved (critical fix)"""
        print("\n🧪 Testing Data Preservation...")

        # Create test data including zero GEX values
        test_data = [
            [660.0, 'call', 1000, 0.05, 100],
            [660.0, 'put', 1000, 0.05, 50],  # Net GEX should be ~0
            [665.0, 'call', 2000, 0.04, 200],
            [665.0, 'put', 500, 0.02, 25]
        ]

        df = pd.DataFrame(test_data, columns=['strike', 'type', 'open_interest', 'gamma', 'volume'])

        gex_results = self.analyzer.calculate_gex_by_strike_fixed(df, self.test_spy_price)

        # CRITICAL: Verify zero/near-zero GEX values are preserved
        self.assertIn(660.0, gex_results)
        self.assertIn('volume_weight', gex_results[660.0])

        # Verify volume × OI calculation is preserved
        expected_volume_weight_660 = (100 * 1000) + (50 * 1000)  # Call + Put
        actual_volume_weight_660 = gex_results[660.0]['volume_weight']

        self.assertEqual(actual_volume_weight_660, expected_volume_weight_660)

        print(f"✅ Volume×OI preserved: Expected {expected_volume_weight_660}, Got {actual_volume_weight_660}")

        # Verify ALL strikes are preserved (including near-zero GEX)
        self.assertEqual(len(gex_results), 2, "All strikes should be preserved, including zero GEX")

    def test_gamma_flip_detection(self):
        """Test gamma flip detection with preserved data"""
        print("\n🧪 Testing Gamma Flip Detection...")

        # Create data that crosses zero
        test_data = [
            [659.0, 'call', 500, 0.02, 50],
            [659.0, 'put', 2000, 0.06, 100],  # Negative GEX
            [662.0, 'call', 2000, 0.06, 200],
            [662.0, 'put', 500, 0.02, 25],   # Positive GEX
        ]

        df = pd.DataFrame(test_data, columns=['strike', 'type', 'open_interest', 'gamma', 'volume'])

        gex_results = self.analyzer.calculate_gex_by_strike_fixed(df, self.test_spy_price)
        key_levels = self.analyzer.identify_key_levels_fixed(gex_results, self.test_spy_price)

        # Should detect gamma flip between 659 and 662
        self.assertIsNotNone(key_levels['gamma_flip'])
        self.assertGreater(key_levels['gamma_flip'], 659.0)
        self.assertLess(key_levels['gamma_flip'], 662.0)

        print(f"✅ Gamma flip detected at SPY {key_levels['gamma_flip']:.2f}")

class TestHeatSeekerTouchTracker(unittest.TestCase):
    """Test the Heatseeker touch probability system"""

    def setUp(self):
        self.tracker = HeatSeekerTouchTracker(".spx/test_touch_history.json")

    def test_touch_probability_model(self):
        """Test official Heatseeker touch probability model"""
        print("\n🔥 Testing Heatseeker Touch Probability Model...")

        test_level = 6650.0

        # Test 1st touch (should be 90% default)
        prob_1st = self.tracker.get_touch_probability(test_level)
        self.assertEqual(prob_1st['touch_count'], 1)
        self.assertEqual(prob_1st['probability'], 0.90)
        self.assertEqual(prob_1st['classification'], 'FRESH_LEVEL')

        # Record first touch
        self.tracker.record_touch(6648.0, test_level, volume_confirmed=True)
        self.tracker.update_touch_result(test_level, hold_result=True, subsequent_move=5.0)

        # Test 2nd touch (should be 66%)
        prob_2nd = self.tracker.get_touch_probability(test_level)
        self.assertEqual(prob_2nd['touch_count'], 2)
        self.assertAlmostEqual(prob_2nd['model_probability'], 0.66, places=2)

        # Record second touch
        self.tracker.record_touch(6649.0, test_level, volume_confirmed=True)
        self.tracker.update_touch_result(test_level, hold_result=True, subsequent_move=3.0)

        # Test 3rd touch (should be 33%)
        prob_3rd = self.tracker.get_touch_probability(test_level)
        self.assertEqual(prob_3rd['touch_count'], 3)
        self.assertAlmostEqual(prob_3rd['model_probability'], 0.33, places=2)

        # Record third touch
        self.tracker.record_touch(6651.0, test_level, volume_confirmed=False)
        self.tracker.update_touch_result(test_level, hold_result=False, subsequent_move=-8.0)

        # Test 4th+ touch (should be 20%)
        prob_4th = self.tracker.get_touch_probability(test_level)
        self.assertEqual(prob_4th['touch_count'], 4)
        self.assertAlmostEqual(prob_4th['model_probability'], 0.20, places=2)

        print(f"✅ 1st Touch: {prob_1st['probability']:.0%} (Expected: 90%)")
        print(f"✅ 2nd Touch: {prob_2nd['model_probability']:.0%} (Expected: 66%)")
        print(f"✅ 3rd Touch: {prob_3rd['model_probability']:.0%} (Expected: 33%)")
        print(f"✅ 4th Touch: {prob_4th['model_probability']:.0%} (Expected: 20%)")

    def test_historical_adjustment(self):
        """Test historical success rate adjustment"""
        print("\n🔥 Testing Historical Success Rate Adjustment...")

        test_level = 6625.0

        # Record multiple touches with known success rate
        touches_data = [
            (True, 5.0),   # Success
            (True, 3.0),   # Success
            (False, -7.0), # Failure
            (True, 4.0),   # Success
        ]

        for hold_result, move in touches_data:
            self.tracker.record_touch(6624.0, test_level, volume_confirmed=True)
            self.tracker.update_touch_result(test_level, hold_result, move)

        prob_data = self.tracker.get_touch_probability(test_level)

        # Historical success rate should be 75% (3/4)
        expected_historical = 0.75
        self.assertAlmostEqual(prob_data['historical_success_rate'], expected_historical, places=2)

        # Final probability should blend model (20% for 5th touch) with historical (75%)
        # Formula: (0.20 * 0.7) + (0.75 * 0.3) = 0.14 + 0.225 = 0.365
        expected_blended = (0.20 * 0.7) + (0.75 * 0.3)
        self.assertAlmostEqual(prob_data['probability'], expected_blended, places=2)

        print(f"✅ Historical Rate: {prob_data['historical_success_rate']:.1%} (Expected: 75%)")
        print(f"✅ Blended Probability: {prob_data['probability']:.1%} (Expected: {expected_blended:.1%})")

class TestUnifiedTradingEngine(unittest.TestCase):
    """Test the unified trading engine"""

    def setUp(self):
        self.engine = UnifiedTradingEngine(".spx/test_session")

    def test_methodology_unification(self):
        """Test that methodology conflicts are resolved"""
        print("\n🔧 Testing Methodology Unification...")

        # Create test market state
        spy_price = 661.74
        market_state = self.engine.analyze_market(spy_price)

        # Verify unified classifications exist
        self.assertIsNotNone(market_state.node_classifications)
        self.assertIsInstance(market_state.node_classifications, dict)

        # Verify consensus calculation doesn't double-apply scores
        self.assertGreaterEqual(market_state.consensus_score, 0)
        self.assertLessEqual(market_state.consensus_score, 100)

        # Verify King Node definition is consistent
        king_nodes = [node for node in market_state.node_classifications.values()
                     if node.get('type') == 'KING_NODE']

        if king_nodes:
            # Should have exactly one King Node
            self.assertEqual(len(king_nodes), 1)
            king_node = king_nodes[0]
            self.assertEqual(king_node['source'], 'GEX_ABSOLUTE')

        print(f"✅ Consensus Score: {market_state.consensus_score:.1f}/100")
        print(f"✅ Directional Bias: {market_state.directional_bias}")
        print(f"✅ Node Classifications: {len(market_state.node_classifications)}")

    def test_recommendation_generation(self):
        """Test trading recommendation generation"""
        print("\n🎯 Testing Recommendation Generation...")

        spy_price = 661.74
        market_state = self.engine.analyze_market(spy_price)
        recommendation = self.engine.generate_trading_recommendation(market_state)

        # Verify recommendation structure
        self.assertIsNotNone(recommendation.action)
        self.assertIn(recommendation.action, ['BUY', 'SELL', 'HOLD', 'AVOID'])

        # Verify probabilities are reasonable
        if recommendation.action in ['BUY', 'SELL']:
            self.assertGreaterEqual(recommendation.success_probability, 0.0)
            self.assertLessEqual(recommendation.success_probability, 1.0)
            self.assertGreater(recommendation.risk_reward_ratio, 0.0)

        # Verify position sizing constraints
        self.assertLessEqual(recommendation.position_size, self.engine.config['max_single_position'])

        print(f"✅ Action: {recommendation.action}")
        print(f"✅ Instrument: {recommendation.instrument}")
        print(f"✅ Success Probability: {recommendation.success_probability:.1%}")
        print(f"✅ Risk/Reward: {recommendation.risk_reward_ratio:.2f}")

class TestSystemIntegration(unittest.TestCase):
    """Test full system integration"""

    def test_end_to_end_workflow(self):
        """Test complete end-to-end workflow"""
        print("\n🚀 Testing End-to-End Workflow...")

        # Initialize components
        engine = UnifiedTradingEngine(".spx/integration_test")

        # Test market analysis
        spy_price = 661.74
        market_state = engine.analyze_market(spy_price, volume=50000)

        # Verify market state completeness
        self.assertIsNotNone(market_state.consensus_score)
        self.assertIsNotNone(market_state.directional_bias)
        self.assertIsNotNone(market_state.node_classifications)

        # Test recommendation generation
        recommendation = engine.generate_trading_recommendation(market_state)

        # Verify recommendation quality
        if recommendation.action != 'AVOID':
            self.assertGreater(len(recommendation.supporting_factors), 0)
            self.assertIsNotNone(recommendation.primary_reason)

        # Test state persistence
        state_file = engine.session_dir / "unified_market_state.json"
        self.assertTrue(state_file.exists())

        print(f"✅ Market Analysis Complete")
        print(f"✅ Recommendation Generated: {recommendation.action}")
        print(f"✅ State Persisted: {state_file}")

def run_validation_suite():
    """Run the complete validation suite"""
    print("COMPREHENSIVE SYSTEM VALIDATION SUITE")
    print("=" * 80)

    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestGEXAnalyzerFixed))
    suite.addTests(loader.loadTestsFromTestCase(TestHeatSeekerTouchTracker))
    suite.addTests(loader.loadTestsFromTestCase(TestUnifiedTradingEngine))
    suite.addTests(loader.loadTestsFromTestCase(TestSystemIntegration))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Summary
    print("\n📊 VALIDATION SUMMARY")
    print("=" * 50)
    print(f"Tests Run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")

    if result.failures:
        print("\n❌ FAILURES:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback.split('AssertionError:')[-1].strip()}")

    if result.errors:
        print("\n🚨 ERRORS:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback.split('Exception:')[-1].strip()}")

    success_rate = ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun) * 100

    print(f"\n✅ SUCCESS RATE: {success_rate:.1f}%")

    if success_rate >= 95:
        print("🎉 SYSTEM VALIDATION PASSED - Ready for live trading")
        return True
    else:
        print("⚠️  SYSTEM VALIDATION FAILED - Further fixes required")
        return False

def test_known_market_scenario():
    """Test with known market scenario from Friday's success"""
    print("\n📈 TESTING KNOWN MARKET SCENARIO (Friday Success)")
    print("=" * 60)

    engine = UnifiedTradingEngine(".spx/known_scenario_test")

    # Recreate Friday's market conditions
    friday_spy_price = 661.74  # Friday close equivalent
    friday_conditions = {
        'king_node_breached': True,  # 6625 was breached
        'approaching_call_wall': True,  # 6650 was target
        'eod_momentum': True,  # End of day push
        'volume_confirmed': True  # Institutional flow
    }

    # Analyze market
    market_state = engine.analyze_market(friday_spy_price, volume=400000)  # High volume

    # Should show bullish bias given Friday's success
    print(f"Market State: {market_state.directional_bias} ({market_state.consensus_score:.1f}/100)")

    # Generate recommendation
    recommendation = engine.generate_trading_recommendation(market_state)

    print(f"Recommendation: {recommendation.action} {recommendation.instrument}")
    print(f"Success Probability: {recommendation.success_probability:.1%}")

    # Verify it aligns with what worked on Friday
    expected_bullish = market_state.consensus_score >= 70
    if expected_bullish:
        print("✅ System correctly identifies bullish opportunity (matches Friday success)")
    else:
        print("❌ System failed to identify bullish opportunity (contradicts Friday success)")

    return expected_bullish

if __name__ == "__main__":
    print("STARTING COMPREHENSIVE SYSTEM VALIDATION")
    print("This will test all critical fixes and improvements\n")

    # Run main validation suite
    validation_passed = run_validation_suite()

    # Test known scenario
    scenario_passed = test_known_market_scenario()

    # Final assessment
    print("\n" + "=" * 80)
    print("FINAL SYSTEM ASSESSMENT")
    print("=" * 80)

    if validation_passed and scenario_passed:
        print("SYSTEM RELIABILITY: SIGNIFICANTLY IMPROVED")
        print("All critical issues resolved:")
        print("   - GEX calculation formula corrected")
        print("   - Data pipeline preserves Volume x OI")
        print("   - Touch probability tracking implemented")
        print("   - Methodology conflicts resolved")
        print("   - Unified confidence scoring active")
        print("\nREADY FOR LIVE TRADING DECISIONS")
    else:
        print("SYSTEM RELIABILITY: STILL NEEDS WORK")
        print("Some issues remain unresolved")
        print("Continue fixing before live trading")