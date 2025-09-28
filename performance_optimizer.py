#!/usr/bin/env python3
"""
Performance Optimizer for High-Frequency Trading
Optimizes system performance for market open and high-volume periods
"""

import os
import json
import time
import threading
import asyncio
import concurrent.futures
from datetime import datetime
from typing import Dict, List, Any, Optional
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

class PerformanceOptimizer:
    """High-frequency trading performance optimization system"""

    def __init__(self):
        self.api_key = os.getenv('ALPHAVANTAGE_API_KEY')
        self.base_url = "https://www.alphavantage.co/query"

        # Performance tracking
        self.api_call_times = []
        self.response_cache = {}
        self.cache_ttl = 30  # 30 second cache for high-frequency data

        # Initialize optimized session
        self.session = self.create_optimized_session()

        # Threading controls
        self.max_workers = 8
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers)

        print("Performance Optimizer initialized for high-frequency trading")

    def create_optimized_session(self) -> requests.Session:
        """Create optimized requests session with connection pooling and retries"""
        session = requests.Session()

        # Configure retry strategy
        retry_strategy = Retry(
            total=3,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"],
            backoff_factor=0.3
        )

        # Configure adapter with connection pooling
        adapter = HTTPAdapter(
            max_retries=retry_strategy,
            pool_connections=20,
            pool_maxsize=20,
            pool_block=False
        )

        session.mount("http://", adapter)
        session.mount("https://", adapter)

        # Set optimized timeouts and headers
        session.headers.update({
            'User-Agent': 'SPX-Trading-System/1.0',
            'Connection': 'keep-alive',
            'Accept-Encoding': 'gzip, deflate'
        })

        return session

    def is_cache_valid(self, cache_key: str) -> bool:
        """Check if cached data is still valid"""
        if cache_key not in self.response_cache:
            return False

        cached_time = self.response_cache[cache_key]['timestamp']
        return (time.time() - cached_time) < self.cache_ttl

    def get_cached_or_fetch(self, cache_key: str, url: str, params: Dict) -> Dict:
        """Get data from cache or fetch if expired"""
        if self.is_cache_valid(cache_key):
            return self.response_cache[cache_key]['data']

        # Fetch fresh data
        start_time = time.time()
        try:
            response = self.session.get(url, params=params, timeout=(5, 10))
            response.raise_for_status()
            data = response.json()

            # Cache the response
            self.response_cache[cache_key] = {
                'data': data,
                'timestamp': time.time()
            }

            # Track performance
            self.api_call_times.append(time.time() - start_time)

            return data

        except Exception as e:
            print(f"API call failed for {cache_key}: {e}")
            return {}

    def batch_api_calls(self, call_configs: List[Dict]) -> Dict[str, Any]:
        """Execute multiple API calls in parallel with caching"""

        def execute_call(config):
            cache_key = config['cache_key']
            params = config['params']
            return cache_key, self.get_cached_or_fetch(cache_key, self.base_url, params)

        # Execute calls in parallel
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_key = {executor.submit(execute_call, config): config['cache_key']
                           for config in call_configs}

            results = {}
            for future in concurrent.futures.as_completed(future_to_key):
                cache_key = future_to_key[future]
                try:
                    key, data = future.result()
                    results[key] = data
                except Exception as e:
                    print(f"Failed to fetch {cache_key}: {e}")
                    results[cache_key] = {}

            return results

    def optimize_multi_asset_analysis(self) -> Dict[str, Any]:
        """Optimized multi-asset analysis with parallel processing"""

        print("OPTIMIZED MULTI-ASSET ANALYSIS")
        print("High-frequency parallel processing enabled")
        print("=" * 50)

        start_time = time.time()

        # Define all API calls needed for 5-asset analysis
        api_calls = [
            # Core quotes
            {
                'cache_key': 'spy_quote',
                'params': {'function': 'GLOBAL_QUOTE', 'symbol': 'SPY', 'apikey': self.api_key}
            },
            {
                'cache_key': 'qqq_quote',
                'params': {'function': 'GLOBAL_QUOTE', 'symbol': 'QQQ', 'apikey': self.api_key}
            },
            {
                'cache_key': 'iwm_quote',
                'params': {'function': 'GLOBAL_QUOTE', 'symbol': 'IWM', 'apikey': self.api_key}
            },
            # Technical indicators
            {
                'cache_key': 'spy_rsi',
                'params': {'function': 'RSI', 'symbol': 'SPY', 'interval': '5min',
                          'time_period': 14, 'series_type': 'close', 'apikey': self.api_key}
            },
            {
                'cache_key': 'qqq_rsi',
                'params': {'function': 'RSI', 'symbol': 'QQQ', 'interval': '5min',
                          'time_period': 14, 'series_type': 'close', 'apikey': self.api_key}
            },
            # EMA indicators
            {
                'cache_key': 'spy_ema9',
                'params': {'function': 'EMA', 'symbol': 'SPY', 'interval': '5min',
                          'time_period': 9, 'series_type': 'close', 'apikey': self.api_key}
            },
            {
                'cache_key': 'spy_ema21',
                'params': {'function': 'EMA', 'symbol': 'SPY', 'interval': '5min',
                          'time_period': 21, 'series_type': 'close', 'apikey': self.api_key}
            }
        ]

        # Execute all calls in parallel
        print("Executing 7 API calls in parallel...")
        batch_start = time.time()
        results = self.batch_api_calls(api_calls)
        batch_time = time.time() - batch_start

        print(f"Parallel execution completed in {batch_time:.2f} seconds")

        # Process results quickly
        analysis = self.process_batch_results(results)

        total_time = time.time() - start_time
        analysis['performance_metrics'] = {
            'total_time': total_time,
            'batch_time': batch_time,
            'api_calls': len(api_calls),
            'calls_per_second': len(api_calls) / batch_time,
            'avg_call_time': sum(self.api_call_times[-len(api_calls):]) / len(api_calls) if self.api_call_times else 0
        }

        print(f"\nPERFORMANCE METRICS:")
        print(f"Total Analysis Time: {total_time:.2f}s")
        print(f"API Calls per Second: {analysis['performance_metrics']['calls_per_second']:.1f}")
        print(f"Average Call Time: {analysis['performance_metrics']['avg_call_time']:.3f}s")

        return analysis

    def process_batch_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Process batched API results into trading analysis"""

        analysis = {
            'timestamp': datetime.now().isoformat(),
            'assets': {},
            'consensus': {},
            'recommendations': []
        }

        # Process SPY data
        if 'spy_quote' in results and 'Global Quote' in results['spy_quote']:
            spy_data = results['spy_quote']['Global Quote']
            spy_price = float(spy_data['05. price'])
            spy_change_pct = float(spy_data['10. change percent'].replace('%', ''))

            analysis['assets']['SPY'] = {
                'price': spy_price,
                'change_pct': spy_change_pct,
                'spx_estimate': spy_price * 10
            }

            # Process SPY RSI
            if 'spy_rsi' in results and 'Technical Analysis: RSI' in results['spy_rsi']:
                rsi_data = results['spy_rsi']['Technical Analysis: RSI']
                latest_rsi = float(list(rsi_data.values())[0]['RSI'])
                analysis['assets']['SPY']['rsi'] = latest_rsi

            # Process SPY EMAs
            if 'spy_ema9' in results and 'Technical Analysis: EMA' in results['spy_ema9']:
                ema9_data = results['spy_ema9']['Technical Analysis: EMA']
                ema9 = float(list(ema9_data.values())[0]['EMA'])
                analysis['assets']['SPY']['ema9'] = ema9

            if 'spy_ema21' in results and 'Technical Analysis: EMA' in results['spy_ema21']:
                ema21_data = results['spy_ema21']['Technical Analysis: EMA']
                ema21 = float(list(ema21_data.values())[0]['EMA'])
                analysis['assets']['SPY']['ema21'] = ema21

        # Process QQQ data
        if 'qqq_quote' in results and 'Global Quote' in results['qqq_quote']:
            qqq_data = results['qqq_quote']['Global Quote']
            qqq_price = float(qqq_data['05. price'])
            qqq_change_pct = float(qqq_data['10. change percent'].replace('%', ''))

            analysis['assets']['QQQ'] = {
                'price': qqq_price,
                'change_pct': qqq_change_pct,
                'ndx_estimate': qqq_price * 28.5
            }

            # Process QQQ RSI
            if 'qqq_rsi' in results and 'Technical Analysis: RSI' in results['qqq_rsi']:
                rsi_data = results['qqq_rsi']['Technical Analysis: RSI']
                latest_rsi = float(list(rsi_data.values())[0]['RSI'])
                analysis['assets']['QQQ']['rsi'] = latest_rsi

        # Process IWM data
        if 'iwm_quote' in results and 'Global Quote' in results['iwm_quote']:
            iwm_data = results['iwm_quote']['Global Quote']
            iwm_price = float(iwm_data['05. price'])
            iwm_change_pct = float(iwm_data['10. change percent'].replace('%', ''))

            analysis['assets']['IWM'] = {
                'price': iwm_price,
                'change_pct': iwm_change_pct
            }

        # Generate fast consensus
        analysis['consensus'] = self.calculate_fast_consensus(analysis['assets'])

        # Generate quick recommendations
        analysis['recommendations'] = self.generate_quick_recommendations(analysis['assets'], analysis['consensus'])

        return analysis

    def calculate_fast_consensus(self, assets: Dict) -> Dict[str, Any]:
        """Fast consensus calculation for high-frequency trading"""

        consensus = {
            'bullish_signals': 0,
            'bearish_signals': 0,
            'neutral_signals': 0,
            'overall_bias': 'NEUTRAL',
            'confidence': 0.0
        }

        for asset, data in assets.items():
            if 'rsi' in data:
                rsi = data['rsi']
                if rsi > 55:
                    consensus['bullish_signals'] += 1
                elif rsi < 45:
                    consensus['bearish_signals'] += 1
                else:
                    consensus['neutral_signals'] += 1

            if 'ema9' in data and 'ema21' in data:
                if data['ema9'] > data['ema21']:
                    consensus['bullish_signals'] += 1
                else:
                    consensus['bearish_signals'] += 1

            if 'change_pct' in data:
                if data['change_pct'] > 0.2:
                    consensus['bullish_signals'] += 1
                elif data['change_pct'] < -0.2:
                    consensus['bearish_signals'] += 1
                else:
                    consensus['neutral_signals'] += 1

        # Determine overall bias
        total_signals = consensus['bullish_signals'] + consensus['bearish_signals'] + consensus['neutral_signals']
        if total_signals > 0:
            if consensus['bullish_signals'] > consensus['bearish_signals']:
                consensus['overall_bias'] = 'BULLISH'
                consensus['confidence'] = consensus['bullish_signals'] / total_signals
            elif consensus['bearish_signals'] > consensus['bullish_signals']:
                consensus['overall_bias'] = 'BEARISH'
                consensus['confidence'] = consensus['bearish_signals'] / total_signals
            else:
                consensus['overall_bias'] = 'NEUTRAL'
                consensus['confidence'] = 0.5

        return consensus

    def generate_quick_recommendations(self, assets: Dict, consensus: Dict) -> List[Dict]:
        """Generate quick trading recommendations for high-frequency scenarios"""

        recommendations = []

        if consensus['confidence'] >= 0.7:
            if consensus['overall_bias'] == 'BULLISH':
                # Quick bullish plays
                if 'SPY' in assets:
                    spy_price = assets['SPY']['price']
                    recommendations.append({
                        'asset': 'SPY',
                        'action': 'BUY_CALLS',
                        'strike': round(spy_price + 1),
                        'reasoning': f'Bullish consensus {consensus["confidence"]:.1%}',
                        'urgency': 'HIGH'
                    })

                if 'QQQ' in assets:
                    qqq_price = assets['QQQ']['price']
                    recommendations.append({
                        'asset': 'QQQ',
                        'action': 'BUY_CALLS',
                        'strike': round(qqq_price + 2),
                        'reasoning': f'Tech momentum with {consensus["confidence"]:.1%} confidence',
                        'urgency': 'HIGH'
                    })

            elif consensus['overall_bias'] == 'BEARISH':
                # Quick bearish plays
                if 'SPY' in assets:
                    spy_price = assets['SPY']['price']
                    recommendations.append({
                        'asset': 'SPY',
                        'action': 'BUY_PUTS',
                        'strike': round(spy_price - 1),
                        'reasoning': f'Bearish consensus {consensus["confidence"]:.1%}',
                        'urgency': 'HIGH'
                    })

        return recommendations

    def performance_report(self) -> Dict[str, Any]:
        """Generate performance optimization report"""

        if not self.api_call_times:
            return {'error': 'No performance data available'}

        avg_time = sum(self.api_call_times) / len(self.api_call_times)
        max_time = max(self.api_call_times)
        min_time = min(self.api_call_times)

        report = {
            'total_calls': len(self.api_call_times),
            'average_response_time': avg_time,
            'fastest_response': min_time,
            'slowest_response': max_time,
            'cache_hit_rate': len([k for k in self.response_cache.keys() if self.is_cache_valid(k)]) / max(len(self.response_cache), 1),
            'recommended_optimizations': []
        }

        # Performance recommendations
        if avg_time > 2.0:
            report['recommended_optimizations'].append("Consider reducing API call frequency")
        if avg_time > 1.0:
            report['recommended_optimizations'].append("Implement more aggressive caching")
        if len(self.api_call_times) > 100:
            report['recommended_optimizations'].append("Consider API call batching")

        return report

def main():
    """Test performance optimization system"""
    optimizer = PerformanceOptimizer()

    print("PERFORMANCE OPTIMIZATION TEST")
    print("=" * 40)

    # Run optimized analysis
    analysis = optimizer.optimize_multi_asset_analysis()

    # Display results
    print(f"\nASSET ANALYSIS:")
    for asset, data in analysis['assets'].items():
        print(f"{asset}: ${data['price']:.2f} ({data['change_pct']:+.2f}%)")
        if 'rsi' in data:
            print(f"  RSI: {data['rsi']:.1f}")

    print(f"\nCONSENSUS:")
    consensus = analysis['consensus']
    print(f"Bias: {consensus['overall_bias']} ({consensus['confidence']:.1%} confidence)")

    print(f"\nRECOMMENDATIONS:")
    for rec in analysis['recommendations']:
        print(f"- {rec['action']}: {rec['asset']} ${rec['strike']} ({rec['urgency']})")
        print(f"  Reasoning: {rec['reasoning']}")

    # Performance report
    print(f"\nPERFORMANCE REPORT:")
    perf_report = optimizer.performance_report()
    print(f"Average Response: {perf_report['average_response_time']:.3f}s")
    print(f"Cache Hit Rate: {perf_report['cache_hit_rate']:.1%}")

    # Save results
    try:
        os.makedirs('.spx', exist_ok=True)
        with open('.spx/performance_optimization_results.json', 'w') as f:
            json.dump(analysis, f, indent=2)
        print(f"\nResults saved to .spx/performance_optimization_results.json")
    except Exception as e:
        print(f"Warning: Could not save results: {e}")

if __name__ == "__main__":
    main()