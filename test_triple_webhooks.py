"""
Test Triple Discord Webhook System
Tests TESTING, ALERTS, and SPX channels separately
"""

import requests
import json
from datetime import datetime

# Webhook URLs
WEBHOOK_TESTING = "https://discord.com/api/webhooks/1422928703972970516/59EBn9XvN6VautbSfjE8p_pFDNX4qIrU6ephGS--UvSiD7nSahftbhQDSW66fQwfXajp"
WEBHOOK_ALERTS = "https://discord.com/api/webhooks/1422763517974417478/0AAxHmLLjC389OXRi5KY_P2puAY8BhGAgEYTXSxj7TiKlqK_WH1PXPW6d_osA219ZFPu"
WEBHOOK_SPX = "https://discord.com/api/webhooks/1422930069290225694/PKiahdQzpgIZuceHRU254dgpmSEOcgho0-o-DpkQXeCUsQ5AYH1mv3OmJ_gG-1eB7FU-"

def send_test_message(webhook_url, channel_name, color, emoji):
    """Send test message to specified webhook"""

    # Channel-specific descriptions
    descriptions = {
        'Testing': '**This message is for TESTING only**\n\nDevelopment and validation messages',
        'Alerts': '**This message is for GENERAL ALERTS**\n\nAll non-SPX trading alerts',
        'SPX Trades': '**This message is for SPX TRADES ONLY**\n\nExclusive SPX/SPXW 0DTE trading signals'
    }

    payload = {
        'username': f'{emoji} {channel_name} Channel',
        'embeds': [{
            'title': f'✅ {channel_name.upper()} CHANNEL TEST',
            'description': descriptions[channel_name],
            'color': color,
            'timestamp': datetime.utcnow().isoformat(),
            'fields': [
                {
                    'name': '📱 Channel Type',
                    'value': channel_name,
                    'inline': True
                },
                {
                    'name': '🎯 Purpose',
                    'value': 'SPX trades only' if 'SPX' in channel_name else 'Testing only' if 'Testing' in channel_name else 'General alerts',
                    'inline': True
                },
                {
                    'name': '💰 Example Content',
                    'value': 'SPXW 6650P, 6675C signals' if 'SPX' in channel_name else 'System tests' if 'Testing' in channel_name else 'QQQ, IWM, stocks',
                    'inline': False
                },
                {
                    'name': '⏰ Timestamp',
                    'value': datetime.now().strftime('%Y-%m-%d %H:%M:%S ET'),
                    'inline': True
                },
                {
                    'name': '🔧 Webhook ID',
                    'value': webhook_url.split('/')[-2],
                    'inline': True
                }
            ],
            'footer': {
                'text': f'SPX Trading System - {channel_name} Channel'
            }
        }]
    }

    response = requests.post(webhook_url, json=payload, timeout=10)
    return response.status_code

def main():
    print('=' * 70)
    print('TRIPLE WEBHOOK SYSTEM TEST')
    print('=' * 70)
    print()

    # Test TESTING channel
    print('1. Testing TESTING channel (Gold)...')
    print(f'   Webhook ID: {WEBHOOK_TESTING.split("/")[-2]}')
    print('   Purpose: Development/Testing messages only')
    status_test = send_test_message(WEBHOOK_TESTING, 'Testing', 15844367, '🧪')

    if status_test == 204:
        print('   ✅ SUCCESS: Testing channel received message')
    else:
        print(f'   ❌ FAILED: Status {status_test}')

    print()

    # Test ALERTS channel
    print('2. Testing ALERTS channel (Blue)...')
    print(f'   Webhook ID: {WEBHOOK_ALERTS.split("/")[-2]}')
    print('   Purpose: General alerts (non-SPX trades)')
    status_alerts = send_test_message(WEBHOOK_ALERTS, 'Alerts', 3447003, '🔔')

    if status_alerts == 204:
        print('   ✅ SUCCESS: Alerts channel received message')
    else:
        print(f'   ❌ FAILED: Status {status_alerts}')

    print()

    # Test SPX channel
    print('3. Testing SPX TRADES channel (Green)...')
    print(f'   Webhook ID: {WEBHOOK_SPX.split("/")[-2]}')
    print('   Purpose: SPX/SPXW 0DTE trades ONLY')
    status_spx = send_test_message(WEBHOOK_SPX, 'SPX Trades', 3066993, '📈')

    if status_spx == 204:
        print('   ✅ SUCCESS: SPX channel received message')
    else:
        print(f'   ❌ FAILED: Status {status_spx}')

    print()
    print('=' * 70)
    print('TEST SUMMARY')
    print('=' * 70)

    if status_test == 204 and status_alerts == 204 and status_spx == 204:
        print('✅ ALL THREE CHANNELS WORKING CORRECTLY')
        print()
        print('📋 Channel Usage:')
        print('   🧪 TESTING (Gold): Development/testing messages')
        print('   🔔 ALERTS (Blue): General alerts (QQQ, IWM, stocks)')
        print('   📈 SPX TRADES (Green): SPX/SPXW 0DTE trades ONLY')
        print()
        print('🎯 All three webhooks are configured and operational!')
        print()
        print('🚀 Routing Logic:')
        print('   • is_test=True → TESTING channel')
        print('   • is_spx=True → SPX TRADES channel')
        print('   • Default → ALERTS channel')
    else:
        print('⚠️  SOME CHANNELS FAILED')
        print(f'   Testing: {"✅" if status_test == 204 else "❌"}')
        print(f'   Alerts: {"✅" if status_alerts == 204 else "❌"}')
        print(f'   SPX: {"✅" if status_spx == 204 else "❌"}')

    print('=' * 70)

if __name__ == "__main__":
    main()
