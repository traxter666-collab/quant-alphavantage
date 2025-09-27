#!/usr/bin/env python3
"""
QQQ Options Integration
Add QQQ option analysis to our unified SPX trading system
"""

import sys
import json
import requests
from datetime import datetime
sys.path.append('.')

def get_qqq_options_data():
    """Get real-time QQQ options data from AlphaVantage"""
    try:
        api_key = 'ZFL38ZY98GSN7E1S'
        url = f'https://www.alphavantage.co/query?function=REALTIME_OPTIONS&symbol=QQQ&apikey={api_key}'

        response = requests.get(url, timeout=15)
        data = response.json()

        if 'data' not in data or len(data['data']) == 0:
            raise Exception("No QQQ options data available")

        options_data = data['data']
        print(f"QQQ Options Retrieved: {len(options_data)} contracts")

        return options_data

    except Exception as e:
        print(f"QQQ options data error: {e}")
        return None

def analyze_qqq_price_and_levels(options_data=None):
    """Analyze QQQ price and key levels"""
    try:
        api_key = 'ZFL38ZY98GSN7E1S'

        # Get QQQ current price
        qqq_url = f'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=QQQ&apikey={api_key}'
        qqq_response = requests.get(qqq_url, timeout=10)
        qqq_data = qqq_response.json()

        if 'Global Quote' not in qqq_data:
            raise Exception("Could not get QQQ price")

        current_qqq = float(qqq_data['Global Quote']['05. price'])
        qqq_change = float(qqq_data['Global Quote']['09. change'])
        qqq_change_pct = qqq_data['Global Quote']['10. change percent'].rstrip('%')

        print(f"QQQ Current: ${current_qqq:.2f} ({qqq_change:+.2f}, {qqq_change_pct}%)")

        # Key QQQ levels (tech-heavy ETF)
        key_levels = {
            'support_levels': [490, 485, 480, 475, 470],
            'resistance_levels': [500, 505, 510, 515, 520],
            'psychological_levels': [475, 500, 525]
        }

        # Find nearest levels
        all_levels = key_levels['support_levels'] + key_levels['resistance_levels']
        level_distances = [(level, abs(current_qqq - level)) for level in all_levels]
        level_distances.sort(key=lambda x: x[1])

        nearest_levels = level_distances[:3]

        print(f"Nearest Key Levels:")
        for level, distance in nearest_levels:
            direction = "above" if current_qqq > level else "below"
            level_type = "resistance" if current_qqq < level else "support"
            print(f"  ${level:.0f}: {distance:.2f} points {direction} ({level_type})")

        return {
            'current_price': current_qqq,
            'change': qqq_change,
            'change_percent': float(qqq_change_pct),
            'key_levels': key_levels,
            'nearest_levels': nearest_levels[:3]
        }

    except Exception as e:
        print(f"QQQ analysis error: {e}")
        return None

def calculate_qqq_consensus_score(qqq_price, qqq_options=None):
    """Calculate consensus score for QQQ similar to SPX methodology"""
    try:
        api_key = 'ZFL38ZY98GSN7E1S'

        # Get QQQ RSI for momentum context
        rsi_url = f'https://www.alphavantage.co/query?function=RSI&symbol=QQQ&interval=5min&time_period=14&series_type=close&apikey={api_key}'
        rsi_response = requests.get(rsi_url, timeout=10)
        rsi_data = rsi_response.json()

        current_rsi = 50  # Default neutral
        if 'Technical Analysis: RSI' in rsi_data:
            rsi_values = list(rsi_data['Technical Analysis: RSI'].values())
            if rsi_values:
                current_rsi = float(list(rsi_values[0].values())[0])

        print(f"QQQ RSI (5min): {current_rsi:.1f}")

        # QQQ-specific consensus scoring (adapted from SPX methodology)
        consensus_components = {}

        # 1. Tech Momentum (25 points) - QQQ is tech-heavy
        if current_rsi > 60:
            tech_momentum = 22
        elif current_rsi > 50:
            tech_momentum = 18
        elif current_rsi > 40:
            tech_momentum = 14
        else:
            tech_momentum = 10
        consensus_components['Tech_Momentum'] = tech_momentum

        # 2. Key Level Proximity (20 points)
        key_levels = [475, 485, 490, 500, 510, 515, 525]
        distances = [abs(qqq_price - level) for level in key_levels]
        min_distance = min(distances)

        if min_distance < 2:
            level_score = 18
        elif min_distance < 5:
            level_score = 15
        elif min_distance < 10:
            level_score = 12
        else:
            level_score = 8
        consensus_components['Level_Proximity'] = level_score

        # 3. Options Flow Analysis (20 points) - simplified
        if qqq_options and len(qqq_options) > 100:
            options_flow = 16  # Good liquidity
        elif qqq_options and len(qqq_options) > 50:
            options_flow = 12  # Moderate liquidity
        else:
            options_flow = 8   # Low liquidity
        consensus_components['Options_Flow'] = options_flow

        # 4. Volatility Assessment (15 points)
        if 30 <= current_rsi <= 70:  # Normal volatility range
            vol_score = 12
        else:  # Extreme readings
            vol_score = 8
        consensus_components['Volatility_Assessment'] = vol_score

        # 5. Trend Strength (15 points)
        if current_rsi > 55:
            trend_score = 13
            trend_direction = 'BULLISH'
        elif current_rsi < 45:
            trend_score = 13
            trend_direction = 'BEARISH'
        else:
            trend_score = 8
            trend_direction = 'NEUTRAL'
        consensus_components['Trend_Strength'] = trend_score

        # 6. Base Technical Score (remaining points to reach ~200 total)
        base_technical = 90  # Conservative base for QQQ
        consensus_components['Base_Technical'] = base_technical

        # Calculate total score
        total_score = sum(consensus_components.values())

        return {
            'total_score': total_score,
            'components': consensus_components,
            'directional_bias': trend_direction,
            'rsi_context': current_rsi,
            'qqq_price': qqq_price
        }

    except Exception as e:
        print(f"QQQ consensus calculation error: {e}")
        # Return conservative default
        return {
            'total_score': 120,  # Conservative default
            'components': {'Error': 'Using default values'},
            'directional_bias': 'NEUTRAL',
            'rsi_context': 50,
            'qqq_price': qqq_price
        }

def find_optimal_qqq_strikes(qqq_price, options_data, directional_bias):
    """Find optimal QQQ option strikes based on analysis"""
    if not options_data:
        return None

    try:
        # Filter options for reasonable strikes (within $20 of current price)
        reasonable_strikes = []
        for option in options_data:
            try:
                strike = float(option['strike'])
                if abs(strike - qqq_price) <= 20:  # Within $20
                    reasonable_strikes.append(option)
            except (ValueError, KeyError):
                continue

        if not reasonable_strikes:
            return None

        # Separate calls and puts
        calls = [opt for opt in reasonable_strikes if opt['type'] == 'call']
        puts = [opt for opt in reasonable_strikes if opt['type'] == 'put']

        # Find ATM and OTM options based on bias
        recommendations = {}

        if directional_bias == 'BULLISH':
            # For bullish bias, look for calls
            atm_calls = [c for c in calls if abs(float(c['strike']) - qqq_price) <= 2]
            otm_calls = [c for c in calls if float(c['strike']) > qqq_price and float(c['strike']) <= qqq_price + 10]

            if atm_calls:
                best_atm = min(atm_calls, key=lambda x: abs(float(x['strike']) - qqq_price))
                recommendations['ATM_Call'] = {
                    'strike': float(best_atm['strike']),
                    'bid': float(best_atm['bid']),
                    'ask': float(best_atm['ask']),
                    'volume': int(best_atm.get('volume', 0)),
                    'open_interest': int(best_atm.get('open_interest', 0))
                }

            if otm_calls:
                best_otm = min(otm_calls, key=lambda x: float(x['strike']) - qqq_price)
                recommendations['OTM_Call'] = {
                    'strike': float(best_otm['strike']),
                    'bid': float(best_otm['bid']),
                    'ask': float(best_otm['ask']),
                    'volume': int(best_otm.get('volume', 0)),
                    'open_interest': int(best_otm.get('open_interest', 0))
                }

        elif directional_bias == 'BEARISH':
            # For bearish bias, look for puts
            atm_puts = [p for p in puts if abs(float(p['strike']) - qqq_price) <= 2]
            otm_puts = [p for p in puts if float(p['strike']) < qqq_price and float(p['strike']) >= qqq_price - 10]

            if atm_puts:
                best_atm = min(atm_puts, key=lambda x: abs(float(x['strike']) - qqq_price))
                recommendations['ATM_Put'] = {
                    'strike': float(best_atm['strike']),
                    'bid': float(best_atm['bid']),
                    'ask': float(best_atm['ask']),
                    'volume': int(best_atm.get('volume', 0)),
                    'open_interest': int(best_atm.get('open_interest', 0))
                }

            if otm_puts:
                best_otm = max(otm_puts, key=lambda x: float(x['strike']))
                recommendations['OTM_Put'] = {
                    'strike': float(best_otm['strike']),
                    'bid': float(best_otm['bid']),
                    'ask': float(best_otm['ask']),
                    'volume': int(best_otm.get('volume', 0)),
                    'open_interest': int(best_otm.get('open_interest', 0))
                }

        return recommendations

    except Exception as e:
        print(f"QQQ strike analysis error: {e}")
        return None

def run_qqq_analysis():
    """Run complete QQQ options analysis"""
    print("QQQ OPTIONS ANALYSIS INTEGRATION")
    print("Adding QQQ to SPX unified trading system")
    print("=" * 60)

    try:
        # Step 1: Get QQQ options data
        print("Step 1: Getting QQQ options data...")
        qqq_options = get_qqq_options_data()

        # Step 2: Analyze QQQ price and levels
        print("\nStep 2: Analyzing QQQ price and levels...")
        qqq_analysis = analyze_qqq_price_and_levels(qqq_options)

        if not qqq_analysis:
            print("ERROR: Could not analyze QQQ")
            return False

        # Step 3: Calculate QQQ consensus score
        print("\nStep 3: Calculating QQQ consensus score...")
        qqq_consensus = calculate_qqq_consensus_score(qqq_analysis['current_price'], qqq_options)

        print(f"QQQ Consensus: {qqq_consensus['total_score']}/195")
        print(f"Directional Bias: {qqq_consensus['directional_bias']}")

        # Apply our optimized thresholds (scaled for QQQ's lower max score)
        qqq_threshold_percentage = (qqq_consensus['total_score'] / 195) * 100

        if qqq_threshold_percentage >= 75:
            qqq_confidence = 'TRADE_WORTHY'
            qqq_action = 'CONSIDER_TRADING'
        elif qqq_threshold_percentage >= 60:
            qqq_confidence = 'MODERATE'
            qqq_action = 'WATCH_CLOSELY'
        else:
            qqq_confidence = 'LOW'
            qqq_action = 'NO_TRADE'

        print(f"QQQ Threshold: {qqq_threshold_percentage:.1f}%")
        print(f"QQQ Confidence: {qqq_confidence}")
        print(f"QQQ Action: {qqq_action}")

        # Step 4: Find optimal strikes
        print("\nStep 4: Finding optimal QQQ strikes...")
        optimal_strikes = find_optimal_qqq_strikes(
            qqq_analysis['current_price'],
            qqq_options,
            qqq_consensus['directional_bias']
        )

        if optimal_strikes:
            print("Optimal QQQ Strikes:")
            for option_type, details in optimal_strikes.items():
                mid_price = (details['bid'] + details['ask']) / 2
                print(f"  {option_type}: ${details['strike']:.0f} @ ${mid_price:.2f}")
                print(f"    Volume: {details['volume']}, OI: {details['open_interest']}")

        # Step 5: Generate QQQ recommendation
        print(f"\n" + "=" * 60)
        print("QQQ TRADING RECOMMENDATION")
        print("=" * 60)

        print(f"QQQ Price: ${qqq_analysis['current_price']:.2f}")
        print(f"Consensus: {qqq_consensus['total_score']}/195 ({qqq_threshold_percentage:.1f}%)")
        print(f"Direction: {qqq_consensus['directional_bias']}")
        print(f"Action: {qqq_action}")

        if qqq_action == 'CONSIDER_TRADING' and optimal_strikes:
            print(f"\nQQQ TRADE SUGGESTIONS:")
            for option_type, details in optimal_strikes.items():
                mid_price = (details['bid'] + details['ask']) / 2
                print(f"  {option_type}: QQQ ${details['strike']:.0f} @ ${mid_price:.2f}")
        else:
            print(f"\nNO QQQ TRADES RECOMMENDED")
            print(f"  Reason: Score {qqq_threshold_percentage:.1f}% below 75% threshold")

        # Save QQQ analysis
        qqq_results = {
            'timestamp': datetime.now().isoformat(),
            'qqq_analysis': qqq_analysis,
            'qqq_consensus': qqq_consensus,
            'threshold_percentage': qqq_threshold_percentage,
            'confidence_level': qqq_confidence,
            'action_recommendation': qqq_action,
            'optimal_strikes': optimal_strikes
        }

        with open('.spx/qqq_analysis_results.json', 'w') as f:
            json.dump(qqq_results, f, indent=2)

        print(f"\nQQQ analysis saved to .spx/qqq_analysis_results.json")

        return True

    except Exception as e:
        print(f"QQQ analysis failed: {e}")
        return False

if __name__ == "__main__":
    print("Starting QQQ Options Integration...")

    success = run_qqq_analysis()

    if success:
        print("\nQQQ INTEGRATION: SUCCESSFUL")
        print("QQQ options analysis ready for trading system")
    else:
        print("\nQQQ INTEGRATION: FAILED")
        print("Check API connectivity and try again")