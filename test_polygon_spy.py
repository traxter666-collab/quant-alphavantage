"""
Quick Polygon API Test for SPY
Tests both API keys with redundancy
"""

import requests
import json
from datetime import datetime

# Dual API keys
PRIMARY_KEY = "_u0zA0CH5ZspOHecb2G8uBxd2DUo4r9D"
BACKUP_KEY = "CiDDZJqQS88A0QhaoJbn0rLqaenps6Pq"

def test_polygon_spy(api_key, key_name):
    """Test Polygon API with SPY quote"""
    print(f'\n{"="*70}')
    print(f'Testing {key_name}')
    print(f'{"="*70}')

    url = f"https://api.polygon.io/v2/aggs/ticker/SPY/prev?adjusted=true&apiKey={api_key}"

    try:
        response = requests.get(url, timeout=10)
        print(f'Status Code: {response.status_code}')

        if response.status_code == 200:
            data = response.json()

            if 'results' in data and len(data['results']) > 0:
                result = data['results'][0]

                print(f'\n✅ SUCCESS - {key_name} is working!\n')
                print(f'SPY Data:')
                print(f'  Open:   ${result.get("o", 0):.2f}')
                print(f'  High:   ${result.get("h", 0):.2f}')
                print(f'  Low:    ${result.get("l", 0):.2f}')
                print(f'  Close:  ${result.get("c", 0):.2f}')
                print(f'  Volume: {result.get("v", 0):,}')
                print(f'  Timestamp: {datetime.fromtimestamp(result.get("t", 0)/1000).strftime("%Y-%m-%d %H:%M:%S")}')

                return True, result.get("c", 0)
            else:
                print(f'❌ No results in response')
                return False, None

        elif response.status_code == 401:
            print(f'❌ AUTHENTICATION FAILED - Invalid API key')
            return False, None
        elif response.status_code == 429:
            print(f'⚠️  RATE LIMIT EXCEEDED - Too many requests')
            return False, None
        else:
            print(f'❌ FAILED with status {response.status_code}')
            print(f'Response: {response.text[:200]}')
            return False, None

    except requests.exceptions.ConnectionError as e:
        print(f'❌ CONNECTION ERROR: Cannot reach api.polygon.io')
        print(f'Details: {str(e)[:200]}')
        return False, None
    except Exception as e:
        print(f'❌ ERROR: {str(e)[:200]}')
        return False, None

def test_spy_realtime(api_key, key_name):
    """Test real-time SPY quote"""
    print(f'\n{"="*70}')
    print(f'Testing Real-Time Quote - {key_name}')
    print(f'{"="*70}')

    url = f"https://api.polygon.io/v2/last/trade/SPY?apiKey={api_key}"

    try:
        response = requests.get(url, timeout=10)
        print(f'Status Code: {response.status_code}')

        if response.status_code == 200:
            data = response.json()

            if 'results' in data:
                result = data['results']

                print(f'\n✅ REAL-TIME DATA WORKING!\n')
                print(f'Last Trade:')
                print(f'  Price: ${result.get("p", 0):.2f}')
                print(f'  Size:  {result.get("s", 0):,} shares')
                print(f'  Time:  {datetime.fromtimestamp(result.get("t", 0)/1000000000).strftime("%Y-%m-%d %H:%M:%S")}')

                return True, result.get("p", 0)
            else:
                print(f'❌ No results in response')
                return False, None

        else:
            print(f'❌ FAILED with status {response.status_code}')
            return False, None

    except requests.exceptions.ConnectionError as e:
        print(f'❌ CONNECTION ERROR: Cannot reach api.polygon.io')
        return False, None
    except Exception as e:
        print(f'❌ ERROR: {str(e)[:200]}')
        return False, None

def main():
    print('╔' + '═'*68 + '╗')
    print('║' + ' '*15 + 'POLYGON API VALIDATION TEST - SPY' + ' '*20 + '║')
    print('╚' + '═'*68 + '╝')

    # Test Primary Key
    primary_success, primary_price = test_polygon_spy(PRIMARY_KEY, "PRIMARY KEY")

    print('\n' + '-'*70)

    # Test Backup Key
    backup_success, backup_price = test_polygon_spy(BACKUP_KEY, "BACKUP KEY")

    # Test Real-Time (if primary works)
    if primary_success:
        rt_success, rt_price = test_spy_realtime(PRIMARY_KEY, "PRIMARY KEY")

    # Summary
    print('\n' + '='*70)
    print('TEST SUMMARY')
    print('='*70)

    if primary_success and backup_success:
        print('✅ BOTH API KEYS WORKING')
        print(f'   Primary Key: ✅ Operational (SPY: ${primary_price:.2f})')
        print(f'   Backup Key:  ✅ Operational (SPY: ${backup_price:.2f})')
        print('\n🎯 DUAL API SYSTEM READY FOR STREAMING')
    elif primary_success:
        print('⚠️  PRIMARY KEY WORKING, BACKUP FAILED')
        print(f'   Primary Key: ✅ Operational (SPY: ${primary_price:.2f})')
        print(f'   Backup Key:  ❌ Failed')
        print('\n⚠️  Single API available, consider backup key issue')
    elif backup_success:
        print('⚠️  BACKUP KEY WORKING, PRIMARY FAILED')
        print(f'   Primary Key: ❌ Failed')
        print(f'   Backup Key:  ✅ Operational (SPY: ${backup_price:.2f})')
        print('\n⚠️  Backup active, but primary should be fixed')
    else:
        print('❌ BOTH API KEYS FAILED')
        print('   Primary Key: ❌ Failed')
        print('   Backup Key:  ❌ Failed')
        print('\n🚨 Check network connectivity or API key validity')

    print('='*70)

if __name__ == "__main__":
    main()
