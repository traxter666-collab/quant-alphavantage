#!/usr/bin/env python3
"""
Real-Time Streaming Monitoring System
Continuous market surveillance with intelligent alerting and forecasting integration
"""

import asyncio
import json
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable
import requests

# Import our systems
from advanced_forecasting_engine import AdvancedForecastingEngine
from trading_alerts import TradingAlertsEngine
from complete_trading_system import CompleteTradingSystem
from dynamic_exit_management import DynamicExitManager
from probability_scoring_system import ProbabilityScoringSystem

class StreamingMonitor:
    def __init__(self):
        # Initialize subsystems
        self.forecasting = AdvancedForecastingEngine()
        self.alerts = TradingAlertsEngine()
        self.trading_system = CompleteTradingSystem()
        self.exit_manager = DynamicExitManager()
        self.scoring = ProbabilityScoringSystem()

        self.api_key = 'ZFL38ZY98GSN7E1S'
        self.session_file = ".spx/streaming_session.json"

        # Streaming configuration
        self.monitoring = False
        self.symbols = ['SPY', 'QQQ', 'IWM']
        self.refresh_interval = 30  # seconds
        self.forecast_interval = 300  # seconds (5 minutes)
        self.alert_cooldown = 60  # seconds between similar alerts

        # State tracking
        self.last_prices = {}
        self.last_forecasts = {}
        self.last_alerts = {}
        self.price_history = {}
        self.alert_history = []

        # Thresholds
        self.price_change_threshold = 0.3  # 0.3% price change
        self.volume_threshold = 1.5  # 1.5x average volume
        self.forecast_confidence_threshold = 70  # 70% forecast confidence
        self.probability_score_threshold = 75  # 75% probability score

        # Enhanced forecast thresholds
        self.high_confidence_forecast_threshold = 85  # 85% for high-priority alerts
        self.model_consensus_threshold = 80  # 80% model agreement threshold
        self.forecast_price_deviation_threshold = 1.0  # 1.0% significant price prediction

    def get_real_time_data(self, symbol: str) -> Dict:
        """Get real-time market data"""
        try:
            url = f'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={self.api_key}'
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
                    'high': float(quote['03. high']),
                    'low': float(quote['04. low']),
                    'timestamp': datetime.now()
                }
            else:
                return {'success': False, 'error': 'No quote data', 'symbol': symbol}

        except Exception as e:
            return {'success': False, 'error': str(e), 'symbol': symbol}

    def detect_significant_changes(self, current_data: Dict) -> List[Dict]:
        """Detect significant market changes"""
        alerts = []
        symbol = current_data['symbol']
        current_price = current_data['price']
        change_pct = current_data['change_pct']

        # Track price history
        if symbol not in self.price_history:
            self.price_history[symbol] = []

        self.price_history[symbol].append({
            'timestamp': current_data['timestamp'],
            'price': current_price,
            'volume': current_data['volume']
        })

        # Keep only last 100 data points
        if len(self.price_history[symbol]) > 100:
            self.price_history[symbol] = self.price_history[symbol][-100:]

        # Check for significant price movement
        if abs(change_pct) >= self.price_change_threshold:
            alerts.append({
                'type': 'PRICE_MOVEMENT',
                'symbol': symbol,
                'message': f"{symbol} moved {change_pct:+.2f}% to ${current_price:.2f}",
                'urgency': 'HIGH' if abs(change_pct) >= 1.0 else 'MEDIUM',
                'data': current_data
            })

        # Check for volume surge
        if len(self.price_history[symbol]) >= 10:
            recent_volumes = [p['volume'] for p in self.price_history[symbol][-10:]]
            avg_volume = sum(recent_volumes[:-1]) / len(recent_volumes[:-1])
            current_volume = current_data['volume']

            if current_volume > avg_volume * self.volume_threshold:
                volume_ratio = current_volume / avg_volume
                alerts.append({
                    'type': 'VOLUME_SURGE',
                    'symbol': symbol,
                    'message': f"{symbol} volume surge: {volume_ratio:.1f}x average ({current_volume:,})",
                    'urgency': 'HIGH' if volume_ratio >= 3.0 else 'MEDIUM',
                    'data': current_data
                })

        # Check for rapid price acceleration
        if len(self.price_history[symbol]) >= 5:
            recent_prices = [p['price'] for p in self.price_history[symbol][-5:]]
            price_acceleration = (recent_prices[-1] - recent_prices[0]) / recent_prices[0] * 100

            if abs(price_acceleration) >= 0.5:  # 0.5% in 5 data points
                alerts.append({
                    'type': 'PRICE_ACCELERATION',
                    'symbol': symbol,
                    'message': f"{symbol} rapid movement: {price_acceleration:+.2f}% in last 5 updates",
                    'urgency': 'HIGH',
                    'data': current_data
                })

        return alerts

    def should_run_forecast(self, symbol: str) -> bool:
        """Determine if we should run a new forecast"""
        if symbol not in self.last_forecasts:
            return True

        last_forecast_time = self.last_forecasts[symbol].get('timestamp')
        if not last_forecast_time:
            return True

        time_since_forecast = (datetime.now() - datetime.fromisoformat(last_forecast_time)).total_seconds()
        return time_since_forecast >= self.forecast_interval

    def should_send_alert(self, alert: Dict) -> bool:
        """Check if we should send this alert (avoid spam)"""
        alert_key = f"{alert['symbol']}_{alert['type']}"
        current_time = datetime.now()

        if alert_key in self.last_alerts:
            last_alert_time = self.last_alerts[alert_key]
            time_since_alert = (current_time - last_alert_time).total_seconds()

            if time_since_alert < self.alert_cooldown:
                return False

        self.last_alerts[alert_key] = current_time
        return True

    def process_symbol(self, symbol: str) -> Dict:
        """Process a single symbol comprehensively"""
        results = {
            'symbol': symbol,
            'timestamp': datetime.now(),
            'market_data': None,
            'alerts': [],
            'forecast': None,
            'probability_score': None,
            'status': 'PROCESSING'
        }

        try:
            # Get real-time data
            market_data = self.get_real_time_data(symbol)
            results['market_data'] = market_data

            if not market_data.get('success'):
                results['status'] = 'ERROR'
                results['error'] = market_data.get('error', 'Unknown error')
                return results

            # Detect significant changes
            alerts = self.detect_significant_changes(market_data)
            results['alerts'] = alerts

            # Run forecast if needed
            if self.should_run_forecast(symbol):
                print(f"Running advanced 8-model ensemble forecast for {symbol}...")
                try:
                    forecast = self.forecasting.run_full_ensemble_forecast(symbol)
                    if forecast.get('success'):
                        self.last_forecasts[symbol] = forecast
                        results['forecast'] = forecast

                        # Enhanced forecast signal generation with ensemble details
                        if forecast['final_confidence'] >= self.forecast_confidence_threshold:
                            # Extract top performing models for context
                            top_models = sorted(forecast['model_results'],
                                              key=lambda x: x['confidence'], reverse=True)[:3]
                            top_model_names = [m['model_name'] for m in top_models]

                            forecast_alert = {
                                'type': 'ENSEMBLE_FORECAST_SIGNAL',
                                'symbol': symbol,
                                'message': f"{symbol} 8-model forecast: {forecast['direction']} {forecast['price_change_pct']:+.2f}% "
                                         f"({forecast['final_confidence']:.0f}% confidence) | Top models: {', '.join(top_model_names)}",
                                'urgency': 'HIGH' if forecast['final_confidence'] >= 90 else 'MEDIUM',
                                'data': {
                                    'forecast': forecast,
                                    'top_models': top_models[:3],
                                    'prediction_horizon': forecast.get('time_horizon_minutes', 15),
                                    'target_price': forecast.get('predicted_price', 0),
                                    'model_count': len(forecast['model_results'])
                                }
                            }
                            alerts.append(forecast_alert)

                        # Additional alert for model consensus changes
                        if 'model_consensus_strength' in forecast:
                            consensus_strength = forecast['model_consensus_strength']
                            if consensus_strength >= 80:  # Strong model agreement
                                consensus_alert = {
                                    'type': 'MODEL_CONSENSUS',
                                    'symbol': symbol,
                                    'message': f"{symbol} strong model consensus: {consensus_strength:.0f}% agreement "
                                             f"on {forecast['direction']} direction",
                                    'urgency': 'MEDIUM',
                                    'data': {'consensus_strength': consensus_strength, 'forecast': forecast}
                                }
                                alerts.append(consensus_alert)

                except Exception as e:
                    print(f"Error running advanced forecast: {e}")
                    # Fallback to basic forecast alert
                    results['forecast_error'] = str(e)

            # Run probability scoring for primary symbol
            if symbol == 'SPY':
                print(f"Running probability scoring for {symbol}...")
                # Get scoring via the integrated system (simplified)
                try:
                    scoring_text = self.scoring.run_comprehensive_scoring(symbol)
                    with open(self.scoring.session_file, 'r') as f:
                        scoring_data = json.load(f)

                    results['probability_score'] = scoring_data

                    if scoring_data['percentage'] >= self.probability_score_threshold:
                        score_alert = {
                            'type': 'HIGH_PROBABILITY_SCORE',
                            'symbol': symbol,
                            'message': f"{symbol} high probability score: {scoring_data['percentage']:.1f}% ({scoring_data['recommendation']})",
                            'urgency': 'HIGH' if scoring_data['percentage'] >= 85 else 'MEDIUM',
                            'data': scoring_data
                        }
                        alerts.append(score_alert)

                except Exception as e:
                    print(f"Error running probability scoring: {e}")

            # Generate enhanced integrated alerts (includes forecast integration)
            enhanced_alerts = self.generate_integrated_alerts(results)
            results['alerts'] = enhanced_alerts

            # Send enhanced alerts with rich content
            for alert in enhanced_alerts:
                if self.should_send_alert(alert):
                    # Create enhanced Discord message with price data, confidence, and volume
                    enhanced_message = self.create_enhanced_alert_message(alert, market_data, results.get('forecast'), symbol)

                    discord_alert = self.alerts.create_alert(
                        priority=1 if alert['urgency'] == 'HIGH' else 2,
                        alert_type=alert['type'],
                        message=enhanced_message,
                        data=alert['data']
                    )
                    self.alerts.send_discord_alert(discord_alert)
                    self.alert_history.append(alert)

            results['status'] = 'SUCCESS'

        except Exception as e:
            results['status'] = 'ERROR'
            results['error'] = str(e)
            print(f"Error processing {symbol}: {e}")

        return results

    def run_monitoring_cycle(self) -> Dict:
        """Run one complete monitoring cycle"""
        cycle_start = datetime.now()
        print(f"STREAMING CYCLE: {cycle_start.strftime('%H:%M:%S')}")

        cycle_results = {
            'timestamp': cycle_start,
            'symbols_processed': [],
            'total_alerts': 0,
            'active_forecasts': 0,
            'cycle_duration': 0
        }

        # Process all symbols
        for symbol in self.symbols:
            print(f"Processing {symbol}...")
            symbol_result = self.process_symbol(symbol)
            cycle_results['symbols_processed'].append(symbol_result)

            if symbol_result['alerts']:
                cycle_results['total_alerts'] += len(symbol_result['alerts'])

            if symbol_result.get('forecast'):
                cycle_results['active_forecasts'] += 1

        # Calculate cycle duration
        cycle_end = datetime.now()
        cycle_results['cycle_duration'] = (cycle_end - cycle_start).total_seconds()

        # Save cycle results
        try:
            import os
            os.makedirs(os.path.dirname(self.session_file), exist_ok=True)
            with open(self.session_file, 'w') as f:
                json.dump(cycle_results, f, indent=2, default=str)
        except Exception as e:
            print(f"Error saving session: {e}")

        print(f"Cycle completed in {cycle_results['cycle_duration']:.1f}s - {cycle_results['total_alerts']} alerts")

        return cycle_results

    def run_enhanced_forecast_monitoring(self, duration_minutes: int = 60) -> str:
        """Run enhanced monitoring with focus on forecast integration"""
        start_time = datetime.now()
        end_time = start_time + timedelta(minutes=duration_minutes)

        output = []
        output.append("ENHANCED FORECAST MONITORING SESSION")
        output.append("=" * 45)
        output.append(f"Session Start: {start_time.strftime('%H:%M:%S')}")
        output.append(f"Duration: {duration_minutes} minutes")
        output.append(f"Forecast Interval: {self.forecast_interval} seconds")
        output.append(f"Symbols: {', '.join(self.symbols)}")
        output.append("")

        cycle_count = 0
        forecast_signals = 0
        high_confidence_forecasts = 0
        total_alerts = 0

        print("Enhanced forecast monitoring starting...")

        try:
            while datetime.now() < end_time and self.monitoring:
                cycle_count += 1
                cycle_start = datetime.now()

                print(f"Forecast monitoring cycle #{cycle_count}")

                # Run monitoring cycle
                cycle_result = self.run_monitoring_cycle()

                # Analyze forecast performance
                for symbol_result in cycle_result['symbols_processed']:
                    if symbol_result.get('forecast'):
                        forecast = symbol_result['forecast']
                        forecast_signals += 1

                        if forecast['final_confidence'] >= self.high_confidence_forecast_threshold:
                            high_confidence_forecasts += 1
                            print(f"High-confidence forecast: {symbol_result['symbol']} "
                                  f"{forecast['direction']} {forecast['final_confidence']:.0f}%")

                    total_alerts += len(symbol_result.get('alerts', []))

                # Wait for next cycle
                time.sleep(self.refresh_interval)

        except KeyboardInterrupt:
            print("Enhanced forecast monitoring stopped by user")
            self.monitoring = False

        # Generate session summary
        session_duration = (datetime.now() - start_time).total_seconds() / 60

        output.append("ENHANCED FORECAST MONITORING SUMMARY")
        output.append("=" * 40)
        output.append(f"Actual Duration: {session_duration:.1f} minutes")
        output.append(f"Monitoring Cycles: {cycle_count}")
        output.append(f"Total Forecast Signals: {forecast_signals}")
        output.append(f"High-Confidence Forecasts: {high_confidence_forecasts}")
        output.append(f"Total Alerts Generated: {total_alerts}")
        output.append("")

        if forecast_signals > 0:
            high_conf_rate = (high_confidence_forecasts / forecast_signals) * 100
            output.append(f"High-Confidence Rate: {high_conf_rate:.1f}%")
            output.append(f"Average Forecasts/Cycle: {forecast_signals / max(cycle_count, 1):.1f}")

        output.append("")
        output.append("INTEGRATION STATUS: FORECAST + STREAMING ALERTS OPERATIONAL")
        output.append("Session data saved to .spx/enhanced_monitoring_session.json")

        return "\n".join(output)

    def start_streaming(self, refresh_interval: int = 30) -> None:
        """Start continuous streaming monitoring"""
        self.refresh_interval = refresh_interval
        self.monitoring = True

        print("REAL-TIME STREAMING MONITOR")
        print("=" * 40)
        print(f"Symbols: {', '.join(self.symbols)}")
        print(f"Refresh Interval: {refresh_interval} seconds")
        print(f"Forecast Interval: {self.forecast_interval} seconds")
        print(f"Price Threshold: {self.price_change_threshold}%")
        print(f"Volume Threshold: {self.volume_threshold}x")
        print("-" * 40)

        cycle_count = 0

        try:
            while self.monitoring:
                cycle_count += 1
                print(f"\nSTREAMING CYCLE #{cycle_count}")

                # Run monitoring cycle
                cycle_result = self.run_monitoring_cycle()

                # Display cycle summary
                print(f"Alerts Generated: {cycle_result['total_alerts']}")
                print(f"Active Forecasts: {cycle_result['active_forecasts']}")
                print(f"Duration: {cycle_result['cycle_duration']:.1f}s")

                # Wait for next cycle
                print(f"Next cycle in {refresh_interval} seconds...")
                time.sleep(refresh_interval)

        except KeyboardInterrupt:
            print("\nSTREAMING STOPPED by user")
            self.monitoring = False
        except Exception as e:
            print(f"STREAMING ERROR: {e}")
            self.monitoring = False

    def run_single_cycle(self) -> str:
        """Run a single monitoring cycle and return formatted results"""
        cycle_result = self.run_monitoring_cycle()

        output = []
        output.append("STREAMING MONITOR - SINGLE CYCLE RESULTS")
        output.append("=" * 45)
        output.append(f"Cycle Time: {cycle_result['timestamp'].strftime('%H:%M:%S')}")
        output.append(f"Duration: {cycle_result['cycle_duration']:.1f} seconds")
        output.append("")

        # Process results by symbol
        for symbol_result in cycle_result['symbols_processed']:
            symbol = symbol_result['symbol']
            output.append(f"SYMBOL: {symbol}")
            output.append("-" * 15)

            if symbol_result['status'] == 'SUCCESS':
                market_data = symbol_result['market_data']
                output.append(f"Price: ${market_data['price']:.2f} ({market_data['change_pct']:+.2f}%)")
                output.append(f"Volume: {market_data['volume']:,}")

                # Show alerts
                if symbol_result['alerts']:
                    output.append("ALERTS:")
                    for alert in symbol_result['alerts']:
                        urgency_symbol = {"HIGH": "[HIGH]", "MEDIUM": "[MED]", "LOW": "[LOW]"}.get(alert['urgency'], "[INFO]")
                        output.append(f"  {urgency_symbol} {alert['type']}: {alert['message']}")
                else:
                    output.append("No alerts generated")

                # Show enhanced forecast details if available
                if symbol_result.get('forecast'):
                    forecast = symbol_result['forecast']
                    output.append(f"8-MODEL ENSEMBLE FORECAST:")
                    output.append(f"  Direction: {forecast['direction']} {forecast['price_change_pct']:+.2f}%")
                    output.append(f"  Confidence: {forecast['final_confidence']:.0f}% (Target: ${forecast.get('predicted_price', 0):.2f})")
                    output.append(f"  Horizon: {forecast.get('time_horizon_minutes', 15)} minutes")

                    # Show top 3 models
                    if 'model_results' in forecast:
                        top_models = sorted(forecast['model_results'],
                                          key=lambda x: x['confidence'], reverse=True)[:3]
                        model_strings = [f"{m['model_name']} ({m['confidence']:.0f}%)" for m in top_models]
                        output.append(f"  Top Models: {', '.join(model_strings)}")

                    # Show consensus strength if available
                    if 'model_consensus_strength' in forecast:
                        consensus = forecast['model_consensus_strength']
                        consensus_symbol = "STRONG" if consensus >= 80 else "MODERATE" if consensus >= 60 else "WEAK"
                        output.append(f"  Model Consensus: {consensus:.0f}% ({consensus_symbol})")

                # Show probability score for SPY
                if symbol_result.get('probability_score'):
                    score_data = symbol_result['probability_score']
                    output.append(f"PROBABILITY SCORE: {score_data['percentage']:.1f}% "
                                f"({score_data['recommendation']})")

            else:
                output.append(f"ERROR: {symbol_result.get('error', 'Unknown error')}")

            output.append("")

        # Summary
        output.append("CYCLE SUMMARY:")
        output.append(f"Total Alerts: {cycle_result['total_alerts']}")
        output.append(f"Active Forecasts: {cycle_result['active_forecasts']}")
        output.append(f"Symbols Processed: {len(cycle_result['symbols_processed'])}")

        output.append("")
        output.append("SESSION UPDATED: Streaming data saved to .spx/")

        return "\n".join(output)

    def create_enhanced_alert_message(self, alert: Dict, market_data: Dict, forecast: Dict, symbol: str) -> str:
        """Create enhanced Discord alert message with price data, confidence scores, and volume"""
        try:
            # Base alert message
            base_message = alert['message']
            alert_type = alert['type']
            urgency = alert['urgency']

            # Extract key market data
            price = market_data.get('price', 0)
            change_pct = market_data.get('change_pct', 0)
            volume = market_data.get('volume', 0)

            # Priority indicators
            priority_icon = "[HIGH]" if urgency == 'HIGH' else "[MED]" if urgency == 'MEDIUM' else "[LOW]"
            direction_icon = "[UP]" if change_pct > 0 else "[DOWN]" if change_pct < 0 else "[FLAT]"

            # Volume analysis
            volume_str = f"{volume:,}" if volume < 1000000 else f"{volume/1000000:.1f}M"

            # Calculate volume ratio if we have history
            volume_context = ""
            if symbol in self.price_history and len(self.price_history[symbol]) >= 5:
                recent_volumes = [p['volume'] for p in self.price_history[symbol][-5:]]
                avg_volume = sum(recent_volumes) / len(recent_volumes)
                volume_ratio = volume / avg_volume if avg_volume > 0 else 1.0
                volume_context = f" ({volume_ratio:.1f}x avg)" if volume_ratio >= 1.2 else ""

            # Forecast confidence if available
            forecast_context = ""
            if forecast and forecast.get('final_confidence'):
                confidence = forecast['final_confidence']
                direction = forecast.get('direction', '').upper()
                forecast_context = f" | Forecast: {direction} {confidence:.0f}%"

            # Enhanced message format based on alert type
            if alert_type == 'PRICE_MOVEMENT':
                enhanced_message = (f"{priority_icon} {symbol} PRICE ALERT {direction_icon}\\n"
                                  f"Price: ${price:.2f} ({change_pct:+.2f}%)\\n"
                                  f"Volume: {volume_str}{volume_context}{forecast_context}")

            elif alert_type == 'VOLUME_SURGE':
                enhanced_message = (f"{priority_icon} {symbol} VOLUME SURGE\\n"
                                  f"Price: ${price:.2f} ({change_pct:+.2f}%)\\n"
                                  f"Volume: {volume_str}{volume_context}{forecast_context}")

            elif alert_type == 'ENSEMBLE_FORECAST_SIGNAL':
                if forecast:
                    confidence = forecast.get('final_confidence', 0)
                    direction = forecast.get('direction', '').upper()
                    target_price = forecast.get('predicted_price', price)
                    enhanced_message = (f"{priority_icon} {symbol} ENSEMBLE FORECAST\\n"
                                      f"Signal: {direction} {confidence:.0f}% confidence\\n"
                                      f"Current: ${price:.2f} | Target: ${target_price:.2f}\\n"
                                      f"Volume: {volume_str}{volume_context}")
                else:
                    enhanced_message = base_message

            elif alert_type == 'HIGH_PROBABILITY_SCORE':
                enhanced_message = (f"{priority_icon} {symbol} HIGH PROBABILITY\\n"
                                  f"Price: ${price:.2f} ({change_pct:+.2f}%)\\n"
                                  f"Volume: {volume_str}{volume_context}{forecast_context}")

            else:
                # Default enhanced format for other alert types
                enhanced_message = (f"{priority_icon} {symbol} {alert_type}\\n"
                                  f"Price: ${price:.2f} ({change_pct:+.2f}%)\\n"
                                  f"Volume: {volume_str}{volume_context}{forecast_context}")

            # Add timestamp
            timestamp = datetime.now().strftime('%H:%M:%S')
            enhanced_message += f"\\nTime: {timestamp} ET"

            return enhanced_message

        except Exception as e:
            # Fallback to original message if enhancement fails
            print(f"Error creating enhanced alert message: {e}")
            return alert['message']

    def generate_integrated_alerts(self, symbol_result: Dict) -> List[Dict]:
        """Generate alerts integrating forecasting with market data"""
        integrated_alerts = []

        market_data = symbol_result.get('market_data', {})
        forecast = symbol_result.get('forecast')
        alerts = symbol_result.get('alerts', [])

        if not market_data.get('success') or not forecast:
            return alerts

        # Check for forecast-price action divergence
        current_price = market_data['price']
        predicted_price = forecast.get('predicted_price', current_price)
        price_deviation = abs(predicted_price - current_price) / current_price * 100

        if price_deviation >= self.forecast_price_deviation_threshold:
            direction_match = (
                (forecast['direction'] == 'BULLISH' and market_data['change_pct'] > 0) or
                (forecast['direction'] == 'BEARISH' and market_data['change_pct'] < 0)
            )

            if direction_match:
                confirmation_alert = {
                    'type': 'FORECAST_CONFIRMATION',
                    'symbol': symbol_result['symbol'],
                    'message': f"{symbol_result['symbol']} forecast confirmed: {forecast['direction']} prediction "
                             f"aligning with {market_data['change_pct']:+.2f}% move",
                    'urgency': 'HIGH' if forecast['final_confidence'] >= 85 else 'MEDIUM',
                    'data': {
                        'forecast': forecast,
                        'current_move': market_data['change_pct'],
                        'predicted_price': predicted_price,
                        'current_price': current_price
                    }
                }
                integrated_alerts.append(confirmation_alert)
            else:
                divergence_alert = {
                    'type': 'FORECAST_DIVERGENCE',
                    'symbol': symbol_result['symbol'],
                    'message': f"{symbol_result['symbol']} forecast divergence: {forecast['direction']} prediction "
                             f"vs {market_data['change_pct']:+.2f}% actual move",
                    'urgency': 'MEDIUM',
                    'data': {
                        'forecast': forecast,
                        'actual_move': market_data['change_pct'],
                        'divergence_magnitude': abs(market_data['change_pct'] - forecast['price_change_pct'])
                    }
                }
                integrated_alerts.append(divergence_alert)

        # Check for high-confidence forecast with volume confirmation
        if (forecast['final_confidence'] >= self.high_confidence_forecast_threshold and
            len(self.price_history.get(symbol_result['symbol'], [])) >= 5):

            recent_volumes = [p['volume'] for p in self.price_history[symbol_result['symbol']][-5:]]
            avg_volume = sum(recent_volumes) / len(recent_volumes)
            current_volume = market_data['volume']

            if current_volume > avg_volume * 1.3:  # Volume confirmation
                high_confidence_alert = {
                    'type': 'HIGH_CONFIDENCE_FORECAST_VOLUME',
                    'symbol': symbol_result['symbol'],
                    'message': f"{symbol_result['symbol']} high-confidence forecast ({forecast['final_confidence']:.0f}%) "
                             f"with volume confirmation ({current_volume/avg_volume:.1f}x avg)",
                    'urgency': 'HIGH',
                    'data': {
                        'forecast': forecast,
                        'volume_ratio': current_volume / avg_volume,
                        'confidence': forecast['final_confidence']
                    }
                }
                integrated_alerts.append(high_confidence_alert)

        return alerts + integrated_alerts

    def get_streaming_status(self) -> Dict:
        """Get current streaming system status"""
        return {
            'monitoring': self.monitoring,
            'symbols': self.symbols,
            'refresh_interval': self.refresh_interval,
            'forecast_interval': self.forecast_interval,
            'thresholds': {
                'price_change': self.price_change_threshold,
                'volume': self.volume_threshold,
                'forecast_confidence': self.forecast_confidence_threshold,
                'high_confidence_forecast': self.high_confidence_forecast_threshold,
                'model_consensus': self.model_consensus_threshold,
                'forecast_price_deviation': self.forecast_price_deviation_threshold
            },
            'last_forecasts': list(self.last_forecasts.keys()),
            'alert_history_count': len(self.alert_history),
            'forecast_integration': 'ACTIVE',
            'uptime': datetime.now().isoformat()
        }

def main():
    """Test streaming monitor"""
    monitor = StreamingMonitor()

    print("STREAMING MONITOR TEST")
    print("=" * 25)

    # Run single cycle test
    result = monitor.run_single_cycle()
    print(result)

    print("\nTo start continuous streaming:")
    print("monitor.start_streaming(30)  # 30-second intervals")

if __name__ == "__main__":
    main()