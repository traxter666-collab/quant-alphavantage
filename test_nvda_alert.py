#!/usr/bin/env python3
"""
Test NVDA Alert with 9/12 data - Market Open Alert System
"""

import time
from alert_manager import AlertManager

def test_nvda_alert():
    # Initialize alert manager
    manager = AlertManager()
    manager.start()
    
    # NVDA 9/12 data test alert
    nvda_alert = {
        'title': 'MARKET OPEN ALERT: NVDA Test - 9/12 Data',
        'message': '''NVIDIA (NVDA) - Market Open Analysis

Current: $177.82 (+0.37%) | Volume: 125M shares

TECHNICAL STATUS:
- Above 20-day EMA: $175.04 (BULLISH)
- Near 52-week high: $184.47
- Strong volume: 125M vs avg 50M
- Support zone: $175-170

AI CATALYST CONFIRMATION:
- GPU market dominance: 80%+
- H100/H200 demand surge
- Data center revenue acceleration
- Enterprise AI adoption wave

ANALYST CONSENSUS:
- Target: $208.59 (+17% upside)
- 58/65 analysts positive (89%)
- Strong Buy/Buy rating majority

PRIORITY ALERT: High institutional activity
Market Open Protocol: ACTIVE
System Status: OPERATIONAL

This is a TEST alert using 9/12/2025 market data to validate the alert management system during simulated market open conditions.''',
        'type': 'CRITICAL'
    }
    
    # Send the test alert
    print("Sending NVDA test alert to Discord...")
    manager.add_alert(
        priority=1,  # Highest priority
        title=nvda_alert['title'],
        message=nvda_alert['message'], 
        alert_type=nvda_alert['type']
    )
    
    # Wait for processing
    print("Waiting for alert to process...")
    time.sleep(10)
    
    # Stop manager
    manager.stop()
    print("Test completed")

if __name__ == "__main__":
    test_nvda_alert()