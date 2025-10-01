"""
Test Dual Discord Webhook System
Tests both TESTING and ALERTS channels separately
"""

import requests
import json
from datetime import datetime

# Webhook URLs
WEBHOOK_TESTING = "https://discord.com/api/webhooks/1422928703972970516/59EBn9XvN6VautbSfjE8p_pFDNX4qIrU6ephGS--UvSiD7nSahftbhQDSW66fQwfXajp"
WEBHOOK_ALERTS = "https://discord.com/api/webhooks/1422763517974417478/0AAxHmLLjC389OXRi5KY_P2puAY8BhGAgEYTXSxj7TiKlqK_WH1PXPW6d_osA219ZFPu"

def send_test_message(webhook_url, channel_name, color):
    """Send test message to specified webhook"""
    payload = {
        'username': f'🔧 {channel_name} Channel',
        'embeds': [{
            'title': f'✅ {channel_name.upper()} CHANNEL TEST',
            'description': f'**This message is going to the {channel_name} channel**\n\nDual webhook system is operational.',
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
                    'value': 'Testing only' if 'Testing' in channel_name else 'Live alerts',
                    'inline': True
                },
                {
                    'name': '⏰ Timestamp',
                    'value': datetime.now().strftime('%Y-%m-%d %H:%M:%S ET'),
                    'inline': False
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
    print('DUAL WEBHOOK SYSTEM TEST')
    print('=' * 70)
    print()

    # Test TESTING channel
    print('1. Testing TESTING channel...')
    print(f'   Webhook ID: {WEBHOOK_TESTING.split("/")[-2]}')
    status_test = send_test_message(WEBHOOK_TESTING, 'Testing', 15844367)  # Gold

    if status_test == 204:
        print('   ✅ SUCCESS: Testing channel received message')
    else:
        print(f'   ❌ FAILED: Status {status_test}')

    print()

    # Test ALERTS channel
    print('2. Testing ALERTS channel...')
    print(f'   Webhook ID: {WEBHOOK_ALERTS.split("/")[-2]}')
    status_alerts = send_test_message(WEBHOOK_ALERTS, 'Alerts', 3066993)  # Green

    if status_alerts == 204:
        print('   ✅ SUCCESS: Alerts channel received message')
    else:
        print(f'   ❌ FAILED: Status {status_alerts}')

    print()
    print('=' * 70)
    print('TEST SUMMARY')
    print('=' * 70)

    if status_test == 204 and status_alerts == 204:
        print('✅ BOTH CHANNELS WORKING CORRECTLY')
        print()
        print('📋 Channel Usage:')
        print('   • TESTING (Gold): For development/testing messages')
        print('   • ALERTS (Green): For live trading alerts')
        print()
        print('🎯 Both webhooks are configured and operational!')
    else:
        print('⚠️  SOME CHANNELS FAILED')
        print(f'   Testing: {"✅" if status_test == 204 else "❌"}')
        print(f'   Alerts: {"✅" if status_alerts == 204 else "❌"}')

    print('=' * 70)

if __name__ == "__main__":
    main()
