#!/usr/bin/env python3
"""
Backtesting Validation System
Historical performance validation for SPX/QQQ/IWM trading strategies
"""

import requests
import json
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import numpy as np

class BacktestingEngine:
    def __init__(self):
        self.api_key = 'ZFL38ZY98GSN7E1S'
        self.results_file = ".spx/backtest_results.json"
        self.trades_log = []
        self.performance_metrics = {}

    def get_historical_data(self, symbol: str, period_days: int = 30) -> Dict:
        """Get historical price data for backtesting"""
        url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={self.api_key}'

        try:
            response = requests.get(url, timeout=20)
            data = response.json()

            if 'Time Series (Daily)' in data:
                time_series = data['Time Series (Daily)']

                # Convert to list of dictionaries
                historical_data = []
                for date_str, price_data in time_series.items():
                    date_obj = datetime.strptime(date_str, '%Y-%m-%d')

                    # Only include recent data
                    if date_obj >= datetime.now() - timedelta(days=period_days):
                        historical_data.append({
                            'date': date_obj,
                            'open': float(price_data['1. open']),
                            'high': float(price_data['2. high']),
                            'low': float(price_data['3. low']),
                            'close': float(price_data['4. close']),
                            'volume': int(price_data['5. volume'])
                        })

                # Sort by date
                historical_data.sort(key=lambda x: x['date'])

                return {
                    'success': True,
                    'symbol': symbol,
                    'data': historical_data,
                    'period_days': period_days
                }
            else:
                return {'success': False, 'error': 'No time series data', 'symbol': symbol}

        except Exception as e:
            return {'success': False, 'error': str(e), 'symbol': symbol}

    def calculate_technical_indicators(self, price_data: List[Dict]) -> List[Dict]:
        """Calculate RSI, EMAs for historical analysis"""
        enhanced_data = []

        for i, day in enumerate(price_data):
            enhanced_day = day.copy()

            # Calculate RSI (simplified 14-day)
            if i >= 14:
                recent_closes = [price_data[j]['close'] for j in range(i-13, i+1)]
                gains = [max(0, recent_closes[j] - recent_closes[j-1]) for j in range(1, len(recent_closes))]
                losses = [max(0, recent_closes[j-1] - recent_closes[j]) for j in range(1, len(recent_closes))]

                avg_gain = sum(gains) / len(gains) if gains else 0
                avg_loss = sum(losses) / len(losses) if losses else 0

                if avg_loss != 0:
                    rs = avg_gain / avg_loss
                    rsi = 100 - (100 / (1 + rs))
                else:
                    rsi = 100

                enhanced_day['rsi'] = rsi
            else:
                enhanced_day['rsi'] = 50  # Neutral default

            # Calculate EMA 9 and 21 (simplified)
            if i >= 8:
                recent_closes_9 = [price_data[j]['close'] for j in range(i-8, i+1)]
                enhanced_day['ema_9'] = sum(recent_closes_9) / len(recent_closes_9)
            else:
                enhanced_day['ema_9'] = day['close']

            if i >= 20:
                recent_closes_21 = [price_data[j]['close'] for j in range(i-20, i+1)]
                enhanced_day['ema_21'] = sum(recent_closes_21) / len(recent_closes_21)
            else:
                enhanced_day['ema_21'] = day['close']

            enhanced_data.append(enhanced_day)

        return enhanced_data

    def simulate_trading_strategy(self, historical_data: List[Dict], strategy_name: str) -> Dict:
        """Simulate trading strategy on historical data"""
        trades = []
        current_position = None
        account_value = 10000  # Starting capital
        trade_count = 0

        for i, day in enumerate(historical_data[1:], 1):  # Skip first day
            yesterday = historical_data[i-1]

            if strategy_name == "RSI_REVERSAL":
                # RSI reversal strategy
                if not current_position:
                    # Entry conditions
                    if yesterday['rsi'] <= 30 and day['rsi'] > 30:  # Oversold bounce
                        current_position = {
                            'type': 'CALL',
                            'entry_date': day['date'],
                            'entry_price': day['open'],
                            'stop_loss': day['open'] * 0.95,  # 5% stop
                            'target': day['open'] * 1.10,     # 10% target
                            'contracts': 10
                        }
                        trade_count += 1

                    elif yesterday['rsi'] >= 70 and day['rsi'] < 70:  # Overbought fade
                        current_position = {
                            'type': 'PUT',
                            'entry_date': day['date'],
                            'entry_price': day['open'],
                            'stop_loss': day['open'] * 1.05,  # 5% stop
                            'target': day['open'] * 0.90,     # 10% target
                            'contracts': 10
                        }
                        trade_count += 1

                else:
                    # Exit conditions
                    exit_trade = False
                    exit_reason = ""
                    exit_price = day['close']

                    if current_position['type'] == 'CALL':
                        if day['high'] >= current_position['target']:
                            exit_trade = True
                            exit_reason = "TARGET_HIT"
                            exit_price = current_position['target']
                        elif day['low'] <= current_position['stop_loss']:
                            exit_trade = True
                            exit_reason = "STOP_LOSS"
                            exit_price = current_position['stop_loss']

                    else:  # PUT
                        if day['low'] <= current_position['target']:
                            exit_trade = True
                            exit_reason = "TARGET_HIT"
                            exit_price = current_position['target']
                        elif day['high'] >= current_position['stop_loss']:
                            exit_trade = True
                            exit_reason = "STOP_LOSS"
                            exit_price = current_position['stop_loss']

                    # Time-based exit (hold for max 5 days)
                    if (day['date'] - current_position['entry_date']).days >= 5:
                        exit_trade = True
                        exit_reason = "TIME_EXIT"
                        exit_price = day['close']

                    if exit_trade:
                        # Calculate P&L (simplified option simulation)
                        if current_position['type'] == 'CALL':
                            pnl_pct = (exit_price - current_position['entry_price']) / current_position['entry_price']
                            option_pnl = pnl_pct * 3  # Leverage factor for options
                        else:  # PUT
                            pnl_pct = (current_position['entry_price'] - exit_price) / current_position['entry_price']
                            option_pnl = pnl_pct * 3  # Leverage factor for options

                        # Cap losses at -100% (option can't go below 0)
                        option_pnl = max(option_pnl, -1.0)

                        trade_amount = account_value * 0.02  # 2% risk per trade
                        trade_pnl = trade_amount * option_pnl

                        trade_record = {
                            'trade_id': trade_count,
                            'type': current_position['type'],
                            'entry_date': current_position['entry_date'],
                            'exit_date': day['date'],
                            'entry_price': current_position['entry_price'],
                            'exit_price': exit_price,
                            'exit_reason': exit_reason,
                            'hold_days': (day['date'] - current_position['entry_date']).days,
                            'pnl_pct': option_pnl * 100,
                            'pnl_dollar': trade_pnl
                        }

                        trades.append(trade_record)
                        account_value += trade_pnl
                        current_position = None

            elif strategy_name == "EMA_MOMENTUM":
                # EMA crossover strategy
                if not current_position and i > 1:
                    prev_day = historical_data[i-2]

                    # Bullish crossover
                    if (prev_day['ema_9'] <= prev_day['ema_21'] and
                        yesterday['ema_9'] > yesterday['ema_21']):

                        current_position = {
                            'type': 'CALL',
                            'entry_date': day['date'],
                            'entry_price': day['open'],
                            'stop_loss': day['open'] * 0.96,
                            'target': day['open'] * 1.08,
                            'contracts': 10
                        }
                        trade_count += 1

                    # Bearish crossover
                    elif (prev_day['ema_9'] >= prev_day['ema_21'] and
                          yesterday['ema_9'] < yesterday['ema_21']):

                        current_position = {
                            'type': 'PUT',
                            'entry_date': day['date'],
                            'entry_price': day['open'],
                            'stop_loss': day['open'] * 1.04,
                            'target': day['open'] * 0.92,
                            'contracts': 10
                        }
                        trade_count += 1

                else:
                    # Exit logic (similar to RSI strategy)
                    if current_position:
                        exit_trade = False
                        exit_reason = ""
                        exit_price = day['close']

                        # Target/Stop logic
                        if current_position['type'] == 'CALL':
                            if day['high'] >= current_position['target']:
                                exit_trade = True
                                exit_reason = "TARGET_HIT"
                                exit_price = current_position['target']
                            elif day['low'] <= current_position['stop_loss']:
                                exit_trade = True
                                exit_reason = "STOP_LOSS"
                                exit_price = current_position['stop_loss']
                        else:  # PUT
                            if day['low'] <= current_position['target']:
                                exit_trade = True
                                exit_reason = "TARGET_HIT"
                                exit_price = current_position['target']
                            elif day['high'] >= current_position['stop_loss']:
                                exit_trade = True
                                exit_reason = "STOP_LOSS"
                                exit_price = current_position['stop_loss']

                        # Time exit
                        if (day['date'] - current_position['entry_date']).days >= 3:
                            exit_trade = True
                            exit_reason = "TIME_EXIT"
                            exit_price = day['close']

                        if exit_trade:
                            # Calculate P&L
                            if current_position['type'] == 'CALL':
                                pnl_pct = (exit_price - current_position['entry_price']) / current_position['entry_price']
                                option_pnl = pnl_pct * 2.5  # Leverage factor
                            else:
                                pnl_pct = (current_position['entry_price'] - exit_price) / current_position['entry_price']
                                option_pnl = pnl_pct * 2.5

                            option_pnl = max(option_pnl, -1.0)
                            trade_amount = account_value * 0.02
                            trade_pnl = trade_amount * option_pnl

                            trade_record = {
                                'trade_id': trade_count,
                                'type': current_position['type'],
                                'entry_date': current_position['entry_date'],
                                'exit_date': day['date'],
                                'entry_price': current_position['entry_price'],
                                'exit_price': exit_price,
                                'exit_reason': exit_reason,
                                'hold_days': (day['date'] - current_position['entry_date']).days,
                                'pnl_pct': option_pnl * 100,
                                'pnl_dollar': trade_pnl
                            }

                            trades.append(trade_record)
                            account_value += trade_pnl
                            current_position = None

        return {
            'strategy': strategy_name,
            'trades': trades,
            'final_account_value': account_value,
            'total_return': ((account_value - 10000) / 10000) * 100,
            'trade_count': len(trades)
        }

    def calculate_performance_metrics(self, backtest_results: Dict) -> Dict:
        """Calculate comprehensive performance metrics"""
        trades = backtest_results['trades']

        if not trades:
            return {'error': 'No trades to analyze'}

        # Basic metrics
        win_trades = [t for t in trades if t['pnl_dollar'] > 0]
        loss_trades = [t for t in trades if t['pnl_dollar'] <= 0]

        win_rate = len(win_trades) / len(trades) * 100 if trades else 0
        avg_win = sum([t['pnl_dollar'] for t in win_trades]) / len(win_trades) if win_trades else 0
        avg_loss = sum([t['pnl_dollar'] for t in loss_trades]) / len(loss_trades) if loss_trades else 0

        profit_factor = abs(avg_win * len(win_trades) / (avg_loss * len(loss_trades))) if loss_trades and avg_loss != 0 else float('inf')

        # Drawdown calculation
        account_values = [10000]  # Starting value
        for trade in trades:
            account_values.append(account_values[-1] + trade['pnl_dollar'])

        peak = account_values[0]
        max_drawdown = 0
        for value in account_values:
            if value > peak:
                peak = value
            drawdown = (peak - value) / peak * 100
            max_drawdown = max(max_drawdown, drawdown)

        # Hold time analysis
        hold_times = [t['hold_days'] for t in trades]
        avg_hold_time = sum(hold_times) / len(hold_times) if hold_times else 0

        return {
            'total_trades': len(trades),
            'winning_trades': len(win_trades),
            'losing_trades': len(loss_trades),
            'win_rate': round(win_rate, 2),
            'average_win': round(avg_win, 2),
            'average_loss': round(avg_loss, 2),
            'profit_factor': round(profit_factor, 2),
            'total_return': round(backtest_results['total_return'], 2),
            'max_drawdown': round(max_drawdown, 2),
            'average_hold_time': round(avg_hold_time, 1),
            'final_account_value': round(backtest_results['final_account_value'], 2)
        }

    def run_comprehensive_backtest(self, symbols: List[str], strategies: List[str], period_days: int = 30) -> str:
        """Run comprehensive backtesting across multiple assets and strategies"""
        output = []

        output.append("COMPREHENSIVE BACKTESTING ANALYSIS")
        output.append("=" * 50)
        output.append(f"Period: {period_days} days")
        output.append(f"Symbols: {', '.join(symbols)}")
        output.append(f"Strategies: {', '.join(strategies)}")
        output.append("")

        all_results = {}

        for symbol in symbols:
            output.append(f"ANALYZING {symbol}")
            output.append("-" * 30)

            # Get historical data
            historical = self.get_historical_data(symbol, period_days)

            if not historical['success']:
                output.append(f"ERROR getting data for {symbol}: {historical['error']}")
                continue

            # Calculate technical indicators
            enhanced_data = self.calculate_technical_indicators(historical['data'])

            symbol_results = {}

            for strategy in strategies:
                output.append(f"\nStrategy: {strategy}")

                # Run backtest
                backtest_result = self.simulate_trading_strategy(enhanced_data, strategy)

                # Calculate metrics
                metrics = self.calculate_performance_metrics(backtest_result)

                symbol_results[strategy] = {
                    'backtest': backtest_result,
                    'metrics': metrics
                }

                # Display results
                if 'error' not in metrics:
                    output.append(f"   Trades: {metrics['total_trades']}")
                    output.append(f"   Win Rate: {metrics['win_rate']}%")
                    output.append(f"   Total Return: {metrics['total_return']}%")
                    output.append(f"   Profit Factor: {metrics['profit_factor']}")
                    output.append(f"   Max Drawdown: {metrics['max_drawdown']}%")
                    output.append(f"   Avg Hold: {metrics['average_hold_time']} days")
                else:
                    output.append(f"   No trades generated")

            all_results[symbol] = symbol_results
            output.append("")

        # Summary comparison
        output.append("STRATEGY COMPARISON SUMMARY")
        output.append("=" * 40)

        for strategy in strategies:
            output.append(f"\n{strategy} Performance:")
            strategy_returns = []
            strategy_win_rates = []

            for symbol in symbols:
                if symbol in all_results and strategy in all_results[symbol]:
                    metrics = all_results[symbol][strategy]['metrics']
                    if 'error' not in metrics:
                        strategy_returns.append(metrics['total_return'])
                        strategy_win_rates.append(metrics['win_rate'])
                        output.append(f"   {symbol}: {metrics['total_return']}% return, {metrics['win_rate']}% win rate")

            if strategy_returns:
                avg_return = sum(strategy_returns) / len(strategy_returns)
                avg_win_rate = sum(strategy_win_rates) / len(strategy_win_rates)
                output.append(f"   Average: {avg_return:.2f}% return, {avg_win_rate:.2f}% win rate")

        # Save results
        results_data = {
            'backtest_date': datetime.now().isoformat(),
            'period_days': period_days,
            'symbols': symbols,
            'strategies': strategies,
            'results': all_results
        }

        import os
        os.makedirs(os.path.dirname(self.results_file), exist_ok=True)
        with open(self.results_file, 'w') as f:
            json.dump(results_data, f, indent=2, default=str)

        output.append(f"\nResults saved to {self.results_file}")

        return "\n".join(output)

def main():
    """Test backtesting system"""
    backtest = BacktestingEngine()

    print("BACKTESTING VALIDATION SYSTEM")
    print("=" * 35)

    # Run comprehensive backtest
    symbols = ['SPY', 'QQQ', 'IWM']
    strategies = ['RSI_REVERSAL', 'EMA_MOMENTUM']

    results = backtest.run_comprehensive_backtest(symbols, strategies, period_days=30)
    print(results)

if __name__ == "__main__":
    main()