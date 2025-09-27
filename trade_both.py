#!/usr/bin/env python3
"""
SPX + QQQ Trading System
Simple command to analyze both SPX and QQQ options
"""

import sys
import json
from datetime import datetime
sys.path.append('.')

def main():
    print("SPX + QQQ MULTI-ASSET TRADING SYSTEM")
    print("Analyzing both markets for optimal opportunities")
    print("=" * 60)

    start_time = datetime.now()

    try:
        # Run SPX analysis
        print("RUNNING SPX ANALYSIS...")
        print("-" * 30)
        from spx_unified_launcher import run_unified_analysis
        spx_success = run_unified_analysis()

        print(f"\nRUNNING QQQ ANALYSIS...")
        print("-" * 30)
        from qqq_integration import run_qqq_analysis
        qqq_success = run_qqq_analysis()

        # Summary
        print(f"\n" + "=" * 60)
        print("MULTI-ASSET SUMMARY")
        print("=" * 60)

        print(f"SPX Analysis: {'SUCCESS' if spx_success else 'FAILED'}")
        print(f"QQQ Analysis: {'SUCCESS' if qqq_success else 'FAILED'}")

        if spx_success and qqq_success:
            # Load and compare results
            try:
                with open('.spx/unified_analysis_results.json', 'r') as f:
                    spx_data = json.load(f)
                with open('.spx/qqq_analysis_results.json', 'r') as f:
                    qqq_data = json.load(f)

                # Extract key info
                spx_score = spx_data['market_analysis']['consensus_score']
                spx_action = spx_data['trading_decision']['action']
                qqq_score = f"{qqq_data['qqq_consensus']['total_score']}/195 ({qqq_data['threshold_percentage']:.1f}%)"
                qqq_action = qqq_data['action_recommendation']

                print(f"\nCOMPARISON:")
                print(f"  SPX: {spx_score} -> {spx_action}")
                print(f"  QQQ: {qqq_score} -> {qqq_action}")

                # Recommendation
                spx_tradeable = "AVOID" not in spx_action
                qqq_tradeable = "CONSIDER" in qqq_action

                if spx_tradeable and qqq_tradeable:
                    recommendation = "BOTH markets show opportunities"
                elif spx_tradeable:
                    recommendation = "SPX preferred"
                elif qqq_tradeable:
                    recommendation = "QQQ preferred"
                else:
                    recommendation = "NO trades recommended (conservative thresholds)"

                print(f"\nRECOMMENDATION: {recommendation}")

            except Exception as e:
                print(f"Comparison error: {e}")

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        print(f"\nTotal Analysis Time: {duration:.1f} seconds")
        print(f"Results saved to individual asset files")

        overall_success = spx_success or qqq_success

        if overall_success:
            print(f"\nSUCCESS: Multi-asset analysis complete")
            print("Check individual results above for trading decisions")
        else:
            print(f"\nERROR: Both analyses failed")

        return overall_success

    except Exception as e:
        print(f"Multi-asset error: {e}")
        return False

if __name__ == "__main__":
    main()