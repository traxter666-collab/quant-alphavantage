"""
Simple test of polling system components
"""

import requests
import sys

# API Key
POLYGON_PRIMARY = "_u0zA0CH5ZspOHecb2G8uBxd2DUo4r9D"
WEBHOOK_SPX = "https://discord.com/api/webhooks/1422930069290225694/PKiahdQzpgIZuceHRU254dgpmSEOcgho0-o-DpkQXeCUsQ5AYH1mv3OmJ_gG-1eB7FU-"

print("=" * 70)
print("SIMPLE POLLING SYSTEM TEST")
print("=" * 70)

# Test 1: Get SPY Price
print("\n1. Testing Polygon API...")
try:
    url = f"https://api.polygon.io/v2/last/trade/SPY?apiKey={POLYGON_PRIMARY}"
    response = requests.get(url, timeout=5)
    print(f"   Status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        spy_price = data['results']['p']
        spx_price = spy_price * 10
        print(f"   ✅ SPY: ${spy_price:.2f}")
        print(f"   ✅ SPX Equivalent: ${spx_price:.2f}")
    else:
        print(f"   ❌ Failed: {response.text}")
        sys.exit(1)
except Exception as e:
    print(f"   ❌ Error: {e}")
    sys.exit(1)

# Test 2: Check level proximity
print("\n2. Testing level proximity check...")
pivot = 6659
distance = abs(spx_price - pivot)
print(f"   Distance to pivot ({pivot}): {distance:.2f} points")

if distance <= 20:
    print(f"   ✅ Near pivot (within 20 points)")
    alert_needed = True
else:
    print(f"   ℹ️  Not near pivot (>20 points away)")
    alert_needed = False

# Test 3: Send Discord alert
if alert_needed:
    print("\n3. Testing Discord alert...")
    payload = {
        'username': '🧪 Test Alert',
        'embeds': [{
            'title': '🧪 POLLING SYSTEM TEST',
            'description': f'**SPX: ${spx_price:.2f}**\nDistance to pivot: {distance:.2f} points',
            'color': 15844367,
            'fields': [
                {
                    'name': 'Test Status',
                    'value': '✅ System Working',
                    'inline': True
                }
            ]
        }]
    }

    try:
        response = requests.post(WEBHOOK_SPX, json=payload, timeout=10)
        if response.status_code == 204:
            print(f"   ✅ Discord alert sent successfully!")
        else:
            print(f"   ❌ Discord failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Discord error: {e}")
else:
    print("\n3. Skipping Discord alert (not near levels)")

print("\n" + "=" * 70)
print("TEST COMPLETE")
print("=" * 70)
