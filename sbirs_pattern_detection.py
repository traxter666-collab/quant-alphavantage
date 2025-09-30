#!/usr/bin/env python3
"""
SBIRS Pattern Detection System
Smart Breakout/Reversal Signal System using real market data
"""

import requests
import json
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

class SBIRSPatternDetector:
    def __init__(self):
        self.api_key = 'ZFL38ZY98GSN7E1S'
        self.session_file = ".spx/sbirs_session.json"

    def get_intraday_data(self, symbol: str, interval: str = "5min") -> Dict:
        """Get intraday data for pattern analysis"""
        url = f'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval={interval}&apikey={self.api_key}'

        try:
            response = requests.get(url, timeout=15)
            data = response.json()

            if f'Time Series ({interval})' in data:
                time_series = data[f'Time Series ({interval})']

                # Convert to list format
                bars = []
                for timestamp, bar_data in time_series.items():
                    bars.append({
                        'timestamp': datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S'),
                        'open': float(bar_data['1. open']),
                        'high': float(bar_data['2. high']),
                        'low': float(bar_data['3. low']),
                        'close': float(bar_data['4. close']),
                        'volume': int(bar_data['5. volume'])
                    })

                # Sort by timestamp (newest first)
                bars.sort(key=lambda x: x['timestamp'], reverse=True)

                return {
                    'success': True,
                    'symbol': symbol,
                    'interval': interval,
                    'bars': bars[:50]  # Last 50 bars
                }
            else:
                return {'success': False, 'error': 'No time series data', 'data': data}

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def detect_breakout_patterns(self, bars: List[Dict]) -> List[Dict]:
        """Detect breakout patterns (flags, triangles, consolidations)"""
        patterns = []

        if len(bars) < 20:
            return patterns

        # Get recent price action
        recent_highs = [bar['high'] for bar in bars[:10]]
        recent_lows = [bar['low'] for bar in bars[:10]]
        recent_closes = [bar['close'] for bar in bars[:10]]
        recent_volumes = [bar['volume'] for bar in bars[:10]]

        current_price = bars[0]['close']
        avg_volume = sum(recent_volumes[1:]) / len(recent_volumes[1:])

        # Flag Pattern Detection
        flag_pattern = self.detect_flag_pattern(bars)
        if flag_pattern:
            patterns.append(flag_pattern)

        # Triangle Breakout Detection
        triangle_pattern = self.detect_triangle_breakout(bars)
        if triangle_pattern:
            patterns.append(triangle_pattern)

        # Consolidation Breakout
        consolidation_pattern = self.detect_consolidation_breakout(bars)
        if consolidation_pattern:
            patterns.append(consolidation_pattern)

        return patterns

    def detect_flag_pattern(self, bars: List[Dict]) -> Optional[Dict]:
        """Detect bull/bear flag patterns"""
        if len(bars) < 15:
            return None

        # Look for strong move followed by consolidation
        recent_bars = bars[:10]
        setup_bars = bars[10:15]

        # Calculate initial move strength
        setup_high = max([bar['high'] for bar in setup_bars])
        setup_low = min([bar['low'] for bar in setup_bars])
        setup_range = setup_high - setup_low

        # Current consolidation range
        recent_high = max([bar['high'] for bar in recent_bars])
        recent_low = min([bar['low'] for bar in recent_bars])
        recent_range = recent_high - recent_low

        current_price = bars[0]['close']
        current_volume = bars[0]['volume']
        avg_volume = sum([bar['volume'] for bar in recent_bars[1:]]) / 9

        # Bull Flag: Strong up move, tight consolidation, volume surge
        if (setup_high > setup_bars[0]['close'] * 1.015 and  # Strong initial move up
            recent_range < setup_range * 0.5 and            # Tight consolidation
            current_price > recent_high * 0.995 and         # Near highs
            current_volume > avg_volume * 1.5):             # Volume confirmation

            return {
                'type': 'BULL_FLAG_BREAKOUT',
                'confidence': 85,
                'direction': 'BULLISH',
                'entry_price': current_price,
                'target': current_price * 1.02,
                'stop_loss': recent_low * 0.998,
                'pattern_strength': 'HIGH',
                'volume_confirmation': True,
                'breakout_level': recent_high,
                'risk_reward': (current_price * 1.02 - current_price) / (current_price - recent_low * 0.998)
            }

        # Bear Flag: Strong down move, tight consolidation, volume surge
        elif (setup_low < setup_bars[0]['close'] * 0.985 and  # Strong initial move down
              recent_range < setup_range * 0.5 and            # Tight consolidation
              current_price < recent_low * 1.005 and          # Near lows
              current_volume > avg_volume * 1.5):             # Volume confirmation

            return {
                'type': 'BEAR_FLAG_BREAKDOWN',
                'confidence': 85,
                'direction': 'BEARISH',
                'entry_price': current_price,
                'target': current_price * 0.98,
                'stop_loss': recent_high * 1.002,
                'pattern_strength': 'HIGH',
                'volume_confirmation': True,
                'breakdown_level': recent_low,
                'risk_reward': (current_price - current_price * 0.98) / (recent_high * 1.002 - current_price)
            }

        return None

    def detect_triangle_breakout(self, bars: List[Dict]) -> Optional[Dict]:
        """Detect triangle breakout patterns"""
        if len(bars) < 20:
            return None

        # Get triangle formation data
        triangle_bars = bars[:15]
        highs = [bar['high'] for bar in triangle_bars]
        lows = [bar['low'] for bar in triangle_bars]

        # Calculate triangle boundaries (simplified)
        recent_high = max(highs[:5])
        recent_low = min(lows[:5])
        older_high = max(highs[10:])
        older_low = min(lows[10:])

        triangle_range = recent_high - recent_low
        current_price = bars[0]['close']
        current_volume = bars[0]['volume']
        avg_volume = sum([bar['volume'] for bar in triangle_bars[1:]]) / 14

        # Ascending Triangle (resistance at top, rising lows)
        if (abs(recent_high - older_high) < triangle_range * 0.1 and  # Flat resistance
            recent_low > older_low and                               # Rising lows
            current_price > recent_high * 0.999 and                 # Breakout above resistance
            current_volume > avg_volume * 2.0):                     # Strong volume

            return {
                'type': 'ASCENDING_TRIANGLE_BREAKOUT',
                'confidence': 80,
                'direction': 'BULLISH',
                'entry_price': current_price,
                'target': current_price + triangle_range,
                'stop_loss': recent_low * 0.995,
                'pattern_strength': 'MEDIUM',
                'volume_confirmation': True,
                'resistance_level': recent_high
            }

        # Descending Triangle (support at bottom, falling highs)
        elif (abs(recent_low - older_low) < triangle_range * 0.1 and  # Flat support
              recent_high < older_high and                           # Falling highs
              current_price < recent_low * 1.001 and                # Breakdown below support
              current_volume > avg_volume * 2.0):                   # Strong volume

            return {
                'type': 'DESCENDING_TRIANGLE_BREAKDOWN',
                'confidence': 80,
                'direction': 'BEARISH',
                'entry_price': current_price,
                'target': current_price - triangle_range,
                'stop_loss': recent_high * 1.005,
                'pattern_strength': 'MEDIUM',
                'volume_confirmation': True,
                'support_level': recent_low
            }

        return None

    def detect_consolidation_breakout(self, bars: List[Dict]) -> Optional[Dict]:
        """Detect consolidation breakout patterns"""
        if len(bars) < 12:
            return None

        consolidation_bars = bars[:10]
        highs = [bar['high'] for bar in consolidation_bars]
        lows = [bar['low'] for bar in consolidation_bars]

        consolidation_high = max(highs)
        consolidation_low = min(lows)
        consolidation_range = consolidation_high - consolidation_low

        current_price = bars[0]['close']
        current_volume = bars[0]['volume']
        avg_volume = sum([bar['volume'] for bar in consolidation_bars[1:]]) / 9

        # Range must be tight (less than 1% of price)
        if consolidation_range > current_price * 0.01:
            return None

        # Upward breakout
        if (current_price > consolidation_high * 1.001 and
            current_volume > avg_volume * 1.8):

            return {
                'type': 'CONSOLIDATION_BREAKOUT_UP',
                'confidence': 75,
                'direction': 'BULLISH',
                'entry_price': current_price,
                'target': current_price + consolidation_range * 2,
                'stop_loss': consolidation_low * 0.997,
                'pattern_strength': 'MEDIUM',
                'volume_confirmation': True,
                'breakout_level': consolidation_high
            }

        # Downward breakdown
        elif (current_price < consolidation_low * 0.999 and
              current_volume > avg_volume * 1.8):

            return {
                'type': 'CONSOLIDATION_BREAKDOWN',
                'confidence': 75,
                'direction': 'BEARISH',
                'entry_price': current_price,
                'target': current_price - consolidation_range * 2,
                'stop_loss': consolidation_high * 1.003,
                'pattern_strength': 'MEDIUM',
                'volume_confirmation': True,
                'breakdown_level': consolidation_low
            }

        return None

    def detect_reversal_patterns(self, bars: List[Dict]) -> List[Dict]:
        """Detect reversal patterns (double tops/bottoms, head & shoulders)"""
        patterns = []

        if len(bars) < 25:
            return patterns

        # Double Top/Bottom Detection
        double_pattern = self.detect_double_pattern(bars)
        if double_pattern:
            patterns.append(double_pattern)

        # Head & Shoulders Detection
        hs_pattern = self.detect_head_shoulders(bars)
        if hs_pattern:
            patterns.append(hs_pattern)

        return patterns

    def detect_double_pattern(self, bars: List[Dict]) -> Optional[Dict]:
        """Detect double top/bottom patterns"""
        if len(bars) < 20:
            return None

        # Look for two similar highs/lows with valley/peak between
        highs = [bar['high'] for bar in bars[:15]]
        lows = [bar['low'] for bar in bars[:15]]

        current_price = bars[0]['close']
        current_volume = bars[0]['volume']

        # Find potential double top
        max_high = max(highs)
        high_indices = [i for i, h in enumerate(highs) if h > max_high * 0.995]

        if len(high_indices) >= 2:
            first_high_idx = high_indices[-1]  # Most recent
            second_high_idx = high_indices[0]   # Older

            # Check for valley between peaks
            valley_bars = bars[first_high_idx:second_high_idx]
            if valley_bars:
                valley_low = min([bar['low'] for bar in valley_bars])

                # Double top confirmed if breaking valley support
                if (current_price < valley_low * 0.998 and
                    current_volume > sum([bar['volume'] for bar in bars[1:6]]) / 5 * 1.5):

                    return {
                        'type': 'DOUBLE_TOP_BREAKDOWN',
                        'confidence': 82,
                        'direction': 'BEARISH',
                        'entry_price': current_price,
                        'target': current_price - (max_high - valley_low),
                        'stop_loss': valley_low * 1.002,
                        'pattern_strength': 'HIGH',
                        'volume_confirmation': True,
                        'neckline': valley_low
                    }

        # Find potential double bottom
        min_low = min(lows)
        low_indices = [i for i, l in enumerate(lows) if l < min_low * 1.005]

        if len(low_indices) >= 2:
            first_low_idx = low_indices[-1]   # Most recent
            second_low_idx = low_indices[0]   # Older

            # Check for peak between valleys
            peak_bars = bars[first_low_idx:second_low_idx]
            if peak_bars:
                peak_high = max([bar['high'] for bar in peak_bars])

                # Double bottom confirmed if breaking peak resistance
                if (current_price > peak_high * 1.002 and
                    current_volume > sum([bar['volume'] for bar in bars[1:6]]) / 5 * 1.5):

                    return {
                        'type': 'DOUBLE_BOTTOM_BREAKOUT',
                        'confidence': 82,
                        'direction': 'BULLISH',
                        'entry_price': current_price,
                        'target': current_price + (peak_high - min_low),
                        'stop_loss': peak_high * 0.998,
                        'pattern_strength': 'HIGH',
                        'volume_confirmation': True,
                        'neckline': peak_high
                    }

        return None

    def detect_head_shoulders(self, bars: List[Dict]) -> Optional[Dict]:
        """Detect head and shoulders patterns (simplified)"""
        if len(bars) < 25:
            return None

        # Look for three peaks pattern
        highs = [bar['high'] for bar in bars[:20]]
        current_price = bars[0]['close']

        # Find three highest peaks
        sorted_highs = sorted(enumerate(highs), key=lambda x: x[1], reverse=True)[:3]
        sorted_highs.sort(key=lambda x: x[0])  # Sort by time order

        if len(sorted_highs) == 3:
            left_shoulder, head, right_shoulder = sorted_highs

            # Head should be highest, shoulders similar
            if (head[1] > left_shoulder[1] * 1.01 and
                head[1] > right_shoulder[1] * 1.01 and
                abs(left_shoulder[1] - right_shoulder[1]) < head[1] * 0.005):

                # Find neckline (lows between shoulders and head)
                left_valley_bars = bars[left_shoulder[0]:head[0]]
                right_valley_bars = bars[head[0]:right_shoulder[0]]

                if left_valley_bars and right_valley_bars:
                    left_valley = min([bar['low'] for bar in left_valley_bars])
                    right_valley = min([bar['low'] for bar in right_valley_bars])
                    neckline = (left_valley + right_valley) / 2

                    # Breakdown confirmation
                    if current_price < neckline * 0.998:
                        return {
                            'type': 'HEAD_SHOULDERS_BREAKDOWN',
                            'confidence': 85,
                            'direction': 'BEARISH',
                            'entry_price': current_price,
                            'target': current_price - (head[1] - neckline),
                            'stop_loss': neckline * 1.003,
                            'pattern_strength': 'HIGH',
                            'volume_confirmation': True,
                            'neckline': neckline
                        }

        return None

    def run_sbirs_analysis(self, symbol: str = "SPY") -> Dict:
        """Run complete SBIRS analysis"""
        output = {}

        # Get intraday data
        data_result = self.get_intraday_data(symbol)
        if not data_result['success']:
            return {'success': False, 'error': data_result['error']}

        bars = data_result['bars']

        # Detect patterns
        breakout_patterns = self.detect_breakout_patterns(bars)
        reversal_patterns = self.detect_reversal_patterns(bars)

        all_patterns = breakout_patterns + reversal_patterns

        # Sort by confidence
        all_patterns.sort(key=lambda x: x['confidence'], reverse=True)

        # Calculate overall SBIRS score
        if all_patterns:
            max_confidence = max([p['confidence'] for p in all_patterns])
            pattern_count = len(all_patterns)
            sbirs_score = min(100, max_confidence + (pattern_count - 1) * 5)
        else:
            sbirs_score = 0

        return {
            'success': True,
            'symbol': symbol,
            'timestamp': datetime.now().isoformat(),
            'sbirs_score': sbirs_score,
            'pattern_count': len(all_patterns),
            'patterns': all_patterns,
            'recommendation': 'TRADE' if sbirs_score >= 70 else 'MONITOR' if sbirs_score >= 50 else 'AVOID',
            'current_price': bars[0]['close'] if bars else 0
        }

    def format_sbirs_output(self, analysis: Dict) -> str:
        """Format SBIRS analysis for display"""
        if not analysis['success']:
            return f"SBIRS Error: {analysis['error']}"

        output = []

        output.append("SBIRS PATTERN DETECTION ANALYSIS")
        output.append("=" * 40)
        output.append(f"Symbol: {analysis['symbol']}")
        output.append(f"Current Price: ${analysis['current_price']:.2f}")
        output.append(f"SBIRS Score: {analysis['sbirs_score']}/100")
        output.append(f"Recommendation: {analysis['recommendation']}")
        output.append("")

        if analysis['patterns']:
            output.append(f"DETECTED PATTERNS ({analysis['pattern_count']}):")
            output.append("-" * 30)

            for i, pattern in enumerate(analysis['patterns'], 1):
                output.append(f"{i}. {pattern['type']} - {pattern['direction']}")
                output.append(f"   Confidence: {pattern['confidence']}%")
                output.append(f"   Entry: ${pattern['entry_price']:.2f}")
                output.append(f"   Target: ${pattern['target']:.2f}")
                output.append(f"   Stop: ${pattern['stop_loss']:.2f}")
                if 'risk_reward' in pattern:
                    output.append(f"   Risk/Reward: 1:{pattern['risk_reward']:.2f}")
                output.append("")
        else:
            output.append("No significant patterns detected")
            output.append("Market conditions: Range-bound or unclear")

        # Save to session
        import os
        os.makedirs(os.path.dirname(self.session_file), exist_ok=True)
        with open(self.session_file, 'w') as f:
            json.dump(analysis, f, indent=2, default=str)

        output.append("SESSION UPDATED: SBIRS analysis saved to .spx/")

        return "\n".join(output)

def main():
    """Test SBIRS pattern detection"""
    sbirs = SBIRSPatternDetector()

    print("SBIRS PATTERN DETECTION SYSTEM")
    print("=" * 35)

    # Run analysis
    analysis = sbirs.run_sbirs_analysis("SPY")
    result = sbirs.format_sbirs_output(analysis)
    print(result)

if __name__ == "__main__":
    main()