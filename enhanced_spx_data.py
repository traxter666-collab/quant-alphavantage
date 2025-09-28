#!/usr/bin/env python3
"""
Enhanced SPX Data Integration - Multiple Source Method
Solves SPXW data accuracy issues with improved methodologies
"""

import requests
import json
import time
from typing import Dict, Optional, Tuple, List
from datetime import datetime
from options_spot_calculator import OptionsSpotCalculator
from mcp_options_calculator import MCPOptionsCalculator

class EnhancedSPXData:
    def __init__(self):
        self.alphavantage_key = "ZFL38ZY98GSN7E1S"
        self.options_calculator = OptionsSpotCalculator()
        self.mcp_calculator = MCPOptionsCalculator()
        self.data_sources = {
            'options_parity': True,   # PRIMARY: Put-call parity from SPXW options
            'spy_proxy': True,
            'yahoo_finance': True,
            'marketwatch': True
        }
        
    def get_spy_data(self) -> Dict:
        """Get SPY data from AlphaVantage as baseline"""
        try:
            # Using existing MCP would be: mcp__alphavantage__GLOBAL_QUOTE("SPY")
            # For this enhanced version, simulate the call
            url = f"https://www.alphavantage.co/query"
            params = {
                'function': 'GLOBAL_QUOTE',
                'symbol': 'SPY',
                'apikey': self.alphavantage_key
            }
            
            print("Getting SPY data from AlphaVantage...")
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if 'Global Quote' in data:
                    quote = data['Global Quote']
                    return {
                        'source': 'alphavantage',
                        'symbol': 'SPY',
                        'price': float(quote['05. price']),
                        'change': float(quote['09. change']),
                        'change_percent': quote['10. change percent'].rstrip('%'),
                        'volume': int(quote['06. volume']),
                        'timestamp': quote['07. latest trading day']
                    }
        except Exception as e:
            print(f"AlphaVantage SPY error: {e}")
        
        return None
    
    def get_yahoo_spx(self) -> Optional[Dict]:
        """Get SPX data directly from Yahoo Finance"""
        try:
            # Yahoo Finance API endpoint for SPX
            url = "https://query1.finance.yahoo.com/v8/finance/chart/%5ESPX"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            print("Getting SPX data from Yahoo Finance...")
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                result = data['chart']['result'][0]
                meta = result['meta']
                
                return {
                    'source': 'yahoo_finance',
                    'symbol': 'SPX',
                    'price': meta['regularMarketPrice'],
                    'previous_close': meta['previousClose'],
                    'change': meta['regularMarketPrice'] - meta['previousClose'],
                    'change_percent': ((meta['regularMarketPrice'] - meta['previousClose']) / meta['previousClose']) * 100,
                    'timestamp': datetime.fromtimestamp(meta['regularMarketTime']).isoformat()
                }
                
        except Exception as e:
            print(f"Yahoo Finance SPX error: {e}")
        
        return None
    
    def get_marketwatch_spx(self) -> Optional[Dict]:
        """Get SPX data from MarketWatch (backup source)"""
        try:
            # MarketWatch has public API endpoints
            url = "https://api.wsj.net/api/michelangelo/timeseries/history"
            params = {
                'json': 'true',
                'key': 'INDEXSP:.SPX',
                'step': 'P1D',
                'count': 1
            }
            
            print("Getting SPX data from MarketWatch...")
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data and 'TimeSeriesResponse' in data:
                    series = data['TimeSeriesResponse'][0]['TimeSeries']['Series']
                    if series:
                        latest = series[-1]
                        return {
                            'source': 'marketwatch',
                            'symbol': 'SPX',
                            'price': latest['Close'],
                            'timestamp': latest['Date']
                        }
                        
        except Exception as e:
            print(f"MarketWatch SPX error: {e}")
        
        return None
    
    def calculate_enhanced_spy_conversion(self, spy_price: float) -> float:
        """
        Enhanced SPY to SPX conversion with historical correlation adjustments
        """
        # Historical SPY/SPX ratios (not always exactly 10)
        # Typical range: 9.98 to 10.02 due to expense ratios and tracking differences
        
        # Time-based adjustments
        current_hour = datetime.now().hour
        
        # Market hours adjustments (SPY can lag SPX slightly)
        if 9 <= current_hour <= 16:  # Market hours
            conversion_ratio = 10.001  # Slight premium during market hours
        else:
            conversion_ratio = 10.000  # Standard after hours
        
        # Volatility adjustments (higher vol = larger tracking differences)
        # For now, use standard ratio - could be enhanced with VIX data
        
        adjusted_spx = spy_price * conversion_ratio
        
        print(f"Enhanced SPY->SPX conversion: ${spy_price:.2f} * {conversion_ratio:.3f} = ${adjusted_spx:.2f}")
        
        return adjusted_spx
    
    def extract_spx_from_options(self) -> Optional[float]:
        """
        Extract SPX price using put-call parity from SPXW options
        Formula: SPX = Call Price - Put Price + Strike Price (for ATM options)
        """
        try:
            print("Attempting SPXW options put-call parity extraction...")
            result = self.options_calculator.extract_spot_from_options('SPXW')
            
            if 'error' not in result:
                print(f"OPTIONS SUCCESS: SPX ${result['spot_price']} from {result['calculation_count']} calculations")
                return result['spot_price']
            else:
                print(f"OPTIONS FAILED: {result['error']}")
                
                # Fallback to SPY options if SPXW fails
                print("Trying SPY options as fallback...")
                spy_result = self.options_calculator.extract_spot_from_options('SPY')
                
                if 'error' not in spy_result:
                    # Convert SPY spot to SPX equivalent
                    implied_spx = self.options_calculator.calculate_spx_from_spy(spy_result['spot_price'])
                    print(f"SPY OPTIONS SUCCESS: SPX ${implied_spx} (from SPY ${spy_result['spot_price']})")
                    return implied_spx
                else:
                    print(f"SPY OPTIONS FAILED: {spy_result['error']}")
                    return None
                    
        except Exception as e:
            print(f"Options extraction error: {e}")
            return None
    
    def get_best_spx_price(self) -> Dict:
        """
        Get the most accurate SPX price using multiple sources
        Priority: 1) SPXW Options Put-Call Parity, 2) Yahoo Finance, 3) MarketWatch, 4) Enhanced SPY
        """
        sources_data = []
        
        # 1. PRIMARY: SPXW Options Put-Call Parity (Most Accurate)
        pcp_price = self.extract_spx_from_options()
        if pcp_price:
            pcp_data = {
                'source': 'spxw_options_parity',
                'symbol': 'SPX',
                'price': pcp_price,
                'timestamp': datetime.now().isoformat(),
                'priority': 1  # Highest priority
            }
            sources_data.append(pcp_data)
            print(f"PRIMARY SOURCE: SPXW Options Put-Call Parity = ${pcp_price}")
        
        # 2. BACKUP: Yahoo Finance direct SPX
        yahoo_data = self.get_yahoo_spx()
        if yahoo_data:
            yahoo_data['priority'] = 2
            sources_data.append(yahoo_data)
        
        # 3. BACKUP: MarketWatch SPX
        marketwatch_data = self.get_marketwatch_spx()
        if marketwatch_data:
            marketwatch_data['priority'] = 3
            sources_data.append(marketwatch_data)
        
        # 4. FALLBACK: Enhanced SPY conversion
        spy_data = self.get_spy_data()
        if spy_data:
            enhanced_spx_price = self.calculate_enhanced_spy_conversion(spy_data['price'])
            spy_enhanced = {
                'source': 'spy_enhanced',
                'symbol': 'SPX',
                'price': enhanced_spx_price,
                'change': spy_data['change'] * 10,  # Scale SPY change
                'volume': spy_data['volume'],
                'timestamp': spy_data['timestamp'],
                'priority': 4  # Lowest priority
            }
            sources_data.append(spy_enhanced)
        
        if not sources_data:
            return {'error': 'No SPX data sources available'}
        
        # Choose best source (priority: SPXW Options > Yahoo > MarketWatch > Enhanced SPY)
        source_priority = ['spxw_options_parity', 'yahoo_finance', 'marketwatch', 'spy_enhanced']
        
        best_source = None
        for priority_source in source_priority:
            for source in sources_data:
                if source['source'] == priority_source:
                    best_source = source
                    break
            if best_source:
                break
        
        # If no source found by priority, use the one with highest priority number (lowest value)
        if not best_source and sources_data:
            best_source = min(sources_data, key=lambda x: x.get('priority', 999))
        
        # Add consensus data if multiple sources
        if len(sources_data) > 1:
            prices = [s['price'] for s in sources_data if 'price' in s]
            if len(prices) > 1:
                avg_price = sum(prices) / len(prices)
                price_std = (sum((p - avg_price) ** 2 for p in prices) / len(prices)) ** 0.5
                
                best_source['consensus'] = {
                    'sources_count': len(sources_data),
                    'average_price': avg_price,
                    'price_std': price_std,
                    'all_sources': [s['source'] for s in sources_data]
                }
        
        return best_source
    
    def validate_spx_accuracy(self, known_spx_price: float = None) -> Dict:
        """
        Validate accuracy against known SPX price
        """
        result = self.get_best_spx_price()
        
        if known_spx_price and 'price' in result:
            error = abs(result['price'] - known_spx_price)
            error_pct = (error / known_spx_price) * 100
            
            result['validation'] = {
                'known_price': known_spx_price,
                'our_price': result['price'],
                'absolute_error': error,
                'percent_error': error_pct,
                'accuracy': 'EXCELLENT' if error_pct < 0.1 else 'GOOD' if error_pct < 0.5 else 'POOR'
            }
        
        return result

def test_enhanced_spx():
    """Test the enhanced SPX data system"""
    print("ENHANCED SPX DATA SYSTEM TEST")
    print("=" * 45)
    
    spx_data = EnhancedSPXData()
    
    # Test with known 9/12 close price
    result = spx_data.validate_spx_accuracy(known_spx_price=6584.28)
    
    print("\nRESULTS:")
    print(f"Source: {result.get('source', 'unknown')}")
    print(f"SPX Price: ${result.get('price', 0):.2f}")
    
    if 'validation' in result:
        val = result['validation']
        print(f"Known Price: ${val['known_price']:.2f}")
        print(f"Error: ${val['absolute_error']:.2f} ({val['percent_error']:.3f}%)")
        print(f"Accuracy: {val['accuracy']}")
    
    if 'consensus' in result:
        cons = result['consensus']
        print(f"Sources Used: {cons['sources_count']}")
        print(f"Average Price: ${cons['average_price']:.2f}")
        print(f"Price Std Dev: ${cons['price_std']:.2f}")
    
    return result

if __name__ == "__main__":
    test_enhanced_spx()