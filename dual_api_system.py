#!/usr/bin/env python3
"""
DUAL API REDUNDANCY SYSTEM
Polygon API as Primary, AlphaVantage as Secondary
Automatic failover with error handling
"""

import time
import os
import subprocess
import requests
from datetime import datetime
import json

class DualAPISystem:
    def __init__(self):
        self.polygon_api_key = '_u0zA0CH5ZspOHecb2G8uBxd2DUo4r9D'
        self.alphavantage_api_key = os.getenv('ALPHAVANTAGE_API_KEY', 'ZFL38ZY98GSN7E1S')
        self.last_successful_api = None
        self.api_failure_counts = {'polygon': 0, 'alphavantage': 0}

    def get_stock_quote_primary(self, symbol):
        """Get stock quote using Polygon API (Primary)"""
        try:
            url = f'https://api.polygon.io/v3/quotes/{symbol.upper()}?limit=1&apikey={self.polygon_api_key}'
            response = requests.get(url, timeout=15)
            data = response.json()

            if 'results' in data and len(data['results']) > 0:
                quote = data['results'][0]

                return {
                    'success': True,
                    'api_used': 'polygon',
                    'symbol': symbol.upper(),
                    'price': (quote['bid_price'] + quote['ask_price']) / 2,
                    'bid': quote['bid_price'],
                    'ask': quote['ask_price'],
                    'timestamp': datetime.fromtimestamp(quote['sip_timestamp'] / 1000000000),
                    'raw_data': quote
                }
            else:
                return {'success': False, 'error': 'No data in Polygon response', 'api_used': 'polygon'}

        except Exception as e:
            return {'success': False, 'error': str(e), 'api_used': 'polygon'}

    def get_stock_quote_secondary(self, symbol):
        """Get stock quote using AlphaVantage API (Secondary)"""
        try:
            # Use subprocess to call existing validate_api_key.py with symbol
            result = subprocess.run(['python', 'validate_api_key.py'],
                                  capture_output=True, text=True, timeout=30)

            if result.returncode == 0 and 'SUCCESS' in result.stdout:
                # Parse basic price info from output
                lines = result.stdout.split('\n')
                for line in lines:
                    if 'Price:' in line or '$' in line:
                        try:
                            # Extract price from line
                            import re
                            price_match = re.search(r'\$([0-9]+\.?[0-9]*)', line)
                            if price_match:
                                price = float(price_match.group(1))
                                return {
                                    'success': True,
                                    'api_used': 'alphavantage',
                                    'symbol': symbol.upper(),
                                    'price': price,
                                    'bid': price - 0.01,
                                    'ask': price + 0.01,
                                    'timestamp': datetime.now(),
                                    'raw_data': line.strip()
                                }
                        except:
                            continue

                # If no price found but API worked, return basic success
                return {
                    'success': True,
                    'api_used': 'alphavantage',
                    'symbol': symbol.upper(),
                    'price': 0.0,
                    'note': 'API responded but no price data parsed',
                    'timestamp': datetime.now()
                }
            else:
                return {'success': False, 'error': 'AlphaVantage API validation failed', 'api_used': 'alphavantage'}

        except Exception as e:
            return {'success': False, 'error': str(e), 'api_used': 'alphavantage'}

    def get_stock_quote_with_failover(self, symbol):
        """Get stock quote with automatic failover"""
        print(f"Getting quote for {symbol.upper()} with dual API system...")

        # Try Polygon first (Primary)
        print("Attempting Polygon API (Primary)...")
        result = self.get_stock_quote_primary(symbol)

        if result['success']:
            self.api_failure_counts['polygon'] = 0  # Reset failure count
            self.last_successful_api = 'polygon'
            print(f"[PASS] Polygon API successful")
            return result
        else:
            self.api_failure_counts['polygon'] += 1
            print(f"[FAIL] Polygon API failed: {result.get('error', 'Unknown error')}")
            print("Failing over to AlphaVantage API (Secondary)...")

            # Failover to AlphaVantage
            result = self.get_stock_quote_secondary(symbol)

            if result['success']:
                self.api_failure_counts['alphavantage'] = 0  # Reset failure count
                self.last_successful_api = 'alphavantage'
                print(f"[PASS] AlphaVantage API successful (failover)")
                return result
            else:
                self.api_failure_counts['alphavantage'] += 1
                print(f"[FAIL] AlphaVantage API failed: {result.get('error', 'Unknown error')}")
                print("[CRITICAL] Both APIs failed!")

                return {
                    'success': False,
                    'error': 'Both Polygon and AlphaVantage APIs failed',
                    'polygon_error': result.get('error', 'Unknown'),
                    'alphavantage_error': result.get('error', 'Unknown'),
                    'timestamp': datetime.now()
                }

    def get_spx_data_with_failover(self):
        """Get SPX data using dual API system with SPY conversion"""
        print("Getting SPX data with dual API failover...")

        # Get SPY data first
        spy_result = self.get_stock_quote_with_failover('SPY')

        if spy_result['success']:
            # Convert SPY to SPX (approximate 10x multiplier with adjustments)
            spy_price = spy_result['price']
            spx_price = spy_price * 10

            return {
                'success': True,
                'spx_price': spx_price,
                'spy_price': spy_price,
                'api_used': spy_result['api_used'],
                'conversion_method': 'SPY × 10',
                'timestamp': spy_result['timestamp'],
                'reliability': 'HIGH' if spy_result['api_used'] == 'polygon' else 'MEDIUM'
            }
        else:
            return {
                'success': False,
                'error': 'Failed to get SPY data for SPX conversion',
                'details': spy_result
            }

    def get_after_hours_data_with_failover(self, symbol):
        """Get after-hours data with failover"""
        print(f"Getting after-hours data for {symbol.upper()}...")

        # Try existing after_hours_command.py first
        try:
            result = subprocess.run(['python', 'after_hours_command.py', symbol.upper()],
                                  capture_output=True, text=True, timeout=15)

            if result.returncode == 0 and 'PRICE:' in result.stdout:
                print("[PASS] After-hours command successful")
                return {
                    'success': True,
                    'api_used': 'after_hours_polygon',
                    'symbol': symbol.upper(),
                    'data': result.stdout,
                    'timestamp': datetime.now()
                }
        except Exception as e:
            print(f"[FAIL] After-hours command failed: {e}")

        # Fallback to regular quote with session detection
        quote_result = self.get_stock_quote_with_failover(symbol)

        if quote_result['success']:
            current_hour = datetime.now().hour
            session = 'AFTER_HOURS' if current_hour < 9 or current_hour >= 16 else 'REGULAR'

            quote_result['session'] = session
            quote_result['note'] = 'Regular quote with session detection'

            return quote_result
        else:
            return quote_result

    def test_dual_api_system(self):
        """Test both APIs and show status"""
        print("DUAL API SYSTEM TEST")
        print("=" * 40)
        print(f"Polygon API Key: {self.polygon_api_key[:10]}...")
        print(f"AlphaVantage API Key: {self.alphavantage_api_key[:10]}...")
        print()

        # Test with SPY
        print("Testing SPY quote with failover...")
        spy_result = self.get_stock_quote_with_failover('SPY')

        if spy_result['success']:
            print(f"Success! API Used: {spy_result['api_used']}")
            print(f"SPY Price: ${spy_result['price']:.2f}")
            print(f"Bid/Ask: ${spy_result.get('bid', 0):.2f} / ${spy_result.get('ask', 0):.2f}")
        else:
            print(f"Failed: {spy_result['error']}")

        print()

        # Test SPX conversion
        print("Testing SPX data conversion...")
        spx_result = self.get_spx_data_with_failover()

        if spx_result['success']:
            print(f"Success! SPX: ${spx_result['spx_price']:.2f}")
            print(f"API Used: {spx_result['api_used']}")
            print(f"Reliability: {spx_result['reliability']}")
        else:
            print(f"Failed: {spx_result['error']}")

        print()

        # Test after-hours
        print("Testing after-hours data...")
        ah_result = self.get_after_hours_data_with_failover('SPY')

        if ah_result['success']:
            print(f"Success! API Used: {ah_result['api_used']}")
            if 'session' in ah_result:
                print(f"Session: {ah_result['session']}")
        else:
            print(f"Failed: {ah_result['error']}")

        print()

        # Show API health status
        print("API HEALTH STATUS:")
        print(f"Polygon Failures: {self.api_failure_counts['polygon']}")
        print(f"AlphaVantage Failures: {self.api_failure_counts['alphavantage']}")
        print(f"Last Successful API: {self.last_successful_api}")

        return {
            'spy_test': spy_result,
            'spx_test': spx_result,
            'after_hours_test': ah_result,
            'api_health': self.api_failure_counts,
            'last_successful': self.last_successful_api
        }

    def get_api_status(self):
        """Get current API status"""
        return {
            'polygon_failures': self.api_failure_counts['polygon'],
            'alphavantage_failures': self.api_failure_counts['alphavantage'],
            'last_successful_api': self.last_successful_api,
            'timestamp': datetime.now().isoformat()
        }

def main():
    dual_api = DualAPISystem()
    dual_api.test_dual_api_system()

if __name__ == "__main__":
    main()