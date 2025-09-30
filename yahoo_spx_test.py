import requests
import json
from datetime import datetime

def test_yahoo_spx():
    """Test Yahoo Finance for SPX data"""
    
    print("Testing Yahoo Finance SPX Data")
    print("=" * 35)
    
    # Try different Yahoo endpoints
    endpoints = [
        "https://query1.finance.yahoo.com/v8/finance/chart/%5EGSPC",
        "https://query2.finance.yahoo.com/v8/finance/chart/%5EGSPC", 
        "https://finance.yahoo.com/quote/%5EGSPC"
    ]
    
    for i, url in enumerate(endpoints, 1):
        print(f"\nTesting endpoint {i}:")
        print(f"URL: {url}")
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                if 'json' in response.headers.get('content-type', '').lower():
                    data = response.json()
                    
                    # Try to extract SPX data
                    if 'chart' in data:
                        result = data['chart']['result'][0]
                        meta = result['meta']
                        
                        price = meta.get('regularMarketPrice', meta.get('previousClose', 'N/A'))
                        
                        print(f"SUCCESS!")
                        print(f"SPX Price: {price}")
                        print(f"High: {meta.get('regularMarketDayHigh', 'N/A')}")
                        print(f"Low: {meta.get('regularMarketDayLow', 'N/A')}")
                        
                        return True
                        
                else:
                    print("Response is HTML, not JSON")
            else:
                print(f"HTTP Error: {response.status_code}")
                
        except requests.exceptions.Timeout:
            print("Timeout error")
        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}")
        except json.JSONDecodeError:
            print("JSON decode error")
        except Exception as e:
            print(f"Other error: {e}")
    
    print(f"\nAll Yahoo endpoints failed.")
    print(f"Alternatives:")
    print(f"1. Screenshot analysis (most reliable)")
    print(f"2. Manual SPX entry") 
    print(f"3. Set up Polygon.io API key")
    print(f"4. Set up IEX Cloud API key")
    
    return False

def show_api_setup_instructions():
    """Show setup instructions for paid APIs"""
    
    print(f"\nAPI SETUP INSTRUCTIONS:")
    print(f"=" * 25)
    
    print(f"\nPOLYGON.IO (Free tier: 5 calls/min):")
    print(f"1. Go to polygon.io")
    print(f"2. Sign up free")
    print(f"3. Get API key")
    print(f"4. Run: setx POLYGON_API_KEY \"your_key\"")
    
    print(f"\nIEX CLOUD (Free tier: 500k calls/month):")
    print(f"1. Go to iexcloud.io") 
    print(f"2. Sign up free")
    print(f"3. Get publishable key")
    print(f"4. Run: setx IEX_API_KEY \"your_key\"")
    
    print(f"\nTRADINGVIEW (Advanced):")
    print(f"1. TradingView Pine Script alerts")
    print(f"2. Webhook integration")
    print(f"3. Custom data pipeline")

if __name__ == "__main__":
    success = test_yahoo_spx()
    
    if not success:
        show_api_setup_instructions()
        
        print(f"\nRECOMMENDATION:")
        print(f"For 0DTE trading, screenshot analysis is most reliable")
        print(f"Continue using image analysis for real-time data")