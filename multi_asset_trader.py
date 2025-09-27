#!/usr/bin/env python3
"""
Multi-Asset Trading System
Unified SPX + QQQ options analysis with single command execution
"""

import sys
import json
from datetime import datetime
sys.path.append('.')

def run_multi_asset_analysis():
    """Run unified analysis for both SPX and QQQ"""
    print("MULTI-ASSET TRADING SYSTEM")
    print("Unified SPX + QQQ Options Analysis")
    print("=" * 80)

    start_time = datetime.now()
    results = {}

    try:
        # Import both analysis systems
        from spx_unified_launcher import run_unified_analysis as run_spx_analysis
        from qqq_integration import run_qqq_analysis

        print("🔴 RUNNING SPX ANALYSIS...")
        print("-" * 40)
        spx_success = run_spx_analysis()
        results['spx_success'] = spx_success

        print(f"\n🔵 RUNNING QQQ ANALYSIS...")
        print("-" * 40)
        qqq_success = run_qqq_analysis()
        results['qqq_success'] = qqq_success

        # Load results for comparison
        spx_results = None
        qqq_results = None

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

        # Generate comparative analysis
        print(f"\n" + "=" * 80)
        print("MULTI-ASSET COMPARISON")
        print("=" * 80)

        if spx_results and qqq_results:
            # Extract key data
            spx_price = spx_results.get('spx_price', 0)
            spx_consensus = spx_results['market_analysis']['consensus_score']
            spx_direction = spx_results['market_analysis']['directional_bias']
            spx_action = spx_results['trading_decision']['action']

            qqq_price = qqq_results['qqq_analysis']['current_price']
            qqq_consensus_raw = qqq_results['qqq_consensus']['total_score']
            qqq_threshold_pct = qqq_results['threshold_percentage']
            qqq_direction = qqq_results['qqq_consensus']['directional_bias']
            qqq_action = qqq_results['action_recommendation']

            print(f"ASSET COMPARISON:")
            print(f"                    SPX              QQQ")
            print(f"  Price:           {spx_price:8.1f}        ${qqq_price:6.2f}")
            print(f"  Consensus:       {spx_consensus:>12s}   {qqq_consensus_raw}/195 ({qqq_threshold_pct:.1f}%)")
            print(f"  Direction:       {spx_direction:>12s}   {qqq_direction:>12s}")
            print(f"  Action:          {spx_action:>12s}   {qqq_action:>12s}")

            # Determine best opportunity
            spx_score_pct = float(spx_consensus.split('(')[1].split('%')[0]) if '(' in spx_consensus else 0

            if spx_score_pct >= 75 and qqq_threshold_pct >= 75:
                best_opportunity = "BOTH ASSETS TRADEABLE"
                recommendation = "Consider both SPX and QQQ based on direction alignment"
            elif spx_score_pct >= 75:
                best_opportunity = "SPX PREFERRED"
                recommendation = "Focus on SPX - higher confidence score"
            elif qqq_threshold_pct >= 75:
                best_opportunity = "QQQ PREFERRED"
                recommendation = "Focus on QQQ - meets threshold requirements"
            else:
                best_opportunity = "NO TRADES RECOMMENDED"
                recommendation = "Both assets below 75% threshold - wait for better setups"

            print(f"\nOPPORTUNITY ASSESSMENT:")
            print(f"  Best Opportunity: {best_opportunity}")
            print(f"  Recommendation: {recommendation}")

            # Direction correlation analysis
            if spx_direction == qqq_direction:
                correlation_status = "ALIGNED"
                correlation_note = "Both assets showing same directional bias"
            else:
                correlation_status = "DIVERGENT"
                correlation_note = "Assets showing different directional bias - analyze individually"

            print(f"\nCORRELATION ANALYSIS:")
            print(f"  Direction Correlation: {correlation_status}")
            print(f"  Note: {correlation_note}")

        else:
            print("Could not load analysis results for comparison")

        # Save multi-asset results
        multi_asset_summary = {
            'timestamp': datetime.now().isoformat(),
            'analysis_type': 'MULTI_ASSET_SPX_QQQ',
            'spx_success': spx_success,
            'qqq_success': qqq_success,
            'best_opportunity': best_opportunity if 'best_opportunity' in locals() else 'ANALYSIS_ERROR',
            'recommendation': recommendation if 'recommendation' in locals() else 'CHECK_INDIVIDUAL_RESULTS',
            'correlation_status': correlation_status if 'correlation_status' in locals() else 'UNKNOWN'
        }

        with open('.spx/multi_asset_results.json', 'w') as f:
            json.dump(multi_asset_summary, f, indent=2)

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        print(f"\nMulti-Asset Analysis Duration: {duration:.1f} seconds")
        print(f"Results saved to .spx/multi_asset_results.json")

        overall_success = spx_success or qqq_success
        return overall_success

    except Exception as e:
        print(f"Multi-asset analysis error: {e}")
        return False

if __name__ == "__main__":
    print("Starting Multi-Asset Trading System...")

    success = run_multi_asset_analysis()

    if success:
        print(f"\nMULTI-ASSET SYSTEM: OPERATIONAL")
        print("SPX + QQQ analysis complete - check results above")
    else:
        print(f"\nMULTI-ASSET SYSTEM: ERROR")
        print("Check individual asset analysis for issues")