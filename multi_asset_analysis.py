#!/usr/bin/env python3
"""
Multi-Asset Options Analysis System
Extends SPX system to include QQQ and IWM with cross-correlation intelligence
"""

import requests
import json
import os
from datetime import datetime
from typing import Dict, List, Optional

class MultiAssetAnalyzer:
    def __init__(self):
        self.api_key = 'ZFL38ZY98GSN7E1S'
        self.assets = {
            'SPX': {'proxy': 'SPY', 'multiplier': 10.0, 'name': 'S&P 500'},
            'QQQ': {'proxy': 'QQQ', 'multiplier': 1.0, 'name': 'Nasdaq 100'},
            'IWM': {'proxy': 'IWM', 'multiplier': 1.0, 'name': 'Russell 2000'}
        }
        self.session_file = ".spx/multi_asset_session.json"

    def get_asset_quote(self, symbol: str) -> Dict:
        """Get current quote for any asset"""
        url = f'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={self.api_key}'

        try:
            response = requests.get(url, timeout=10)
            data = response.json()

            if 'Global Quote' in data:
                quote = data['Global Quote']
                return {
                    'success': True,
                    'symbol': symbol,
                    'price': float(quote['05. price']),
                    'change': float(quote['09. change']),
                    'change_pct': float(quote['10. change percent'].rstrip('%')),
                    'volume': int(quote['06. volume']),
                    'timestamp': datetime.now()
                }
            else:
                return {'success': False, 'error': 'No quote data', 'symbol': symbol}

        except Exception as e:
            return {'success': False, 'error': str(e), 'symbol': symbol}

    def get_asset_rsi(self, symbol: str, timeframe: str = "5min") -> Dict:
        """Get RSI for asset analysis"""
        url = f'https://www.alphavantage.co/query?function=RSI&symbol={symbol}&interval={timeframe}&time_period=14&series_type=close&apikey={self.api_key}'

        try:
            response = requests.get(url, timeout=15)
            data = response.json()

            if 'Technical Analysis: RSI' in data:
                rsi_data = data['Technical Analysis: RSI']
                latest_date = max(rsi_data.keys())
                latest_rsi = float(rsi_data[latest_date]['RSI'])

                return {
                    'success': True,
                    'symbol': symbol,
                    'rsi': latest_rsi,
                    'timestamp': latest_date
                }
            else:
                return {'success': False, 'error': 'No RSI data', 'symbol': symbol}

        except Exception as e:
            return {'success': False, 'error': str(e), 'symbol': symbol}

    def calculate_correlation_matrix(self, quotes: Dict) -> Dict:
        """Calculate cross-asset correlation intelligence"""
        correlations = {}

        # Standard correlation assumptions (update with real data in production)
        correlations['SPX_QQQ'] = 0.85  # High tech correlation
        correlations['SPX_IWM'] = 0.75  # Moderate small cap correlation
        correlations['QQQ_IWM'] = 0.65  # Lower correlation between tech/small cap

        # Analyze current divergences
        spx_change = quotes.get('SPX', {}).get('change_pct', 0)
        qqq_change = quotes.get('QQQ', {}).get('change_pct', 0)
        iwm_change = quotes.get('IWM', {}).get('change_pct', 0)

        divergences = {
            'SPX_QQQ_divergence': abs(spx_change - qqq_change),
            'SPX_IWM_divergence': abs(spx_change - iwm_change),
            'QQQ_IWM_divergence': abs(qqq_change - iwm_change)
        }

        return {
            'correlations': correlations,
            'divergences': divergences,
            'max_divergence': max(divergences.values()),
            'analysis_timestamp': datetime.now().isoformat()
        }

    def analyze_cross_asset_signals(self, quotes: Dict, rsi_data: Dict) -> Dict:
        """Generate cross-asset trading signals"""
        signals = []

        # Get price and RSI data
        spx_price = quotes.get('SPX', {}).get('price', 0)
        qqq_price = quotes.get('QQQ', {}).get('price', 0)
        iwm_price = quotes.get('IWM', {}).get('price', 0)

        spx_rsi = rsi_data.get('SPX', {}).get('rsi', 50)
        qqq_rsi = rsi_data.get('QQQ', {}).get('rsi', 50)
        iwm_rsi = rsi_data.get('IWM', {}).get('rsi', 50)

        # Cross-asset momentum signals
        if spx_rsi > 60 and qqq_rsi > 60 and iwm_rsi < 40:
            signals.append({
                'type': 'IWM_CATCH_UP',
                'asset': 'IWM',
                'direction': 'BULLISH',
                'logic': 'Large/mid caps strong, small caps oversold - catch up trade',
                'confidence': 75,
                'entry': f'IWM calls near ${iwm_price:.2f}',
                'risk_reward': '1:3'
            })

        if qqq_rsi > 70 and spx_rsi < 50:
            signals.append({
                'type': 'TECH_DIVERGENCE',
                'asset': 'QQQ',
                'direction': 'BEARISH',
                'logic': 'Tech overbought while SPX neutral - tech pullback expected',
                'confidence': 70,
                'entry': f'QQQ puts near ${qqq_price:.2f}',
                'risk_reward': '1:2.5'
            })

        if spx_rsi < 30 and qqq_rsi < 30 and iwm_rsi < 30:
            signals.append({
                'type': 'BROAD_OVERSOLD',
                'asset': 'ALL',
                'direction': 'BULLISH',
                'logic': 'All major indices oversold - broad market bounce expected',
                'confidence': 85,
                'entry': 'SPX/QQQ/IWM calls across board',
                'risk_reward': '1:4'
            })

        return {
            'signals': signals,
            'signal_count': len(signals),
            'max_confidence': max([s['confidence'] for s in signals]) if signals else 0,
            'analysis_timestamp': datetime.now().isoformat()
        }

    def generate_option_recommendations(self, quotes: Dict, signals: Dict) -> Dict:
        """Generate specific option trade recommendations"""
        recommendations = []

        for signal in signals['signals']:
            if signal['asset'] == 'IWM':
                iwm_price = quotes.get('IWM', {}).get('price', 0)
                if signal['direction'] == 'BULLISH':
                    # Calculate ATM and OTM strikes
                    atm_strike = round(iwm_price)
                    otm_strike = round(iwm_price * 1.02)  # 2% OTM

                    recommendations.append({
                        'symbol': 'IWM',
                        'type': 'CALL',
                        'strike': atm_strike,
                        'contract': f"IWM{atm_strike}C",
                        'entry_logic': signal['logic'],
                        'confidence': signal['confidence'],
                        'expected_premium': '$1.50-3.00',
                        'target': f"${otm_strike} (+{((otm_strike/iwm_price-1)*100):.1f}%)"
                    })

            elif signal['asset'] == 'QQQ':
                qqq_price = quotes.get('QQQ', {}).get('price', 0)
                if signal['direction'] == 'BEARISH':
                    # Calculate OTM put strikes
                    otm_strike = round(qqq_price * 0.98)  # 2% OTM

                    recommendations.append({
                        'symbol': 'QQQ',
                        'type': 'PUT',
                        'strike': otm_strike,
                        'contract': f"QQQ{otm_strike}P",
                        'entry_logic': signal['logic'],
                        'confidence': signal['confidence'],
                        'expected_premium': '$2.00-4.00',
                        'target': f"${round(qqq_price * 0.95)} (-3% move)"
                    })

        return {
            'recommendations': recommendations,
            'recommendation_count': len(recommendations),
            'analysis_timestamp': datetime.now().isoformat()
        }

    def run_full_multi_asset_analysis(self) -> str:
        """Complete multi-asset analysis with cross-correlation intelligence"""
        output = []

        output.append("MULTI-ASSET OPTIONS ANALYSIS")
        output.append("=" * 50)

        # Get quotes for all assets
        quotes = {}
        rsi_data = {}

        for asset, config in self.assets.items():
            symbol = config['proxy']

            # Get quote
            quote = self.get_asset_quote(symbol)
            if quote['success']:
                if asset == 'SPX':
                    # Use SPX multiplier for accurate pricing
                    quote['price'] *= config['multiplier']
                quotes[asset] = quote

                # Get RSI
                rsi = self.get_asset_rsi(symbol)
                if rsi['success']:
                    rsi_data[asset] = rsi

        # Display current prices
        output.append("CURRENT MARKET LEVELS:")
        for asset, quote in quotes.items():
            if asset == 'SPX':
                output.append(f"{asset}: ${quote['price']:,.0f} ({quote['change']:+.0f}, {quote['change_pct']:+.2f}%)")
            else:
                output.append(f"{asset}: ${quote['price']:.2f} ({quote['change']:+.2f}, {quote['change_pct']:+.2f}%)")

        output.append("")

        # Display RSI levels
        output.append("RSI MOMENTUM ANALYSIS:")
        for asset, rsi in rsi_data.items():
            rsi_value = rsi['rsi']
            condition = "OVERBOUGHT" if rsi_value > 70 else "OVERSOLD" if rsi_value < 30 else "NEUTRAL"
            output.append(f"{asset} RSI: {rsi_value:.1f} ({condition})")

        output.append("")

        # Cross-correlation analysis
        correlation_analysis = self.calculate_correlation_matrix(quotes)
        output.append("CROSS-ASSET CORRELATION:")
        output.append(f"Max Divergence: {correlation_analysis['max_divergence']:.2f}%")
        for pair, divergence in correlation_analysis['divergences'].items():
            output.append(f"{pair}: {divergence:.2f}% divergence")

        output.append("")

        # Generate trading signals
        signals = self.analyze_cross_asset_signals(quotes, rsi_data)
        if signals['signals']:
            output.append("CROSS-ASSET TRADING SIGNALS:")
            for signal in signals['signals']:
                output.append(f"🎯 {signal['type']} - {signal['asset']}")
                output.append(f"   Direction: {signal['direction']}")
                output.append(f"   Logic: {signal['logic']}")
                output.append(f"   Confidence: {signal['confidence']}%")
                output.append(f"   Entry: {signal['entry']}")
                output.append("")

        # Generate option recommendations
        recommendations = self.generate_option_recommendations(quotes, signals)
        if recommendations['recommendations']:
            output.append("SPECIFIC OPTION RECOMMENDATIONS:")
            for rec in recommendations['recommendations']:
                output.append(f"📈 {rec['contract']} @ {rec['expected_premium']}")
                output.append(f"   Logic: {rec['entry_logic']}")
                output.append(f"   Target: {rec['target']}")
                output.append(f"   Confidence: {rec['confidence']}%")
                output.append("")

        # Save session data
        session_data = {
            'timestamp': datetime.now().isoformat(),
            'quotes': quotes,
            'rsi_data': rsi_data,
            'correlation_analysis': correlation_analysis,
            'signals': signals,
            'recommendations': recommendations
        }

        os.makedirs(os.path.dirname(self.session_file), exist_ok=True)
        with open(self.session_file, 'w') as f:
            json.dump(session_data, f, indent=2, default=str)

        output.append("SESSION UPDATED: Multi-asset analysis saved to .spx/")

        return "\n".join(output)

def main():
    """Test multi-asset analysis"""
    analyzer = MultiAssetAnalyzer()

    print("MULTI-ASSET OPTIONS ANALYSIS SYSTEM")
    print("=" * 40)

    analysis = analyzer.run_full_multi_asset_analysis()
    print(analysis)

if __name__ == "__main__":
    main()