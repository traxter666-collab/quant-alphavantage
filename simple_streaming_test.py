"""
Minimal Streaming Test - Guaranteed Output
"""
import requests
import sys

POLYGON_KEY = "_u0zA0CH5ZspOHecb2G8uBxd2DUo4r9D"
WEBHOOK_SPX = "https://discord.com/api/webhooks/1422930069290225694/PKiahdQzpgIZuceHRU254dgpmSEOcgho0-o-DpkQXeCUsQ5AYH1mv3OmJ_gG-1eB7FU-"

print("Starting streaming test...", flush=True)

# Get SPY price
print("Getting SPY price...", flush=True)
url = f"https://api.polygon.io/v2/aggs/ticker/SPY/prev?adjusted=true&apiKey={POLYGON_KEY}"
response = requests.get(url, timeout=5)

if response.status_code == 200:
    data = response.json()
    spy_price = data['results'][0]['c']
    spx_price = spy_price * 10

    print(f"SPY: ${spy_price:.2f}", flush=True)
    print(f"SPX: ${spx_price:.2f}", flush=True)

    # Send to Discord
    print("Sending to Discord...", flush=True)
    payload = {
        'username': '✅ Streaming Test',
        'content': f'**SPX Streaming System Online**\\n\\nCurrent SPX: ${spx_price:.2f}'
    }

    disc_response = requests.post(WEBHOOK_SPX, json=payload, timeout=10)
    if disc_response.status_code == 204:
        print("✅ Discord alert sent!", flush=True)
    else:
        print(f"❌ Discord failed: {disc_response.status_code}", flush=True)
else:
    print(f"❌ API failed: {response.status_code}", flush=True)

print("Test complete!", flush=True)
