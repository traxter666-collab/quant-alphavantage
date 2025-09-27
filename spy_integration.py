#!/usr/bin/env python3
"""
SPY + IWM Options Integration
Complete the multi-asset trading system by adding SPY and IWM as additional assets
"""

import sys
import json
import requests
from datetime import datetime
sys.path.append('.')

def get_spy_options_data():
    """Get real-time SPY options data from AlphaVantage"""
    try:
        api_key = 'ZFL38ZY98GSN7E1S'
        url = f'https://www.alphavantage.co/query?function=REALTIME_OPTIONS&symbol=SPY&apikey={api_key}'

        response = requests.get(url, timeout=15)
        data = response.json()

        if 'data' not in data or len(data['data']) == 0:
            raise Exception("No SPY options data available")

        options_data = data['data']
        print(f"SPY Options Retrieved: {len(options_data)} contracts")

        return options_data

    except Exception as e:
        print(f"SPY options data error: {e}")
        return None

def analyze_spy_price_and_levels():
    """Analyze SPY price and key levels"""
    try:
        api_key = 'ZFL38ZY98GSN7E1S'

        # Get SPY current price
        spy_url = f'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=SPY&apikey={api_key}'
        spy_response = requests.get(spy_url, timeout=10)
        spy_data = spy_response.json()

        if 'Global Quote' not in spy_data:
            raise Exception("Could not get SPY price")

        current_spy = float(spy_data['Global Quote']['05. price'])
        spy_change = float(spy_data['Global Quote']['09. change'])
        spy_change_pct = spy_data['Global Quote']['10. change percent'].rstrip('%')

        print(f"SPY Current: ${current_spy:.2f} ({spy_change:+.2f}, {spy_change_pct}%)")

        # Key SPY levels (broad market ETF)
        key_levels = {
            'support_levels': [650, 655, 660, 665, 670],
            'resistance_levels': [675, 680, 685, 690, 695],
            'psychological_levels': [650, 675, 700]
        }

        # Find nearest levels
        all_levels = key_levels['support_levels'] + key_levels['resistance_levels']
        level_distances = [(level, abs(current_spy - level)) for level in all_levels]
        level_distances.sort(key=lambda x: x[1])

        nearest_levels = level_distances[:3]

        print(f"Nearest Key Levels:")
        for level, distance in nearest_levels:
            direction = "above" if current_spy > level else "below"
            level_type = "resistance" if current_spy < level else "support"
            print(f"  ${level:.0f}: {distance:.2f} points {direction} ({level_type})")

        return {
            'current_price': current_spy,
            'change': spy_change,
            'change_percent': float(spy_change_pct),
            'key_levels': key_levels,
            'nearest_levels': nearest_levels[:3]
        }

    except Exception as e:
        print(f"SPY analysis error: {e}")
        return None

def calculate_spy_consensus_score(spy_price, spy_options=None):
    """Calculate consensus score for SPY similar to SPX/QQQ methodology"""
    try:
        api_key = 'ZFL38ZY98GSN7E1S'

        # Get SPY RSI for momentum context
        rsi_url = f'https://www.alphavantage.co/query?function=RSI&symbol=SPY&interval=5min&time_period=14&series_type=close&apikey={api_key}'
        rsi_response = requests.get(rsi_url, timeout=10)
        rsi_data = rsi_response.json()

        current_rsi = 50  # Default neutral
        if 'Technical Analysis: RSI' in rsi_data:
            rsi_values = list(rsi_data['Technical Analysis: RSI'].values())
            if rsi_values:
                current_rsi = float(list(rsi_values[0].values())[0])

        print(f"SPY RSI (5min): {current_rsi:.1f}")

        # SPY-specific consensus scoring (broad market methodology)
        consensus_components = {}

        # 1. Broad Market Momentum (30 points) - SPY represents entire market
        if current_rsi > 60:
            market_momentum = 26
        elif current_rsi > 50:
            market_momentum = 22
        elif current_rsi > 40:
            market_momentum = 16
        else:
            market_momentum = 12
        consensus_components['Market_Momentum'] = market_momentum

        # 2. Key Level Proximity (25 points)
        key_levels = [650, 655, 660, 665, 670, 675, 680, 685, 690, 695]
        distances = [abs(spy_price - level) for level in key_levels]
        min_distance = min(distances)

        if min_distance < 1:
            level_score = 22
        elif min_distance < 2.5:
            level_score = 18
        elif min_distance < 5:
            level_score = 14
        else:
            level_score = 10
        consensus_components['Level_Proximity'] = level_score

        # 3. Options Activity Analysis (25 points)
        if spy_options and len(spy_options) > 500:
            options_flow = 22  # Excellent liquidity
        elif spy_options and len(spy_options) > 250:
            options_flow = 18  # Good liquidity
        elif spy_options and len(spy_options) > 100:
            options_flow = 14  # Moderate liquidity
        else:
            options_flow = 10  # Lower liquidity
        consensus_components['Options_Activity'] = options_flow

        # 4. Broad Market Stability (20 points)
        if 35 <= current_rsi <= 65:  # Stable market range
            stability_score = 16
        elif 30 <= current_rsi <= 70:  # Moderately stable
            stability_score = 12
        else:  # Extreme readings
            stability_score = 8
        consensus_components['Market_Stability'] = stability_score

        # 5. Trend Consistency (20 points)
        if current_rsi > 55:
            trend_score = 17
            trend_direction = 'BULLISH'
        elif current_rsi < 45:
            trend_score = 17
            trend_direction = 'BEARISH'
        else:
            trend_score = 10
            trend_direction = 'NEUTRAL'
        consensus_components['Trend_Consistency'] = trend_score

        # 6. Base Technical Score (remaining points to reach ~220 total)
        base_technical = 100  # Higher base for SPY (most liquid ETF)
        consensus_components['Base_Technical'] = base_technical

        # Calculate total score
        total_score = sum(consensus_components.values())

        return {
            'total_score': total_score,
            'components': consensus_components,
            'directional_bias': trend_direction,
            'rsi_context': current_rsi,
            'spy_price': spy_price
        }

    except Exception as e:
        print(f"SPY consensus calculation error: {e}")
        # Return conservative default
        return {
            'total_score': 140,  # Conservative default
            'components': {'Error': 'Using default values'},
            'directional_bias': 'NEUTRAL',
            'rsi_context': 50,
            'spy_price': spy_price
        }

def find_optimal_spy_strikes(spy_price, options_data, directional_bias):
    """Find optimal SPY option strikes based on analysis"""
    if not options_data:
        return None

    try:
        # Filter options for reasonable strikes (within $10 of current price)
        reasonable_strikes = []
        for option in options_data:
            try:
                strike = float(option['strike'])
                if abs(strike - spy_price) <= 10:  # Within $10
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
            atm_calls = [c for c in calls if abs(float(c['strike']) - spy_price) <= 1]
            otm_calls = [c for c in calls if float(c['strike']) > spy_price and float(c['strike']) <= spy_price + 5]

            if atm_calls:
                best_atm = min(atm_calls, key=lambda x: abs(float(x['strike']) - spy_price))
                recommendations['ATM_Call'] = {
                    'strike': float(best_atm['strike']),
                    'bid': float(best_atm['bid']),
                    'ask': float(best_atm['ask']),
                    'volume': int(best_atm.get('volume', 0)),
                    'open_interest': int(best_atm.get('open_interest', 0))
                }

            if otm_calls:
                best_otm = min(otm_calls, key=lambda x: float(x['strike']) - spy_price)
                recommendations['OTM_Call'] = {
                    'strike': float(best_otm['strike']),
                    'bid': float(best_otm['bid']),
                    'ask': float(best_otm['ask']),
                    'volume': int(best_otm.get('volume', 0)),
                    'open_interest': int(best_otm.get('open_interest', 0))
                }

        elif directional_bias == 'BEARISH':
            # For bearish bias, look for puts
            atm_puts = [p for p in puts if abs(float(p['strike']) - spy_price) <= 1]
            otm_puts = [p for p in puts if float(p['strike']) < spy_price and float(p['strike']) >= spy_price - 5]

            if atm_puts:
                best_atm = min(atm_puts, key=lambda x: abs(float(x['strike']) - spy_price))
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
        print(f"SPY strike analysis error: {e}")
        return None

def run_spy_analysis():
    """Run complete SPY options analysis"""
    print("SPY OPTIONS ANALYSIS INTEGRATION")
    print("Adding SPY to multi-asset trading system")
    print("=" * 60)

    try:
        # Step 1: Get SPY options data
        print("Step 1: Getting SPY options data...")
        spy_options = get_spy_options_data()

        # Step 2: Analyze SPY price and levels
        print("\nStep 2: Analyzing SPY price and levels...")
        spy_analysis = analyze_spy_price_and_levels()

        if not spy_analysis:
            print("ERROR: Could not analyze SPY")
            return False

        # Step 3: Calculate SPY consensus score
        print("\nStep 3: Calculating SPY consensus score...")
        spy_consensus = calculate_spy_consensus_score(spy_analysis['current_price'], spy_options)

        print(f"SPY Consensus: {spy_consensus['total_score']}/220")
        print(f"Directional Bias: {spy_consensus['directional_bias']}")

        # Apply optimized thresholds (scaled for SPY's higher max score)
        spy_threshold_percentage = (spy_consensus['total_score'] / 220) * 100

        if spy_threshold_percentage >= 75:
            spy_confidence = 'TRADE_WORTHY'
            spy_action = 'CONSIDER_TRADING'
        elif spy_threshold_percentage >= 60:
            spy_confidence = 'MODERATE'
            spy_action = 'WATCH_CLOSELY'
        else:
            spy_confidence = 'LOW'
            spy_action = 'NO_TRADE'

        print(f"SPY Threshold: {spy_threshold_percentage:.1f}%")
        print(f"SPY Confidence: {spy_confidence}")
        print(f"SPY Action: {spy_action}")

        # Step 4: Find optimal strikes
        print("\nStep 4: Finding optimal SPY strikes...")
        optimal_strikes = find_optimal_spy_strikes(
            spy_analysis['current_price'],
            spy_options,
            spy_consensus['directional_bias']
        )

        if optimal_strikes:
            print("Optimal SPY Strikes:")
            for option_type, details in optimal_strikes.items():
                mid_price = (details['bid'] + details['ask']) / 2
                print(f"  {option_type}: ${details['strike']:.0f} @ ${mid_price:.2f}")
                print(f"    Volume: {details['volume']}, OI: {details['open_interest']}")

        # Step 5: Generate SPY recommendation
        print(f"\n" + "=" * 60)
        print("SPY TRADING RECOMMENDATION")
        print("=" * 60)

        print(f"SPY Price: ${spy_analysis['current_price']:.2f}")
        print(f"Consensus: {spy_consensus['total_score']}/220 ({spy_threshold_percentage:.1f}%)")
        print(f"Direction: {spy_consensus['directional_bias']}")
        print(f"Action: {spy_action}")

        if spy_action == 'CONSIDER_TRADING' and optimal_strikes:
            print(f"\nSPY TRADE SUGGESTIONS:")
            for option_type, details in optimal_strikes.items():
                mid_price = (details['bid'] + details['ask']) / 2
                print(f"  {option_type}: SPY ${details['strike']:.0f} @ ${mid_price:.2f}")
        else:
            print(f"\nNO SPY TRADES RECOMMENDED")
            print(f"  Reason: Score {spy_threshold_percentage:.1f}% below 75% threshold")

        # Save SPY analysis
        spy_results = {
            'timestamp': datetime.now().isoformat(),
            'spy_analysis': spy_analysis,
            'spy_consensus': spy_consensus,
            'threshold_percentage': spy_threshold_percentage,
            'confidence_level': spy_confidence,
            'action_recommendation': spy_action,
            'optimal_strikes': optimal_strikes
        }

        with open('.spx/spy_analysis_results.json', 'w') as f:
            json.dump(spy_results, f, indent=2)

        print(f"\nSPY analysis saved to .spx/spy_analysis_results.json")

        return True

    except Exception as e:
        print(f"SPY analysis failed: {e}")
        return False

if __name__ == "__main__":
    print("Starting SPY Options Integration...")

    success = run_spy_analysis()

    if success:
        print("\nSPY INTEGRATION: SUCCESSFUL")
        print("SPY options analysis ready for multi-asset trading system")
    else:
        print("\nSPY INTEGRATION: FAILED")
        print("Check API connectivity and try again")

def get_iwm_options_data():
    """Get real-time IWM options data from AlphaVantage"""
    try:
        api_key = 'ZFL38ZY98GSN7E1S'
        url = f'https://www.alphavantage.co/query?function=REALTIME_OPTIONS&symbol=IWM&apikey={api_key}'

        response = requests.get(url, timeout=15)
        data = response.json()

        if 'data' not in data or len(data['data']) == 0:
            raise Exception("No IWM options data available")

        options_data = data['data']
        print(f"IWM Options Retrieved: {len(options_data)} contracts")

        return options_data

    except Exception as e:
        print(f"IWM options data error: {e}")
        return None

def analyze_iwm_price_and_levels():
    """Analyze IWM price and key levels"""
    try:
        api_key = 'ZFL38ZY98GSN7E1S'

        # Get IWM current price
        iwm_url = f'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=IWM&apikey={api_key}'
        iwm_response = requests.get(iwm_url, timeout=10)
        iwm_data = iwm_response.json()

        if 'Global Quote' not in iwm_data:
            raise Exception("Could not get IWM price")

        current_iwm = float(iwm_data['Global Quote']['05. price'])
        iwm_change = float(iwm_data['Global Quote']['09. change'])
        iwm_change_pct = iwm_data['Global Quote']['10. change percent'].rstrip('%')

        print(f"IWM Current: ${current_iwm:.2f} ({iwm_change:+.2f}, {iwm_change_pct}%)")

        # Key IWM levels (small-cap ETF)
        key_levels = {
            'support_levels': [210, 215, 220, 225, 230],
            'resistance_levels': [235, 240, 245, 250, 255],
            'psychological_levels': [220, 240, 260]
        }

        # Find nearest levels
        all_levels = key_levels['support_levels'] + key_levels['resistance_levels']
        level_distances = [(level, abs(current_iwm - level)) for level in all_levels]
        level_distances.sort(key=lambda x: x[1])

        nearest_levels = level_distances[:3]

        print(f"Nearest Key Levels:")
        for level, distance in nearest_levels:
            direction = "above" if current_iwm > level else "below"
            level_type = "resistance" if current_iwm < level else "support"
            print(f"  ${level:.0f}: {distance:.2f} points {direction} ({level_type})")

        return {
            'current_price': current_iwm,
            'change': iwm_change,
            'change_percent': float(iwm_change_pct),
            'key_levels': key_levels,
            'nearest_levels': nearest_levels[:3]
        }

    except Exception as e:
        print(f"IWM analysis error: {e}")
        return None

def calculate_iwm_consensus_score(iwm_price, iwm_options=None):
    """Calculate consensus score for IWM similar to other assets"""
    try:
        api_key = 'ZFL38ZY98GSN7E1S'

        # Get IWM RSI for momentum context
        rsi_url = f'https://www.alphavantage.co/query?function=RSI&symbol=IWM&interval=5min&time_period=14&series_type=close&apikey={api_key}'
        rsi_response = requests.get(rsi_url, timeout=10)
        rsi_data = rsi_response.json()

        current_rsi = 50  # Default neutral
        if 'Technical Analysis: RSI' in rsi_data:
            rsi_values = list(rsi_data['Technical Analysis: RSI'].values())
            if rsi_values:
                current_rsi = float(list(rsi_values[0].values())[0])

        print(f"IWM RSI (5min): {current_rsi:.1f}")

        # IWM-specific consensus scoring (small-cap methodology)
        consensus_components = {}

        # 1. Small-Cap Momentum (25 points) - IWM represents small-cap risk appetite
        if current_rsi > 60:
            smallcap_momentum = 22
        elif current_rsi > 50:
            smallcap_momentum = 18
        elif current_rsi > 40:
            smallcap_momentum = 14
        else:
            smallcap_momentum = 10
        consensus_components['SmallCap_Momentum'] = smallcap_momentum

        # 2. Key Level Proximity (20 points)
        key_levels = [210, 215, 220, 225, 230, 235, 240, 245, 250, 255]
        distances = [abs(iwm_price - level) for level in key_levels]
        min_distance = min(distances)

        if min_distance < 1:
            level_score = 18
        elif min_distance < 2.5:
            level_score = 15
        elif min_distance < 5:
            level_score = 12
        else:
            level_score = 8
        consensus_components['Level_Proximity'] = level_score

        # 3. Options Activity Analysis (20 points)
        if iwm_options and len(iwm_options) > 300:
            options_flow = 18  # Good liquidity for small-cap
        elif iwm_options and len(iwm_options) > 150:
            options_flow = 14  # Moderate liquidity
        elif iwm_options and len(iwm_options) > 50:
            options_flow = 10  # Lower liquidity
        else:
            options_flow = 6   # Minimal liquidity
        consensus_components['Options_Activity'] = options_flow

        # 4. Risk Appetite Assessment (15 points)
        if 35 <= current_rsi <= 65:  # Normal risk appetite
            risk_score = 12
        elif 30 <= current_rsi <= 70:  # Moderate risk appetite
            risk_score = 9
        else:  # Extreme readings
            risk_score = 6
        consensus_components['Risk_Appetite'] = risk_score

        # 5. Trend Consistency (15 points)
        if current_rsi > 55:
            trend_score = 13
            trend_direction = 'BULLISH'
        elif current_rsi < 45:
            trend_score = 13
            trend_direction = 'BEARISH'
        else:
            trend_score = 7
            trend_direction = 'NEUTRAL'
        consensus_components['Trend_Consistency'] = trend_score

        # 6. Base Technical Score (remaining points to reach ~200 total)
        base_technical = 85  # Conservative base for IWM (more volatile)
        consensus_components['Base_Technical'] = base_technical

        # Calculate total score
        total_score = sum(consensus_components.values())

        return {
            'total_score': total_score,
            'components': consensus_components,
            'directional_bias': trend_direction,
            'rsi_context': current_rsi,
            'iwm_price': iwm_price
        }

    except Exception as e:
        print(f"IWM consensus calculation error: {e}")
        # Return conservative default
        return {
            'total_score': 120,  # Conservative default
            'components': {'Error': 'Using default values'},
            'directional_bias': 'NEUTRAL',
            'rsi_context': 50,
            'iwm_price': iwm_price
        }

def find_optimal_iwm_strikes(iwm_price, options_data, directional_bias):
    """Find optimal IWM option strikes based on analysis"""
    if not options_data:
        return None

    try:
        # Filter options for reasonable strikes (within $15 of current price)
        reasonable_strikes = []
        for option in options_data:
            try:
                strike = float(option['strike'])
                if abs(strike - iwm_price) <= 15:  # Within $15
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
            atm_calls = [c for c in calls if abs(float(c['strike']) - iwm_price) <= 2]
            otm_calls = [c for c in calls if float(c['strike']) > iwm_price and float(c['strike']) <= iwm_price + 8]

            if atm_calls:
                best_atm = min(atm_calls, key=lambda x: abs(float(x['strike']) - iwm_price))
                recommendations['ATM_Call'] = {
                    'strike': float(best_atm['strike']),
                    'bid': float(best_atm['bid']),
                    'ask': float(best_atm['ask']),
                    'volume': int(best_atm.get('volume', 0)),
                    'open_interest': int(best_atm.get('open_interest', 0))
                }

            if otm_calls:
                best_otm = min(otm_calls, key=lambda x: float(x['strike']) - iwm_price)
                recommendations['OTM_Call'] = {
                    'strike': float(best_otm['strike']),
                    'bid': float(best_otm['bid']),
                    'ask': float(best_otm['ask']),
                    'volume': int(best_otm.get('volume', 0)),
                    'open_interest': int(best_otm.get('open_interest', 0))
                }

        elif directional_bias == 'BEARISH':
            # For bearish bias, look for puts
            atm_puts = [p for p in puts if abs(float(p['strike']) - iwm_price) <= 2]
            otm_puts = [p for p in puts if float(p['strike']) < iwm_price and float(p['strike']) >= iwm_price - 8]

            if atm_puts:
                best_atm = min(atm_puts, key=lambda x: abs(float(x['strike']) - iwm_price))
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
        print(f"IWM strike analysis error: {e}")
        return None

def run_iwm_analysis():
    """Run complete IWM options analysis"""
    print("IWM OPTIONS ANALYSIS INTEGRATION")
    print("Adding IWM to multi-asset trading system")
    print("=" * 60)

    try:
        # Step 1: Get IWM options data
        print("Step 1: Getting IWM options data...")
        iwm_options = get_iwm_options_data()

        # Step 2: Analyze IWM price and levels
        print("\nStep 2: Analyzing IWM price and levels...")
        iwm_analysis = analyze_iwm_price_and_levels()

        if not iwm_analysis:
            print("ERROR: Could not analyze IWM")
            return False

        # Step 3: Calculate IWM consensus score
        print("\nStep 3: Calculating IWM consensus score...")
        iwm_consensus = calculate_iwm_consensus_score(iwm_analysis['current_price'], iwm_options)

        print(f"IWM Consensus: {iwm_consensus['total_score']}/200")
        print(f"Directional Bias: {iwm_consensus['directional_bias']}")

        # Apply optimized thresholds (scaled for IWM's 200 max score)
        iwm_threshold_percentage = (iwm_consensus['total_score'] / 200) * 100

        if iwm_threshold_percentage >= 75:
            iwm_confidence = 'TRADE_WORTHY'
            iwm_action = 'CONSIDER_TRADING'
        elif iwm_threshold_percentage >= 60:
            iwm_confidence = 'MODERATE'
            iwm_action = 'WATCH_CLOSELY'
        else:
            iwm_confidence = 'LOW'
            iwm_action = 'NO_TRADE'

        print(f"IWM Threshold: {iwm_threshold_percentage:.1f}%")
        print(f"IWM Confidence: {iwm_confidence}")
        print(f"IWM Action: {iwm_action}")

        # Step 4: Find optimal strikes
        print("\nStep 4: Finding optimal IWM strikes...")
        optimal_strikes = find_optimal_iwm_strikes(
            iwm_analysis['current_price'],
            iwm_options,
            iwm_consensus['directional_bias']
        )

        if optimal_strikes:
            print("Optimal IWM Strikes:")
            for option_type, details in optimal_strikes.items():
                mid_price = (details['bid'] + details['ask']) / 2
                print(f"  {option_type}: ${details['strike']:.0f} @ ${mid_price:.2f}")
                print(f"    Volume: {details['volume']}, OI: {details['open_interest']}")

        # Step 5: Generate IWM recommendation
        print(f"\n" + "=" * 60)
        print("IWM TRADING RECOMMENDATION")
        print("=" * 60)

        print(f"IWM Price: ${iwm_analysis['current_price']:.2f}")
        print(f"Consensus: {iwm_consensus['total_score']}/200 ({iwm_threshold_percentage:.1f}%)")
        print(f"Direction: {iwm_consensus['directional_bias']}")
        print(f"Action: {iwm_action}")

        if iwm_action == 'CONSIDER_TRADING' and optimal_strikes:
            print(f"\nIWM TRADE SUGGESTIONS:")
            for option_type, details in optimal_strikes.items():
                mid_price = (details['bid'] + details['ask']) / 2
                print(f"  {option_type}: IWM ${details['strike']:.0f} @ ${mid_price:.2f}")
        else:
            print(f"\nNO IWM TRADES RECOMMENDED")
            print(f"  Reason: Score {iwm_threshold_percentage:.1f}% below 75% threshold")

        # Save IWM analysis
        iwm_results = {
            'timestamp': datetime.now().isoformat(),
            'iwm_analysis': iwm_analysis,
            'iwm_consensus': iwm_consensus,
            'threshold_percentage': iwm_threshold_percentage,
            'confidence_level': iwm_confidence,
            'action_recommendation': iwm_action,
            'optimal_strikes': optimal_strikes
        }

        with open('.spx/iwm_analysis_results.json', 'w') as f:
            json.dump(iwm_results, f, indent=2)

        print(f"\nIWM analysis saved to .spx/iwm_analysis_results.json")

        return True

    except Exception as e:
        print(f"IWM analysis failed: {e}")
        return False