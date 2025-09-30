# This is the replacement for the get_spx_data_with_failover function
def get_spx_data_with_failover(self):
    """Get SPX data using Polygon indices endpoint - works both during and after market hours"""
    print("Getting SPX data with dual API failover...")
    
    from datetime import datetime
    today = datetime.now().strftime('%Y-%m-%d')
    
    # STANDARD APPROACH: Always try I:SPX daily bars endpoint first
    # This endpoint works both during market hours and after close
    # It gives the ACTUAL closing data, not the previous day
    try:
        url = f'https://api.polygon.io/v2/aggs/ticker/I:SPX/range/1/day/{today}/{today}?adjusted=true&apikey={self.polygon_api_key}'
        
        response = requests.get(url, timeout=20)
        data = response.json()
        
        if 'results' in data and data['results']:
            bar = data['results'][0]
            spx_price = bar['c']  # Close price (or latest if market open)
            
            print(f"[PASS] Polygon I:SPX daily bar: ${spx_price:.2f}")
            
            return {
                'success': True,
                'spx_price': spx_price,
                'api_used': 'polygon_indices',
                'conversion_method': 'Direct I:SPX Daily Bar',
                'timestamp': datetime.fromtimestamp(bar['t'] / 1000),
                'reliability': 'VERY_HIGH',
                'open': bar['o'],
                'high': bar['h'],
                'low': bar['l']
            }
    except Exception as e:
        print(f"[FAIL] Polygon I:SPX daily bar failed: {e}")
    
    # Fallback: Get SPY and convert (only if daily bar fails)
    print("Falling back to SPY conversion...")
    spy_result = self.get_stock_quote_with_failover('SPY')
    
    if spy_result['success']:
        spy_price = spy_result['price']
        spx_price = spy_price * 10
        
        return {
            'success': True,
            'spx_price': spx_price,
            'spy_price': spy_price,
            'api_used': spy_result['api_used'],
            'conversion_method': 'SPY × 10 Fallback',
            'timestamp': spy_result['timestamp'],
            'reliability': 'MEDIUM'
        }
    
    return {
        'success': False,
        'error': 'All SPX data sources failed'
    }
