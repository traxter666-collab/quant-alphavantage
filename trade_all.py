#!/usr/bin/env python3
"""
Multi-Asset Trading System - SPX + QQQ + SPY + IWM
Complete four-asset options analysis with unified execution and comparison
"""

import sys
import json
from datetime import datetime
sys.path.append('.')

def run_multi_asset_analysis():
    """Run unified analysis for SPX, QQQ, SPY, and IWM"""
    print("COMPLETE MULTI-ASSET TRADING SYSTEM")
    print("Unified SPX + QQQ + SPY + IWM Options Analysis")
    print("=" * 80)

    start_time = datetime.now()
    results = {}

    try:
        # Import all analysis systems
        from spx_unified_launcher import run_unified_analysis as run_spx_analysis
        from qqq_integration import run_qqq_analysis
        from spy_integration import run_spy_analysis, run_iwm_analysis

        print("RUNNING SPX ANALYSIS...")
        print("-" * 40)
        spx_success = run_spx_analysis()
        results['spx_success'] = spx_success

        print(f"\nRUNNING QQQ ANALYSIS...")
        print("-" * 40)
        qqq_success = run_qqq_analysis()
        results['qqq_success'] = qqq_success

        print(f"\nRUNNING SPY ANALYSIS...")
        print("-" * 40)
        spy_success = run_spy_analysis()
        results['spy_success'] = spy_success

        print(f"\nRUNNING IWM ANALYSIS...")
        print("-" * 40)
        iwm_success = run_iwm_analysis()
        results['iwm_success'] = iwm_success

        # Load results for comprehensive comparison
        spx_results = None
        qqq_results = None
        spy_results = None
        iwm_results = None

        try:
            with open('.spx/unified_analysis_results.json', 'r') as f:
                spx_results = json.load(f)
        except:
            pass

        try:
            with open('.spx/qqq_analysis_results.json', 'r') as f:
                qqq_results = json.load(f)
        except:
            pass

        try:
            with open('.spx/spy_analysis_results.json', 'r') as f:
                spy_results = json.load(f)
        except:
            pass

        try:
            with open('.spx/iwm_analysis_results.json', 'r') as f:
                iwm_results = json.load(f)
        except:
            pass

        # Generate comprehensive four-asset analysis
        print(f"\n" + "=" * 80)
        print("MULTI-ASSET COMPREHENSIVE COMPARISON")
        print("=" * 80)

        if spx_results and qqq_results and spy_results and iwm_results:
            # Extract key data from all four assets
            spx_price = spx_results.get('spx_price', 0)
            spx_consensus = spx_results['market_analysis']['consensus_score']
            spx_direction = spx_results['market_analysis']['directional_bias']
            spx_action = spx_results['trading_decision']['action']

            qqq_price = qqq_results['qqq_analysis']['current_price']
            qqq_consensus_raw = qqq_results['qqq_consensus']['total_score']
            qqq_threshold_pct = qqq_results['threshold_percentage']
            qqq_direction = qqq_results['qqq_consensus']['directional_bias']
            qqq_action = qqq_results['action_recommendation']

            spy_price = spy_results['spy_analysis']['current_price']
            spy_consensus_raw = spy_results['spy_consensus']['total_score']
            spy_threshold_pct = spy_results['threshold_percentage']
            spy_direction = spy_results['spy_consensus']['directional_bias']
            spy_action = spy_results['action_recommendation']

            iwm_price = iwm_results['iwm_analysis']['current_price']
            iwm_consensus_raw = iwm_results['iwm_consensus']['total_score']
            iwm_threshold_pct = iwm_results['threshold_percentage']
            iwm_direction = iwm_results['iwm_consensus']['directional_bias']
            iwm_action = iwm_results['action_recommendation']

            print(f"FOUR-ASSET COMPARISON:")
            print(f"                    SPX              QQQ              SPY              IWM")
            print(f"  Price:           {spx_price:8.1f}        ${qqq_price:6.2f}         ${spy_price:6.2f}         ${iwm_price:6.2f}")
            print(f"  Consensus:       {spx_consensus:>12s}   {qqq_consensus_raw}/195 ({qqq_threshold_pct:.1f}%)   {spy_consensus_raw}/220 ({spy_threshold_pct:.1f}%)   {iwm_consensus_raw}/200 ({iwm_threshold_pct:.1f}%)")
            print(f"  Direction:       {spx_direction:>12s}   {qqq_direction:>12s}    {spy_direction:>12s}    {iwm_direction:>12s}")
            print(f"  Action:          {spx_action:>12s}   {qqq_action:>12s}    {spy_action:>12s}    {iwm_action:>12s}")

            # Determine best opportunities across all assets
            spx_score_pct = float(spx_consensus.split('(')[1].split('%')[0]) if '(' in spx_consensus else 0

            # Count tradeable assets
            tradeable_assets = []
            if spx_score_pct >= 75:
                tradeable_assets.append("SPX")
            if qqq_threshold_pct >= 75:
                tradeable_assets.append("QQQ")
            if spy_threshold_pct >= 75:
                tradeable_assets.append("SPY")
            if iwm_threshold_pct >= 75:
                tradeable_assets.append("IWM")

            # Best opportunity assessment
            if len(tradeable_assets) >= 4:
                best_opportunity = "ALL FOUR ASSETS TRADEABLE"
                recommendation = "Full diversification - spread risk across SPX, QQQ, SPY, and IWM"
            elif len(tradeable_assets) == 3:
                best_opportunity = f"THREE ASSETS TRADEABLE: {' + '.join(tradeable_assets)}"
                recommendation = f"Strong multi-asset approach with {' + '.join(tradeable_assets)}"
            elif len(tradeable_assets) == 2:
                best_opportunity = f"TWO ASSETS TRADEABLE: {' + '.join(tradeable_assets)}"
                recommendation = f"Focus on {' and '.join(tradeable_assets)} - dual asset approach"
            elif len(tradeable_assets) == 1:
                best_opportunity = f"SINGLE ASSET: {tradeable_assets[0]} PREFERRED"
                recommendation = f"Focus exclusively on {tradeable_assets[0]} - highest confidence"
            else:
                best_opportunity = "NO TRADES RECOMMENDED"
                recommendation = "All assets below 75% threshold - wait for better setups"

            print(f"\nOPPORTUNITY ASSESSMENT:")
            print(f"  Best Opportunity: {best_opportunity}")
            print(f"  Recommendation: {recommendation}")
            print(f"  Tradeable Assets: {len(tradeable_assets)}/4")

            # Direction correlation analysis across all four
            directions = [spx_direction, qqq_direction, spy_direction, iwm_direction]
            unique_directions = set(directions)

            if len(unique_directions) == 1:
                correlation_status = "PERFECT ALIGNMENT"
                correlation_note = "All four assets showing same directional bias - strong market consensus"
            elif len(unique_directions) == 2:
                correlation_status = "PARTIAL ALIGNMENT"
                correlation_note = "Mixed signals - analyze individual asset strength"
            else:
                correlation_status = "DIVERGENT SIGNALS"
                correlation_note = "Multiple directional biases - high uncertainty environment"

            print(f"\nCORRELATION ANALYSIS:")
            print(f"  Four-Asset Correlation: {correlation_status}")
            print(f"  Note: {correlation_note}")

            # Asset ranking by confidence
            asset_scores = [
                ("SPX", spx_score_pct),
                ("QQQ", qqq_threshold_pct),
                ("SPY", spy_threshold_pct),
                ("IWM", iwm_threshold_pct)
            ]
            asset_scores.sort(key=lambda x: x[1], reverse=True)

            print(f"\nASSET RANKING BY CONFIDENCE:")
            for i, (asset, score) in enumerate(asset_scores, 1):
                print(f"  #{i}: {asset} ({score:.1f}%)")

            # Risk diversification recommendations
            if len(tradeable_assets) > 1:
                print(f"\nRISK DIVERSIFICATION:")
                print(f"  Multi-Asset Approach: Spread 2-4% across {len(tradeable_assets)} assets")
                print(f"  Individual Allocation: 0.5-1.0% per asset for full diversification")
                print(f"  Correlation Benefit: Maximum diversification across large/mid/small cap and tech")

        else:
            print("Could not load all analysis results for comprehensive comparison")

        # Save comprehensive multi-asset results
        multi_asset_summary = {
            'timestamp': datetime.now().isoformat(),
            'analysis_type': 'COMPLETE_MULTI_ASSET_SPX_QQQ_SPY_IWM',
            'spx_success': spx_success,
            'qqq_success': qqq_success,
            'spy_success': spy_success,
            'iwm_success': iwm_success,
            'best_opportunity': best_opportunity if 'best_opportunity' in locals() else 'ANALYSIS_ERROR',
            'recommendation': recommendation if 'recommendation' in locals() else 'CHECK_INDIVIDUAL_RESULTS',
            'correlation_status': correlation_status if 'correlation_status' in locals() else 'UNKNOWN',
            'tradeable_assets': tradeable_assets if 'tradeable_assets' in locals() else [],
            'asset_ranking': asset_scores if 'asset_scores' in locals() else []
        }

        with open('.spx/multi_asset_complete_results.json', 'w') as f:
            json.dump(multi_asset_summary, f, indent=2)

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        print(f"\nComplete Multi-Asset Analysis Duration: {duration:.1f} seconds")
        print(f"Results saved to .spx/multi_asset_complete_results.json")

        overall_success = spx_success or qqq_success or spy_success or iwm_success
        return overall_success

    except Exception as e:
        print(f"Multi-asset analysis error: {e}")
        return False

def generate_trading_plan():
    """Generate a comprehensive trading plan based on all three assets"""
    try:
        with open('.spx/multi_asset_complete_results.json', 'r') as f:
            results = json.load(f)

        print(f"\n" + "=" * 80)
        print("COMPREHENSIVE TRADING PLAN")
        print("=" * 80)

        print(f"Market Analysis Time: {results['timestamp']}")
        print(f"Tradeable Assets: {len(results.get('tradeable_assets', []))}/4")
        print(f"Overall Assessment: {results.get('best_opportunity', 'Unknown')}")

        if results.get('tradeable_assets'):
            print(f"\nRECOMMENDED TRADING APPROACH:")
            print(f"1. Primary Strategy: {results.get('recommendation', 'See individual analysis')}")
            print(f"2. Asset Allocation: Distribute risk across {len(results['tradeable_assets'])} assets")
            print(f"3. Position Sizing: 0.5-1.0% per asset for full diversification")
            print(f"4. Correlation Status: {results.get('correlation_status', 'Unknown')}")

            print(f"\nASSET PRIORITY ORDER:")
            for i, (asset, score) in enumerate(results.get('asset_ranking', []), 1):
                print(f"  {i}. {asset}: {score:.1f}% confidence")

        else:
            print(f"\nNO TRADING RECOMMENDED:")
            print(f"  All four assets below threshold")
            print(f"  Wait for better market conditions")
            print(f"  Monitor for setup improvement")

        print(f"\nRISK MANAGEMENT:")
        print(f"  Maximum Total Risk: 3-4% across all assets")
        print(f"  Per-Asset Limit: 1.0% maximum")
        print(f"  Exit Triggers: 75% threshold breach on any asset")
        print(f"  Correlation Risk: Monitor for simultaneous moves across market caps")

        return True

    except Exception as e:
        print(f"Trading plan generation error: {e}")
        return False

if __name__ == "__main__":
    print("Starting Complete Multi-Asset Trading System...")

    success = run_multi_asset_analysis()

    if success:
        print(f"\nMULTI-ASSET SYSTEM: OPERATIONAL")
        print("SPX + QQQ + SPY + IWM analysis complete")

        # Generate comprehensive trading plan
        plan_success = generate_trading_plan()

        if plan_success:
            print(f"\nTRADING PLAN: GENERATED")
            print("Complete four-asset trading recommendations available")

    else:
        print(f"\nMULTI-ASSET SYSTEM: ERROR")
        print("Check individual asset analysis for issues")