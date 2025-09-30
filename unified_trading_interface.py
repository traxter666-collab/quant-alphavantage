#!/usr/bin/env python3
"""
Unified Trading Interface - Master Command System
Intelligent routing and analysis across all trading systems
"""

import os
import json
import re
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

class UnifiedTradingInterface:
    """Master trading interface with intelligent command routing"""

    def __init__(self):
        # Available systems and their capabilities
        self.systems = {
            'options': {
                'symbols': ['SPX', 'NDX', 'SPY', 'QQQ', 'IWM'],
                'modules': {
                    'basic': 'spx_auto.py',
                    'ndx': 'ndx_integration.py',
                    'multi_asset': 'five_asset_integration.py'
                },
                'strengths': ['0DTE', 'pattern_recognition', 'consensus_scoring']
            },
            'futures': {
                'symbols': ['ES', 'NQ', 'GC'],
                'modules': {
                    'basic': 'futures_integration.py',
                    'smart': 'smart_futures_integration.py',
                    'enhanced_logic': 'enhanced_futures_logic.py'
                },
                'strengths': ['24_hour_trading', 'leverage', 'market_correlation']
            },
            'integrated': {
                'symbols': ['ALL'],
                'modules': {
                    'multi_asset': 'multi_asset_system.py',
                    'portfolio': 'multi_asset_system.py',
                    'performance': 'performance_optimizer.py'
                },
                'strengths': ['portfolio_allocation', 'risk_management', 'diversification']
            }
        }

        # Command patterns and their mappings
        self.command_patterns = {
            # Natural language patterns
            r'trade (\w+)': 'smart_analysis',
            r'(\w+) price': 'quick_price',
            r'(\w+) analysis': 'detailed_analysis',
            r'buy (\w+)': 'trade_signal',
            r'sell (\w+)': 'trade_signal',
            r'portfolio': 'portfolio_analysis',
            r'multi asset': 'multi_asset_analysis',
            r'performance': 'performance_tracking',
            r'risk check': 'risk_assessment',
            r'market status': 'market_overview',
            r'best trade': 'opportunity_scan',
            r'smart (\w+)': 'enhanced_analysis'
        }

        # Intent classification
        self.intent_keywords = {
            'quick': ['price', 'quote', 'current', 'now', 'quick'],
            'detailed': ['analysis', 'full', 'complete', 'detailed', 'comprehensive'],
            'trading': ['trade', 'buy', 'sell', 'signal', 'setup', 'entry'],
            'portfolio': ['portfolio', 'allocation', 'multi', 'diversify'],
            'risk': ['risk', 'sizing', 'management', 'heat', 'stop'],
            'smart': ['smart', 'enhanced', 'intelligent', 'ai', 'advanced']
        }

        print("Unified Trading Interface initialized")
        print("Natural language command processing enabled")
        print("Available: Options | Futures | Multi-Asset | Portfolio")

    def process_command(self, user_input: str) -> Dict[str, Any]:
        """Process natural language trading command"""

        # Clean and normalize input
        command = user_input.lower().strip()

        print(f"\nProcessing command: '{user_input}'")
        print("=" * 60)

        # Step 1: Parse command and extract intent
        parsed = self._parse_command(command)

        # Step 2: Determine optimal routing
        routing = self._determine_routing(parsed)

        # Step 3: Execute analysis
        result = self._execute_analysis(routing, parsed)

        # Step 4: Format unified response
        unified_response = self._format_unified_response(result, parsed)

        return unified_response

    def _parse_command(self, command: str) -> Dict[str, Any]:
        """Parse command to extract symbols, intent, and parameters"""

        parsed = {
            'original_command': command,
            'symbols': [],
            'intent': 'unknown',
            'analysis_type': 'basic',
            'parameters': {},
            'confidence': 0.0
        }

        # Extract symbols
        symbols = self._extract_symbols(command)
        parsed['symbols'] = symbols

        # Determine intent
        intent, confidence = self._classify_intent(command)
        parsed['intent'] = intent
        parsed['confidence'] = confidence

        # Determine analysis type
        analysis_type = self._determine_analysis_type(command, symbols)
        parsed['analysis_type'] = analysis_type

        # Extract parameters
        parameters = self._extract_parameters(command)
        parsed['parameters'] = parameters

        print(f"Parsed: Symbols={symbols}, Intent={intent}, Type={analysis_type}")

        return parsed

    def _extract_symbols(self, command: str) -> List[str]:
        """Extract trading symbols from command"""

        symbols = []

        # Known symbols to look for
        all_symbols = ['SPX', 'NDX', 'SPY', 'QQQ', 'IWM', 'ES', 'NQ', 'GC', 'GOLD']

        # Direct symbol matches
        for symbol in all_symbols:
            if symbol.lower() in command:
                symbols.append(symbol)

        # Handle aliases
        aliases = {
            'es': 'ES',
            'emini': 'ES',
            's&p': 'ES',
            'spx': 'SPX',
            'nasdaq': 'NQ',
            'nq': 'NQ',
            'gold': 'GC',
            'gc': 'GC',
            'qqq': 'QQQ',
            'spy': 'SPY',
            'iwm': 'IWM',
            'ndx': 'NDX'
        }

        for alias, symbol in aliases.items():
            if alias in command and symbol not in symbols:
                symbols.append(symbol)

        # If no symbols found, check for portfolio/multi-asset intent
        portfolio_keywords = ['portfolio', 'multi', 'all', 'everything', 'diversified']
        if any(keyword in command for keyword in portfolio_keywords):
            symbols = ['PORTFOLIO']

        return symbols

    def _classify_intent(self, command: str) -> Tuple[str, float]:
        """Classify user intent with confidence score"""

        intent_scores = {intent: 0 for intent in self.intent_keywords.keys()}

        # Score based on keyword presence
        for intent, keywords in self.intent_keywords.items():
            for keyword in keywords:
                if keyword in command:
                    intent_scores[intent] += 1

        # Determine highest scoring intent
        if max(intent_scores.values()) == 0:
            return 'detailed', 0.5  # Default to detailed analysis

        best_intent = max(intent_scores, key=intent_scores.get)
        max_score = intent_scores[best_intent]
        confidence = min(max_score / 3.0, 1.0)  # Normalize to 0-1

        return best_intent, confidence

    def _determine_analysis_type(self, command: str, symbols: List[str]) -> str:
        """Determine what type of analysis to perform"""

        # Portfolio analysis
        if 'PORTFOLIO' in symbols or any(word in command for word in ['portfolio', 'allocation', 'multi asset']):
            return 'portfolio'

        # Performance tracking
        if any(word in command for word in ['performance', 'tracking', 'history', 'stats']):
            return 'performance'

        # Smart/enhanced analysis
        if any(word in command for word in ['smart', 'enhanced', 'intelligent', 'advanced']):
            return 'smart'

        # Quick price check
        if any(word in command for word in ['price', 'quote', 'current', 'now']) and len(symbols) == 1:
            return 'quick'

        # Multi-asset analysis
        if len(symbols) > 1:
            return 'multi_asset'

        # Single asset analysis
        if len(symbols) == 1:
            symbol = symbols[0]
            if symbol in ['ES', 'NQ', 'GC']:
                return 'futures'
            elif symbol in ['SPX', 'NDX', 'SPY', 'QQQ', 'IWM']:
                return 'options'

        # Default
        return 'detailed'

    def _extract_parameters(self, command: str) -> Dict[str, Any]:
        """Extract additional parameters from command"""

        parameters = {}

        # Account size
        account_match = re.search(r'(\$?[\d,]+k?)\s*account', command)
        if account_match:
            account_str = account_match.group(1).replace('$', '').replace(',', '')
            if 'k' in account_str.lower():
                parameters['account_size'] = float(account_str.lower().replace('k', '')) * 1000
            else:
                parameters['account_size'] = float(account_str)

        # Risk level
        if 'conservative' in command:
            parameters['risk_level'] = 'conservative'
        elif 'aggressive' in command:
            parameters['risk_level'] = 'aggressive'
        elif 'moderate' in command:
            parameters['risk_level'] = 'moderate'

        # Time horizon
        if 'scalp' in command or '0dte' in command:
            parameters['time_horizon'] = 'scalp'
        elif 'swing' in command:
            parameters['time_horizon'] = 'swing'
        elif 'day' in command:
            parameters['time_horizon'] = 'day'

        return parameters

    def _determine_routing(self, parsed: Dict[str, Any]) -> Dict[str, Any]:
        """Determine optimal system routing based on parsed command"""

        routing = {
            'system': 'options',  # default
            'module': 'basic',
            'command': '',
            'parameters': [],
            'confidence': 0.8
        }

        symbols = parsed['symbols']
        intent = parsed['intent']
        analysis_type = parsed['analysis_type']

        # Portfolio analysis
        if analysis_type == 'portfolio' or 'PORTFOLIO' in symbols:
            routing.update({
                'system': 'integrated',
                'module': 'multi_asset',
                'command': 'python multi_asset_system.py',
                'confidence': 0.9
            })
            return routing

        # Performance tracking
        if analysis_type == 'performance':
            routing.update({
                'system': 'integrated',
                'module': 'performance',
                'command': 'python performance_optimizer.py',
                'confidence': 0.9
            })
            return routing

        # Single symbol analysis
        if len(symbols) == 1:
            symbol = symbols[0]

            # Futures routing
            if symbol in ['ES', 'NQ', 'GC']:
                if analysis_type == 'smart':
                    routing.update({
                        'system': 'futures',
                        'module': 'smart',
                        'command': f'python smart_futures_integration.py {symbol}',
                        'confidence': 0.95
                    })
                elif analysis_type == 'quick':
                    routing.update({
                        'system': 'futures',
                        'module': 'basic',
                        'command': f'python futures_integration.py {symbol}',
                        'confidence': 0.9
                    })
                else:
                    routing.update({
                        'system': 'futures',
                        'module': 'smart',
                        'command': f'python smart_futures_integration.py {symbol}',
                        'confidence': 0.85
                    })

            # Options routing
            elif symbol in ['SPX', 'NDX', 'SPY', 'QQQ', 'IWM']:
                if symbol == 'NDX':
                    routing.update({
                        'system': 'options',
                        'module': 'ndx',
                        'command': 'python ndx_integration.py',
                        'confidence': 0.9
                    })
                elif analysis_type == 'quick':
                    routing.update({
                        'system': 'options',
                        'module': 'basic',
                        'command': f'python spx_auto.py',  # Placeholder
                        'confidence': 0.8
                    })
                else:
                    routing.update({
                        'system': 'options',
                        'module': 'basic',
                        'command': f'python spx_auto.py',  # Placeholder
                        'confidence': 0.85
                    })

        # Multi-asset analysis
        elif len(symbols) > 1:
            routing.update({
                'system': 'integrated',
                'module': 'multi_asset',
                'command': 'python multi_asset_system.py',
                'confidence': 0.9
            })

        return routing

    def _execute_analysis(self, routing: Dict[str, Any], parsed: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the analysis using the determined routing"""

        print(f"Executing: {routing['system']}.{routing['module']}")
        print(f"Command: {routing['command']}")

        try:
            # Import required modules based on routing
            if routing['system'] == 'futures':
                if routing['module'] == 'smart':
                    from smart_futures_integration import SmartFuturesIntegration
                    system = SmartFuturesIntegration()

                    symbol = parsed['symbols'][0] if parsed['symbols'] else 'ES'
                    account_size = parsed['parameters'].get('account_size', 25000)

                    result = system.smart_futures_analysis(symbol, account_size)

                elif routing['module'] == 'basic':
                    from futures_integration import FuturesIntegration
                    system = FuturesIntegration()

                    symbol = parsed['symbols'][0] if parsed['symbols'] else 'ES'
                    result = system.analyze_futures_contract(symbol)

            elif routing['system'] == 'options':
                if routing['module'] == 'ndx':
                    from ndx_integration import NDXIntegration
                    system = NDXIntegration()
                    result = system.run_ndx_analysis()

                else:
                    # Placeholder for SPX options
                    result = {
                        'symbol': parsed['symbols'][0] if parsed['symbols'] else 'SPX',
                        'status': 'Options analysis placeholder',
                        'message': 'SPX options analysis would be executed here'
                    }

            elif routing['system'] == 'integrated':
                if routing['module'] == 'multi_asset':
                    from multi_asset_system import MultiAssetTradingSystem
                    system = MultiAssetTradingSystem()

                    account_size = parsed['parameters'].get('account_size', 100000)
                    result = system.run_multi_asset_analysis(account_size)

                elif routing['module'] == 'performance':
                    from performance_optimizer import PerformanceOptimizer
                    system = PerformanceOptimizer()
                    result = system.optimize_multi_asset_analysis()

            else:
                result = {'error': f'Unknown routing: {routing}'}

        except ImportError as e:
            result = {
                'error': f'Module import failed: {e}',
                'routing': routing,
                'suggestion': 'Ensure all required modules are in the same directory'
            }
        except Exception as e:
            result = {
                'error': f'Execution failed: {e}',
                'routing': routing
            }

        return result

    def _format_unified_response(self, result: Dict[str, Any], parsed: Dict[str, Any]) -> Dict[str, Any]:
        """Format response in unified format across all systems"""

        if 'error' in result:
            return {
                'success': False,
                'error': result['error'],
                'parsed_command': parsed,
                'timestamp': datetime.now().isoformat()
            }

        # Determine response format based on result type
        unified_response = {
            'success': True,
            'command_processed': parsed['original_command'],
            'analysis_type': parsed['analysis_type'],
            'symbols': parsed['symbols'],
            'timestamp': datetime.now().isoformat()
        }

        # Extract key information based on result structure
        if 'final_recommendation' in result:
            # Smart futures format
            recommendation = result['final_recommendation']
            unified_response.update({
                'primary_recommendation': {
                    'action': recommendation.get('action', 'UNKNOWN'),
                    'confidence': recommendation.get('confidence', 'UNKNOWN'),
                    'contracts': recommendation.get('contracts', 0),
                    'reasoning': recommendation.get('reasoning', 'No reasoning provided')
                },
                'risk_metrics': {
                    'risk_percent': recommendation.get('risk_percent', 0),
                    'score': result.get('combined_insights', {}).get('combined_score', 0)
                }
            })

        elif 'signals' in result:
            # Basic futures format
            signals = result.get('signals', [])
            if signals:
                signal = signals[0]
                unified_response.update({
                    'primary_recommendation': {
                        'action': signal.get('action', 'UNKNOWN'),
                        'contracts': signal.get('contracts', 0),
                        'entry_price': signal.get('entry_price', 0),
                        'stop_loss': signal.get('stop_loss', 0),
                        'profit_target': signal.get('profit_target', 0)
                    }
                })

        elif 'portfolio_allocation' in result:
            # Multi-asset format
            allocation = result['portfolio_allocation']
            unified_response.update({
                'portfolio_analysis': {
                    'total_allocation': allocation.get('total_allocation', 0) * 100,
                    'options_opportunities': len(allocation.get('allocations', {}).get('options', [])),
                    'futures_opportunities': len(allocation.get('allocations', {}).get('futures', [])),
                    'risk_compliance': allocation.get('risk_management', {}).get('compliance', False)
                }
            })

        # Add raw result for detailed access
        unified_response['detailed_result'] = result

        return unified_response

    def display_unified_response(self, response: Dict[str, Any]) -> None:
        """Display response in user-friendly format"""

        if not response.get('success'):
            print(f"\nERROR: {response.get('error', 'Unknown error')}")
            return

        print(f"\nUNIFIED TRADING ANALYSIS")
        print(f"Command: {response['command_processed']}")
        print(f"Analysis: {response['analysis_type'].upper()}")
        print(f"Symbols: {', '.join(response['symbols'])}")
        print("=" * 60)

        # Display primary recommendation
        if 'primary_recommendation' in response:
            rec = response['primary_recommendation']
            print(f"\nPRIMARY RECOMMENDATION:")
            print(f"Action: {rec.get('action', 'N/A')}")

            if 'confidence' in rec:
                print(f"Confidence: {rec['confidence']}")

            if 'contracts' in rec and rec['contracts'] > 0:
                print(f"Contracts: {rec['contracts']}")

            if 'entry_price' in rec:
                print(f"Entry: ${rec['entry_price']:.2f}")

            if 'reasoning' in rec:
                print(f"Reasoning: {rec['reasoning']}")

        # Display portfolio analysis
        if 'portfolio_analysis' in response:
            portfolio = response['portfolio_analysis']
            print(f"\nPORTFOLIO ANALYSIS:")
            print(f"Total Allocation: {portfolio.get('total_allocation', 0):.1f}%")
            print(f"Options Opportunities: {portfolio.get('options_opportunities', 0)}")
            print(f"Futures Opportunities: {portfolio.get('futures_opportunities', 0)}")
            print(f"Risk Compliance: {'PASS' if portfolio.get('risk_compliance') else 'FAIL'}")

        # Display risk metrics
        if 'risk_metrics' in response:
            risk = response['risk_metrics']
            print(f"\nRISK METRICS:")
            if 'risk_percent' in risk:
                print(f"Account Risk: {risk['risk_percent']:.1f}%")
            if 'score' in risk:
                print(f"Analysis Score: {risk['score']:.1f}%")

        print(f"\nAnalysis completed at {response['timestamp']}")

def main():
    """Main interface for unified trading commands"""

    interface = UnifiedTradingInterface()

    if len(sys.argv) > 1:
        # Command line usage
        command = ' '.join(sys.argv[1:])
        response = interface.process_command(command)
        interface.display_unified_response(response)
    else:
        # Interactive mode
        print("\nUNIFIED TRADING INTERFACE")
        print("Enter natural language trading commands:")
        print("Examples:")
        print("  - 'trade ES'")
        print("  - 'smart NQ analysis'")
        print("  - 'portfolio allocation'")
        print("  - 'ES price'")
        print("  - 'buy SPX calls'")
        print("  - Type 'exit' to quit")
        print()

        while True:
            try:
                user_input = input("trading> ").strip()

                if user_input.lower() in ['exit', 'quit', 'q']:
                    print("Goodbye!")
                    break

                if user_input:
                    response = interface.process_command(user_input)
                    interface.display_unified_response(response)

            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except Exception as e:
                print(f"Error: {e}")

if __name__ == "__main__":
    main()