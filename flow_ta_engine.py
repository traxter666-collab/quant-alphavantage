#!/usr/bin/env python3
"""
OPTIONS FLOW TECHNICAL ANALYSIS ENGINE
Analyzes underlying stocks to identify setups primed for movement
Integrates: AlphaVantage + Polygon Level 2/3 data + Technical indicators
"""
import os
import requests
from datetime import datetime, timedelta

class FlowTechnicalAnalyzer:
    def __init__(self):
        self.av_key = os.getenv('ALPHAVANTAGE_API_KEY', 'ZFL38ZY98GSN7E1S')
        self.polygon_key = os.getenv('POLYGON_API_KEY', '')  # User needs to provide

    def analyze_ticker(self, ticker, option_type, strike, premium_value):
        """
        Complete technical analysis to determine if underlying is primed for move

        Args:
            ticker: Stock symbol
            option_type: 'calls_bought', 'puts_sold', 'puts_bought', 'calls_sold'
            strike: Option strike price
            premium_value: Premium in dollars

        Returns:
            dict with TA score (0-100) and analysis details
        """
        print(f"\n🔍 Analyzing {ticker} for {option_type}...")

        analysis = {
            'ticker': ticker,
            'option_type': option_type,
            'strike': strike,
            'premium_value': premium_value,
            'ta_score': 0,
            'price': 0,
            'setup_quality': 'UNKNOWN',
            'signals': [],
            'level2_data': {},
            'technical_indicators': {},
            'recommendation': 'ANALYZE'
        }

        try:
            # Step 1: Get current price and basic data
            price_data = self._get_current_price(ticker)
            if not price_data:
                return analysis

            analysis['price'] = price_data['price']
            analysis['volume'] = price_data.get('volume', 0)
            analysis['change_pct'] = price_data.get('change_pct', 0)

            # Step 2: Technical indicators analysis
            technical_score = self._analyze_technical_indicators(ticker, analysis)

            # Step 3: Volume analysis
            volume_score = self._analyze_volume_profile(ticker, analysis)

            # Step 4: Level 2/3 data from Polygon (if available)
            level2_score = self._analyze_level2_data(ticker, analysis)

            # Step 5: Momentum and trend analysis
            momentum_score = self._analyze_momentum(ticker, analysis)

            # Step 6: Strike relationship analysis
            strike_score = self._analyze_strike_relationship(
                analysis['price'], strike, option_type, analysis
            )

            # Step 7: Options flow confirmation
            flow_score = self._analyze_flow_confirmation(
                option_type, premium_value, analysis
            )

            # Calculate total TA score (0-100)
            analysis['ta_score'] = (
                technical_score * 0.25 +
                volume_score * 0.15 +
                level2_score * 0.20 +
                momentum_score * 0.20 +
                strike_score * 0.10 +
                flow_score * 0.10
            )

            # Determine setup quality
            if analysis['ta_score'] >= 75:
                analysis['setup_quality'] = 'EXCELLENT'
                analysis['recommendation'] = 'STRONG BUY'
            elif analysis['ta_score'] >= 60:
                analysis['setup_quality'] = 'GOOD'
                analysis['recommendation'] = 'BUY'
            elif analysis['ta_score'] >= 45:
                analysis['setup_quality'] = 'FAIR'
                analysis['recommendation'] = 'CONSIDER'
            else:
                analysis['setup_quality'] = 'POOR'
                analysis['recommendation'] = 'AVOID'

        except Exception as e:
            print(f"⚠️ Error analyzing {ticker}: {e}")

        return analysis

    def _get_current_price(self, ticker):
        """Get current price from AlphaVantage"""
        try:
            url = f"https://www.alphavantage.co/query"
            params = {
                'function': 'GLOBAL_QUOTE',
                'symbol': ticker,
                'apikey': self.av_key
            }

            response = requests.get(url, params=params, timeout=10)
            data = response.json()

            if 'Global Quote' in data and data['Global Quote']:
                quote = data['Global Quote']
                return {
                    'price': float(quote.get('05. price', 0)),
                    'volume': int(quote.get('06. volume', 0)),
                    'change_pct': float(quote.get('10. change percent', '0').replace('%', ''))
                }
        except Exception as e:
            print(f"⚠️ Error fetching price for {ticker}: {e}")

        return None

    def _analyze_technical_indicators(self, ticker, analysis):
        """
        Analyze RSI, MACD, EMA for setup quality
        Returns score 0-100
        """
        score = 0
        signals = []

        try:
            # Get RSI
            rsi = self._get_rsi(ticker)
            if rsi:
                analysis['technical_indicators']['rsi'] = rsi

                # RSI scoring
                if 30 <= rsi <= 40:  # Oversold but not extreme
                    score += 25
                    signals.append(f"RSI {rsi:.1f} - Oversold bounce setup")
                elif 60 <= rsi <= 70:  # Overbought but sustainable
                    score += 20
                    signals.append(f"RSI {rsi:.1f} - Strong momentum")
                elif rsi > 70:
                    score += 10
                    signals.append(f"RSI {rsi:.1f} - Overbought warning")
                elif rsi < 30:
                    score += 15
                    signals.append(f"RSI {rsi:.1f} - Extreme oversold")
                else:
                    score += 12

            # Get MACD
            macd_data = self._get_macd(ticker)
            if macd_data:
                analysis['technical_indicators']['macd'] = macd_data

                macd = macd_data.get('macd', 0)
                signal = macd_data.get('signal', 0)

                if macd > signal and macd > 0:
                    score += 25
                    signals.append("MACD bullish crossover")
                elif macd > signal:
                    score += 20
                    signals.append("MACD turning bullish")
                elif macd < signal and macd < 0:
                    score += 15
                    signals.append("MACD bearish (contrarian opportunity)")

            # Get EMA analysis
            ema_data = self._get_ema_structure(ticker)
            if ema_data:
                analysis['technical_indicators']['ema'] = ema_data

                if ema_data.get('bullish_alignment'):
                    score += 25
                    signals.append("EMA bullish alignment (9>21>50)")
                elif ema_data.get('near_crossover'):
                    score += 20
                    signals.append("EMA near bullish crossover")
                else:
                    score += 10

        except Exception as e:
            print(f"⚠️ Technical indicators error for {ticker}: {e}")

        analysis['signals'].extend(signals)
        return min(score, 100)

    def _analyze_volume_profile(self, ticker, analysis):
        """
        Analyze volume patterns for institutional activity
        Returns score 0-100
        """
        score = 0
        signals = []

        try:
            current_volume = analysis.get('volume', 0)

            # Get average volume
            avg_volume = self._get_average_volume(ticker)

            if avg_volume and current_volume:
                volume_ratio = current_volume / avg_volume

                if volume_ratio > 2.0:
                    score += 30
                    signals.append(f"Volume {volume_ratio:.1f}x average - Strong institutional activity")
                elif volume_ratio > 1.5:
                    score += 25
                    signals.append(f"Volume {volume_ratio:.1f}x average - Above average interest")
                elif volume_ratio > 1.0:
                    score += 15
                    signals.append(f"Volume {volume_ratio:.1f}x average - Normal activity")
                else:
                    score += 5
                    signals.append(f"Volume {volume_ratio:.1f}x average - Below average")

                analysis['technical_indicators']['volume_ratio'] = volume_ratio

        except Exception as e:
            print(f"⚠️ Volume analysis error for {ticker}: {e}")

        analysis['signals'].extend(signals)
        return min(score, 100)

    def _analyze_level2_data(self, ticker, analysis):
        """
        Analyze Level 2/3 data from Polygon if available
        Returns score 0-100
        """
        score = 50  # Default neutral score if no Polygon key
        signals = []

        if not self.polygon_key:
            signals.append("Level 2 data unavailable (Polygon API key not set)")
            analysis['signals'].extend(signals)
            return score

        try:
            # Get Level 2 quotes from Polygon
            level2 = self._get_polygon_level2(ticker)

            if level2:
                analysis['level2_data'] = level2

                # Analyze bid/ask spread
                spread = level2.get('spread', 0)
                spread_pct = level2.get('spread_pct', 0)

                if spread_pct < 0.1:
                    score += 20
                    signals.append(f"Tight spread {spread_pct:.2f}% - High liquidity")
                elif spread_pct < 0.5:
                    score += 10
                    signals.append(f"Normal spread {spread_pct:.2f}%")
                else:
                    score -= 10
                    signals.append(f"Wide spread {spread_pct:.2f}% - Low liquidity warning")

                # Analyze bid/ask size imbalance
                bid_size = level2.get('bid_size', 0)
                ask_size = level2.get('ask_size', 0)

                if bid_size and ask_size:
                    imbalance = (bid_size - ask_size) / (bid_size + ask_size)

                    if imbalance > 0.3:
                        score += 15
                        signals.append(f"Strong bid support - {imbalance*100:.1f}% imbalance")
                    elif imbalance < -0.3:
                        score -= 10
                        signals.append(f"Heavy ask resistance - {abs(imbalance)*100:.1f}% imbalance")

                # Get NBBO (National Best Bid/Offer)
                nbbo = self._get_polygon_nbbo(ticker)
                if nbbo:
                    analysis['level2_data']['nbbo'] = nbbo
                    signals.append("NBBO data available - institutional routing confirmed")

        except Exception as e:
            print(f"⚠️ Level 2 analysis error for {ticker}: {e}")

        analysis['signals'].extend(signals)
        return min(max(score, 0), 100)

    def _analyze_momentum(self, ticker, analysis):
        """
        Analyze price momentum and trend strength
        Returns score 0-100
        """
        score = 0
        signals = []

        try:
            change_pct = analysis.get('change_pct', 0)

            # Today's momentum
            if abs(change_pct) > 3:
                score += 25
                direction = "up" if change_pct > 0 else "down"
                signals.append(f"Strong momentum - {abs(change_pct):.1f}% {direction} today")
            elif abs(change_pct) > 1:
                score += 15
                direction = "up" if change_pct > 0 else "down"
                signals.append(f"Moderate momentum - {abs(change_pct):.1f}% {direction} today")
            else:
                score += 5

            # Multi-day momentum
            momentum_5d = self._get_momentum_5day(ticker)
            if momentum_5d:
                analysis['technical_indicators']['momentum_5d'] = momentum_5d

                if abs(momentum_5d) > 10:
                    score += 20
                    direction = "bullish" if momentum_5d > 0 else "bearish"
                    signals.append(f"Strong 5-day trend - {abs(momentum_5d):.1f}% {direction}")
                elif abs(momentum_5d) > 5:
                    score += 15

        except Exception as e:
            print(f"⚠️ Momentum analysis error for {ticker}: {e}")

        analysis['signals'].extend(signals)
        return min(score, 100)

    def _analyze_strike_relationship(self, price, strike, option_type, analysis):
        """
        Analyze relationship between current price and option strike
        Returns score 0-100
        """
        score = 0
        signals = []

        try:
            strike_float = float(strike)
            distance_pct = ((strike_float - price) / price) * 100

            if option_type == 'calls_bought':
                # For calls bought, want price to move up to strike
                if 0 < distance_pct < 5:  # 0-5% OTM
                    score = 80
                    signals.append(f"Excellent strike - {distance_pct:.1f}% OTM (easy target)")
                elif 5 <= distance_pct < 10:  # 5-10% OTM
                    score = 60
                    signals.append(f"Good strike - {distance_pct:.1f}% OTM (achievable)")
                elif distance_pct < 0:  # ITM
                    score = 70
                    signals.append(f"ITM calls - {abs(distance_pct):.1f}% ITM (high conviction)")
                else:
                    score = 30
                    signals.append(f"Far OTM - {distance_pct:.1f}% (lottery ticket)")

            elif option_type == 'puts_sold':
                # For puts sold, want price to stay above strike
                if 0 < distance_pct < 10:  # Strike 0-10% below price
                    score = 85
                    signals.append(f"Strong support - ${strike_float:.2f} is {distance_pct:.1f}% below")
                elif distance_pct > 10:
                    score = 60
                    signals.append(f"Deep support - ${strike_float:.2f} is {distance_pct:.1f}% below")
                else:
                    score = 40
                    signals.append(f"At-risk support - ${strike_float:.2f}")

        except Exception as e:
            print(f"⚠️ Strike analysis error: {e}")

        analysis['signals'].extend(signals)
        return score

    def _analyze_flow_confirmation(self, option_type, premium_value, analysis):
        """
        Score the options flow itself
        Returns score 0-100
        """
        score = 0
        signals = []

        # Premium size scoring
        if premium_value > 5_000_000:
            score += 40
            signals.append(f"Massive premium - ${premium_value/1_000_000:.1f}M (whale trade)")
        elif premium_value > 2_000_000:
            score += 30
            signals.append(f"Large premium - ${premium_value/1_000_000:.1f}M (institutional)")
        elif premium_value > 500_000:
            score += 20
            signals.append(f"Significant premium - ${premium_value/1_000:.0f}K")
        else:
            score += 10

        # Option type confirmation
        if option_type in ['calls_bought', 'puts_sold']:
            signals.append("Bullish flow - aligns with upside setup")
        else:
            signals.append("Bearish flow - hedge or downside bet")

        analysis['signals'].extend(signals)
        return score

    # Helper functions for data retrieval

    def _get_rsi(self, ticker, interval='daily', period=14):
        """Get RSI from AlphaVantage"""
        try:
            url = f"https://www.alphavantage.co/query"
            params = {
                'function': 'RSI',
                'symbol': ticker,
                'interval': interval,
                'time_period': period,
                'series_type': 'close',
                'apikey': self.av_key
            }

            response = requests.get(url, params=params, timeout=10)
            data = response.json()

            if 'Technical Analysis: RSI' in data:
                latest = list(data['Technical Analysis: RSI'].values())[0]
                return float(latest['RSI'])
        except:
            pass
        return None

    def _get_macd(self, ticker, interval='daily'):
        """Get MACD from AlphaVantage"""
        try:
            url = f"https://www.alphavantage.co/query"
            params = {
                'function': 'MACD',
                'symbol': ticker,
                'interval': interval,
                'series_type': 'close',
                'apikey': self.av_key
            }

            response = requests.get(url, params=params, timeout=10)
            data = response.json()

            if 'Technical Analysis: MACD' in data:
                latest = list(data['Technical Analysis: MACD'].values())[0]
                return {
                    'macd': float(latest['MACD']),
                    'signal': float(latest['MACD_Signal']),
                    'histogram': float(latest['MACD_Hist'])
                }
        except:
            pass
        return None

    def _get_ema_structure(self, ticker, interval='daily'):
        """Get EMA 9, 21, 50 structure"""
        try:
            emas = {}
            for period in [9, 21, 50]:
                url = f"https://www.alphavantage.co/query"
                params = {
                    'function': 'EMA',
                    'symbol': ticker,
                    'interval': interval,
                    'time_period': period,
                    'series_type': 'close',
                    'apikey': self.av_key
                }

                response = requests.get(url, params=params, timeout=10)
                data = response.json()

                if 'Technical Analysis: EMA' in data:
                    latest = list(data['Technical Analysis: EMA'].values())[0]
                    emas[f'ema_{period}'] = float(latest['EMA'])

            if len(emas) == 3:
                bullish = emas['ema_9'] > emas['ema_21'] > emas['ema_50']
                near_cross = abs(emas['ema_9'] - emas['ema_21']) / emas['ema_21'] < 0.01

                return {
                    **emas,
                    'bullish_alignment': bullish,
                    'near_crossover': near_cross
                }
        except:
            pass
        return None

    def _get_average_volume(self, ticker):
        """Get 20-day average volume"""
        try:
            url = f"https://www.alphavantage.co/query"
            params = {
                'function': 'TIME_SERIES_DAILY',
                'symbol': ticker,
                'outputsize': 'compact',
                'apikey': self.av_key
            }

            response = requests.get(url, params=params, timeout=10)
            data = response.json()

            if 'Time Series (Daily)' in data:
                volumes = [
                    int(day['5. volume'])
                    for day in list(data['Time Series (Daily)'].values())[:20]
                ]
                return sum(volumes) / len(volumes)
        except:
            pass
        return None

    def _get_momentum_5day(self, ticker):
        """Get 5-day price momentum"""
        try:
            url = f"https://www.alphavantage.co/query"
            params = {
                'function': 'TIME_SERIES_DAILY',
                'symbol': ticker,
                'outputsize': 'compact',
                'apikey': self.av_key
            }

            response = requests.get(url, params=params, timeout=10)
            data = response.json()

            if 'Time Series (Daily)' in data:
                prices = list(data['Time Series (Daily)'].values())
                if len(prices) >= 5:
                    current = float(prices[0]['4. close'])
                    five_days_ago = float(prices[4]['4. close'])
                    return ((current - five_days_ago) / five_days_ago) * 100
        except:
            pass
        return None

    def _get_polygon_level2(self, ticker):
        """Get Level 2 quotes from Polygon"""
        if not self.polygon_key:
            return None

        try:
            url = f"https://api.polygon.io/v2/last/nbbo/{ticker}"
            params = {'apiKey': self.polygon_key}

            response = requests.get(url, params=params, timeout=10)
            data = response.json()

            if data.get('status') == 'OK' and 'results' in data:
                results = data['results']
                bid = results.get('P', 0)
                ask = results.get('p', 0)

                return {
                    'bid': bid,
                    'ask': ask,
                    'spread': ask - bid,
                    'spread_pct': ((ask - bid) / bid * 100) if bid else 0,
                    'bid_size': results.get('S', 0),
                    'ask_size': results.get('s', 0)
                }
        except Exception as e:
            print(f"⚠️ Polygon Level 2 error for {ticker}: {e}")

        return None

    def _get_polygon_nbbo(self, ticker):
        """Get NBBO from Polygon"""
        if not self.polygon_key:
            return None

        try:
            url = f"https://api.polygon.io/v3/quotes/{ticker}"
            params = {
                'apiKey': self.polygon_key,
                'limit': 1,
                'order': 'desc',
                'sort': 'timestamp'
            }

            response = requests.get(url, params=params, timeout=10)
            data = response.json()

            if data.get('status') == 'OK' and data.get('results'):
                return data['results'][0]
        except Exception as e:
            print(f"⚠️ Polygon NBBO error for {ticker}: {e}")

        return None


def main():
    """Test the TA engine"""
    analyzer = FlowTechnicalAnalyzer()

    # Test with sample ticker
    test_ticker = "AAPL"
    test_strike = 180
    test_premium = 2_500_000

    print(f"Testing TA Engine with {test_ticker}")
    print("="*60)

    result = analyzer.analyze_ticker(
        test_ticker,
        'calls_bought',
        test_strike,
        test_premium
    )

    print(f"\n{'='*60}")
    print(f"📊 TA SCORE: {result['ta_score']:.1f}/100")
    print(f"🎯 SETUP: {result['setup_quality']}")
    print(f"💡 RECOMMENDATION: {result['recommendation']}")
    print(f"\n📈 Signals:")
    for signal in result['signals']:
        print(f"  • {signal}")

    if result['technical_indicators']:
        print(f"\n📊 Technical Indicators:")
        for key, value in result['technical_indicators'].items():
            print(f"  • {key}: {value}")


if __name__ == "__main__":
    main()
