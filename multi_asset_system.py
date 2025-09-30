#!/usr/bin/env python3
"""
Multi-Asset Trading System - Options + Futures Integration
Complete trading system combining SPX/NDX options with ES/NQ/GC futures
"""

import os
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional

class MultiAssetTradingSystem:
    """Comprehensive multi-asset trading system"""

    def __init__(self):
        self.api_key = os.getenv('ALPHAVANTAGE_API_KEY')

        # Asset specifications
        self.assets = {
            'options': {
                'SPX': {'name': 'S&P 500 Index Options', 'proxy': 'SPY', 'multiplier': 10},
                'NDX': {'name': 'NASDAQ-100 Index Options', 'proxy': 'QQQ', 'multiplier': 28.5},
                'SPY': {'name': 'SPDR S&P 500 ETF Options', 'proxy': 'SPY', 'multiplier': 1},
                'QQQ': {'name': 'Invesco QQQ Trust Options', 'proxy': 'QQQ', 'multiplier': 1},
                'IWM': {'name': 'iShares Russell 2000 ETF Options', 'proxy': 'IWM', 'multiplier': 1}
            },
            'futures': {
                'ES': {
                    'name': 'E-mini S&P 500',
                    'symbol': 'ES=F',
                    'point_value': 50,
                    'margin_day': 500,
                    'margin_overnight': 12500,
                    'correlation': 'SPX'
                },
                'NQ': {
                    'name': 'E-mini NASDAQ',
                    'symbol': 'NQ=F',
                    'point_value': 20,
                    'margin_day': 300,
                    'margin_overnight': 7500,
                    'correlation': 'NDX'
                },
                'GC': {
                    'name': 'Gold',
                    'symbol': 'GC=F',
                    'point_value': 100,
                    'margin_day': 1000,
                    'margin_overnight': 10000,
                    'correlation': 'SAFE_HAVEN'
                }
            }
        }

        # Portfolio allocation rules
        self.allocation_rules = {
            'max_options_allocation': 0.60,  # 60% max in options
            'max_futures_allocation': 0.40,  # 40% max in futures
            'max_single_asset': 0.20,       # 20% max in any single asset
            'max_portfolio_heat': 0.15,     # 15% max total risk
            'correlation_limit': 0.70       # Max 70% in correlated assets
        }

        print("Multi-Asset Trading System initialized")
        print("Options: SPX, NDX, SPY, QQQ, IWM")
        print("Futures: ES, NQ, GC")

    def get_multi_asset_data(self) -> Dict[str, Any]:
        """Get real-time data for all assets"""

        data = {
            'options_underlyings': {},
            'futures': {},
            'timestamp': datetime.now().isoformat()
        }

        try:
            import requests

            # Get options underlying data
            options_symbols = ['SPY', 'QQQ', 'IWM']
            for symbol in options_symbols:
                try:
                    quote_url = f"https://www.alphavantage.co/query"
                    quote_params = {
                        'function': 'GLOBAL_QUOTE',
                        'symbol': symbol,
                        'apikey': self.api_key
                    }

                    response = requests.get(quote_url, params=quote_params, timeout=10)
                    quote_data = response.json()

                    if 'Global Quote' in quote_data:
                        quote = quote_data['Global Quote']
                        price = float(quote['05. price'])
                        change = float(quote['09. change'])
                        change_percent = float(quote['10. change percent'].replace('%', ''))

                        data['options_underlyings'][symbol] = {
                            'price': price,
                            'change': change,
                            'change_percent': change_percent,
                            'success': True
                        }

                        # Calculate index estimates
                        if symbol == 'SPY':
                            data['options_underlyings']['SPX_ESTIMATE'] = {
                                'price': price * 10,
                                'change_percent': change_percent
                            }
                        elif symbol == 'QQQ':
                            data['options_underlyings']['NDX_ESTIMATE'] = {
                                'price': price * 28.5,
                                'change_percent': change_percent
                            }

                except Exception as e:
                    print(f"Failed to get {symbol}: {e}")
                    # Fallback data
                    fallback_prices = {'SPY': 565.0, 'QQQ': 496.0, 'IWM': 225.0}
                    data['options_underlyings'][symbol] = {
                        'price': fallback_prices.get(symbol, 500.0),
                        'change': 2.50,
                        'change_percent': 0.45,
                        'success': False,
                        'note': 'Fallback data'
                    }

            # Get futures data
            futures_symbols = ['ES=F', 'NQ=F', 'GC=F']
            futures_keys = ['ES', 'NQ', 'GC']

            for i, symbol in enumerate(futures_symbols):
                key = futures_keys[i]
                try:
                    quote_url = f"https://www.alphavantage.co/query"
                    quote_params = {
                        'function': 'GLOBAL_QUOTE',
                        'symbol': symbol,
                        'apikey': self.api_key
                    }

                    response = requests.get(quote_url, params=quote_params, timeout=10)
                    quote_data = response.json()

                    if 'Global Quote' in quote_data:
                        quote = quote_data['Global Quote']
                        price = float(quote['05. price'])
                        change = float(quote['09. change'])
                        change_percent = float(quote['10. change percent'].replace('%', ''))

                        spec = self.assets['futures'][key]
                        data['futures'][key] = {
                            'price': price,
                            'change': change,
                            'change_percent': change_percent,
                            'dollar_value': price * spec['point_value'],
                            'dollar_change': change * spec['point_value'],
                            'success': True
                        }

                except Exception as e:
                    print(f"Failed to get {symbol}: {e}")
                    # Fallback data
                    fallback_prices = {'ES': 5650.0, 'NQ': 19800.0, 'GC': 2650.0}
                    fallback_changes = {'ES': 15.25, 'NQ': 95.50, 'GC': -12.30}

                    spec = self.assets['futures'][key]
                    price = fallback_prices.get(key, 5000.0)
                    change = fallback_changes.get(key, 0.0)

                    data['futures'][key] = {
                        'price': price,
                        'change': change,
                        'change_percent': (change / price) * 100,
                        'dollar_value': price * spec['point_value'],
                        'dollar_change': change * spec['point_value'],
                        'success': False,
                        'note': 'Fallback data'
                    }

                time.sleep(0.2)  # Rate limiting

        except Exception as e:
            print(f"Error in multi-asset data fetch: {e}")

        return data

    def calculate_asset_correlations(self, data: Dict) -> Dict[str, Any]:
        """Calculate correlations between assets"""

        correlations = {}

        # Options correlations (based on change percentages)
        options_changes = {}
        for symbol, asset_data in data['options_underlyings'].items():
            if symbol not in ['SPX_ESTIMATE', 'NDX_ESTIMATE'] and 'change_percent' in asset_data:
                options_changes[symbol] = asset_data['change_percent']

        # Futures correlations
        futures_changes = {}
        for symbol, asset_data in data['futures'].items():
            if 'change_percent' in asset_data:
                futures_changes[symbol] = asset_data['change_percent']

        # Calculate correlation groups
        correlations['equity_correlation'] = {
            'spy_qqq': abs(options_changes.get('SPY', 0) - options_changes.get('QQQ', 0)),
            'es_nq': abs(futures_changes.get('ES', 0) - futures_changes.get('NQ', 0)),
            'spy_es': abs(options_changes.get('SPY', 0) - futures_changes.get('ES', 0)),
            'qqq_nq': abs(options_changes.get('QQQ', 0) - futures_changes.get('NQ', 0))
        }

        # Risk-on vs Risk-off analysis
        risk_on_assets = [
            options_changes.get('SPY', 0),
            options_changes.get('QQQ', 0),
            futures_changes.get('ES', 0),
            futures_changes.get('NQ', 0)
        ]

        risk_off_assets = [
            futures_changes.get('GC', 0),  # Gold typically inverse
            -options_changes.get('IWM', 0)  # Small caps risk-sensitive
        ]

        avg_risk_on = sum(risk_on_assets) / len(risk_on_assets)
        avg_risk_off = sum(risk_off_assets) / len(risk_off_assets)

        correlations['market_regime'] = {
            'risk_on_average': avg_risk_on,
            'risk_off_average': avg_risk_off,
            'regime': 'RISK_ON' if avg_risk_on > 0.2 else 'RISK_OFF' if avg_risk_on < -0.2 else 'NEUTRAL'
        }

        return correlations

    def calculate_multi_asset_consensus(self, data: Dict, correlations: Dict) -> Dict[str, Any]:
        """Calculate comprehensive consensus across all assets"""

        consensus = {
            'total_score': 0,
            'max_score': 400,  # Enhanced for multi-asset
            'components': {},
            'asset_scores': {},
            'direction': 'NEUTRAL',
            'confidence': 'LOW'
        }

        # Options strength (120 points max)
        options_score = 0
        options_count = 0

        for symbol, asset_data in data['options_underlyings'].items():
            if symbol not in ['SPX_ESTIMATE', 'NDX_ESTIMATE'] and 'change_percent' in asset_data:
                change_pct = asset_data['change_percent']

                # Score each options asset
                if change_pct > 1.0:
                    asset_score = 30
                elif change_pct > 0.5:
                    asset_score = 25
                elif change_pct > 0:
                    asset_score = 20
                elif change_pct > -0.5:
                    asset_score = 15
                else:
                    asset_score = 10

                options_score += asset_score
                options_count += 1
                consensus['asset_scores'][f'{symbol}_options'] = asset_score

        if options_count > 0:
            options_average = options_score / options_count
            consensus['components']['options_strength'] = min(120, options_average * 4)
        else:
            consensus['components']['options_strength'] = 60

        # Futures strength (120 points max)
        futures_score = 0
        futures_count = 0

        for symbol, asset_data in data['futures'].items():
            change_pct = asset_data['change_percent']

            # Score each futures asset
            if change_pct > 1.5:
                asset_score = 35
            elif change_pct > 0.75:
                asset_score = 30
            elif change_pct > 0:
                asset_score = 25
            elif change_pct > -0.75:
                asset_score = 20
            else:
                asset_score = 15

            futures_score += asset_score
            futures_count += 1
            consensus['asset_scores'][f'{symbol}_futures'] = asset_score

        if futures_count > 0:
            futures_average = futures_score / futures_count
            consensus['components']['futures_strength'] = min(120, futures_average * 4)
        else:
            consensus['components']['futures_strength'] = 60

        # Correlation alignment (80 points max)
        equity_corr = correlations['equity_correlation']

        # Strong correlation = higher score
        correlation_score = 0
        if equity_corr['spy_es'] < 0.3 and equity_corr['qqq_nq'] < 0.3:
            correlation_score = 70  # Strong options-futures alignment
        elif equity_corr['spy_qqq'] < 0.5 and equity_corr['es_nq'] < 0.5:
            correlation_score = 50  # Internal alignment
        else:
            correlation_score = 30  # Weak alignment

        consensus['components']['correlation_alignment'] = correlation_score

        # Market regime consistency (40 points max)
        regime = correlations['market_regime']['regime']
        risk_on_avg = correlations['market_regime']['risk_on_average']

        if regime == 'RISK_ON' and risk_on_avg > 0.5:
            regime_score = 35
        elif regime == 'RISK_OFF' and risk_on_avg < -0.5:
            regime_score = 35
        elif regime == 'NEUTRAL':
            regime_score = 25
        else:
            regime_score = 15  # Mixed signals

        consensus['components']['market_regime'] = regime_score

        # Portfolio diversification bonus (40 points max)
        # Reward for having both options and futures opportunities
        both_positive = (consensus['components']['options_strength'] > 60 and
                        consensus['components']['futures_strength'] > 60)

        if both_positive:
            diversification_score = 35
        elif consensus['components']['options_strength'] > 80 or consensus['components']['futures_strength'] > 80:
            diversification_score = 25
        else:
            diversification_score = 15

        consensus['components']['diversification_bonus'] = diversification_score

        # Calculate total
        total_score = sum(consensus['components'].values())
        consensus['total_score'] = total_score

        # Determine overall direction
        risk_on_avg = correlations['market_regime']['risk_on_average']
        if risk_on_avg > 0.3:
            consensus['direction'] = 'BULLISH'
        elif risk_on_avg < -0.3:
            consensus['direction'] = 'BEARISH'
        else:
            consensus['direction'] = 'NEUTRAL'

        # Confidence based on score and alignment
        percentage = (total_score / consensus['max_score']) * 100
        if percentage >= 80:
            consensus['confidence'] = 'HIGH'
        elif percentage >= 65:
            consensus['confidence'] = 'MEDIUM'
        else:
            consensus['confidence'] = 'LOW'

        consensus['percentage'] = percentage
        consensus['timestamp'] = datetime.now().isoformat()

        return consensus

    def generate_portfolio_allocation(self, data: Dict, consensus: Dict, account_size: float = 100000) -> Dict[str, Any]:
        """Generate optimal portfolio allocation across all assets"""

        allocation = {
            'account_size': account_size,
            'total_allocation': 0,
            'allocations': {},
            'risk_management': {},
            'portfolio_heat': 0
        }

        # Base allocation percentages
        if consensus['confidence'] == 'HIGH':
            base_allocation = 0.12  # 12% per high-confidence opportunity
        elif consensus['confidence'] == 'MEDIUM':
            base_allocation = 0.08  # 8% per medium-confidence opportunity
        else:
            base_allocation = 0.04  # 4% per low-confidence opportunity

        direction = consensus['direction']

        # Options allocations
        options_opportunities = []

        # SPY/SPX options
        if consensus['asset_scores'].get('SPY_options', 0) >= 20:
            spy_data = data['options_underlyings'].get('SPY', {})
            if spy_data.get('change_percent', 0) * (1 if direction == 'BULLISH' else -1) > 0:
                options_opportunities.append({
                    'symbol': 'SPY',
                    'type': 'CALLS' if direction == 'BULLISH' else 'PUTS',
                    'allocation_pct': base_allocation,
                    'reasoning': f'{direction} SPY options based on {spy_data.get("change_percent", 0):.2f}% move'
                })

        # QQQ/NDX options
        if consensus['asset_scores'].get('QQQ_options', 0) >= 20:
            qqq_data = data['options_underlyings'].get('QQQ', {})
            if qqq_data.get('change_percent', 0) * (1 if direction == 'BULLISH' else -1) > 0:
                options_opportunities.append({
                    'symbol': 'QQQ',
                    'type': 'CALLS' if direction == 'BULLISH' else 'PUTS',
                    'allocation_pct': base_allocation,
                    'reasoning': f'{direction} QQQ options based on {qqq_data.get("change_percent", 0):.2f}% move'
                })

        # IWM options
        if consensus['asset_scores'].get('IWM_options', 0) >= 20:
            iwm_data = data['options_underlyings'].get('IWM', {})
            if iwm_data.get('change_percent', 0) * (1 if direction == 'BULLISH' else -1) > 0:
                options_opportunities.append({
                    'symbol': 'IWM',
                    'type': 'CALLS' if direction == 'BULLISH' else 'PUTS',
                    'allocation_pct': base_allocation,
                    'reasoning': f'{direction} IWM options based on {iwm_data.get("change_percent", 0):.2f}% move'
                })

        # Futures allocations
        futures_opportunities = []

        # ES futures
        if consensus['asset_scores'].get('ES_futures', 0) >= 25:
            es_data = data['futures'].get('ES', {})
            if es_data.get('change_percent', 0) * (1 if direction == 'BULLISH' else -1) > 0:
                futures_opportunities.append({
                    'symbol': 'ES',
                    'action': 'BUY' if direction == 'BULLISH' else 'SELL',
                    'allocation_pct': base_allocation,
                    'margin_required': self.assets['futures']['ES']['margin_overnight'],
                    'reasoning': f'{direction} ES futures based on {es_data.get("change_percent", 0):.2f}% move'
                })

        # NQ futures
        if consensus['asset_scores'].get('NQ_futures', 0) >= 25:
            nq_data = data['futures'].get('NQ', {})
            if nq_data.get('change_percent', 0) * (1 if direction == 'BULLISH' else -1) > 0:
                futures_opportunities.append({
                    'symbol': 'NQ',
                    'action': 'BUY' if direction == 'BULLISH' else 'SELL',
                    'allocation_pct': base_allocation,
                    'margin_required': self.assets['futures']['NQ']['margin_overnight'],
                    'reasoning': f'{direction} NQ futures based on {nq_data.get("change_percent", 0):.2f}% move'
                })

        # GC futures (inverse correlation consideration)
        if consensus['asset_scores'].get('GC_futures', 0) >= 25:
            gc_data = data['futures'].get('GC', {})
            # Gold often moves inverse to risk assets
            gc_direction = 'SELL' if direction == 'BULLISH' else 'BUY'
            if abs(gc_data.get('change_percent', 0)) > 0.5:
                futures_opportunities.append({
                    'symbol': 'GC',
                    'action': gc_direction,
                    'allocation_pct': base_allocation * 0.7,  # Smaller allocation for hedge
                    'margin_required': self.assets['futures']['GC']['margin_overnight'],
                    'reasoning': f'{gc_direction} GC as hedge to equity exposure'
                })

        # Apply allocation limits
        total_options_allocation = sum(op['allocation_pct'] for op in options_opportunities)
        total_futures_allocation = sum(op['allocation_pct'] for op in futures_opportunities)

        # Respect allocation limits
        if total_options_allocation > self.allocation_rules['max_options_allocation']:
            scale_factor = self.allocation_rules['max_options_allocation'] / total_options_allocation
            for op in options_opportunities:
                op['allocation_pct'] *= scale_factor

        if total_futures_allocation > self.allocation_rules['max_futures_allocation']:
            scale_factor = self.allocation_rules['max_futures_allocation'] / total_futures_allocation
            for op in futures_opportunities:
                op['allocation_pct'] *= scale_factor

        # Calculate dollar allocations
        allocation['allocations']['options'] = []
        allocation['allocations']['futures'] = []

        total_portfolio_allocation = 0

        for op in options_opportunities:
            dollar_allocation = account_size * op['allocation_pct']
            op['dollar_allocation'] = dollar_allocation
            allocation['allocations']['options'].append(op)
            total_portfolio_allocation += op['allocation_pct']

        for op in futures_opportunities:
            dollar_allocation = account_size * op['allocation_pct']
            op['dollar_allocation'] = dollar_allocation

            # Calculate contracts
            margin_per_contract = op['margin_required']
            max_contracts = int(dollar_allocation / margin_per_contract)
            op['contracts'] = max(1, max_contracts)
            op['actual_margin'] = op['contracts'] * margin_per_contract

            allocation['allocations']['futures'].append(op)
            total_portfolio_allocation += op['allocation_pct']

        allocation['total_allocation'] = total_portfolio_allocation
        allocation['portfolio_heat'] = min(total_portfolio_allocation, self.allocation_rules['max_portfolio_heat'])

        # Risk management summary
        allocation['risk_management'] = {
            'total_risk_pct': total_portfolio_allocation * 100,
            'max_allowed_risk_pct': self.allocation_rules['max_portfolio_heat'] * 100,
            'options_allocation_pct': sum(op['allocation_pct'] for op in options_opportunities) * 100,
            'futures_allocation_pct': sum(op['allocation_pct'] for op in futures_opportunities) * 100,
            'compliance': total_portfolio_allocation <= self.allocation_rules['max_portfolio_heat']
        }

        return allocation

    def run_multi_asset_analysis(self, account_size: float = 100000) -> Dict[str, Any]:
        """Run complete multi-asset analysis"""

        print("MULTI-ASSET TRADING SYSTEM ANALYSIS")
        print("Options (SPY, QQQ, IWM) + Futures (ES, NQ, GC)")
        print("=" * 80)

        # Step 1: Get all asset data
        print("Step 1: Getting multi-asset market data...")
        data = self.get_multi_asset_data()

        # Step 2: Calculate correlations
        print("Step 2: Analyzing asset correlations...")
        correlations = self.calculate_asset_correlations(data)
        print(f"Market Regime: {correlations['market_regime']['regime']}")
        print(f"Risk-On Average: {correlations['market_regime']['risk_on_average']:.2f}%")

        # Step 3: Calculate consensus
        print("Step 3: Calculating multi-asset consensus...")
        consensus = self.calculate_multi_asset_consensus(data, correlations)
        print(f"Consensus: {consensus['total_score']}/{consensus['max_score']} ({consensus['percentage']:.1f}%)")
        print(f"Direction: {consensus['direction']} | Confidence: {consensus['confidence']}")

        # Step 4: Generate portfolio allocation
        print("Step 4: Generating portfolio allocation...")
        allocation = self.generate_portfolio_allocation(data, consensus, account_size)
        print(f"Total Portfolio Allocation: {allocation['total_allocation']*100:.1f}%")
        print(f"Portfolio Heat: {allocation['portfolio_heat']*100:.1f}%")

        # Compile results
        result = {
            'market_data': data,
            'correlations': correlations,
            'consensus': consensus,
            'portfolio_allocation': allocation,
            'timestamp': datetime.now().isoformat()
        }

        # Display detailed results
        print(f"\n{'='*80}")
        print(f"MULTI-ASSET PORTFOLIO RECOMMENDATION")
        print(f"{'='*80}")
        print(f"Account Size: ${account_size:,.0f}")
        print(f"Multi-Asset Consensus: {consensus['percentage']:.1f}%")
        print(f"Direction: {consensus['direction']} | Confidence: {consensus['confidence']}")
        print(f"Market Regime: {correlations['market_regime']['regime']}")

        # Options recommendations
        if allocation['allocations']['options']:
            print(f"\nOPTIONS ALLOCATIONS:")
            for i, op in enumerate(allocation['allocations']['options'], 1):
                print(f"  {i}. {op['type']} {op['symbol']} - ${op['dollar_allocation']:,.0f} ({op['allocation_pct']*100:.1f}%)")
                print(f"     Reasoning: {op['reasoning']}")

        # Futures recommendations
        if allocation['allocations']['futures']:
            print(f"\nFUTURES ALLOCATIONS:")
            for i, op in enumerate(allocation['allocations']['futures'], 1):
                print(f"  {i}. {op['action']} {op['symbol']} {op['contracts']} contracts - ${op['dollar_allocation']:,.0f}")
                print(f"     Margin: ${op['actual_margin']:,.0f} | Reasoning: {op['reasoning']}")

        # Risk management
        print(f"\nRISK MANAGEMENT:")
        rm = allocation['risk_management']
        print(f"Total Portfolio Risk: {rm['total_risk_pct']:.1f}% of account")
        print(f"Options Allocation: {rm['options_allocation_pct']:.1f}%")
        print(f"Futures Allocation: {rm['futures_allocation_pct']:.1f}%")
        print(f"Risk Compliance: {'PASS' if rm['compliance'] else 'FAIL'}")

        if not rm['compliance']:
            print(f"WARNING: Total risk {rm['total_risk_pct']:.1f}% exceeds limit {rm['max_allowed_risk_pct']:.1f}%")

        # Save results
        try:
            os.makedirs('.spx', exist_ok=True)
            with open('.spx/multi_asset_analysis.json', 'w') as f:
                json.dump(result, f, indent=2)
            print(f"\nMulti-asset analysis saved to .spx/multi_asset_analysis.json")
        except Exception as e:
            print(f"Warning: Could not save results: {e}")

        return result

def main():
    """Main execution function"""
    import sys

    system = MultiAssetTradingSystem()

    # Get account size from command line or use default
    account_size = 100000
    if len(sys.argv) > 1:
        try:
            account_size = float(sys.argv[1])
        except ValueError:
            print(f"Invalid account size: {sys.argv[1]}, using default $100,000")

    system.run_multi_asset_analysis(account_size)

if __name__ == "__main__":
    main()