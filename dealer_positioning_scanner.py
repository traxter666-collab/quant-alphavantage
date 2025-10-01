"""
Dealer Positioning Scanner with King Node & Call/Put Wall Detection
Integrates Heatseeker methodology with multi-asset trade scanning
Provides institutional-grade positioning intelligence
"""

import requests
import json
import time
from datetime import datetime
import os

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
        self.last_trade_alert = {}
        self.last_exit_alert = {}  # Track last exit alert per trade
        self.dealer_positioning = {}
        self.king_nodes = {}
        self.call_walls = {}
        self.put_walls = {}

        os.makedirs('.spx', exist_ok=True)
        self.load_trade_history()

    def get_price(self, asset_name):
        """Get current price for any asset"""
        try:
            asset = ASSETS[asset_name]

            if asset['type'] == 'index':
                url = f"https://api.polygon.io/v3/snapshot/indices?ticker={asset['ticker']}&apikey={POLYGON_PRIMARY}"
                response = requests.get(url, timeout=5, verify=True)
                if response.status_code == 200:
                    data = response.json()
                    if 'results' in data and len(data['results']) > 0:
                        return data['results'][0]['value']
            else:
                url = f"https://api.polygon.io/v3/quotes/{asset['ticker']}?limit=1&apikey={POLYGON_PRIMARY}"
                response = requests.get(url, timeout=5, verify=True)
                if response.status_code == 200:
                    data = response.json()
                    if 'results' in data and len(data['results']) > 0:
                        quote = data['results'][0]
                        bid = quote.get('bid_price', 0)
                        ask = quote.get('ask_price', 0)
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

        # Factor 4: Price trend (15 points)
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
        """Calculate momentum"""
        if asset_name not in self.prices or asset_name not in self.previous_prices:
            return 'NEUTRAL'

        current = self.prices[asset_name]
        previous = self.previous_prices[asset_name]
        change_pct = ((current - previous) / previous) * 100

        if change_pct > 0.08:
            return 'BULLISH'
        elif change_pct < -0.08:
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

    def generate_trade_setup(self, asset_name, price, momentum):
        """Generate HIGH CONFIDENCE trades with dealer positioning"""
        trade_key = f"{asset_name}_{int(price)}"
        current_time = time.time()

        # Longer cooldown for SPX/NDX to reduce alert frequency
        cooldown = 600 if asset_name in ['SPX', 'NDX'] else 300  # 10min for indices, 5min for ETFs

        if trade_key in self.last_trade_alert:
            if current_time - self.last_trade_alert[trade_key] < cooldown:
                return None

        # Get asset-specific minimum confidence
        min_confidence = ASSETS[asset_name]['min_confidence']

        # Analyze dealer positioning
        positioning = self.analyze_options_chain(asset_name, price)

        if asset_name in ['SPX', 'NDX']:
            support, resistance = self.find_nearest_levels(asset_name, price)

            if support and resistance:
                distance_to_support = price - support
                distance_to_resistance = resistance - price

                # LONG setup - Near support OR bullish breakout at resistance
                if (distance_to_support <= 10 and momentum in ['BULLISH', 'NEUTRAL']) or \
                   (distance_to_resistance <= 10 and momentum == 'BULLISH'):

                    # Different reasons based on setup type
                    if distance_to_support <= 10:
                        setup_reason = f'Near support {support} with {momentum} momentum'
                    else:
                        setup_reason = f'Bullish breakout at resistance {resistance}'

                    confidence_score, confidence_reasons = self.calculate_confidence_score(
                        asset_name, price, momentum, 'LONG', positioning
                    )

                    if confidence_score < min_confidence:
                        return None

                    self.last_trade_alert[trade_key] = current_time
                    target1 = round(price + (distance_to_resistance * 0.5), 2)
                    contract, strike = self.calculate_option_strike(asset_name, price, 'LONG', target1)

                    return {
                        'asset': asset_name,
                        'type': 'LONG',
                        'reason': setup_reason,
                        'entry': round(price, 2),
                        'stop': round(support - 5, 2) if distance_to_support <= 10 else round(resistance - 5, 2),
                        'target1': target1,
                        'target2': round(resistance + 10, 2) if distance_to_support <= 10 else round(resistance + 20, 2),
                        'confidence_score': confidence_score,
                        'confidence_reasons': confidence_reasons,
                        'contract': contract,
                        'strike': strike,
                        'option_type': 'CALL',
                        'timestamp': datetime.now().isoformat(),
                        'positioning': positioning
                    }

                # SHORT setup - Near resistance OR bearish breakdown at support
                elif (distance_to_resistance <= 10 and momentum in ['BEARISH', 'NEUTRAL']) or \
                     (distance_to_support <= 10 and momentum == 'BEARISH'):

                    # Different reasons based on setup type
                    if distance_to_resistance <= 10:
                        setup_reason = f'Near resistance {resistance} with {momentum} momentum'
                    else:
                        setup_reason = f'Bearish breakdown at support {support}'

                    confidence_score, confidence_reasons = self.calculate_confidence_score(
                        asset_name, price, momentum, 'SHORT', positioning
                    )

                    if confidence_score < min_confidence:
                        return None

                    self.last_trade_alert[trade_key] = current_time
                    target1 = round(price - (distance_to_support * 0.5), 2)
                    contract, strike = self.calculate_option_strike(asset_name, price, 'SHORT', target1)

                    return {
                        'asset': asset_name,
                        'type': 'SHORT',
                        'reason': setup_reason,
                        'entry': round(price, 2),
                        'stop': round(resistance + 5, 2) if distance_to_resistance <= 10 else round(support + 5, 2),
                        'target1': target1,
                        'target2': round(support - 10, 2) if distance_to_resistance <= 10 else round(support - 20, 2),
                        'confidence_score': confidence_score,
                        'confidence_reasons': confidence_reasons,
                        'contract': contract,
                        'strike': strike,
                        'option_type': 'PUT',
                        'timestamp': datetime.now().isoformat(),
                        'positioning': positioning
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

                    self.last_trade_alert[trade_key] = current_time
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

                    self.last_trade_alert[trade_key] = current_time
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

        payload = {
            'username': f'{emoji} Dealer Positioning Scanner',
            'embeds': [{
                'title': title,
                'description': f"**{trade['reason']}**\n\n📄 **CONTRACT:** `{trade['contract']}`{positioning_text}\n\n**Confidence Factors:**\n{reasons_text}",
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
        except Exception as e:
            print(f"❌ Error: {e}")

    def check_exit_conditions(self, trade_id, current_price):
        """Monitor exits"""
        if trade_id not in self.active_trades:
            return None

        trade = self.active_trades[trade_id]
        exit_reason = None
        exit_action = None

        if trade['type'] == 'LONG':
            if current_price <= trade['stop']:
                exit_reason = f"🛑 STOP LOSS @ ${current_price:,.2f}"
                exit_action = 'STOP_LOSS'
            elif current_price >= trade['target1'] and not trade.get('target1_hit'):
                exit_reason = f"🎯 TARGET 1 @ ${current_price:,.2f} - Take 50%"
                exit_action = 'TARGET1'
                trade['target1_hit'] = True
            elif current_price >= trade['target2']:
                exit_reason = f"🎯 TARGET 2 @ ${current_price:,.2f} - FULL EXIT!"
                exit_action = 'TARGET2'
        else:
            if current_price >= trade['stop']:
                exit_reason = f"🛑 STOP LOSS @ ${current_price:,.2f}"
                exit_action = 'STOP_LOSS'
            elif current_price <= trade['target1'] and not trade.get('target1_hit'):
                exit_reason = f"🎯 TARGET 1 @ ${current_price:,.2f} - Take 50%"
                exit_action = 'TARGET1'
                trade['target1_hit'] = True
            elif current_price <= trade['target2']:
                exit_reason = f"🎯 TARGET 2 @ ${current_price:,.2f} - FULL EXIT!"
                exit_action = 'TARGET2'

        if exit_reason:
            if trade['type'] == 'LONG':
                pnl_pct = ((current_price - trade['entry']) / trade['entry']) * 100
            else:
                pnl_pct = ((trade['entry'] - current_price) / trade['entry']) * 100

            return {
                'trade_id': trade_id,
                'exit_reason': exit_reason,
                'exit_action': exit_action,
                'current_price': current_price,
                'pnl_pct': round(pnl_pct, 2),
                'trade': trade
            }
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

        payload = {
            'username': f'{emoji} Exit Alert',
            'embeds': [{
                'title': f"{emoji} {trade['asset']} {trade['type']} - {exit_info['exit_action']}",
                'description': f"**{exit_info['exit_reason']}**\n\n📄 `{trade['contract']}`",
                'color': color,
                'timestamp': datetime.utcnow().isoformat(),
                'fields': [
                    {'name': '📍 Entry', 'value': f"${trade['entry']:,.2f}", 'inline': True},
                    {'name': '📍 Exit', 'value': f"${exit_info['current_price']:,.2f}", 'inline': True},
                    {'name': '💵 P&L', 'value': f"{exit_info['pnl_pct']:+.2f}%", 'inline': True}
                ]
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
            if exit_info['exit_action'] in ['TARGET2', 'STOP_LOSS']:
                self.trade_history.append({'trade': self.active_trades[exit_info['trade_id']], 'exit': exit_info})
                del self.active_trades[exit_info['trade_id']]
                self.save_trade_history()

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
            time.sleep(10)

    def stop(self):
        """Stop scanner"""
        self.running = False
        print(f"\n{'='*80}")
        print(f"🛑 SCANNER STOPPED | Active: {len(self.active_trades)} | Completed: {len(self.trade_history)}")
        print(f"{'='*80}")

if __name__ == "__main__":
    scanner = DealerPositioningScanner()
    try:
        scanner.start()
    except KeyboardInterrupt:
        print("\n\nInterrupt received...")
        scanner.stop()
