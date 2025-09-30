#!/usr/bin/env python3
"""
Advanced 8-Model Ensemble Forecasting System
Sophisticated strike prediction using multiple quantitative models
"""

import requests
import json
import numpy as np
import math
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

@dataclass
class ForecastResult:
    model_name: str
    predicted_price: float
    confidence: float
    time_horizon: int  # minutes
    reasoning: str

class AdvancedForecastingEngine:
    def __init__(self):
        self.api_key = 'ZFL38ZY98GSN7E1S'
        self.session_file = ".spx/advanced_forecasting_session.json"

        # Model weights (sum to 1.0)
        self.model_weights = {
            'momentum_regression': 0.15,
            'mean_reversion': 0.12,
            'volatility_breakout': 0.13,
            'support_resistance': 0.14,
            'volume_price_trend': 0.11,
            'options_flow': 0.10,
            'market_microstructure': 0.12,
            'ensemble_meta': 0.13
        }

    def get_enhanced_market_data(self, symbol: str) -> Dict:
        """Get comprehensive market data for all models"""
        try:
            # Get multiple data sources
            quote_url = f'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={self.api_key}'
            quote_response = requests.get(quote_url, timeout=10)
            quote_data = quote_response.json()

            # Get intraday data for technical analysis
            intraday_url = f'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval=5min&apikey={self.api_key}'
            intraday_response = requests.get(intraday_url, timeout=15)
            intraday_data = intraday_response.json()

            # Get RSI for momentum
            rsi_url = f'https://www.alphavantage.co/query?function=RSI&symbol={symbol}&interval=5min&time_period=14&series_type=close&apikey={self.api_key}'
            rsi_response = requests.get(rsi_url, timeout=15)
            rsi_data = rsi_response.json()

            # Get EMA for trend analysis
            ema_url = f'https://www.alphavantage.co/query?function=EMA&symbol={symbol}&interval=5min&time_period=21&series_type=close&apikey={self.api_key}'
            ema_response = requests.get(ema_url, timeout=15)
            ema_data = ema_response.json()

            result = {'success': True, 'symbol': symbol, 'timestamp': datetime.now()}

            # Process quote data
            if 'Global Quote' in quote_data:
                quote = quote_data['Global Quote']
                result.update({
                    'current_price': float(quote['05. price']),
                    'change_pct': float(quote['10. change percent'].rstrip('%')),
                    'volume': int(quote['06. volume']),
                    'high': float(quote['03. high']),
                    'low': float(quote['04. low']),
                    'open': float(quote['02. open'])
                })

            # Process intraday bars for technical analysis
            if 'Time Series (5min)' in intraday_data:
                time_series = intraday_data['Time Series (5min)']
                bars = []

                for timestamp, bar_data in list(time_series.items())[:50]:  # Last 50 bars
                    bars.append({
                        'timestamp': datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S'),
                        'open': float(bar_data['1. open']),
                        'high': float(bar_data['2. high']),
                        'low': float(bar_data['3. low']),
                        'close': float(bar_data['4. close']),
                        'volume': int(bar_data['5. volume'])
                    })

                result['bars'] = sorted(bars, key=lambda x: x['timestamp'], reverse=True)

            # Process RSI data
            if 'Technical Analysis: RSI' in rsi_data:
                rsi_series = rsi_data['Technical Analysis: RSI']
                rsi_values = []
                for timestamp, rsi_val in list(rsi_series.items())[:20]:
                    rsi_values.append({
                        'timestamp': datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S'),
                        'rsi': float(rsi_val['RSI'])
                    })
                result['rsi_series'] = sorted(rsi_values, key=lambda x: x['timestamp'], reverse=True)
                result['current_rsi'] = rsi_values[0]['rsi'] if rsi_values else 50

            # Process EMA data
            if 'Technical Analysis: EMA' in ema_data:
                ema_series = ema_data['Technical Analysis: EMA']
                latest_ema_date = max(ema_series.keys())
                result['ema_21'] = float(ema_series[latest_ema_date]['EMA'])

            return result

        except Exception as e:
            return {'success': False, 'error': str(e), 'symbol': symbol}

    def momentum_regression_model(self, data: Dict) -> ForecastResult:
        """Model 1: Momentum-based regression forecasting"""
        if not data.get('bars') or len(data['bars']) < 20:
            return ForecastResult("Momentum Regression", data.get('current_price', 0), 0, 30, "Insufficient data")

        bars = data['bars'][:20]  # Last 20 bars
        current_price = data['current_price']

        # Calculate momentum indicators
        price_changes = [(bars[i]['close'] - bars[i+1]['close']) for i in range(len(bars)-1)]
        avg_momentum = sum(price_changes) / len(price_changes)
        momentum_strength = abs(avg_momentum) / current_price * 100

        # Calculate trend acceleration
        recent_momentum = sum(price_changes[:5]) / 5
        older_momentum = sum(price_changes[10:15]) / 5
        acceleration = recent_momentum - older_momentum

        # Predict next 30-minute price based on momentum
        time_horizon = 30  # minutes
        momentum_factor = (avg_momentum * 6) + (acceleration * 2)  # 6 periods ahead
        predicted_price = current_price + momentum_factor

        # Confidence based on momentum consistency
        momentum_consistency = 1 - (np.std(price_changes) / abs(avg_momentum)) if avg_momentum != 0 else 0.5
        confidence = max(0, min(100, momentum_consistency * 100))

        reasoning = f"Momentum: {avg_momentum:.3f}, Acceleration: {acceleration:.3f}, Strength: {momentum_strength:.2f}%"

        return ForecastResult("Momentum Regression", predicted_price, confidence, time_horizon, reasoning)

    def mean_reversion_model(self, data: Dict) -> ForecastResult:
        """Model 2: Mean reversion to fair value"""
        if not data.get('bars') or len(data['bars']) < 20:
            return ForecastResult("Mean Reversion", data.get('current_price', 0), 0, 45, "Insufficient data")

        bars = data['bars'][:20]
        current_price = data['current_price']
        current_rsi = data.get('current_rsi', 50)

        # Calculate various means
        sma_10 = sum([bar['close'] for bar in bars[:10]]) / 10
        sma_20 = sum([bar['close'] for bar in bars[:20]]) / 20
        ema_21 = data.get('ema_21', current_price)

        # Volume-weighted average price (simplified)
        total_volume = sum([bar['volume'] for bar in bars[:10]])
        vwap = sum([bar['close'] * bar['volume'] for bar in bars[:10]]) / total_volume if total_volume > 0 else current_price

        # Calculate fair value estimate
        fair_value = (sma_10 * 0.3) + (sma_20 * 0.25) + (ema_21 * 0.25) + (vwap * 0.20)

        # Mean reversion strength based on RSI and distance from means
        distance_from_fair = abs(current_price - fair_value) / fair_value * 100
        rsi_extreme = abs(current_rsi - 50) / 50  # 0 to 1

        # Predict reversion (stronger when more extreme)
        reversion_factor = 0.3 if rsi_extreme > 0.4 else 0.15  # Strong vs weak reversion
        predicted_price = current_price + (fair_value - current_price) * reversion_factor

        # Confidence higher when more extreme from fair value
        confidence = min(95, max(40, distance_from_fair * 3 + rsi_extreme * 30))

        reasoning = f"Fair Value: {fair_value:.2f}, Distance: {distance_from_fair:.2f}%, RSI Extreme: {rsi_extreme:.2f}"

        return ForecastResult("Mean Reversion", predicted_price, confidence, 45, reasoning)

    def volatility_breakout_model(self, data: Dict) -> ForecastResult:
        """Model 3: Volatility-based breakout forecasting"""
        if not data.get('bars') or len(data['bars']) < 20:
            return ForecastResult("Volatility Breakout", data.get('current_price', 0), 0, 20, "Insufficient data")

        bars = data['bars'][:20]
        current_price = data['current_price']

        # Calculate historical volatility
        price_changes = [(bars[i]['close'] - bars[i+1]['close']) / bars[i+1]['close']
                        for i in range(len(bars)-1)]
        volatility = np.std(price_changes) * math.sqrt(252 * 24 * 12)  # Annualized

        # Calculate average true range
        atr_values = []
        for i in range(len(bars)-1):
            high_low = bars[i]['high'] - bars[i]['low']
            high_close = abs(bars[i]['high'] - bars[i+1]['close'])
            low_close = abs(bars[i]['low'] - bars[i+1]['close'])
            true_range = max(high_low, high_close, low_close)
            atr_values.append(true_range)

        atr = sum(atr_values[:14]) / 14  # 14-period ATR

        # Detect volatility regime
        recent_vol = np.std(price_changes[:5])
        historical_vol = np.std(price_changes[10:])
        vol_expansion = recent_vol / historical_vol if historical_vol > 0 else 1

        # Breakout prediction
        if vol_expansion > 1.5:  # High volatility expansion
            breakout_direction = 1 if price_changes[0] > 0 else -1
            breakout_magnitude = atr * 1.5 * breakout_direction
            confidence = min(90, vol_expansion * 40)
        else:  # Low volatility - expect consolidation
            breakout_magnitude = atr * 0.3 * (1 if price_changes[0] > 0 else -1)
            confidence = max(30, 60 - vol_expansion * 20)

        predicted_price = current_price + breakout_magnitude

        reasoning = f"Volatility: {volatility:.3f}, ATR: {atr:.2f}, Vol Expansion: {vol_expansion:.2f}x"

        return ForecastResult("Volatility Breakout", predicted_price, confidence, 20, reasoning)

    def support_resistance_model(self, data: Dict) -> ForecastResult:
        """Model 4: Support/resistance level analysis"""
        if not data.get('bars') or len(data['bars']) < 30:
            return ForecastResult("Support Resistance", data.get('current_price', 0), 0, 60, "Insufficient data")

        bars = data['bars'][:30]
        current_price = data['current_price']

        # Find significant highs and lows
        highs = []
        lows = []

        for i in range(2, len(bars)-2):
            # Local high
            if (bars[i]['high'] > bars[i-1]['high'] and bars[i]['high'] > bars[i-2]['high'] and
                bars[i]['high'] > bars[i+1]['high'] and bars[i]['high'] > bars[i+2]['high']):
                highs.append(bars[i]['high'])

            # Local low
            if (bars[i]['low'] < bars[i-1]['low'] and bars[i]['low'] < bars[i-2]['low'] and
                bars[i]['low'] < bars[i+1]['low'] and bars[i]['low'] < bars[i+2]['low']):
                lows.append(bars[i]['low'])

        # Find closest support and resistance
        resistance_levels = [h for h in highs if h > current_price]
        support_levels = [l for l in lows if l < current_price]

        nearest_resistance = min(resistance_levels) if resistance_levels else current_price * 1.02
        nearest_support = max(support_levels) if support_levels else current_price * 0.98

        # Determine likely direction based on position within range
        range_position = (current_price - nearest_support) / (nearest_resistance - nearest_support)

        if range_position > 0.7:  # Near resistance
            predicted_price = nearest_support + (nearest_resistance - nearest_support) * 0.3
            confidence = 70
            direction = "reversion from resistance"
        elif range_position < 0.3:  # Near support
            predicted_price = nearest_support + (nearest_resistance - nearest_support) * 0.7
            confidence = 70
            direction = "bounce from support"
        else:  # Middle of range
            predicted_price = current_price + (nearest_resistance - current_price) * 0.5
            confidence = 50
            direction = "range continuation"

        reasoning = f"Support: {nearest_support:.2f}, Resistance: {nearest_resistance:.2f}, Position: {range_position:.2f}, {direction}"

        return ForecastResult("Support Resistance", predicted_price, confidence, 60, reasoning)

    def volume_price_trend_model(self, data: Dict) -> ForecastResult:
        """Model 5: Volume-price trend analysis"""
        if not data.get('bars') or len(data['bars']) < 15:
            return ForecastResult("Volume Price Trend", data.get('current_price', 0), 0, 25, "Insufficient data")

        bars = data['bars'][:15]
        current_price = data['current_price']

        # Calculate volume trend
        volumes = [bar['volume'] for bar in bars]
        prices = [bar['close'] for bar in bars]

        avg_volume = sum(volumes) / len(volumes)
        recent_volume = sum(volumes[:5]) / 5
        volume_trend = recent_volume / avg_volume

        # Calculate price-volume relationship
        pv_correlations = []
        for i in range(len(bars)-1):
            price_change = (bars[i]['close'] - bars[i+1]['close']) / bars[i+1]['close']
            volume_ratio = bars[i]['volume'] / bars[i+1]['volume']
            pv_correlations.append(price_change * volume_ratio)

        avg_pv_correlation = sum(pv_correlations) / len(pv_correlations)

        # Volume pressure analysis
        up_volume = sum([bars[i]['volume'] for i in range(len(bars)-1)
                        if bars[i]['close'] > bars[i+1]['close']])
        down_volume = sum([bars[i]['volume'] for i in range(len(bars)-1)
                          if bars[i]['close'] < bars[i+1]['close']])

        volume_pressure = (up_volume - down_volume) / (up_volume + down_volume) if (up_volume + down_volume) > 0 else 0

        # Predict based on volume trends
        volume_factor = volume_trend * volume_pressure * 0.005  # Scale factor
        predicted_price = current_price * (1 + volume_factor)

        confidence = min(85, max(40, abs(volume_pressure) * 100 + (volume_trend - 1) * 50))

        reasoning = f"Volume Trend: {volume_trend:.2f}x, Volume Pressure: {volume_pressure:.3f}, PV Corr: {avg_pv_correlation:.3f}"

        return ForecastResult("Volume Price Trend", predicted_price, confidence, 25, reasoning)

    def options_flow_model(self, data: Dict) -> ForecastResult:
        """Model 6: Options flow and sentiment analysis"""
        current_price = data.get('current_price', 0)
        current_rsi = data.get('current_rsi', 50)

        # Simplified options flow analysis (would use real options data in production)
        # Estimate based on RSI extremes and price action

        # Simulate call/put ratio analysis
        if current_rsi > 70:
            call_put_ratio = 0.6  # More puts being bought (bearish)
            options_sentiment = "BEARISH"
            flow_factor = -0.003
        elif current_rsi < 30:
            call_put_ratio = 1.8  # More calls being bought (bullish)
            options_sentiment = "BULLISH"
            flow_factor = 0.003
        else:
            call_put_ratio = 1.0  # Neutral
            options_sentiment = "NEUTRAL"
            flow_factor = 0

        # Predict based on options flow
        predicted_price = current_price * (1 + flow_factor)

        # Confidence based on extremity of signal
        confidence = min(75, max(35, abs(current_rsi - 50) * 1.5))

        reasoning = f"C/P Ratio: {call_put_ratio:.2f}, Sentiment: {options_sentiment}, RSI: {current_rsi:.1f}"

        return ForecastResult("Options Flow", predicted_price, confidence, 40, reasoning)

    def market_microstructure_model(self, data: Dict) -> ForecastResult:
        """Model 7: Market microstructure analysis"""
        if not data.get('bars') or len(data['bars']) < 10:
            return ForecastResult("Market Microstructure", data.get('current_price', 0), 0, 15, "Insufficient data")

        bars = data['bars'][:10]
        current_price = data['current_price']

        # Analyze bid-ask dynamics (simplified using high-low as proxy)
        spreads = [bar['high'] - bar['low'] for bar in bars]
        avg_spread = sum(spreads) / len(spreads)
        current_spread = bars[0]['high'] - bars[0]['low']

        spread_ratio = current_spread / avg_spread if avg_spread > 0 else 1

        # Analyze tick direction (using close relative to high-low)
        tick_directions = []
        for bar in bars:
            midpoint = (bar['high'] + bar['low']) / 2
            tick_direction = 1 if bar['close'] > midpoint else -1
            tick_directions.append(tick_direction)

        net_tick_direction = sum(tick_directions) / len(tick_directions)

        # Order flow imbalance estimation
        volume_weights = [bar['volume'] for bar in bars]
        weighted_tick = sum([tick_directions[i] * volume_weights[i] for i in range(len(bars))]) / sum(volume_weights)

        # Predict short-term movement
        microstructure_factor = weighted_tick * 0.001 * (2 - spread_ratio)  # Lower spread = higher impact
        predicted_price = current_price * (1 + microstructure_factor)

        confidence = min(80, max(45, abs(weighted_tick) * 50 + (2 - spread_ratio) * 25))

        reasoning = f"Weighted Tick: {weighted_tick:.3f}, Spread Ratio: {spread_ratio:.2f}, Net Direction: {net_tick_direction:.2f}"

        return ForecastResult("Market Microstructure", predicted_price, confidence, 15, reasoning)

    def ensemble_meta_model(self, individual_forecasts: List[ForecastResult], data: Dict) -> ForecastResult:
        """Model 8: Meta-model combining all individual forecasts"""
        if not individual_forecasts:
            return ForecastResult("Ensemble Meta", data.get('current_price', 0), 0, 30, "No individual forecasts")

        current_price = data.get('current_price', 0)

        # Weight individual forecasts by their confidence
        total_weighted_price = 0
        total_weights = 0
        confidence_scores = []

        for forecast in individual_forecasts:
            weight = forecast.confidence / 100
            total_weighted_price += forecast.predicted_price * weight
            total_weights += weight
            confidence_scores.append(forecast.confidence)

        # Calculate ensemble prediction
        if total_weights > 0:
            ensemble_price = total_weighted_price / total_weights
        else:
            ensemble_price = current_price

        # Ensemble confidence based on agreement
        price_predictions = [f.predicted_price for f in individual_forecasts]
        prediction_std = np.std(price_predictions) if len(price_predictions) > 1 else 0
        prediction_range = (max(price_predictions) - min(price_predictions)) / current_price * 100

        # High agreement = high confidence
        agreement_confidence = max(50, 90 - prediction_range * 5)
        avg_individual_confidence = sum(confidence_scores) / len(confidence_scores)

        ensemble_confidence = (agreement_confidence * 0.6) + (avg_individual_confidence * 0.4)

        reasoning = f"Agreement: {agreement_confidence:.1f}%, Avg Confidence: {avg_individual_confidence:.1f}%, Range: {prediction_range:.2f}%"

        return ForecastResult("Ensemble Meta", ensemble_price, ensemble_confidence, 30, reasoning)

    def run_full_ensemble_forecast(self, symbol: str = "SPY") -> Dict:
        """Run complete 8-model ensemble forecasting"""
        print(f"Running 8-model ensemble forecast for {symbol}...")

        # Get enhanced market data
        data = self.get_enhanced_market_data(symbol)

        if not data.get('success'):
            return {'success': False, 'error': data.get('error', 'Unknown error'), 'symbol': symbol}

        current_price = data['current_price']

        # Run all individual models
        individual_forecasts = []

        print("Running individual models...")
        individual_forecasts.append(self.momentum_regression_model(data))
        individual_forecasts.append(self.mean_reversion_model(data))
        individual_forecasts.append(self.volatility_breakout_model(data))
        individual_forecasts.append(self.support_resistance_model(data))
        individual_forecasts.append(self.volume_price_trend_model(data))
        individual_forecasts.append(self.options_flow_model(data))
        individual_forecasts.append(self.market_microstructure_model(data))

        # Run ensemble meta-model
        print("Running ensemble meta-model...")
        ensemble_forecast = self.ensemble_meta_model(individual_forecasts, data)

        # Calculate final weighted prediction
        all_forecasts = individual_forecasts + [ensemble_forecast]

        final_weighted_price = 0
        total_weight = 0

        for i, forecast in enumerate(all_forecasts[:-1]):  # Exclude ensemble for weighting
            model_name = forecast.model_name.lower().replace(' ', '_')
            weight = self.model_weights.get(model_name, 0.1)
            confidence_weight = forecast.confidence / 100
            combined_weight = weight * confidence_weight

            final_weighted_price += forecast.predicted_price * combined_weight
            total_weight += combined_weight

        # Add ensemble with its weight
        ensemble_weight = self.model_weights['ensemble_meta'] * (ensemble_forecast.confidence / 100)
        final_weighted_price += ensemble_forecast.predicted_price * ensemble_weight
        total_weight += ensemble_weight

        final_prediction = final_weighted_price / total_weight if total_weight > 0 else current_price

        # Calculate prediction confidence and direction
        price_change = final_prediction - current_price
        price_change_pct = (price_change / current_price) * 100
        direction = "BULLISH" if price_change > 0 else "BEARISH" if price_change < 0 else "NEUTRAL"

        # Overall ensemble confidence
        avg_confidence = sum([f.confidence for f in individual_forecasts]) / len(individual_forecasts)
        ensemble_agreement = ensemble_forecast.confidence
        final_confidence = (avg_confidence * 0.7) + (ensemble_agreement * 0.3)

        return {
            'success': True,
            'symbol': symbol,
            'timestamp': datetime.now().isoformat(),
            'current_price': current_price,
            'predicted_price': final_prediction,
            'price_change': price_change,
            'price_change_pct': price_change_pct,
            'direction': direction,
            'final_confidence': final_confidence,
            'individual_forecasts': [
                {
                    'model': f.model_name,
                    'prediction': f.predicted_price,
                    'confidence': f.confidence,
                    'time_horizon': f.time_horizon,
                    'reasoning': f.reasoning
                }
                for f in individual_forecasts
            ],
            'ensemble_forecast': {
                'model': ensemble_forecast.model_name,
                'prediction': ensemble_forecast.predicted_price,
                'confidence': ensemble_forecast.confidence,
                'reasoning': ensemble_forecast.reasoning
            },
            'model_weights': self.model_weights
        }

    def format_forecast_output(self, forecast_result: Dict) -> str:
        """Format forecast results for display"""
        if not forecast_result.get('success'):
            return f"Forecast Error: {forecast_result.get('error', 'Unknown error')}"

        output = []

        output.append("8-MODEL ENSEMBLE FORECASTING ANALYSIS")
        output.append("=" * 50)
        output.append(f"Symbol: {forecast_result['symbol']}")
        output.append(f"Current Price: ${forecast_result['current_price']:.2f}")
        output.append(f"Predicted Price: ${forecast_result['predicted_price']:.2f}")
        output.append(f"Expected Change: {forecast_result['price_change_pct']:+.2f}% (${forecast_result['price_change']:+.2f})")
        output.append(f"Direction: {forecast_result['direction']}")
        output.append(f"Ensemble Confidence: {forecast_result['final_confidence']:.1f}%")
        output.append("")

        output.append("INDIVIDUAL MODEL PREDICTIONS:")
        output.append("-" * 40)
        for model in forecast_result['individual_forecasts']:
            change_pct = ((model['prediction'] - forecast_result['current_price']) / forecast_result['current_price']) * 100
            output.append(f"{model['model']:20} ${model['prediction']:7.2f} ({change_pct:+5.2f}%) [{model['confidence']:2.0f}%] {model['time_horizon']}min")
            output.append(f"  Logic: {model['reasoning']}")
            output.append("")

        output.append("ENSEMBLE META-MODEL:")
        ensemble = forecast_result['ensemble_forecast']
        ensemble_change_pct = ((ensemble['prediction'] - forecast_result['current_price']) / forecast_result['current_price']) * 100
        output.append(f"{ensemble['model']:20} ${ensemble['prediction']:7.2f} ({ensemble_change_pct:+5.2f}%) [{ensemble['confidence']:2.0f}%]")
        output.append(f"  Logic: {ensemble['reasoning']}")
        output.append("")

        # Trading recommendations
        confidence = forecast_result['final_confidence']
        change_pct = abs(forecast_result['price_change_pct'])

        if confidence >= 75 and change_pct >= 0.5:
            recommendation = "STRONG SIGNAL"
        elif confidence >= 65 and change_pct >= 0.3:
            recommendation = "MODERATE SIGNAL"
        elif confidence >= 55:
            recommendation = "WEAK SIGNAL"
        else:
            recommendation = "NO CLEAR SIGNAL"

        output.append("TRADING RECOMMENDATION:")
        output.append(f"  Signal Strength: {recommendation}")
        output.append(f"  Confidence Threshold: {confidence:.1f}% (Need >65% for consideration)")
        output.append(f"  Expected Move: {change_pct:.2f}% (Need >0.3% for signal)")

        # Save session
        import os
        os.makedirs(os.path.dirname(self.session_file), exist_ok=True)
        with open(self.session_file, 'w') as f:
            json.dump(forecast_result, f, indent=2, default=str)

        output.append("")
        output.append("SESSION UPDATED: Forecast analysis saved to .spx/")

        return "\n".join(output)

def main():
    """Test 8-model ensemble forecasting"""
    forecaster = AdvancedForecastingEngine()

    print("8-MODEL ENSEMBLE FORECASTING SYSTEM")
    print("=" * 45)

    # Run forecast
    result = forecaster.run_full_ensemble_forecast("SPY")
    formatted_output = forecaster.format_forecast_output(result)
    print(formatted_output)

if __name__ == "__main__":
    main()