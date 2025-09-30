#!/usr/bin/env python3
"""
BACKTEST FRAMEWORK v1.0
Historical data validation, strategy performance testing, pattern recognition
"""

import os
import sys
import json
from datetime import datetime, timedelta
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dual_api_system import DualAPISystem

class BacktestFramework:
    def __init__(self, start_date, end_date):
        """
        Initialize backtest framework

        Args:
            start_date: Start date for backtest (YYYY-MM-DD)
            end_date: End date for backtest (YYYY-MM-DD)
        """
        self.dual_api = DualAPISystem()
        self.start_date = start_date
        self.end_date = end_date

        # Results storage
        self.historical_data = {}
        self.trades = []
        self.performance_metrics = {}
        self.pattern_results = defaultdict(list)

    def fetch_historical_data(self, symbol, timeframe='day'):
        """
        Fetch historical data for backtesting

        Args:
            symbol: Ticker symbol (SPX, SPY, QQQ, IWM, NDX)
            timeframe: 'day' or 'minute' (default: day)

        Returns:
            List of OHLCV data points
        """
        print(f"Fetching historical data for {symbol} ({self.start_date} to {self.end_date})...")

        # Build Polygon API endpoint
        polygon_key = "_u0zA0CH5ZspOHecb2G8uBxd2DUo4r9D"

        # Map symbols to Polygon format
        if symbol == 'SPX':
            polygon_symbol = 'I:SPX'
        elif symbol == 'NDX':
            polygon_symbol = 'I:NDX'
        else:
            polygon_symbol = symbol

        url = f"https://api.polygon.io/v2/aggs/ticker/{polygon_symbol}/range/1/{timeframe}/{self.start_date}/{self.end_date}"
        params = {
            'adjusted': 'true',
            'sort': 'asc',
            'limit': 50000,
            'apiKey': polygon_key
        }

        try:
            import requests
            response = requests.get(url, params=params, timeout=30)

            if response.status_code == 200:
                data = response.json()

                if data.get('status') == 'OK' and 'results' in data:
                    results = data['results']

                    # Convert to standardized format
                    formatted_data = []
                    for bar in results:
                        formatted_data.append({
                            'date': datetime.fromtimestamp(bar['t'] / 1000).strftime('%Y-%m-%d'),
                            'open': bar['o'],
                            'high': bar['h'],
                            'low': bar['l'],
                            'close': bar['c'],
                            'volume': bar.get('v', 0),
                            'timestamp': bar['t']
                        })

                    self.historical_data[symbol] = formatted_data
                    print(f"✅ Fetched {len(formatted_data)} bars for {symbol}")
                    return formatted_data
                else:
                    print(f"❌ No data returned for {symbol}")
                    return []
            else:
                print(f"❌ HTTP {response.status_code} for {symbol}")
                return []

        except Exception as e:
            print(f"❌ Error fetching {symbol}: {e}")
            return []

    def validate_data_accuracy(self, symbol, known_closes=None):
        """
        Validate historical data accuracy against known closing prices

        Args:
            symbol: Ticker symbol
            known_closes: Dict of {date: price} for validation

        Returns:
            Dict with validation results
        """
        if symbol not in self.historical_data:
            return {'error': 'No historical data loaded'}

        data = self.historical_data[symbol]

        validation = {
            'symbol': symbol,
            'total_bars': len(data),
            'date_range': f"{data[0]['date']} to {data[-1]['date']}",
            'missing_days': [],
            'price_accuracy': [],
            'data_quality': 'UNKNOWN'
        }

        # Check for missing days (simple check - could be improved)
        if len(data) > 1:
            dates = [datetime.strptime(d['date'], '%Y-%m-%d') for d in data]
            date_gaps = []
            for i in range(1, len(dates)):
                gap = (dates[i] - dates[i-1]).days
                if gap > 3:  # Weekend is 2-3 days
                    date_gaps.append({
                        'from': dates[i-1].strftime('%Y-%m-%d'),
                        'to': dates[i].strftime('%Y-%m-%d'),
                        'gap_days': gap
                    })
            validation['missing_days'] = date_gaps

        # Validate against known closes if provided
        if known_closes:
            for date, expected_price in known_closes.items():
                matching_bar = next((d for d in data if d['date'] == date), None)
                if matching_bar:
                    actual_price = matching_bar['close']
                    error = abs(actual_price - expected_price)
                    error_pct = (error / expected_price) * 100

                    validation['price_accuracy'].append({
                        'date': date,
                        'expected': expected_price,
                        'actual': actual_price,
                        'error': error,
                        'error_pct': error_pct,
                        'status': 'PASS' if error_pct < 0.01 else 'FAIL'
                    })

        # Determine overall data quality
        if validation['price_accuracy']:
            failed_checks = sum(1 for check in validation['price_accuracy'] if check['status'] == 'FAIL')
            if failed_checks == 0:
                validation['data_quality'] = 'VERY_HIGH'
            elif failed_checks / len(validation['price_accuracy']) < 0.05:
                validation['data_quality'] = 'HIGH'
            elif failed_checks / len(validation['price_accuracy']) < 0.10:
                validation['data_quality'] = 'MEDIUM'
            else:
                validation['data_quality'] = 'LOW'

        return validation

    def test_support_resistance_strategy(self, symbol, support_level, resistance_level):
        """
        Backtest simple support/resistance bounce strategy

        Args:
            symbol: Ticker symbol
            support_level: Support price level
            resistance_level: Resistance price level

        Returns:
            Dict with strategy performance
        """
        if symbol not in self.historical_data:
            return {'error': 'No historical data loaded'}

        data = self.historical_data[symbol]

        trades = []
        position = None

        for i, bar in enumerate(data):
            # Long setup: Price touches support
            if position is None and bar['low'] <= support_level * 1.001:  # 0.1% tolerance
                position = {
                    'type': 'LONG',
                    'entry_date': bar['date'],
                    'entry_price': support_level,
                    'target': resistance_level,
                    'stop': support_level * 0.995  # 0.5% stop
                }

            # Short setup: Price touches resistance
            elif position is None and bar['high'] >= resistance_level * 0.999:  # 0.1% tolerance
                position = {
                    'type': 'SHORT',
                    'entry_date': bar['date'],
                    'entry_price': resistance_level,
                    'target': support_level,
                    'stop': resistance_level * 1.005  # 0.5% stop
                }

            # Check exit conditions for open positions
            elif position is not None:
                exit_price = None
                exit_reason = None

                if position['type'] == 'LONG':
                    # Target hit
                    if bar['high'] >= position['target']:
                        exit_price = position['target']
                        exit_reason = 'TARGET'
                    # Stop hit
                    elif bar['low'] <= position['stop']:
                        exit_price = position['stop']
                        exit_reason = 'STOP'

                elif position['type'] == 'SHORT':
                    # Target hit
                    if bar['low'] <= position['target']:
                        exit_price = position['target']
                        exit_reason = 'TARGET'
                    # Stop hit
                    elif bar['high'] >= position['stop']:
                        exit_price = position['stop']
                        exit_reason = 'STOP'

                # Close position if exit triggered
                if exit_price:
                    if position['type'] == 'LONG':
                        pnl = exit_price - position['entry_price']
                        pnl_pct = (pnl / position['entry_price']) * 100
                    else:  # SHORT
                        pnl = position['entry_price'] - exit_price
                        pnl_pct = (pnl / position['entry_price']) * 100

                    trades.append({
                        'entry_date': position['entry_date'],
                        'exit_date': bar['date'],
                        'type': position['type'],
                        'entry_price': position['entry_price'],
                        'exit_price': exit_price,
                        'exit_reason': exit_reason,
                        'pnl': pnl,
                        'pnl_pct': pnl_pct
                    })

                    position = None

        # Calculate performance metrics
        if trades:
            total_trades = len(trades)
            winners = [t for t in trades if t['pnl'] > 0]
            losers = [t for t in trades if t['pnl'] <= 0]

            win_rate = (len(winners) / total_trades) * 100
            avg_win = sum(t['pnl_pct'] for t in winners) / len(winners) if winners else 0
            avg_loss = sum(t['pnl_pct'] for t in losers) / len(losers) if losers else 0
            total_pnl = sum(t['pnl_pct'] for t in trades)

            performance = {
                'symbol': symbol,
                'strategy': 'Support/Resistance Bounce',
                'support_level': support_level,
                'resistance_level': resistance_level,
                'total_trades': total_trades,
                'winners': len(winners),
                'losers': len(losers),
                'win_rate': win_rate,
                'avg_win_pct': avg_win,
                'avg_loss_pct': avg_loss,
                'total_pnl_pct': total_pnl,
                'trades': trades
            }
        else:
            performance = {
                'symbol': symbol,
                'strategy': 'Support/Resistance Bounce',
                'error': 'No trades generated'
            }

        return performance

    def detect_gamma_flip_pattern(self, symbol, gamma_flip_level):
        """
        Detect gamma flip pattern occurrences in historical data

        Args:
            symbol: Ticker symbol
            gamma_flip_level: Gamma flip price level

        Returns:
            List of gamma flip events with behavior analysis
        """
        if symbol not in self.historical_data:
            return {'error': 'No historical data loaded'}

        data = self.historical_data[symbol]
        events = []

        for i in range(1, len(data)):
            prev_bar = data[i-1]
            curr_bar = data[i]

            # Check if price crossed gamma flip level
            crossed_up = prev_bar['close'] < gamma_flip_level and curr_bar['close'] > gamma_flip_level
            crossed_down = prev_bar['close'] > gamma_flip_level and curr_bar['close'] < gamma_flip_level

            if crossed_up or crossed_down:
                # Analyze next 5 days behavior
                next_5_days = data[i:i+6] if i+6 <= len(data) else data[i:]

                if len(next_5_days) > 1:
                    price_change = next_5_days[-1]['close'] - curr_bar['close']
                    price_change_pct = (price_change / curr_bar['close']) * 100

                    # Calculate volatility (range expansion)
                    avg_range = sum(d['high'] - d['low'] for d in next_5_days) / len(next_5_days)
                    prev_avg_range = sum(data[max(0, i-5):i][j]['high'] - data[max(0, i-5):i][j]['low']
                                       for j in range(len(data[max(0, i-5):i]))) / max(1, len(data[max(0, i-5):i]))
                    volatility_expansion = ((avg_range - prev_avg_range) / prev_avg_range * 100) if prev_avg_range > 0 else 0

                    events.append({
                        'date': curr_bar['date'],
                        'direction': 'UP' if crossed_up else 'DOWN',
                        'gamma_level': gamma_flip_level,
                        'price_at_cross': curr_bar['close'],
                        'price_5d_later': next_5_days[-1]['close'],
                        'change_pct': price_change_pct,
                        'volatility_expansion_pct': volatility_expansion,
                        'behavior': 'ACCELERATED' if abs(price_change_pct) > 2 else 'NORMAL'
                    })

        pattern_summary = {
            'symbol': symbol,
            'gamma_flip_level': gamma_flip_level,
            'total_events': len(events),
            'up_crosses': len([e for e in events if e['direction'] == 'UP']),
            'down_crosses': len([e for e in events if e['direction'] == 'DOWN']),
            'accelerated_moves': len([e for e in events if e['behavior'] == 'ACCELERATED']),
            'events': events
        }

        return pattern_summary

    def generate_report(self, output_file='backtest_report.json'):
        """
        Generate comprehensive backtest report

        Args:
            output_file: Path to save JSON report
        """
        report = {
            'backtest_period': {
                'start_date': self.start_date,
                'end_date': self.end_date
            },
            'historical_data_loaded': list(self.historical_data.keys()),
            'performance_metrics': self.performance_metrics,
            'pattern_results': dict(self.pattern_results),
            'trades': self.trades,
            'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S ET')
        }

        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"\n✅ Backtest report saved to {output_file}")
        return report

def main():
    """Example usage of backtest framework"""

    # Example: Backtest September 2025
    backtest = BacktestFramework('2025-09-01', '2025-09-30')

    # 1. Fetch historical data
    print("\n" + "="*80)
    print("STEP 1: FETCH HISTORICAL DATA")
    print("="*80 + "\n")

    backtest.fetch_historical_data('SPX')
    backtest.fetch_historical_data('SPY')

    # 2. Validate data accuracy
    print("\n" + "="*80)
    print("STEP 2: VALIDATE DATA ACCURACY")
    print("="*80 + "\n")

    # Validate SPX with known September 30 close
    spx_validation = backtest.validate_data_accuracy('SPX', {
        '2025-09-30': 6651.20
    })
    print(f"SPX Validation: {spx_validation['data_quality']}")
    if spx_validation.get('price_accuracy'):
        for check in spx_validation['price_accuracy']:
            print(f"  {check['date']}: Expected ${check['expected']:.2f}, "
                  f"Actual ${check['actual']:.2f}, Error: {check['error_pct']:.4f}% [{check['status']}]")

    # 3. Test support/resistance strategy
    print("\n" + "="*80)
    print("STEP 3: BACKTEST SUPPORT/RESISTANCE STRATEGY")
    print("="*80 + "\n")

    spy_strategy = backtest.test_support_resistance_strategy('SPY', support_level=663, resistance_level=668)
    if 'total_trades' in spy_strategy:
        print(f"SPY Strategy Results:")
        print(f"  Total Trades: {spy_strategy['total_trades']}")
        print(f"  Win Rate: {spy_strategy['win_rate']:.1f}%")
        print(f"  Avg Win: {spy_strategy['avg_win_pct']:.2f}%")
        print(f"  Avg Loss: {spy_strategy['avg_loss_pct']:.2f}%")
        print(f"  Total P&L: {spy_strategy['total_pnl_pct']:.2f}%")

        backtest.performance_metrics['spy_support_resistance'] = spy_strategy

    # 4. Detect gamma flip patterns
    print("\n" + "="*80)
    print("STEP 4: DETECT GAMMA FLIP PATTERNS")
    print("="*80 + "\n")

    gamma_patterns = backtest.detect_gamma_flip_pattern('SPX', gamma_flip_level=6610)
    print(f"SPX Gamma Flip Pattern (Level: $6610):")
    print(f"  Total Events: {gamma_patterns['total_events']}")
    print(f"  Up Crosses: {gamma_patterns['up_crosses']}")
    print(f"  Down Crosses: {gamma_patterns['down_crosses']}")
    print(f"  Accelerated Moves: {gamma_patterns['accelerated_moves']}")

    backtest.pattern_results['spx_gamma_flip'] = gamma_patterns

    # 5. Generate report
    print("\n" + "="*80)
    print("STEP 5: GENERATE REPORT")
    print("="*80 + "\n")

    backtest.generate_report('backtest_report_sep2025.json')

    print("\n✅ Backtest framework demonstration complete!")

if __name__ == "__main__":
    main()
