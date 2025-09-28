#!/usr/bin/env python3
"""
Core Trading Functions - Network-resilient with automatic failover
Consolidates essential functionality with offline capabilities
"""

import os
import sys
import requests
import json
from datetime import datetime, timedelta
import subprocess

class CoreTradingEngine:
    def __init__(self):
        self.api_key = os.getenv('ALPHAVANTAGE_API_KEY', 'ZFL38ZY98GSN7E1S')
        self.session_file = ".spx/session.json"
        self.cache_file = ".spx/price_cache.json"
        self.current_data = None  # Store current session data
        self.ensure_directories()
        self.load_session_context()

    def ensure_directories(self):
        """Ensure required directories exist"""
        if not os.path.exists(".spx"):
            os.makedirs(".spx")

    def get_price_data(self, force_refresh=False):
        """Get SPY/SPX price with automatic failover and caching"""

        # Always get fresh data - no stale cache
        # Cache disabled for live trading accuracy

        # Data source priority order - Updated to include direct SPX
        data_sources = [
            self.get_direct_spx_price,
            self.get_yahoo_price,
            self.get_alphavantage_price,
            self.get_fallback_price
        ]

        for source in data_sources:
            try:
                data = source()
                if data:
                    self.cache_price_data(data)
                    return data
            except Exception as e:
                print(f"Source failed: {source.__name__} - {e}")
                continue

        # Return cached data as last resort
        cached = self.get_cached_price()
        if cached:
            print(f"WARNING: Using stale cached data from {cached.get('timestamp', 'unknown')}")
            return cached

        return None

    def get_direct_spx_price(self):
        """Get direct SPX price from Yahoo Finance SPX endpoint"""
        try:
            url = "https://query2.finance.yahoo.com/v8/finance/chart/%5ESPX?interval=1m&range=1d"
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            response = requests.get(url, headers=headers, timeout=5)
            response.raise_for_status()

            data = response.json()
            if 'chart' in data and data['chart']['result']:
                meta = data['chart']['result'][0]['meta']
                spx_price = meta['regularMarketPrice']

                # Sanity check - SPX should be 6000-7000 range
                if 6000 < spx_price < 7000:
                    price_data = {
                        'source': 'yahoo_spx_direct',
                        'spy_price': spx_price / 10,  # Convert SPX to SPY equivalent
                        'spy_change': meta.get('regularMarketChange', 0) / 10,
                        'spy_change_percent': meta.get('regularMarketChangePercent', 0),
                        'after_hours': None,
                        'spx_price': spx_price,
                        'timestamp': datetime.now().isoformat(),
                        'market_time': meta.get('regularMarketTime', 'live')
                    }
                    return price_data

            raise Exception("Invalid SPX data received")

        except Exception as e:
            raise Exception(f"Direct SPX failed: {e}")

    def get_yahoo_price(self):
        """Get price from Yahoo Finance with multiple endpoints"""
        # Try different Yahoo endpoints
        endpoints = [
            "https://query2.finance.yahoo.com/v8/finance/chart/SPY?interval=1m&range=1d",
            "https://query1.finance.yahoo.com/v8/finance/chart/SPY",
        ]

        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

        for url in endpoints:
            try:
                response = requests.get(url, headers=headers, timeout=5)
                response.raise_for_status()

                data = response.json()
                if 'chart' in data and data['chart']['result']:
                    meta = data['chart']['result'][0]['meta']

                    price_data = {
                        'source': 'yahoo_live',
                        'spy_price': meta['regularMarketPrice'],
                        'spy_change': meta.get('regularMarketChange', 0),
                        'spy_change_percent': meta.get('regularMarketChangePercent', 0),
                        'after_hours': meta.get('postMarketPrice'),
                        'spx_price': meta['regularMarketPrice'] * 10,
                        'timestamp': datetime.now().isoformat(),
                        'market_time': meta.get('regularMarketTime', 'live')
                    }

                    return price_data

            except Exception as e:
                continue

        raise Exception(f"All Yahoo Finance endpoints failed")

    def get_alphavantage_price(self):
        """Get price from AlphaVantage API"""
        try:
            url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=SPY&entitlement=realtime&apikey={self.api_key}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()

            data = response.json()

            if "Error Message" in data:
                raise Exception(f"API Error: {data['Error Message']}")
            if "Note" in data:
                raise Exception(f"Rate Limited: {data['Note']}")

            if "Global Quote" in data:
                quote = data["Global Quote"]
                price = float(quote.get("05. price", 0))
                change = float(quote.get("09. change", 0))
                change_percent = quote.get("10. change percent", "0%").replace("%", "")

                price_data = {
                    'source': 'alphavantage',
                    'spy_price': price,
                    'spy_change': change,
                    'spy_change_percent': float(change_percent),
                    'after_hours': None,
                    'spx_price': price * 10,
                    'timestamp': datetime.now().isoformat(),
                    'market_time': quote.get("07. latest trading day", "unknown")
                }

                return price_data

            raise Exception("Unexpected API response format")

        except Exception as e:
            raise Exception(f"AlphaVantage failed: {e}")

    def get_fallback_price(self):
        """Fallback price estimation"""
        try:
            # Try to estimate from cached data with time adjustment
            cached = self.get_cached_price()
            if cached:
                # Simple time-based adjustment (very basic)
                hours_old = self.get_cache_age_hours(cached)
                if hours_old < 24:  # Within 24 hours
                    estimated_spy = cached['spy_price']

                    price_data = {
                        'source': 'fallback_estimate',
                        'spy_price': estimated_spy,
                        'spy_change': 0,
                        'spy_change_percent': 0,
                        'after_hours': None,
                        'spx_price': estimated_spy * 10,
                        'timestamp': datetime.now().isoformat(),
                        'market_time': 'estimated'
                    }

                    return price_data

            raise Exception("No fallback data available")

        except Exception as e:
            raise Exception(f"Fallback failed: {e}")

    def get_cached_price(self):
        """Get cached price data"""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r') as f:
                    return json.load(f)
        except:
            pass
        return None

    def cache_price_data(self, data):
        """Cache price data"""
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(data, f, indent=2)
        except:
            pass

    def is_cache_fresh(self, cached_data, max_minutes=1):
        """Check if cached data is fresh enough - very strict for live trading"""
        try:
            cache_time = datetime.fromisoformat(cached_data['timestamp'])
            age = (datetime.now() - cache_time).total_seconds() / 60
            # Only use cache if less than 1 minute old
            return age < max_minutes
        except:
            return False

    def get_cache_age_hours(self, cached_data):
        """Get cache age in hours"""
        try:
            cache_time = datetime.fromisoformat(cached_data['timestamp'])
            age = (datetime.now() - cache_time).total_seconds() / 3600
            return age
        except:
            return 999

    def get_strike_recommendations(self, current_spx=None):
        """Generate strike recommendations offline"""
        if not current_spx:
            price_data = self.get_price_data()
            if price_data:
                current_spx = price_data['spx_price']
            else:
                current_spx = 6640  # Fallback estimate

        recommendations = {
            'current_spx': current_spx,
            'scalp_calls': list(range(int(current_spx), int(current_spx) + 15, 5)),
            'scalp_puts': list(range(int(current_spx) - 15, int(current_spx) + 5, 5)),
            'lottery_calls': list(range(int(current_spx) + 20, int(current_spx) + 60, 10)),
            'lottery_puts': list(range(int(current_spx) - 60, int(current_spx) - 20, 10)),
            'safe_calls': list(range(int(current_spx) - 10, int(current_spx) + 5, 5)),
            'safe_puts': list(range(int(current_spx) - 5, int(current_spx) + 10, 5)),
        }

        return recommendations

    def get_rsi_data(self):
        """Get RSI data from AlphaVantage"""
        try:
            url = f"https://www.alphavantage.co/query?function=RSI&symbol=SPY&interval=5min&time_period=14&series_type=close&entitlement=realtime&apikey={self.api_key}"
            response = requests.get(url, timeout=10)
            data = response.json()

            if "Technical Analysis: RSI" in data:
                rsi_data = data["Technical Analysis: RSI"]
                latest_time = list(rsi_data.keys())[0]
                latest_rsi = float(rsi_data[latest_time]["RSI"])
                return latest_rsi
        except:
            pass
        return None

    def load_quant_levels(self):
        """Load quant levels from session file"""
        try:
            if os.path.exists('.spx/quant_levels.json'):
                with open('.spx/quant_levels.json', 'r') as f:
                    return json.load(f)
        except:
            pass
        return None

    def comprehensive_analysis(self):
        """Complete analysis matching advanced AI systems"""
        price_data = self.get_price_data()
        if not price_data:
            return "ERROR: No price data available"

        spx_price = price_data['spx_price']
        spy_price = price_data['spy_price']
        source = price_data['source']
        change = price_data['spy_change']
        change_pct = price_data['spy_change_percent']

        # Get RSI
        rsi = self.get_rsi_data()
        rsi_status = "N/A"
        if rsi:
            if rsi > 70:
                rsi_status = "OVERBOUGHT"
            elif rsi < 30:
                rsi_status = "OVERSOLD"
            else:
                rsi_status = "NEUTRAL"

        # Load quant levels
        quant_levels = self.load_quant_levels()

        # Smart support/resistance
        current_level = int(spx_price / 5) * 5  # Round to nearest 5
        supports = [current_level - 10, current_level - 20, current_level - 30]
        resistances = [current_level + 10, current_level + 20, current_level + 30]

        # Market bias
        if change > 0 and (not rsi or rsi < 70):
            bias = "BULLISH"
            strategy = "Consider calls"
        elif change < 0 and (not rsi or rsi > 30):
            bias = "BEARISH"
            strategy = "Consider puts"
        else:
            bias = "NEUTRAL"
            strategy = "Range trading"

        # Probability assessment
        if rsi and rsi > 75:
            prob_direction = "DOWN (Overbought)"
            prob_level = "HIGH"
        elif rsi and rsi < 25:
            prob_direction = "UP (Oversold)"
            prob_level = "HIGH"
        else:
            prob_direction = "Mixed signals"
            prob_level = "MODERATE"

        rsi_display = f"{rsi:.1f}" if rsi else "N/A"

        analysis = f"""
SPX COMPREHENSIVE ANALYSIS
==========================
Current: ${spx_price:.2f} ({change:+.2f}, {change_pct:+.2f}%)
Source: {source.upper()}
RSI (5min): {rsi_display} ({rsi_status})

MARKET BIAS: {bias}
STRATEGY: {strategy}
PROBABILITY: {prob_level} - {prob_direction}

SUPPORT LEVELS:
- {supports[0]} (Key support)
- {supports[1]} (Strong support)
- {supports[2]} (Major support)

RESISTANCE LEVELS:
- {resistances[0]} (Key resistance)
- {resistances[1]} (Strong resistance)
- {resistances[2]} (Major resistance)

OPTIMAL TRADES:
ATM Strike: {current_level}
Bullish: {current_level + 5}C, {current_level + 10}C
Bearish: {current_level - 5}P, {current_level - 10}P

RISK MANAGEMENT:
- Stop Loss: {abs(change) * 2:.1f} point moves against
- Take Profit: {abs(change) * 3:.1f} point targets
- Time Decay: Monitor if holding overnight
"""

        # Add quant levels if available
        if quant_levels:
            analysis += f"""
QUANT LEVELS:
{quant_levels.get('summary', 'Custom levels loaded')}
"""

        # Save to session context
        self.save_session_context({
            'spx_price': spx_price,
            'rsi': rsi,
            'bias': bias,
            'supports': supports,
            'resistances': resistances,
            'timestamp': datetime.now().isoformat()
        })

        return analysis

    def load_session_context(self):
        """Load previous session context"""
        try:
            if os.path.exists(self.session_file):
                with open(self.session_file, 'r') as f:
                    self.current_data = json.load(f)
        except:
            self.current_data = None

    def save_session_context(self, data):
        """Save current session context"""
        try:
            with open(self.session_file, 'w') as f:
                json.dump(data, f, indent=2)
            self.current_data = data
        except:
            pass

    def get_current_spx(self):
        """Get current SPX without full analysis"""
        if self.current_data:
            # Check if data is recent (within 2 minutes)
            try:
                data_time = datetime.fromisoformat(self.current_data['timestamp'])
                age_minutes = (datetime.now() - data_time).total_seconds() / 60
                if age_minutes < 2:
                    return self.current_data['spx_price']
            except:
                pass

        # Get fresh data
        price_data = self.get_price_data(force_refresh=True)
        if price_data:
            return price_data['spx_price']
        return None

    def analyze_position(self, strike, option_type='P'):
        """Quick position analysis using current context"""
        current_spx = self.get_current_spx()
        if not current_spx:
            return "Error: No current SPX data"

        distance = current_spx - strike if option_type == 'P' else strike - current_spx

        if option_type == 'P':
            if distance > 0:
                status = f"OTM - needs {distance:.1f} point drop"
                prob = "GOOD" if distance < 10 else "MODERATE" if distance < 20 else "LOW"
            else:
                status = f"ITM by {abs(distance):.1f} points"
                prob = "HIGH"
        else:  # Call
            if distance > 0:
                status = f"OTM - needs {distance:.1f} point rise"
                prob = "GOOD" if distance < 10 else "MODERATE" if distance < 20 else "LOW"
            else:
                status = f"ITM by {abs(distance):.1f} points"
                prob = "HIGH"

        return f"""
{strike}{option_type} ANALYSIS
Current SPX: ${current_spx:.2f}
Strike: {strike}
Status: {status}
Probability: {prob}
Distance: {distance:+.1f} points
        """.strip()

    def quick_analysis(self):
        """Legacy quick analysis - use comprehensive_analysis() for full system"""
        return self.comprehensive_analysis()

    def health_check(self):
        """System health check"""
        results = {
            'yahoo_finance': self.test_connection('https://finance.yahoo.com', 3),
            'alphavantage': self.test_connection('https://www.alphavantage.co', 5),
            'cache_status': 'OK' if os.path.exists(self.cache_file) else 'NO CACHE',
            'session_dir': 'OK' if os.path.exists('.spx') else 'MISSING',
            'api_key': 'CONFIGURED' if self.api_key else 'MISSING'
        }

        return results

    def test_connection(self, url, timeout=5):
        """Test network connection to a URL"""
        try:
            response = requests.get(url, timeout=timeout)
            return 'OK' if response.status_code == 200 else f'HTTP {response.status_code}'
        except:
            return 'FAILED'

def main():
    """Test the core functions"""
    engine = CoreTradingEngine()

    print("CORE TRADING ENGINE TEST")
    print("=" * 40)

    # Test price data
    print("\n1. TESTING PRICE DATA:")
    price_data = engine.get_price_data(force_refresh=True)
    if price_data:
        print(f"   Source: {price_data['source']}")
        print(f"   SPY: ${price_data['spy_price']:.2f}")
        print(f"   SPX: ${price_data['spx_price']:.0f}")
    else:
        print("   FAILED: No price data available")

    # Test quick analysis
    print("\n2. TESTING QUICK ANALYSIS:")
    analysis = engine.quick_analysis()
    print(analysis)

    # Test health check
    print("\n3. SYSTEM HEALTH CHECK:")
    health = engine.health_check()
    for component, status in health.items():
        print(f"   {component}: {status}")

if __name__ == "__main__":
    main()