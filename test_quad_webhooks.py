"""
Test Quad Discord Webhook System
Tests TESTING, ALERTS, SPX, and SPX PREMIUM channels separately
"""

import requests
import json
from datetime import datetime

# Webhook URLs
WEBHOOK_TESTING = "https://discord.com/api/webhooks/1422928703972970516/59EBn9XvN6VautbSfjE8p_pFDNX4qIrU6ephGS--UvSiD7nSahftbhQDSW66fQwfXajp"
WEBHOOK_ALERTS = "https://discord.com/api/webhooks/1422763517974417478/0AAxHmLLjC389OXRi5KY_P2puAY8BhGAgEYTXSxj7TiKlqK_WH1PXPW6d_osA219ZFPu"
WEBHOOK_SPX = "https://discord.com/api/webhooks/1422930069290225694/PKiahdQzpgIZuceHRU254dgpmSEOcgho0-o-DpkQXeCUsQ5AYH1mv3OmJ_gG-1eB7FU-"
WEBHOOK_SPX_PREMIUM = "https://discord.com/api/webhooks/1422931192205807677/fddndOqTq-nS1e9Mtevrh7EhR-6ikKNoLWvYvSjUdydCwor9TkwYvJrukPX6TFo-T64a"

def send_test_message(webhook_url, channel_name, color, emoji, description):
    """Send test message to specified webhook"""

    payload = {
        'username': f'{emoji} {channel_name} Channel',
        'embeds': [{
            'title': f'✅ {channel_name.upper()} CHANNEL TEST',
            'description': description,
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
                    'value': get_channel_purpose(channel_name),
                    'inline': True
                },
                {
                    'name': '💰 Example Content',
                    'value': get_example_content(channel_name),
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

def get_channel_purpose(channel_name):
    """Get channel purpose description"""
    purposes = {
        'Testing': 'Development/Testing only',
        'Alerts': 'General alerts (non-SPX)',
        'SPX Trades': 'SPX/SPXW 0DTE trades',
        'SPX Premium': 'High-value SPX (>$11 or >$1000)'
    }
    return purposes.get(channel_name, 'Unknown')

def get_example_content(channel_name):
    """Get example content for channel"""
    examples = {
        'Testing': 'System tests, validation messages',
        'Alerts': 'QQQ, IWM, stock alerts',
        'SPX Trades': 'SPXW 6650P @ $3.50, 6675C @ $5.20',
        'SPX Premium': 'SPXW 6650C @ $15.75, 10-contract positions'
    }
    return examples.get(channel_name, 'Unknown')

def main():
    print('=' * 70)
    print('QUAD WEBHOOK SYSTEM TEST')
    print('=' * 70)
    print()

    # Test TESTING channel
    print('1. Testing TESTING channel (Gold)...')
    print(f'   Webhook ID: {WEBHOOK_TESTING.split("/")[-2]}')
    print('   Purpose: Development/Testing messages only')
    status_test = send_test_message(
        WEBHOOK_TESTING,
        'Testing',
        15844367,  # Gold
        '🧪',
        '**This message is for TESTING only**\n\nDevelopment and validation messages'
    )

    if status_test == 204:
        print('   ✅ SUCCESS: Testing channel received message')
    else:
        print(f'   ❌ FAILED: Status {status_test}')

    print()

    # Test ALERTS channel
    print('2. Testing ALERTS channel (Blue)...')
    print(f'   Webhook ID: {WEBHOOK_ALERTS.split("/")[-2]}')
    print('   Purpose: General alerts (non-SPX trades)')
    status_alerts = send_test_message(
        WEBHOOK_ALERTS,
        'Alerts',
        3447003,  # Blue
        '🔔',
        '**This message is for GENERAL ALERTS**\n\nAll non-SPX trading alerts'
    )

    if status_alerts == 204:
        print('   ✅ SUCCESS: Alerts channel received message')
    else:
        print(f'   ❌ FAILED: Status {status_alerts}')

    print()

    # Test SPX channel
    print('3. Testing SPX TRADES channel (Green)...')
    print(f'   Webhook ID: {WEBHOOK_SPX.split("/")[-2]}')
    print('   Purpose: SPX/SPXW 0DTE trades (standard positions)')
    status_spx = send_test_message(
        WEBHOOK_SPX,
        'SPX Trades',
        3066993,  # Green
        '📈',
        '**This message is for SPX TRADES**\n\nStandard SPX/SPXW 0DTE trading signals (contracts <$11)'
    )

    if status_spx == 204:
        print('   ✅ SUCCESS: SPX channel received message')
    else:
        print(f'   ❌ FAILED: Status {status_spx}')

    print()

    # Test SPX PREMIUM channel
    print('4. Testing SPX PREMIUM channel (Purple)...')
    print(f'   Webhook ID: {WEBHOOK_SPX_PREMIUM.split("/")[-2]}')
    print('   Purpose: High-value SPX trades (>$11 or >$1000)')
    status_spx_premium = send_test_message(
        WEBHOOK_SPX_PREMIUM,
        'SPX Premium',
        10181046,  # Purple
        '💎',
        '**This message is for HIGH-VALUE SPX TRADES**\n\nPremium SPX contracts (>$11 per contract OR >$1000 total position value)'
    )

    if status_spx_premium == 204:
        print('   ✅ SUCCESS: SPX Premium channel received message')
    else:
        print(f'   ❌ FAILED: Status {status_spx_premium}')

    print()
    print('=' * 70)
    print('TEST SUMMARY')
    print('=' * 70)

    if status_test == 204 and status_alerts == 204 and status_spx == 204 and status_spx_premium == 204:
        print('✅ ALL FOUR CHANNELS WORKING CORRECTLY')
        print()
        print('📋 Channel Usage:')
        print('   🧪 TESTING (Gold): Development/testing messages')
        print('   🔔 ALERTS (Blue): General alerts (QQQ, IWM, stocks)')
        print('   📈 SPX TRADES (Green): Standard SPX/SPXW 0DTE trades')
        print('   💎 SPX PREMIUM (Purple): High-value SPX (>$11 or >$1000)')
        print()
        print('🎯 All four webhooks are configured and operational!')
        print()
        print('🚀 Routing Logic:')
        print('   • is_test=True → TESTING channel')
        print('   • is_spx=True + (price>$11 OR value>$1000) → SPX PREMIUM channel')
        print('   • is_spx=True + (price≤$11 AND value≤$1000) → SPX TRADES channel')
        print('   • Default → ALERTS channel')
    else:
        print('⚠️  SOME CHANNELS FAILED')
        print(f'   Testing: {"✅" if status_test == 204 else "❌"}')
        print(f'   Alerts: {"✅" if status_alerts == 204 else "❌"}')
        print(f'   SPX: {"✅" if status_spx == 204 else "❌"}')
        print(f'   SPX Premium: {"✅" if status_spx_premium == 204 else "❌"}')

    print('=' * 70)

if __name__ == "__main__":
    main()
