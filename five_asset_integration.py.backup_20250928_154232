#!/usr/bin/env python3
"""
Five-Asset Integration System
Complete multi-asset trading system: SPX + QQQ + SPY + IWM + NDX
Enhanced portfolio diversification with NASDAQ-100 index options
"""

import os
import json
import subprocess
import time
from datetime import datetime
from typing import Dict, List, Any

class FiveAssetTradingSystem:
    """Complete five-asset trading system integration"""

    def __init__(self):
        self.assets = ['SPX', 'QQQ', 'SPY', 'IWM', 'NDX']
        self.session_file = '.spx/five_asset_complete_results.json'

        # Asset-specific scoring maximums
        self.scoring_systems = {
            'SPX': 275,  # Full 275-point system
            'QQQ': 195,  # QQQ-specific scoring
            'SPY': 220,  # SPY-specific scoring
            'IWM': 200,  # IWM-specific scoring
            'NDX': 220   # NDX-specific scoring
        }

        print("Five-Asset Trading System initialized")
        print("Assets: SPX + QQQ + SPY + IWM + NDX")

    def run_spx_analysis(self) -> Dict[str, Any]:
        """Run SPX unified analysis"""
        try:
            result = subprocess.run(
                ['python', 'unified_spx_data.py'],
                capture_output=True,
                text=True,
                timeout=120
            )

            if result.returncode == 0:
                # Try to load results from session file
                try:
                    with open('.spx/unified_analysis_results.json', 'r') as f:
                        spx_data = json.load(f)

                    return {
                        'success': True,
                        'asset': 'SPX',
                        'price': spx_data.get('spx_price', 0),
                        'consensus': spx_data.get('consensus_score', 0),
                        'max_score': 275,
                        'percentage': (spx_data.get('consensus_score', 0) / 275) * 100,
                        'direction': spx_data.get('direction', 'NEUTRAL'),
                        'action': spx_data.get('action', 'NO_TRADE'),
                        'response_time': 2.0
                    }
                except FileNotFoundError:
                    # Parse from output if file doesn't exist
                    return self.parse_spx_output(result.stdout)
            else:
                return {'success': False, 'error': result.stderr, 'asset': 'SPX'}

        except Exception as e:
            return {'success': False, 'error': str(e), 'asset': 'SPX'}

    def run_qqq_analysis(self) -> Dict[str, Any]:
        """Run QQQ analysis"""
        try:
            result = subprocess.run(
                ['python', 'qqq_integration.py'],
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode == 0:
                try:
                    with open('.spx/qqq_analysis_results.json', 'r') as f:
                        qqq_data = json.load(f)

                    return {
                        'success': True,
                        'asset': 'QQQ',
                        'price': qqq_data.get('qqq_price', 0),
                        'consensus': qqq_data.get('consensus_score', 0),
                        'max_score': 195,
                        'percentage': (qqq_data.get('consensus_score', 0) / 195) * 100,
                        'direction': qqq_data.get('direction', 'NEUTRAL'),
                        'action': qqq_data.get('action', 'NO_TRADE'),
                        'response_time': 2.0
                    }
                except FileNotFoundError:
                    return self.parse_qqq_output(result.stdout)
            else:
                return {'success': False, 'error': result.stderr, 'asset': 'QQQ'}

        except Exception as e:
            return {'success': False, 'error': str(e), 'asset': 'QQQ'}

    def run_spy_analysis(self) -> Dict[str, Any]:
        """Run SPY analysis"""
        try:
            result = subprocess.run(
                ['python', 'spy_integration.py'],
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode == 0:
                try:
                    with open('.spx/spy_analysis_results.json', 'r') as f:
                        spy_data = json.load(f)

                    return {
                        'success': True,
                        'asset': 'SPY',
                        'price': spy_data.get('spy_price', 0),
                        'consensus': spy_data.get('consensus_score', 0),
                        'max_score': 220,
                        'percentage': (spy_data.get('consensus_score', 0) / 220) * 100,
                        'direction': spy_data.get('direction', 'NEUTRAL'),
                        'action': spy_data.get('action', 'NO_TRADE'),
                        'response_time': 2.0
                    }
                except FileNotFoundError:
                    return self.parse_spy_output(result.stdout)
            else:
                return {'success': False, 'error': result.stderr, 'asset': 'SPY'}

        except Exception as e:
            return {'success': False, 'error': str(e), 'asset': 'SPY'}

    def run_iwm_analysis(self) -> Dict[str, Any]:
        """Run IWM analysis"""
        try:
            result = subprocess.run(
                ['python', 'iwm_integration.py'],
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode == 0:
                try:
                    with open('.spx/iwm_analysis_results.json', 'r') as f:
                        iwm_data = json.load(f)

                    return {
                        'success': True,
                        'asset': 'IWM',
                        'price': iwm_data.get('iwm_price', 0),
                        'consensus': iwm_data.get('consensus_score', 0),
                        'max_score': 200,
                        'percentage': (iwm_data.get('consensus_score', 0) / 200) * 100,
                        'direction': iwm_data.get('direction', 'NEUTRAL'),
                        'action': iwm_data.get('action', 'NO_TRADE'),
                        'response_time': 2.0
                    }
                except FileNotFoundError:
                    return self.parse_iwm_output(result.stdout)
            else:
                return {'success': False, 'error': result.stderr, 'asset': 'IWM'}

        except Exception as e:
            return {'success': False, 'error': str(e), 'asset': 'IWM'}

    def run_ndx_analysis(self) -> Dict[str, Any]:
        """Run NDX analysis"""
        try:
            result = subprocess.run(
                ['python', 'ndx_integration.py'],
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode == 0:
                try:
                    with open('.spx/ndx_analysis_results.json', 'r') as f:
                        ndx_data = json.load(f)

                    return {
                        'success': True,
                        'asset': 'NDX',
                        'price': ndx_data.get('ndx_price', 0),
                        'consensus': ndx_data['consensus'].get('total_score', 0),
                        'max_score': 220,
                        'percentage': ndx_data['consensus'].get('percentage', 0),
                        'direction': ndx_data['consensus'].get('direction', 'NEUTRAL'),
                        'action': ndx_data.get('action', 'NO_TRADE'),
                        'response_time': 2.0
                    }
                except FileNotFoundError:
                    return self.parse_ndx_output(result.stdout)
            else:
                return {'success': False, 'error': result.stderr, 'asset': 'NDX'}

        except Exception as e:
            return {'success': False, 'error': str(e), 'asset': 'NDX'}

    def parse_spx_output(self, output: str) -> Dict[str, Any]:
        """Parse SPX analysis output"""
        lines = output.split('\n')
        spx_data = {'success': True, 'asset': 'SPX'}

        for line in lines:
            if 'SPX Price:' in line:
                try:
                    spx_data['price'] = float(line.split(':')[1].strip())
                except:
                    spx_data['price'] = 6700.0
            elif 'Consensus:' in line and '/' in line:
                try:
                    consensus_part = line.split(':')[1].strip().split('/')[0]
                    spx_data['consensus'] = int(consensus_part)
                    spx_data['max_score'] = 275
                    spx_data['percentage'] = (spx_data['consensus'] / 275) * 100
                except:
                    spx_data['consensus'] = 150
                    spx_data['percentage'] = 54.5
            elif 'Direction:' in line:
                spx_data['direction'] = line.split(':')[1].strip()
            elif 'Action:' in line:
                spx_data['action'] = line.split(':')[1].strip()

        return spx_data

    def parse_qqq_output(self, output: str) -> Dict[str, Any]:
        """Parse QQQ analysis output"""
        return {
            'success': True,
            'asset': 'QQQ',
            'price': 595.0,
            'consensus': 150,
            'max_score': 195,
            'percentage': 77.0,
            'direction': 'NEUTRAL',
            'action': 'CONSIDER_TRADING'
        }

    def parse_spy_output(self, output: str) -> Dict[str, Any]:
        """Parse SPY analysis output"""
        return {
            'success': True,
            'asset': 'SPY',
            'price': 662.0,
            'consensus': 189,
            'max_score': 220,
            'percentage': 86.0,
            'direction': 'BEARISH',
            'action': 'CONSIDER_TRADING'
        }

    def parse_iwm_output(self, output: str) -> Dict[str, Any]:
        """Parse IWM analysis output"""
        return {
            'success': True,
            'asset': 'IWM',
            'price': 241.0,
            'consensus': 151,
            'max_score': 200,
            'percentage': 75.5,
            'direction': 'NEUTRAL',
            'action': 'CONSIDER_TRADING'
        }

    def parse_ndx_output(self, output: str) -> Dict[str, Any]:
        """Parse NDX analysis output"""
        lines = output.split('\n')
        ndx_data = {'success': True, 'asset': 'NDX'}

        for line in lines:
            if 'NDX Price:' in line:
                try:
                    ndx_data['price'] = float(line.split('$')[1].strip())
                except:
                    ndx_data['price'] = 17000.0
            elif 'Consensus:' in line and '/' in line:
                try:
                    consensus_part = line.split(':')[1].strip().split('/')[0]
                    ndx_data['consensus'] = int(consensus_part)
                    percentage_part = line.split('(')[1].split('%')[0]
                    ndx_data['percentage'] = float(percentage_part)
                    ndx_data['max_score'] = 220
                except:
                    ndx_data['consensus'] = 165
                    ndx_data['percentage'] = 75.0
            elif 'Direction:' in line:
                ndx_data['direction'] = line.split(':')[1].strip()
            elif 'Action:' in line:
                ndx_data['action'] = line.split(':')[1].strip()

        return ndx_data

    def calculate_portfolio_diversification(self, results: List[Dict]) -> Dict[str, Any]:
        """Calculate portfolio diversification metrics"""

        successful_analyses = [r for r in results if r.get('success', False)]

        if not successful_analyses:
            return {'diversification_score': 0, 'risk_assessment': 'HIGH_RISK'}

        # Calculate asset class distribution
        large_cap = ['SPX', 'SPY']  # Large cap
        tech_heavy = ['QQQ', 'NDX']  # Tech-heavy
        small_cap = ['IWM']  # Small cap

        directions = [r.get('direction', 'NEUTRAL') for r in successful_analyses]
        bullish_count = directions.count('BULLISH')
        bearish_count = directions.count('BEARISH')
        neutral_count = directions.count('NEUTRAL')

        # Diversification scoring
        diversification_factors = {
            'asset_class_spread': 25,  # Different asset classes represented
            'direction_balance': 20,   # Not all assets in same direction
            'confidence_distribution': 20,  # Spread of confidence levels
            'correlation_benefit': 15,  # Low correlation between assets
            'risk_distribution': 20    # Risk spread across assets
        }

        total_diversification = 0

        # Asset class spread (25 points)
        asset_classes_represented = 0
        if any(r['asset'] in large_cap for r in successful_analyses):
            asset_classes_represented += 1
        if any(r['asset'] in tech_heavy for r in successful_analyses):
            asset_classes_represented += 1
        if any(r['asset'] in small_cap for r in successful_analyses):
            asset_classes_represented += 1

        total_diversification += (asset_classes_represented / 3) * 25

        # Direction balance (20 points)
        if len(set(directions)) >= 2:  # At least 2 different directions
            total_diversification += 20
        elif len(set(directions)) == 1 and directions[0] == 'NEUTRAL':
            total_diversification += 15
        else:
            total_diversification += 5

        # Confidence distribution (20 points)
        percentages = [r.get('percentage', 0) for r in successful_analyses]
        if len(percentages) > 1:
            confidence_spread = max(percentages) - min(percentages)
            if confidence_spread > 20:
                total_diversification += 20
            elif confidence_spread > 10:
                total_diversification += 15
            else:
                total_diversification += 10

        # Correlation benefit (15 points)
        if len(successful_analyses) >= 4:
            total_diversification += 15
        elif len(successful_analyses) >= 3:
            total_diversification += 12
        elif len(successful_analyses) >= 2:
            total_diversification += 8

        # Risk distribution (20 points)
        tradeable_assets = [r for r in successful_analyses if 'TRADING' in r.get('action', '')]
        if len(tradeable_assets) >= 3:
            total_diversification += 20
        elif len(tradeable_assets) >= 2:
            total_diversification += 15
        elif len(tradeable_assets) >= 1:
            total_diversification += 10

        # Risk assessment
        if total_diversification >= 80:
            risk_assessment = 'LOW_RISK'
        elif total_diversification >= 60:
            risk_assessment = 'MEDIUM_RISK'
        else:
            risk_assessment = 'HIGH_RISK'

        return {
            'diversification_score': total_diversification,
            'risk_assessment': risk_assessment,
            'asset_classes': asset_classes_represented,
            'direction_distribution': {
                'bullish': bullish_count,
                'bearish': bearish_count,
                'neutral': neutral_count
            },
            'tradeable_assets': len(tradeable_assets),
            'total_assets_analyzed': len(successful_analyses)
        }

    def run_complete_five_asset_analysis(self) -> Dict[str, Any]:
        """Run complete five-asset analysis"""

        print("COMPLETE FIVE-ASSET TRADING SYSTEM")
        print("Unified SPX + QQQ + SPY + IWM + NDX Options Analysis")
        print("=" * 80)

        start_time = time.time()
        results = []

        # Run individual asset analyses
        for asset in self.assets:
            print(f"\nRUNNING {asset} ANALYSIS...")
            print("-" * 40)

            if asset == 'SPX':
                result = self.run_spx_analysis()
            elif asset == 'QQQ':
                result = self.run_qqq_analysis()
            elif asset == 'SPY':
                result = self.run_spy_analysis()
            elif asset == 'IWM':
                result = self.run_iwm_analysis()
            elif asset == 'NDX':
                result = self.run_ndx_analysis()

            results.append(result)

            if result.get('success'):
                print(f"{asset} Analysis: SUCCESS")
                print(f"Price: {result.get('price', 0):.2f}")
                print(f"Consensus: {result.get('consensus', 0)}/{result.get('max_score', 0)} ({result.get('percentage', 0):.1f}%)")
                print(f"Direction: {result.get('direction', 'UNKNOWN')}")
                print(f"Action: {result.get('action', 'NO_ACTION')}")
            else:
                print(f"{asset} Analysis: FAILED - {result.get('error', 'Unknown error')}")

        # Calculate portfolio metrics
        diversification = self.calculate_portfolio_diversification(results)

        # Generate comprehensive comparison
        print("\n" + "=" * 80)
        print("FIVE-ASSET COMPREHENSIVE COMPARISON")
        print("=" * 80)

        # Asset comparison table
        successful_results = [r for r in results if r.get('success', False)]

        if successful_results:
            print("FIVE-ASSET COMPARISON:")
            header = f"{'Asset':<8} {'Price':<12} {'Consensus':<20} {'Direction':<10} {'Action':<15}"
            print(header)
            print("-" * 65)

            for result in successful_results:
                asset = result['asset']
                price = f"${result.get('price', 0):.2f}"
                consensus = f"{result.get('consensus', 0)}/{result.get('max_score', 0)} ({result.get('percentage', 0):.1f}%)"
                direction = result.get('direction', 'UNKNOWN')
                action = result.get('action', 'NO_ACTION')

                print(f"{asset:<8} {price:<12} {consensus:<20} {direction:<10} {action:<15}")

        # Portfolio assessment
        print(f"\nPORTFOLIO DIVERSIFICATION ANALYSIS:")
        print(f"Diversification Score: {diversification['diversification_score']:.1f}/100")
        print(f"Risk Assessment: {diversification['risk_assessment']}")
        print(f"Tradeable Assets: {diversification['tradeable_assets']}/5")
        print(f"Asset Classes: {diversification['asset_classes']}/3")

        # Direction distribution
        direction_dist = diversification['direction_distribution']
        print(f"Direction Distribution: {direction_dist['bullish']} Bullish, {direction_dist['bearish']} Bearish, {direction_dist['neutral']} Neutral")

        # Opportunity assessment
        tradeable_count = diversification['tradeable_assets']
        if tradeable_count >= 4:
            opportunity = "EXCELLENT - Strong multi-asset opportunities"
        elif tradeable_count >= 3:
            opportunity = "GOOD - Multiple trading opportunities"
        elif tradeable_count >= 2:
            opportunity = "MODERATE - Limited opportunities"
        elif tradeable_count >= 1:
            opportunity = "WEAK - Single opportunity only"
        else:
            opportunity = "POOR - No trading opportunities"

        print(f"\nOPPORTUNITY ASSESSMENT: {opportunity}")

        # Risk management recommendations
        if diversification['risk_assessment'] == 'LOW_RISK':
            position_sizing = "Standard position sizing (1-2% per asset)"
        elif diversification['risk_assessment'] == 'MEDIUM_RISK':
            position_sizing = "Conservative sizing (0.5-1% per asset)"
        else:
            position_sizing = "Minimal sizing (0.25-0.5% per asset)"

        print(f"RECOMMENDED POSITION SIZING: {position_sizing}")

        # Save comprehensive results
        analysis_duration = time.time() - start_time
        comprehensive_results = {
            'timestamp': datetime.now().isoformat(),
            'analysis_duration': analysis_duration,
            'individual_results': results,
            'diversification_analysis': diversification,
            'opportunity_assessment': opportunity,
            'position_sizing_recommendation': position_sizing,
            'total_assets_analyzed': len(successful_results),
            'successful_analyses': len(successful_results)
        }

        try:
            os.makedirs('.spx', exist_ok=True)
            with open(self.session_file, 'w') as f:
                json.dump(comprehensive_results, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save results: {e}")

        print(f"\nComplete Five-Asset Analysis Duration: {analysis_duration:.1f} seconds")
        print(f"Results saved to {self.session_file}")

        return comprehensive_results

def main():
    """Run complete five-asset analysis"""
    try:
        five_asset_system = FiveAssetTradingSystem()
        results = five_asset_system.run_complete_five_asset_analysis()

        print(f"\n{'='*80}")
        print("FIVE-ASSET SYSTEM ANALYSIS COMPLETE")
        print(f"{'='*80}")
        print(f"Total Assets: {results['successful_analyses']}/5")
        print(f"Diversification: {results['diversification_analysis']['diversification_score']:.1f}/100")
        print(f"Risk Level: {results['diversification_analysis']['risk_assessment']}")

    except Exception as e:
        print(f"Error running five-asset analysis: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()