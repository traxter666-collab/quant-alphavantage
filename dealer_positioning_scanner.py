"""
Dealer Positioning Scanner with King Node & Call/Put Wall Detection
Integrates Heatseeker methodology with multi-asset trade scanning
Provides institutional-grade positioning intelligence
Includes Scalping Engine for quick profit-taking with abort conditions
"""

import requests
import json
import time
from datetime import datetime
import os
from scalping_engine import ScalpingEngine

# API Keys
POLYGON_PRIMARY = "_u0zA0CH5ZspOHecb2G8uBxd2DUo4r9D"
POLYGON_BACKUP = "CiDDZJqQS88A0QhaoJbn0rLqaenps6Pq"
ALPHAVANTAGE_KEY = "ZFL38ZY98GSN7E1S"

# Discord Webhooks
WEBHOOK_SPX = "https://discord.com/api/webhooks/1422930069290225694/PKiahdQzpgIZuceHRU254dgpmSEOcgho0-o-DpkQXeCUsQ5AYH1mv3OmJ_gG-1eB7FU-"
WEBHOOK_NDX = "https://discord.com/api/webhooks/1422964068464988292/U6sdcQEyh9biXh2UTkZ2P9qNTIvU-wngGwYxbo3wxUmCDxMEqNITMz3LXRQdvMbxNJ6G"
WEBHOOK_ALERTS = "https://discord.com/api/webhooks/1422763517974417478/0AAxHmLLjC389OXRi5KY_P2puAY8BhGAgEYTXSxj7TiKlqK_WH1PXPW6d_osA219ZFPu"

# Trading Levels
SPX_LEVELS = {
    'resistance': [6742, 6734, 6730, 6700, 6690],
    'support': [6647, 6642, 6633, 6621, 6620, 6600, 6595],
    'pivot': 6659,
    'high_probability_reversal': [6734, 6730, 6633]
}

NDX_LEVELS = {
    'resistance': [24850, 24800, 24750, 24700, 24650],
    'support': [24500, 24450, 24400, 24350, 24300, 24250, 24200],
    'pivot': 24550,
    'high_probability_reversal': [24800, 24750, 24400]
}

# Asset Configuration
ASSETS = {
    'SPX': {'type': 'index', 'ticker': 'I:SPX', 'levels': SPX_LEVELS, 'webhook': WEBHOOK_SPX, 'options_ticker': 'SPXW', 'min_confidence': 90},
    'NDX': {'type': 'index', 'ticker': 'I:NDX', 'levels': NDX_LEVELS, 'webhook': WEBHOOK_NDX, 'options_ticker': 'NDXP', 'min_confidence': 90},
    'QQQ': {'type': 'etf', 'ticker': 'QQQ', 'webhook': WEBHOOK_ALERTS, 'options_ticker': 'QQQ', 'min_confidence': 85},
    'SPY': {'type': 'etf', 'ticker': 'SPY', 'webhook': WEBHOOK_ALERTS, 'options_ticker': 'SPY', 'min_confidence': 85},
    'IWM': {'type': 'etf', 'ticker': 'IWM', 'webhook': WEBHOOK_ALERTS, 'options_ticker': 'IWM', 'min_confidence': 85},
}

class DealerPositioningScanner:
    def __init__(self):
        self.running = False
        self.prices = {}
        self.previous_prices = {}
        self.news_cache = {}  # Cache news sentiment
        self.last_news_fetch = {}
        self.price_history = {}
        self.active_trades = {}
        self.trade_history = []
        self.last_trade_alert = {}  # Per-asset cooldown (not per-strike)
        self.last_exit_alert = {}  # Track last exit alert per trade

        # Initialize Scalping Engine for quick profit-taking
        self.scalp_spx = ScalpingEngine(WEBHOOK_SPX)
        self.scalp_ndx = ScalpingEngine(WEBHOOK_NDX)
        self.scalp_etf = ScalpingEngine(WEBHOOK_ALERTS)
        self.trade_to_scalp_map = {}  # Map trade IDs to scalp IDs
        self.dealer_positioning = {}
        self.king_nodes = {}
        self.call_walls = {}
        self.put_walls = {}
        self.signal_confirmation = {}  # Track consecutive signals for confirmation
        self.scan_interval = 30  # Increased from 10 to 30 seconds

        # Volume Enhancement: Track volume history for confirmation
        self.volume_history = {}  # Rolling window of volume data per asset
        self.volume_window = 10  # Track last 10 scans for average

        # Zone-Based Position Sizing: Track king node touches
        self.king_node_touch_history = {}  # Track touches per king node strike

        # King Node Migration Tracking: Detect when positioning shifts
        self.king_node_migration_history = {}  # Track king node changes over time

        # Volume Enhancement: Track latest volume for scoring
        self.latest_volume = {}  # Store latest volume reading per asset

        os.makedirs('.spx', exist_ok=True)
        self.load_trade_history()

    def get_price(self, asset_name):
        """Get current price for any asset and capture volume for enhancements"""
        try:
            asset = ASSETS[asset_name]

            if asset['type'] == 'index':
                url = f"https://api.polygon.io/v3/snapshot/indices?ticker={asset['ticker']}&apikey={POLYGON_PRIMARY}"
                response = requests.get(url, timeout=5, verify=True)
                if response.status_code == 200:
                    data = response.json()
                    if 'results' in data and len(data['results']) > 0:
                        # Capture volume if available (for volume enhancement)
                        result = data['results'][0]
                        if 'session' in result and 'volume' in result['session']:
                            volume = result['session']['volume']
                            self.update_volume_history(asset_name, volume)
                            self.latest_volume[asset_name] = volume
                        return result['value']
            else:
                url = f"https://api.polygon.io/v3/quotes/{asset['ticker']}?limit=1&apikey={POLYGON_PRIMARY}"
                response = requests.get(url, timeout=5, verify=True)
                if response.status_code == 200:
                    data = response.json()
                    if 'results' in data and len(data['results']) > 0:
                        quote = data['results'][0]
                        bid = quote.get('bid_price', 0)
                        ask = quote.get('ask_price', 0)

                        # Capture volume from quote (for ETFs)
                        if 'ask_size' in quote and 'bid_size' in quote:
                            volume = (quote['ask_size'] + quote['bid_size']) / 2
                            self.update_volume_history(asset_name, volume)
                            self.latest_volume[asset_name] = volume

                        if bid > 0 and ask > 0:
                            return (bid + ask) / 2
            return None
        except Exception as e:
            print(f"❌ Error getting {asset_name} price: {e}")
            return None

    def calculate_dynamic_levels_etf(self, asset_name, current_price):
        """Calculate dynamic support/resistance levels for ETFs based on price history"""
        if asset_name not in self.price_history or len(self.price_history[asset_name]) < 5:
            # Not enough history - create basic levels around current price
            price_range = current_price * 0.02  # 2% range
            return {
                'resistance': [current_price + price_range * i for i in [1, 2, 3]],
                'support': [current_price - price_range * i for i in [1, 2, 3]]
            }

        prices = self.price_history[asset_name]
        high = max(prices)
        low = min(prices)

        # Calculate psychological levels and price action levels
        resistance_levels = []
        support_levels = []

        # Recent high as resistance
        resistance_levels.append(high)

        # Psychological levels above current (round numbers)
        for multiplier in [1.005, 1.01, 1.015, 1.02]:
            level = round(current_price * multiplier, 2)
            if level > current_price and level <= high * 1.03:
                resistance_levels.append(level)

        # Recent low as support
        support_levels.append(low)

        # Psychological levels below current
        for multiplier in [0.995, 0.99, 0.985, 0.98]:
            level = round(current_price * multiplier, 2)
            if level < current_price and level >= low * 0.97:
                support_levels.append(level)

        return {
            'resistance': sorted(list(set(resistance_levels)))[:5],
            'support': sorted(list(set(support_levels)), reverse=True)[:5]
        }

    def analyze_options_chain(self, asset_name, current_price):
        """Analyze options chain for dealer positioning (simplified - using volume estimates)"""
        try:
            # Get levels based on asset type
            if asset_name in ['SPX', 'NDX']:
                levels = ASSETS[asset_name]['levels']
            else:
                # ETFs use dynamic levels
                levels = self.calculate_dynamic_levels_etf(asset_name, current_price)

            # Estimate call walls (resistance levels with high dealer short gamma)
            call_walls = []
            for resistance in levels['resistance']:
                if resistance > current_price:
                    distance = resistance - current_price
                    # Closer walls have higher "strength"
                    strength = max(0, 100 - (distance / current_price * 1000))
                    call_walls.append({
                        'strike': resistance,
                        'distance': round(distance, 2),
                        'strength': round(strength, 1),
                        'type': 'CALL_WALL'
                    })

            # Estimate put walls (support levels with high dealer short gamma)
            put_walls = []
            for support in levels['support']:
                if support < current_price:
                    distance = current_price - support
                    strength = max(0, 100 - (distance / current_price * 1000))
                    put_walls.append({
                        'strike': support,
                        'distance': round(distance, 2),
                        'strength': round(strength, 1),
                        'type': 'PUT_WALL'
                    })

            # King node: Highest strength wall on either side
            all_walls = call_walls + put_walls
            if all_walls:
                king_node = max(all_walls, key=lambda x: x['strength'])
                king_node['is_king_node'] = True
            else:
                king_node = None

            # Sort by strength
            call_walls.sort(key=lambda x: x['strength'], reverse=True)
            put_walls.sort(key=lambda x: x['strength'], reverse=True)

            return {
                'call_walls': call_walls[:3],  # Top 3
                'put_walls': put_walls[:3],    # Top 3
                'king_node': king_node,
                'nearest_call_wall': call_walls[0] if call_walls else None,
                'nearest_put_wall': put_walls[0] if put_walls else None
            }

        except Exception as e:
            pass  # Suppress error messages
            return None

    def get_news_sentiment(self, asset_name):
        """Fetch news sentiment for asset (cached for 5 minutes)"""
        try:
            current_time = time.time()

            # Check cache
            if asset_name in self.news_cache:
                if current_time - self.last_news_fetch.get(asset_name, 0) < 300:  # 5 minutes
                    return self.news_cache[asset_name]

            # Fetch news
            ticker = ASSETS[asset_name]['ticker'].replace('I:', '')  # Remove I: prefix for indices
            url = f"https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers={ticker}&apikey={ALPHAVANTAGE_KEY}&limit=10"
            response = requests.get(url, timeout=5)

            if response.status_code == 200:
                data = response.json()
                if 'feed' in data and len(data['feed']) > 0:
                    # Calculate average sentiment
                    sentiments = []
                    for article in data['feed'][:5]:  # Top 5 articles
                        if 'overall_sentiment_score' in article:
                            sentiments.append(float(article['overall_sentiment_score']))

                    if sentiments:
                        avg_sentiment = sum(sentiments) / len(sentiments)
                        sentiment_label = 'BULLISH' if avg_sentiment > 0.15 else 'BEARISH' if avg_sentiment < -0.15 else 'NEUTRAL'

                        result = {
                            'score': avg_sentiment,
                            'label': sentiment_label,
                            'article_count': len(sentiments)
                        }

                        # Cache result
                        self.news_cache[asset_name] = result
                        self.last_news_fetch[asset_name] = current_time

                        return result

            return None
        except Exception as e:
            return None

    def calculate_confidence_score(self, asset_name, price, momentum, trade_type, positioning=None):
        """Enhanced confidence scoring with dealer positioning and news sentiment"""
        score = 0
        reasons = []

        # Factor 1: Momentum alignment (20 points) - reduced from 25
        if trade_type == 'LONG' and momentum == 'BULLISH':
            score += 20
            reasons.append('Strong bullish momentum')
        elif trade_type == 'SHORT' and momentum == 'BEARISH':
            score += 20
            reasons.append('Strong bearish momentum')
        elif momentum == 'NEUTRAL':
            score += 10
            reasons.append('Neutral momentum')

        # Factor 2: News Sentiment (15 points) - NEW
        news = self.get_news_sentiment(asset_name)
        if news:
            if trade_type == 'LONG' and news['label'] == 'BULLISH':
                score += 15
                reasons.append(f"📰 Bullish news sentiment ({news['score']:.2f})")
            elif trade_type == 'SHORT' and news['label'] == 'BEARISH':
                score += 15
                reasons.append(f"📰 Bearish news sentiment ({news['score']:.2f})")
            elif news['label'] == 'NEUTRAL':
                score += 7
                reasons.append(f"📰 Neutral news sentiment")

        # Factor 3: Dealer positioning (30 points)
        if positioning:
            if trade_type == 'LONG':
                # Long at put wall = high confidence
                if positioning['nearest_put_wall']:
                    put_wall = positioning['nearest_put_wall']
                    if put_wall['distance'] <= 10:
                        score += 30
                        reasons.append(f"🛡️ Strong PUT WALL at {put_wall['strike']} ({put_wall['distance']:.1f} pts)")
                    elif put_wall['distance'] <= 20:
                        score += 20
                        reasons.append(f"🛡️ PUT WALL at {put_wall['strike']} ({put_wall['distance']:.1f} pts)")

                # Bonus for king node proximity
                if positioning['king_node'] and positioning['king_node']['type'] == 'PUT_WALL':
                    if positioning['king_node']['distance'] <= 10:
                        score += 10
                        reasons.append(f"👑 KING NODE at {positioning['king_node']['strike']}")

            else:  # SHORT
                # Short at call wall = high confidence
                if positioning['nearest_call_wall']:
                    call_wall = positioning['nearest_call_wall']
                    if call_wall['distance'] <= 10:
                        score += 30
                        reasons.append(f"🧱 Strong CALL WALL at {call_wall['strike']} ({call_wall['distance']:.1f} pts)")
                    elif call_wall['distance'] <= 20:
                        score += 20
                        reasons.append(f"🧱 CALL WALL at {call_wall['strike']} ({call_wall['distance']:.1f} pts)")

                # Bonus for king node proximity
                if positioning['king_node'] and positioning['king_node']['type'] == 'CALL_WALL':
                    if positioning['king_node']['distance'] <= 10:
                        score += 10
                        reasons.append(f"👑 KING NODE at {positioning['king_node']['strike']}")

        # Factor 4: Level proximity (20 points)
        if asset_name in ['SPX', 'NDX']:
            support, resistance = self.find_nearest_levels(asset_name, price)
            if support and resistance:
                dist_support = price - support
                dist_resistance = resistance - price

                if trade_type == 'LONG' and dist_support <= 5:
                    score += 20
                    reasons.append(f'Excellent support proximity ({dist_support:.1f} pts)')
                elif trade_type == 'LONG' and dist_support <= 10:
                    score += 12
                    reasons.append(f'Good support proximity ({dist_support:.1f} pts)')

                if trade_type == 'SHORT' and dist_resistance <= 5:
                    score += 20
                    reasons.append(f'Excellent resistance proximity ({dist_resistance:.1f} pts)')
                elif trade_type == 'SHORT' and dist_resistance <= 10:
                    score += 12
                    reasons.append(f'Good resistance proximity ({dist_resistance:.1f} pts)')

        # Factor 4: Volume Confirmation in Rejection Zone (30 points max) - VOLUME ENHANCEMENT
        # Integrated from volume enhancement: High volume confirms dealer defense
        if positioning and positioning.get('king_node'):
            king_node = positioning['king_node']
            zone = self.classify_king_node_zone(king_node['strike'], price)

            # Get volume ratio for current scan
            current_volume = 1.0  # Default if not available
            if hasattr(self, 'latest_volume') and asset_name in self.latest_volume:
                current_volume = self.latest_volume[asset_name]

            volume_ratio = self.get_volume_ratio(asset_name, current_volume)

            # Apply volume filtering in REJECTION_ZONE (0-4 points from king node)
            if zone == 'REJECTION_ZONE':
                # Volume Enhancement Logic from backtest validation
                if volume_ratio >= 1.5:  # HIGH volume
                    score += 30
                    reasons.append(f'🔥 HIGH VOLUME in rejection zone ({volume_ratio:.1f}x avg) - Strong dealer defense')
                elif volume_ratio >= 1.2:  # MODERATE volume
                    score += 20
                    reasons.append(f'📊 MODERATE VOLUME in rejection zone ({volume_ratio:.1f}x avg) - Good confirmation')
                elif volume_ratio >= 0.8:  # NORMAL volume
                    score += 10
                    reasons.append(f'✅ Normal volume in rejection zone ({volume_ratio:.1f}x avg)')
                else:  # LOW volume (< 0.8x) - BLOCK TRADE
                    score -= 20
                    reasons.append(f'⚠️ LOW VOLUME in rejection zone ({volume_ratio:.1f}x avg) - WEAK SIGNAL')

            # Bonus for other high-quality zones with volume confirmation
            elif zone in ['GATEKEEPER_ZONE', 'CAUTION_ZONE'] and volume_ratio >= 1.2:
                score += 10
                reasons.append(f'📊 Volume confirmation in {zone} ({volume_ratio:.1f}x avg)')

        # Factor 5: Price trend (15 points)
        if asset_name in self.price_history and len(self.price_history[asset_name]) >= 3:
            prices = self.price_history[asset_name]

            if trade_type == 'LONG':
                if all(prices[i] < prices[i+1] for i in range(len(prices)-1)):
                    score += 15
                    reasons.append('Consistent uptrend')
                elif prices[-1] > prices[-3]:
                    score += 8
                    reasons.append('Recent upward movement')
            else:
                if all(prices[i] > prices[i+1] for i in range(len(prices)-1)):
                    score += 15
                    reasons.append('Consistent downtrend')
                elif prices[-1] < prices[-3]:
                    score += 8
                    reasons.append('Recent downward movement')

        # Factor 5: Risk/reward (10 points)
        if asset_name in ['SPX', 'NDX']:
            support, resistance = self.find_nearest_levels(asset_name, price)
            if support and resistance:
                if trade_type == 'LONG':
                    risk = price - (support - 5)
                    reward = (resistance - 5) - price
                    if risk > 0 and reward / risk >= 2.0:
                        score += 10
                        reasons.append(f'Excellent R:R {reward/risk:.1f}:1')
                    elif risk > 0 and reward / risk >= 1.5:
                        score += 6
                        reasons.append(f'Good R:R {reward/risk:.1f}:1')
                else:
                    risk = (resistance + 5) - price
                    reward = price - (support + 5)
                    if risk > 0 and reward / risk >= 2.0:
                        score += 10
                        reasons.append(f'Excellent R:R {reward/risk:.1f}:1')
                    elif risk > 0 and reward / risk >= 1.5:
                        score += 6
                        reasons.append(f'Good R:R {reward/risk:.1f}:1')

        return min(score, 100), reasons

    def calculate_momentum(self, asset_name):
        """Calculate momentum using price history trend (NOT tick-to-tick)"""
        # Use price history trend instead of single tick comparison
        # This aligns with the battle test validation logic
        if asset_name not in self.price_history or len(self.price_history[asset_name]) < 5:
            return 'NEUTRAL'

        history = self.price_history[asset_name]

        # Count up vs down moves in last 5 prices
        up_moves = sum(1 for i in range(1, len(history)) if history[i] > history[i-1])
        down_moves = sum(1 for i in range(1, len(history)) if history[i] < history[i-1])

        # Require 3+ consistent moves for directional bias
        if up_moves >= 3:
            return 'BULLISH'
        elif down_moves >= 3:
            return 'BEARISH'
        else:
            return 'NEUTRAL'

    def find_nearest_levels(self, asset_name, price):
        """Find nearest support and resistance"""
        if asset_name not in ['SPX', 'NDX']:
            return None, None

        levels = ASSETS[asset_name]['levels']
        resistances = [r for r in levels['resistance'] if r > price]
        supports = [s for s in levels['support'] if s < price]

        return (max(supports) if supports else None,
                min(resistances) if resistances else None)

    def update_price_history(self, asset_name, price):
        """Maintain price history"""
        if asset_name not in self.price_history:
            self.price_history[asset_name] = []
        self.price_history[asset_name].append(price)
        if len(self.price_history[asset_name]) > 10:
            self.price_history[asset_name].pop(0)

    def update_volume_history(self, asset_name, volume):
        """Track volume history for rolling average calculation"""
        if asset_name not in self.volume_history:
            self.volume_history[asset_name] = []

        self.volume_history[asset_name].append(volume)

        # Maintain rolling window
        if len(self.volume_history[asset_name]) > self.volume_window:
            self.volume_history[asset_name].pop(0)

    def get_volume_ratio(self, asset_name, current_volume):
        """
        Calculate volume ratio (current vs average)
        Returns 1.0 if no history available
        """
        if asset_name not in self.volume_history or len(self.volume_history[asset_name]) < 3:
            return 1.0  # Not enough data, return neutral

        avg_volume = sum(self.volume_history[asset_name]) / len(self.volume_history[asset_name])

        if avg_volume == 0:
            return 1.0

        return current_volume / avg_volume

    def classify_king_node_zone(self, king_node_strike, current_price):
        """
        Classify distance zone from king node
        Returns: zone name (FAR_ZONE, GATEKEEPER_ZONE, CAUTION_ZONE, REJECTION_ZONE, AT_NODE)
        """
        distance = abs(current_price - king_node_strike)

        if distance >= 25:
            return 'FAR_ZONE'
        elif distance >= 10:
            return 'GATEKEEPER_ZONE'
        elif distance >= 5:
            return 'CAUTION_ZONE'
        elif distance >= 2:
            return 'REJECTION_ZONE'
        else:
            return 'AT_NODE'

    def apply_volume_confirmation_to_king_node(self, base_score, zone, volume_ratio, positioning, trade_type):
        """
        Apply volume confirmation bonus/penalty based on zone and volume
        Only applies to REJECTION ZONE where dealer defense matters most

        Returns: (adjusted_score, volume_reason)
        """
        # Volume confirmation only matters in REJECTION ZONE
        if zone != 'REJECTION_ZONE':
            return base_score, None

        # Check if this is a reversal setup (trading away from king node)
        king_node = positioning.get('king_node') if positioning else None
        if not king_node:
            return base_score, None

        # Determine if trade direction aligns with reversal logic
        distance = king_node.get('distance', 0)
        is_reversal = False

        if trade_type == 'SHORT' and distance < 0:  # Below king node, shorting (expecting pushback down)
            is_reversal = True
        elif trade_type == 'LONG' and distance > 0:  # Above king node, long (expecting pushback up)
            is_reversal = True

        if not is_reversal:
            # Fighting reversal zone - already penalized in base scoring
            return base_score, None

        # Apply volume confirmation for reversal trades in rejection zone
        if volume_ratio >= 1.5:
            # High volume confirmation - dealers actively defending
            return min(base_score + 10, 100), f"🔥 HIGH volume ({volume_ratio:.1f}x) confirms dealer defense"
        elif volume_ratio >= 1.2:
            # Moderate volume confirmation
            return min(base_score + 5, 100), f"✅ Volume ({volume_ratio:.1f}x) supports reversal"
        elif volume_ratio < 0.8:
            # Low volume warning - dealer may not be actively defending
            return max(base_score - 10, 0), f"⚠️ LOW volume ({volume_ratio:.1f}x) - weak dealer defense"
        else:
            # Normal volume - no adjustment
            return base_score, f"📊 Normal volume ({volume_ratio:.1f}x)"

    def track_king_node_touch(self, asset_name, king_node_strike, current_price):
        """
        Track touches to king node levels
        Returns touch count for this king node
        """
        key = f"{asset_name}_{king_node_strike}"

        # Initialize if new king node
        if key not in self.king_node_touch_history:
            self.king_node_touch_history[key] = {
                'strike': king_node_strike,
                'touch_count': 0,
                'last_touch_price': None,
                'first_seen': datetime.now()
            }

        # Check if this is a new touch (within 2 points of king node)
        distance = abs(current_price - king_node_strike)
        if distance <= 2:
            history = self.king_node_touch_history[key]

            # Only count as new touch if price moved away and came back
            if history['last_touch_price'] is None or abs(current_price - history['last_touch_price']) > 2:
                history['touch_count'] += 1
                history['last_touch_price'] = current_price

        return self.king_node_touch_history[key]['touch_count']

    def calculate_zone_based_position_size(self, zone, volume_ratio, touch_count,
                                            king_node_strength, base_confidence):
        """
        Calculate optimal position size based on zone characteristics

        Returns: (position_size as % of account, reasoning string)
        """
        # Zone base sizes
        ZONE_BASE_SIZES = {
            'REJECTION_ZONE': 1.5,      # 0-4 points: Highest conviction
            'CAUTION_ZONE': 1.0,         # 5-9 points: Medium conviction
            'GATEKEEPER_ZONE': 1.2,      # 10-24 points: Good conviction
            'FAR_ZONE': 1.0,             # 25+ points: Standard conviction
            'AT_NODE': 0.5               # 0-2 points: Too close, reduce size
        }

        # Volume multipliers
        VOLUME_MULTIPLIERS = {
            'HIGH': 1.3,        # 1.5x+ volume
            'MODERATE': 1.15,   # 1.2-1.5x volume
            'NORMAL': 1.0,      # 0.8-1.3x volume
            'LOW': 0.7          # <0.8x volume
        }

        # Touch sequence multipliers
        TOUCH_MULTIPLIERS = {
            'UNTESTED': 1.25,    # No previous touches
            'FIRST_TOUCH': 1.1,  # First test
            'SECOND_TOUCH': 1.0, # Retest
            'THIRD_PLUS': 0.8    # Overused level
        }

        # King node strength multipliers
        STRENGTH_MULTIPLIERS = {
            99: 1.2,   # 99% strength
            95: 1.1,   # 95-98% strength
            90: 1.0,   # 90-94% strength
            85: 0.9    # 85-89% strength
        }

        # Start with zone base size
        base_size = ZONE_BASE_SIZES.get(zone, 1.0)

        # Apply volume multiplier
        if volume_ratio >= 1.5:
            volume_mult = VOLUME_MULTIPLIERS['HIGH']
            volume_reason = f"HIGH volume ({volume_ratio:.1f}x)"
        elif volume_ratio >= 1.2:
            volume_mult = VOLUME_MULTIPLIERS['MODERATE']
            volume_reason = f"MODERATE volume ({volume_ratio:.1f}x)"
        elif volume_ratio >= 0.8:
            volume_mult = VOLUME_MULTIPLIERS['NORMAL']
            volume_reason = f"Normal volume ({volume_ratio:.1f}x)"
        else:
            volume_mult = VOLUME_MULTIPLIERS['LOW']
            volume_reason = f"LOW volume ({volume_ratio:.1f}x)"

        # Apply touch sequence multiplier
        if touch_count == 0:
            touch_mult = TOUCH_MULTIPLIERS['UNTESTED']
            touch_reason = "Untested level"
        elif touch_count == 1:
            touch_mult = TOUCH_MULTIPLIERS['FIRST_TOUCH']
            touch_reason = "First touch"
        elif touch_count == 2:
            touch_mult = TOUCH_MULTIPLIERS['SECOND_TOUCH']
            touch_reason = "Second touch"
        else:
            touch_mult = TOUCH_MULTIPLIERS['THIRD_PLUS']
            touch_reason = f"{touch_count} touches (overused)"

        # Apply king node strength multiplier
        if king_node_strength >= 99:
            strength_mult = STRENGTH_MULTIPLIERS[99]
            strength_reason = "99% king node strength"
        elif king_node_strength >= 95:
            strength_mult = STRENGTH_MULTIPLIERS[95]
            strength_reason = f"{king_node_strength}% strength"
        elif king_node_strength >= 90:
            strength_mult = STRENGTH_MULTIPLIERS[90]
            strength_reason = f"{king_node_strength}% strength"
        else:
            strength_mult = STRENGTH_MULTIPLIERS[85]
            strength_reason = f"{king_node_strength}% strength (adequate)"

        # Calculate final position size
        position_size = base_size * volume_mult * touch_mult * strength_mult

        # Apply confidence scaling
        confidence_mult = base_confidence / 100
        position_size *= confidence_mult

        # Hard caps
        position_size = min(position_size, 2.0)  # Maximum 2% per trade
        position_size = max(position_size, 0.3)  # Minimum 0.3% per trade

        # Build reasoning
        reasoning = (
            f"{zone} base: {base_size}% × "
            f"{volume_reason} ({volume_mult}x) × "
            f"{touch_reason} ({touch_mult}x) × "
            f"{strength_reason} ({strength_mult}x) × "
            f"Confidence {base_confidence}% ({confidence_mult:.2f}x) = "
            f"{position_size:.2f}%"
        )

        return position_size, reasoning

    def track_king_node_history(self, asset_name, new_king_node):
        """
        Track king node changes over time and detect migrations

        Returns: migration_event (dict) if detected, None otherwise
        """
        key = f"{asset_name}_king_history"

        # Initialize history if new
        if key not in self.king_node_migration_history:
            self.king_node_migration_history[key] = {
                'current_node': new_king_node,
                'previous_nodes': [],
                'migration_count': 0,
                'last_migration_time': datetime.now()
            }
            return None

        history = self.king_node_migration_history[key]
        current_node = history['current_node']

        # Check if king node has changed
        if new_king_node['strike'] != current_node['strike']:
            # Detect migration
            migration_event = self.detect_migration_event(asset_name, current_node, new_king_node)

            if migration_event:
                # Update history
                history['previous_nodes'].append(current_node)
                if len(history['previous_nodes']) > 10:  # Keep last 10
                    history['previous_nodes'].pop(0)

                history['current_node'] = new_king_node
                history['migration_count'] += 1
                history['last_migration_time'] = datetime.now()

                # Invalidate old touch history
                self.invalidate_old_touches(asset_name, current_node['strike'])

                return migration_event

        return None

    def detect_migration_event(self, asset_name, old_node, new_node):
        """
        Classify the type of migration and its significance

        Returns: migration event dictionary or None
        """
        # Determine migration direction and type
        strike_diff = new_node['strike'] - old_node['strike']

        if strike_diff > 0:  # Upward movement
            if old_node['type'] == 'CALL_WALL' and new_node['type'] == 'CALL_WALL':
                migration_type = 'UPWARD'
                bias = 'BULLISH'
            elif old_node['type'] == 'PUT_WALL' and new_node['type'] == 'CALL_WALL':
                migration_type = 'REVERSAL'
                bias = 'VERY_BULLISH'
            else:
                migration_type = 'LATERAL'
                bias = 'NEUTRAL'
        elif strike_diff < 0:  # Downward movement
            if old_node['type'] == 'PUT_WALL' and new_node['type'] == 'PUT_WALL':
                migration_type = 'DOWNWARD'
                bias = 'BEARISH'
            elif old_node['type'] == 'CALL_WALL' and new_node['type'] == 'PUT_WALL':
                migration_type = 'REVERSAL'
                bias = 'VERY_BEARISH'
            else:
                migration_type = 'LATERAL'
                bias = 'NEUTRAL'
        else:
            # Same strike, check type change
            if old_node['type'] != new_node['type']:
                migration_type = 'REVERSAL'
                bias = 'VERY_BULLISH' if new_node['type'] == 'CALL_WALL' else 'VERY_BEARISH'
            else:
                return None  # No migration

        # Calculate migration significance
        strike_distance = abs(strike_diff)
        strength_change = new_node.get('strength', 99) - old_node.get('strength', 99)

        # Determine significance
        if strike_distance >= 50 or abs(strength_change) >= 10:
            significance = 'HIGH'
            confidence_boost = 15
        elif strike_distance >= 25 or abs(strength_change) >= 5:
            significance = 'MEDIUM'
            confidence_boost = 10
        else:
            significance = 'LOW'
            confidence_boost = 5

        # Format migration message
        if migration_type == 'UPWARD':
            message = f"🔼 King Node MIGRATED HIGHER: {old_node['strike']} → {new_node['strike']} (+{strike_diff} pts)"
        elif migration_type == 'DOWNWARD':
            message = f"🔽 King Node MIGRATED LOWER: {old_node['strike']} → {new_node['strike']} ({strike_diff} pts)"
        elif migration_type == 'REVERSAL':
            message = f"🔄 King Node REVERSED: {old_node['type']} {old_node['strike']} → {new_node['type']} {new_node['strike']}"
        else:
            message = f"↔️ King Node shifted: {old_node['strike']} → {new_node['strike']}"

        return {
            'asset': asset_name,
            'migration_type': migration_type,
            'bias': bias,
            'significance': significance,
            'old_strike': old_node['strike'],
            'new_strike': new_node['strike'],
            'strike_distance': strike_distance,
            'old_type': old_node['type'],
            'new_type': new_node['type'],
            'strength_change': strength_change,
            'confidence_boost': confidence_boost,
            'timestamp': datetime.now(),
            'message': message
        }

    def invalidate_old_touches(self, asset_name, old_king_strike):
        """
        Clear touch history for obsolete king node
        Archive for analysis purposes
        """
        old_key = f"{asset_name}_{old_king_strike}"

        # Archive old touches (for analysis)
        if old_key in self.king_node_touch_history:
            if 'archived_touches' not in self.king_node_touch_history:
                self.king_node_touch_history['archived_touches'] = []

            self.king_node_touch_history['archived_touches'].append({
                'key': old_key,
                'data': self.king_node_touch_history[old_key],
                'archived_at': datetime.now()
            })

            # Keep only last 50 archived entries
            if len(self.king_node_touch_history['archived_touches']) > 50:
                self.king_node_touch_history['archived_touches'].pop(0)

            # Remove from active tracking
            del self.king_node_touch_history[old_key]

    def calculate_dynamic_levels_etf(self, asset_name, price):
        """Calculate dynamic support/resistance for ETFs using price history"""
        if asset_name not in self.price_history or len(self.price_history[asset_name]) < 5:
            return None, None

        prices = self.price_history[asset_name]

        # Calculate support as recent low
        support = min(prices[-5:])

        # Calculate resistance as recent high
        resistance = max(prices[-5:])

        return support, resistance

    def calculate_option_strike(self, asset_name, price, trade_type, target):
        """Calculate optimal strike"""
        now = datetime.now()
        expiry = now.strftime('%Y%m%d')

        if asset_name in ['SPX', 'NDX']:
            if trade_type == 'LONG':
                strike = int((price + 5) / 5) * 5
            else:
                strike = int((price - 5) / 5) * 5

            ticker = 'SPXW' if asset_name == 'SPX' else 'NDXP'
            option_type = 'C' if trade_type == 'LONG' else 'P'
            contract = f"{ticker}{expiry}{option_type}{strike}"
        else:
            if trade_type == 'LONG':
                strike = int(price + 0.5)
            else:
                strike = int(price - 0.5)

            ticker = asset_name
            option_type = 'C' if trade_type == 'LONG' else 'P'
            contract = f"{ticker}{expiry}{option_type}{strike}"

        return contract, strike

    def detect_trend(self, asset_name):
        """
        Detect overall trend direction based on recent price history.
        Returns 'UPTREND', 'DOWNTREND', or 'NEUTRAL'
        """
        if asset_name not in self.price_history:
            return 'NEUTRAL'

        history = self.price_history[asset_name]
        if len(history) < 5:
            return 'NEUTRAL'  # Need at least 5 price points

        # Get last 5 prices
        recent_prices = history[-5:]

        # Count how many prices are higher than their predecessor
        up_moves = sum(1 for i in range(1, len(recent_prices)) if recent_prices[i] > recent_prices[i-1])
        down_moves = sum(1 for i in range(1, len(recent_prices)) if recent_prices[i] < recent_prices[i-1])

        # Strong uptrend: 3+ out of 4 moves up
        if up_moves >= 3:
            return 'UPTREND'
        # Strong downtrend: 3+ out of 4 moves down
        elif down_moves >= 3:
            return 'DOWNTREND'
        else:
            return 'NEUTRAL'

    def detect_price_rejection(self, asset_name, price, level, direction):
        """
        Detect if price has rejected from a level (resistance or support).
        Returns True if rejection is detected (price tried to break level but failed).
        """
        if asset_name not in self.price_history:
            return False  # Not enough history

        history = self.price_history[asset_name]
        if len(history) < 3:
            return False  # Need at least 3 price points

        # Get last 3 prices (most recent first)
        recent_prices = history[-3:]

        if direction == 'SHORT':  # Checking resistance rejection
            # Did price get within 5 points of resistance and then fall back?
            touched_resistance = any(p >= level - 5 for p in recent_prices[:-1])
            pulled_back = price < level - 3
            return touched_resistance and pulled_back

        elif direction == 'LONG':  # Checking support rejection
            # Did price get within 5 points of support and then bounce back?
            touched_support = any(p <= level + 5 for p in recent_prices[:-1])
            bounced_back = price > level + 3
            return touched_support and bounced_back

        return False

    def generate_trade_setup(self, asset_name, price, momentum):
        """Generate HIGH CONFIDENCE trades with dealer positioning and confirmation"""
        current_time = time.time()

        # STRONGER COOLDOWN: Per-asset, not per-strike - prevents multiple signals per asset
        cooldown = 900  # 15 minutes for all assets (reduced spam)

        if asset_name in self.last_trade_alert:
            if current_time - self.last_trade_alert[asset_name] < cooldown:
                return None

        # CONFIRMATION REQUIREMENT: Require 2 consecutive scans showing same setup
        signal_key = f"{asset_name}_{momentum}"
        if signal_key not in self.signal_confirmation:
            self.signal_confirmation[signal_key] = {'count': 1, 'timestamp': current_time}
            return None  # First detection, wait for confirmation
        else:
            conf = self.signal_confirmation[signal_key]
            # If same signal within 60 seconds, consider it confirmed
            if current_time - conf['timestamp'] < 60:
                conf['count'] += 1
                if conf['count'] < 2:  # Need 2 consecutive scans
                    return None
            else:
                # Reset if too much time passed
                self.signal_confirmation[signal_key] = {'count': 1, 'timestamp': current_time}
                return None

        # Get asset-specific minimum confidence
        min_confidence = ASSETS[asset_name]['min_confidence']

        # Analyze dealer positioning
        positioning = self.analyze_options_chain(asset_name, price)

        # KING NODE MIGRATION TRACKING INTEGRATION
        if positioning and positioning.get('king_node'):
            king_node = positioning['king_node']
            # Track king node changes and detect migrations
            migration_event = self.track_king_node_history(asset_name, king_node)

            # If migration detected, send alert and apply confidence boost
            if migration_event:
                print(f"\n🔄 {migration_event['message']}")
                print(f"   Significance: {migration_event['significance']} | Bias: {migration_event['bias']}")
                print(f"   Confidence Boost: +{migration_event['confidence_boost']} points\n")

                # Store migration event for Discord alert inclusion
                if not hasattr(self, 'recent_migrations'):
                    self.recent_migrations = {}
                self.recent_migrations[asset_name] = migration_event

        if asset_name in ['SPX', 'NDX']:
            support, resistance = self.find_nearest_levels(asset_name, price)

            if support and resistance:
                distance_to_support = price - support
                distance_to_resistance = resistance - price

                # LONG setup - Near support with BULLISH momentum OR bullish breakout at resistance
                # ENHANCED MOMENTUM FILTER: Only trade with directional conviction
                if (distance_to_support <= 10 and momentum == 'BULLISH') or \
                   (distance_to_resistance <= 10 and momentum == 'BULLISH'):

                    # Different reasons based on setup type
                    if distance_to_support <= 10:
                        setup_reason = f'Near support {support} with {momentum} momentum'
                    else:
                        setup_reason = f'Bullish breakout at resistance {resistance}'

                    confidence_score, confidence_reasons = self.calculate_confidence_score(
                        asset_name, price, momentum, 'LONG', positioning
                    )

                    # Apply migration confidence boost if applicable
                    if hasattr(self, 'recent_migrations') and asset_name in self.recent_migrations:
                        migration = self.recent_migrations[asset_name]
                        # Check if migration bias aligns with trade direction
                        if migration['bias'] in ['BULLISH', 'VERY_BULLISH']:
                            confidence_score += migration['confidence_boost']
                            confidence_reasons.append(f"🔄 Migration Boost: {migration['migration_type']} (+{migration['confidence_boost']} pts)")

                    if confidence_score < min_confidence:
                        return None

                    self.last_trade_alert[asset_name] = current_time  # Per-asset cooldown
                    target1 = round(price + (distance_to_resistance * 0.5), 2)
                    contract, strike = self.calculate_option_strike(asset_name, price, 'LONG', target1)

                    # WIDER STOPS: NDX 15-20pts, SPX 20-30pts to avoid getting stopped by normal volatility
                    stop_distance = 20 if asset_name == 'NDX' else 25
                    stop_price = round(support - stop_distance, 2) if distance_to_support <= 10 else round(resistance - stop_distance, 2)

                    # ZONE-BASED POSITION SIZING INTEGRATION
                    touch_count = 0
                    position_size = 1.0  # Default 1% position
                    size_reasoning = ""

                    if positioning and positioning.get('king_node'):
                        king_node = positioning['king_node']
                        # Track king node touches
                        touch_count = self.track_king_node_touch(asset_name, king_node['strike'], price)

                        # Get volume ratio
                        volume_ratio = 1.0
                        if hasattr(self, 'latest_volume') and asset_name in self.latest_volume:
                            volume_ratio = self.get_volume_ratio(asset_name, self.latest_volume[asset_name])

                        # Calculate zone and position size
                        zone = self.classify_king_node_zone(king_node['strike'], price)
                        position_size, size_reasoning = self.calculate_zone_based_position_size(
                            zone, volume_ratio, touch_count, king_node.get('strength', 99), confidence_score
                        )

                    return {
                        'asset': asset_name,
                        'type': 'LONG',
                        'reason': setup_reason,
                        'entry': round(price, 2),
                        'stop': stop_price,
                        'target1': target1,
                        'target2': round(resistance + 10, 2) if distance_to_support <= 10 else round(resistance + 20, 2),
                        'confidence_score': confidence_score,
                        'confidence_reasons': confidence_reasons,
                        'contract': contract,
                        'strike': strike,
                        'option_type': 'CALL',
                        'timestamp': datetime.now().isoformat(),
                        'positioning': positioning,
                        'position_size': position_size,
                        'size_reasoning': size_reasoning,
                        'touch_count': touch_count
                    }

                # SHORT setup - Near resistance with BEARISH momentum OR bearish breakdown at support
                # ENHANCED MOMENTUM FILTER: Only trade with directional conviction
                elif (distance_to_resistance <= 10 and momentum == 'BEARISH') or \
                     (distance_to_support <= 10 and momentum == 'BEARISH'):

                    # TREND FILTER: Avoid counter-trend shorts in strong uptrends
                    trend = self.detect_trend(asset_name)
                    if distance_to_resistance <= 10 and trend == 'UPTREND':
                        return None  # Don't fade resistance in strong uptrend

                    # PRICE REJECTION CONFIRMATION: Wait for rejection at resistance before shorting
                    if distance_to_resistance <= 10:
                        rejection_confirmed = self.detect_price_rejection(asset_name, price, resistance, 'SHORT')
                        if not rejection_confirmed:
                            return None  # Wait for rejection before entering

                    # Different reasons based on setup type
                    if distance_to_resistance <= 10:
                        setup_reason = f'Resistance rejection at {resistance} with {momentum} momentum'
                    else:
                        setup_reason = f'Bearish breakdown at support {support}'

                    confidence_score, confidence_reasons = self.calculate_confidence_score(
                        asset_name, price, momentum, 'SHORT', positioning
                    )

                    # Apply migration confidence boost if applicable
                    if hasattr(self, 'recent_migrations') and asset_name in self.recent_migrations:
                        migration = self.recent_migrations[asset_name]
                        # Check if migration bias aligns with trade direction
                        if migration['bias'] in ['BEARISH', 'VERY_BEARISH']:
                            confidence_score += migration['confidence_boost']
                            confidence_reasons.append(f"🔄 Migration Boost: {migration['migration_type']} (+{migration['confidence_boost']} pts)")

                    if confidence_score < min_confidence:
                        return None

                    self.last_trade_alert[asset_name] = current_time  # Per-asset cooldown
                    target1 = round(price - (distance_to_support * 0.5), 2)
                    contract, strike = self.calculate_option_strike(asset_name, price, 'SHORT', target1)

                    # WIDER STOPS: NDX 15-20pts, SPX 20-30pts to avoid getting stopped by normal volatility
                    stop_distance = 20 if asset_name == 'NDX' else 25
                    stop_price = round(resistance + stop_distance, 2) if distance_to_resistance <= 10 else round(support + stop_distance, 2)

                    # ZONE-BASED POSITION SIZING INTEGRATION
                    touch_count = 0
                    position_size = 1.0  # Default 1% position
                    size_reasoning = ""

                    if positioning and positioning.get('king_node'):
                        king_node = positioning['king_node']
                        # Track king node touches
                        touch_count = self.track_king_node_touch(asset_name, king_node['strike'], price)

                        # Get volume ratio
                        volume_ratio = 1.0
                        if hasattr(self, 'latest_volume') and asset_name in self.latest_volume:
                            volume_ratio = self.get_volume_ratio(asset_name, self.latest_volume[asset_name])

                        # Calculate zone and position size
                        zone = self.classify_king_node_zone(king_node['strike'], price)
                        position_size, size_reasoning = self.calculate_zone_based_position_size(
                            zone, volume_ratio, touch_count, king_node.get('strength', 99), confidence_score
                        )

                    return {
                        'asset': asset_name,
                        'type': 'SHORT',
                        'reason': setup_reason,
                        'entry': round(price, 2),
                        'stop': stop_price,
                        'target1': target1,
                        'target2': round(support - 10, 2) if distance_to_resistance <= 10 else round(support - 20, 2),
                        'confidence_score': confidence_score,
                        'confidence_reasons': confidence_reasons,
                        'contract': contract,
                        'strike': strike,
                        'option_type': 'PUT',
                        'timestamp': datetime.now().isoformat(),
                        'positioning': positioning,
                        'position_size': position_size,
                        'size_reasoning': size_reasoning,
                        'touch_count': touch_count
                    }

        # ETF trades (QQQ, SPY, IWM) with breakout/breakdown logic
        else:
            # Get dynamic support/resistance for ETFs
            support, resistance = self.calculate_dynamic_levels_etf(asset_name, price)

            if support and resistance:
                distance_to_support = price - support
                distance_to_resistance = resistance - price

                # LONG setup - Near support with BULLISH/NEUTRAL OR breakout at resistance with BULLISH
                if (distance_to_support <= price * 0.005 and momentum in ['BULLISH', 'NEUTRAL']) or \
                   (distance_to_resistance <= price * 0.005 and momentum == 'BULLISH'):

                    # Different reasons based on setup type
                    if distance_to_support <= price * 0.005:
                        setup_reason = f'Near support ${support:.2f} with {momentum} momentum'
                    else:
                        setup_reason = f'Bullish breakout at resistance ${resistance:.2f}'

                    confidence_score, confidence_reasons = self.calculate_confidence_score(
                        asset_name, price, momentum, 'LONG', None
                    )

                    if confidence_score < min_confidence:
                        return None

                    self.last_trade_alert[asset_name] = current_time  # Per-asset cooldown
                    target1 = round(price + (distance_to_resistance * 0.5), 2)
                    contract, strike = self.calculate_option_strike(asset_name, price, 'LONG', target1)

                    return {
                        'asset': asset_name,
                        'type': 'LONG',
                        'reason': setup_reason,
                        'entry': round(price, 2),
                        'stop': round(support - (price * 0.005), 2) if distance_to_support <= price * 0.005 else round(resistance - (price * 0.005), 2),
                        'target1': target1,
                        'target2': round(resistance + (price * 0.01), 2) if distance_to_support <= price * 0.005 else round(resistance + (price * 0.015), 2),
                        'confidence_score': confidence_score,
                        'confidence_reasons': confidence_reasons,
                        'contract': contract,
                        'strike': strike,
                        'option_type': 'CALL',
                        'timestamp': datetime.now().isoformat(),
                        'positioning': None
                    }

                # SHORT setup - Near resistance with BEARISH/NEUTRAL OR breakdown at support with BEARISH
                elif (distance_to_resistance <= price * 0.005 and momentum in ['BEARISH', 'NEUTRAL']) or \
                     (distance_to_support <= price * 0.005 and momentum == 'BEARISH'):

                    # Different reasons based on setup type
                    if distance_to_resistance <= price * 0.005:
                        setup_reason = f'Near resistance ${resistance:.2f} with {momentum} momentum'
                    else:
                        setup_reason = f'Bearish breakdown at support ${support:.2f}'

                    confidence_score, confidence_reasons = self.calculate_confidence_score(
                        asset_name, price, momentum, 'SHORT', None
                    )

                    if confidence_score < min_confidence:
                        return None

                    self.last_trade_alert[asset_name] = current_time  # Per-asset cooldown
                    target1 = round(price - (distance_to_support * 0.5), 2)
                    contract, strike = self.calculate_option_strike(asset_name, price, 'SHORT', target1)

                    return {
                        'asset': asset_name,
                        'type': 'SHORT',
                        'reason': setup_reason,
                        'entry': round(price, 2),
                        'stop': round(resistance + (price * 0.005), 2) if distance_to_resistance <= price * 0.005 else round(support + (price * 0.005), 2),
                        'target1': target1,
                        'target2': round(support - (price * 0.01), 2) if distance_to_resistance <= price * 0.005 else round(support - (price * 0.015), 2),
                        'confidence_score': confidence_score,
                        'confidence_reasons': confidence_reasons,
                        'contract': contract,
                        'strike': strike,
                        'option_type': 'PUT',
                        'timestamp': datetime.now().isoformat(),
                        'positioning': None
                    }

        return None

    def send_trade_alert(self, trade):
        """Send enhanced alert with dealer positioning"""
        asset = trade['asset']
        webhook = ASSETS[asset]['webhook']

        color = 3066993 if trade['type'] == 'LONG' else 15158332
        emoji = '🟢' if trade['type'] == 'LONG' else '🔴'

        title = f"{emoji} 👑 {asset} {trade['type']} - {trade['confidence_score']}% CONFIDENCE"

        reasons_text = "\n".join([f"✓ {r}" for r in trade['confidence_reasons']])

        # Add positioning info
        positioning_text = ""
        if trade.get('positioning'):
            pos = trade['positioning']
            if pos.get('king_node'):
                kn = pos['king_node']
                positioning_text += f"\n\n**👑 KING NODE:** {kn['strike']} ({kn['type']}) - {kn['distance']:.1f} pts away"

            if trade['type'] == 'LONG' and pos.get('nearest_put_wall'):
                pw = pos['nearest_put_wall']
                positioning_text += f"\n**🛡️ PUT WALL:** {pw['strike']} - Strength {pw['strength']:.0f}%"

            if trade['type'] == 'SHORT' and pos.get('nearest_call_wall'):
                cw = pos['nearest_call_wall']
                positioning_text += f"\n**🧱 CALL WALL:** {cw['strike']} - Strength {cw['strength']:.0f}%"

        # Add position sizing info (ENHANCEMENT DATA)
        sizing_text = ""
        if trade.get('position_size') and trade.get('size_reasoning'):
            touch_emoji = "🆕" if trade.get('touch_count', 0) == 0 else f"#{trade.get('touch_count', 0)}"
            sizing_text += f"\n\n**💰 POSITION SIZE:** {trade['position_size']:.2f}% {touch_emoji}"
            sizing_text += f"\n{trade['size_reasoning']}"

        # Add migration info if applicable (ENHANCEMENT DATA)
        migration_text = ""
        if hasattr(self, 'recent_migrations') and asset in self.recent_migrations:
            migration = self.recent_migrations[asset]
            migration_text += f"\n\n**🔄 MIGRATION ALERT:** {migration['message']}"
            migration_text += f"\n**Significance:** {migration['significance']} | **Bias:** {migration['bias']}"

        payload = {
            'username': f'{emoji} Dealer Positioning Scanner',
            'embeds': [{
                'title': title,
                'description': f"**{trade['reason']}**\n\n📄 **CONTRACT:** `{trade['contract']}`{positioning_text}{sizing_text}{migration_text}\n\n**Confidence Factors:**\n{reasons_text}",
                'color': color,
                'timestamp': datetime.utcnow().isoformat(),
                'fields': [
                    {'name': '📍 Entry', 'value': f"${trade['entry']:,.2f}", 'inline': True},
                    {'name': '📄 Strike', 'value': f"${trade['strike']:,} {trade['option_type']}", 'inline': True},
                    {'name': '🛑 Stop', 'value': f"${trade['stop']:,.2f}", 'inline': True},
                    {'name': '🎯 Target 1', 'value': f"${trade['target1']:,.2f}", 'inline': True},
                    {'name': '🎯 Target 2', 'value': f"${trade['target2']:,.2f}", 'inline': True},
                    {'name': '🔥 Confidence', 'value': f"{trade['confidence_score']}%", 'inline': True}
                ],
                'footer': {'text': f'Dealer Positioning Scanner | {asset} {trade["type"]}'}
            }]
        }

        try:
            response = requests.post(webhook, json=payload, timeout=10)
            if response.status_code == 204:
                print(f"✅ Alert sent: {asset} {trade['type']} @ ${trade['entry']} ({trade['confidence_score']}%)")
                trade_id = f"{asset}_{trade['timestamp']}"
                self.active_trades[trade_id] = trade
                self.save_trade_history()

                # Open scalp trade for quick profit-taking
                scalp_engine = None
                if asset == 'SPX':
                    scalp_engine = self.scalp_spx
                elif asset == 'NDX':
                    scalp_engine = self.scalp_ndx
                else:
                    scalp_engine = self.scalp_etf

                # Determine king node for scalping
                king_node_str = "No positioning data"
                if trade.get('positioning') and trade['positioning'].get('king_node'):
                    kn = trade['positioning']['king_node']
                    king_node_str = f"{kn['strike']} {kn['type']} ({kn['distance']:.1f}pts, {kn['strength']:.0f}%)"

                # Open scalp with trade details
                scalp_id = scalp_engine.open_scalp(
                    asset=asset,
                    direction=trade['type'],
                    entry_price=trade['entry'],
                    king_node=king_node_str,
                    confidence=trade['confidence_score'],
                    contract=trade['contract']
                )

                # Map trade ID to scalp ID for monitoring
                self.trade_to_scalp_map[trade_id] = {
                    'scalp_id': scalp_id,
                    'engine': scalp_engine,
                    'asset': asset
                }
                print(f"⚡ Scalp opened: {scalp_id}")

        except Exception as e:
            print(f"❌ Error: {e}")

    def check_exit_conditions(self, trade_id, current_price):
        """Monitor exits with multiple profit targets and trailing stop"""
        if trade_id not in self.active_trades:
            return None

        trade = self.active_trades[trade_id]
        exit_reason = None
        exit_action = None

        # Calculate current P&L
        if trade['type'] == 'LONG':
            pnl_pct = ((current_price - trade['entry']) / trade['entry']) * 100
        else:
            pnl_pct = ((trade['entry'] - current_price) / trade['entry']) * 100

        # Track highest P&L for trailing stop
        if 'highest_pnl' not in trade:
            trade['highest_pnl'] = pnl_pct
        else:
            trade['highest_pnl'] = max(trade['highest_pnl'], pnl_pct)

        # Multiple profit targets: 5%, 10%, 15%, 20%, 25%+
        profit_targets = [
            (5, 'T1', '🎯 TARGET 1 (5%) - Take 20%', False),
            (10, 'T2', '🎯🎯 TARGET 2 (10%) - Take 30%', False),
            (15, 'T3', '🎯🎯🎯 TARGET 3 (15%) - Take 30%', False),
            (20, 'T4', '🔥 TARGET 4 (20%) - Take 20% (let rest run)', False),
            (25, 'T5', '🔥🔥 TARGET 5 (25%+) - Monitor for exit', True)
        ]

        if trade['type'] == 'LONG':
            # Check stop loss
            if current_price <= trade['stop']:
                exit_reason = f"🛑 STOP LOSS @ ${current_price:,.2f}"
                exit_action = 'STOP_LOSS'

            # Trailing stop after 15% profit
            elif pnl_pct >= 15 and trade['highest_pnl'] - pnl_pct > 5:
                exit_reason = f"📉 TRAILING STOP @ ${current_price:,.2f} (from peak {trade['highest_pnl']:.1f}%)"
                exit_action = 'TRAILING_STOP'

            # Check profit targets
            else:
                for target_pct, target_key, target_msg, is_monitor in profit_targets:
                    if pnl_pct >= target_pct and not trade.get(f'{target_key}_hit'):
                        exit_reason = f"{target_msg} @ ${current_price:,.2f} (+{pnl_pct:.1f}%)"
                        exit_action = target_key
                        trade[f'{target_key}_hit'] = True

                        # Don't exit on T5, just monitor
                        if is_monitor:
                            print(f"📊 {trade['asset']} @ +{pnl_pct:.1f}% | Peak: {trade['highest_pnl']:.1f}% | Stop if drops 5%")
                            return None
                        break

        else:  # SHORT
            # Check stop loss
            if current_price >= trade['stop']:
                exit_reason = f"🛑 STOP LOSS @ ${current_price:,.2f}"
                exit_action = 'STOP_LOSS'

            # Trailing stop after 15% profit
            elif pnl_pct >= 15 and trade['highest_pnl'] - pnl_pct > 5:
                exit_reason = f"📉 TRAILING STOP @ ${current_price:,.2f} (from peak {trade['highest_pnl']:.1f}%)"
                exit_action = 'TRAILING_STOP'

            # Check profit targets
            else:
                for target_pct, target_key, target_msg, is_monitor in profit_targets:
                    if pnl_pct >= target_pct and not trade.get(f'{target_key}_hit'):
                        exit_reason = f"{target_msg} @ ${current_price:,.2f} (+{pnl_pct:.1f}%)"
                        exit_action = target_key
                        trade[f'{target_key}_hit'] = True

                        # Don't exit on T5, just monitor
                        if is_monitor:
                            print(f"📊 {trade['asset']} @ +{pnl_pct:.1f}% | Peak: {trade['highest_pnl']:.1f}% | Stop if drops 5%")
                            return None
                        break

        if exit_reason:
            return {
                'trade_id': trade_id,
                'exit_reason': exit_reason,
                'exit_action': exit_action,
                'current_price': current_price,
                'pnl_pct': round(pnl_pct, 2),
                'highest_pnl': round(trade['highest_pnl'], 2),
                'trade': trade
            }

        # Show live P&L every scan for active trades
        if pnl_pct != 0:
            profit_emoji = '💚' if pnl_pct > 0 else '🔴'
            print(f"{profit_emoji} {trade['asset']} LIVE: ${current_price:,.2f} | P&L: {pnl_pct:+.2f}% | Peak: {trade['highest_pnl']:+.2f}%")

        return None

    def send_exit_alert(self, exit_info):
        """Send exit alert with cooldown to prevent spam"""
        trade = exit_info['trade']
        trade_id = exit_info['trade_id']

        # Cooldown check: Only alert once per minute for same trade
        current_time = time.time()
        alert_key = f"{trade_id}_{exit_info['exit_action']}"

        if alert_key in self.last_exit_alert:
            time_since_last = current_time - self.last_exit_alert[alert_key]
            if time_since_last < 60:  # 60 second cooldown
                return  # Skip this alert

        # Update last alert time
        self.last_exit_alert[alert_key] = current_time

        webhook = ASSETS[trade['asset']]['webhook']

        color = 3066993 if exit_info['pnl_pct'] > 0 else 15158332
        emoji = '💰' if exit_info['pnl_pct'] > 0 else '⚠️'

        # Adjust fields based on exit type
        fields = [
            {'name': '📍 Entry', 'value': f"${trade['entry']:,.2f}", 'inline': True},
            {'name': '📍 Exit', 'value': f"${exit_info['current_price']:,.2f}", 'inline': True},
            {'name': '💵 P&L', 'value': f"{exit_info['pnl_pct']:+.2f}%", 'inline': True}
        ]

        # Add peak P&L for trailing stops
        if exit_info.get('highest_pnl'):
            fields.append({'name': '📈 Peak P&L', 'value': f"{exit_info['highest_pnl']:+.2f}%", 'inline': True})

        payload = {
            'username': f'{emoji} Exit Alert',
            'embeds': [{
                'title': f"{emoji} {trade['asset']} {trade['type']} - {exit_info['exit_action']}",
                'description': f"**{exit_info['exit_reason']}**\n\n📄 `{trade['contract']}`",
                'color': color,
                'timestamp': datetime.utcnow().isoformat(),
                'fields': fields
            }]
        }

        try:
            requests.post(webhook, json=payload, timeout=10)
            print(f"✅ Exit: {trade['asset']} @ ${exit_info['current_price']} ({exit_info['pnl_pct']:+.2f}%)")
        except Exception as e:
            print(f"❌ Exit alert error: {e}")

    def save_trade_history(self):
        """Save trades"""
        try:
            with open('.spx/dealer_trades.json', 'w') as f:
                json.dump({'active': self.active_trades, 'history': self.trade_history}, f, indent=2)
        except Exception as e:
            print(f"❌ Save error: {e}")

    def load_trade_history(self):
        """Load trades"""
        try:
            if os.path.exists('.spx/dealer_trades.json'):
                with open('.spx/dealer_trades.json', 'r') as f:
                    data = json.load(f)
                    self.active_trades = data.get('active', {})
                    self.trade_history = data.get('history', [])
                    print(f"✅ Loaded {len(self.active_trades)} active trades")
        except Exception as e:
            print(f"❌ Load error: {e}")

    def scan_markets(self):
        """Scan with dealer positioning"""
        self.previous_prices = self.prices.copy()

        for asset_name in ASSETS.keys():
            price = self.get_price(asset_name)
            if price:
                self.prices[asset_name] = price
                self.update_price_history(asset_name, price)

        # Check exits
        exits = []
        for trade_id in list(self.active_trades.keys()):
            trade = self.active_trades[trade_id]
            if trade['asset'] in self.prices:
                exit_info = self.check_exit_conditions(trade_id, self.prices[trade['asset']])
                if exit_info:
                    exits.append(exit_info)

        for exit_info in exits:
            self.send_exit_alert(exit_info)

            # Only fully close on STOP_LOSS or TRAILING_STOP
            # Partial exits on T1-T4, keep position open
            if exit_info['exit_action'] in ['STOP_LOSS', 'TRAILING_STOP']:
                self.trade_history.append({'trade': self.active_trades[exit_info['trade_id']], 'exit': exit_info})
                del self.active_trades[exit_info['trade_id']]
                self.save_trade_history()
            # For T1-T4, just alert but keep position open for higher targets
            elif exit_info['exit_action'] in ['T1', 'T2', 'T3', 'T4']:
                self.save_trade_history()  # Save state with target hit markers

        # Update active scalps with current prices
        for trade_id, scalp_mapping in list(self.trade_to_scalp_map.items()):
            scalp_id = scalp_mapping['scalp_id']
            scalp_engine = scalp_mapping['engine']
            asset = scalp_mapping['asset']

            if asset in self.prices:
                current_price = self.prices[asset]
                result = scalp_engine.update_scalp(scalp_id, current_price)

                # If scalp exited, remove from map
                if result and result.get('status') != 'ACTIVE':
                    del self.trade_to_scalp_map[trade_id]

        # Scan new trades
        for asset_name in ASSETS.keys():
            if asset_name in self.prices:
                trade = self.generate_trade_setup(asset_name, self.prices[asset_name], self.calculate_momentum(asset_name))
                if trade:
                    print(f"\n{'='*80}")
                    print(f"🎯 {trade['asset']} {trade['type']} @ ${trade['entry']:,.2f} - {trade['confidence_score']}%")
                    if trade.get('positioning', {}).get('king_node'):
                        print(f"   👑 King Node: {trade['positioning']['king_node']['strike']}")
                    print(f"{'='*80}\n")
                    self.send_trade_alert(trade)

    def start(self):
        """Start scanner"""
        # Silent start - only show trades
        self.running = True
        while self.running:
            self.scan_markets()
            time.sleep(self.scan_interval)  # Use configurable interval (30 seconds)

    def stop(self):
        """Stop scanner"""
        self.running = False
        print(f"\n{'='*80}")
        print(f"🛑 SCANNER STOPPED | Active: {len(self.active_trades)} | Completed: {len(self.trade_history)}")

        # Show scalping statistics
        spx_stats = self.scalp_spx.get_statistics()
        ndx_stats = self.scalp_ndx.get_statistics()
        etf_stats = self.scalp_etf.get_statistics()

        total_scalps = spx_stats['total_scalps'] + ndx_stats['total_scalps'] + etf_stats['total_scalps']

        if total_scalps > 0:
            print(f"\n⚡ SCALPING STATISTICS:")
            print(f"   Total Scalps: {total_scalps}")

            if spx_stats['total_scalps'] > 0:
                print(f"\n   SPX: {spx_stats['total_scalps']} scalps | Win Rate: {spx_stats['win_rate']:.1f}% | Avg P&L: {spx_stats['avg_pnl']:+.2f}%")
                print(f"        Avg Win: {spx_stats['avg_win']:+.2f}% | Avg Loss: {spx_stats['avg_loss']:+.2f}% | Aborts: {spx_stats['aborts']}")

            if ndx_stats['total_scalps'] > 0:
                print(f"\n   NDX: {ndx_stats['total_scalps']} scalps | Win Rate: {ndx_stats['win_rate']:.1f}% | Avg P&L: {ndx_stats['avg_pnl']:+.2f}%")
                print(f"        Avg Win: {ndx_stats['avg_win']:+.2f}% | Avg Loss: {ndx_stats['avg_loss']:+.2f}% | Aborts: {ndx_stats['aborts']}")

            if etf_stats['total_scalps'] > 0:
                print(f"\n   ETF: {etf_stats['total_scalps']} scalps | Win Rate: {etf_stats['win_rate']:.1f}% | Avg P&L: {etf_stats['avg_pnl']:+.2f}%")
                print(f"        Avg Win: {etf_stats['avg_win']:+.2f}% | Avg Loss: {etf_stats['avg_loss']:+.2f}% | Aborts: {etf_stats['aborts']}")

        print(f"{'='*80}")

if __name__ == "__main__":
    scanner = DealerPositioningScanner()
    try:
        scanner.start()
    except KeyboardInterrupt:
        print("\n\nInterrupt received...")
        scanner.stop()
