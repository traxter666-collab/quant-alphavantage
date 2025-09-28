#!/usr/bin/env python3
"""
Market Open Alert Manager - Rate Limited Discord Integration
Handles high-frequency alerts during market open with proper rate limiting
"""

import time
import json
import queue
import threading
from datetime import datetime, timezone
import requests
from typing import Dict, List, Optional

class AlertManager:
    def __init__(self):
        self.discord_webhook = "https://discord.com/api/webhooks/1409686499745595432/BcxhXaFGMLy2rSPBMsN9Tb0wpKWxVYOnZnsfmETvHOeEJGsRep3N-lhZQcKxzrbMfHgk"
        self.alert_queue = queue.PriorityQueue()
        self.rate_limiter = {
            'requests_sent': 0,
            'window_start': time.time(),
            'max_per_minute': 25  # Conservative limit
        }
        self.is_running = False
        
    def add_alert(self, priority: int, title: str, message: str, alert_type: str = "INFO"):
        """
        Add alert to queue with priority (1=highest, 5=lowest)
        """
        timestamp = datetime.now(timezone.utc).isoformat()
        alert_data = {
            'title': title,
            'message': message,
            'type': alert_type,
            'timestamp': timestamp
        }
        
        # Priority queue: lower number = higher priority
        self.alert_queue.put((priority, time.time(), alert_data))
        print(f"Alert queued: Priority {priority} - {title[:50]}")
    
    def check_rate_limit(self) -> bool:
        """Check if we can send another request"""
        now = time.time()
        
        # Reset window if minute has passed
        if now - self.rate_limiter['window_start'] >= 60:
            self.rate_limiter['requests_sent'] = 0
            self.rate_limiter['window_start'] = now
        
        return self.rate_limiter['requests_sent'] < self.rate_limiter['max_per_minute']
    
    def send_to_discord(self, alert_data: Dict) -> bool:
        """Send single alert to Discord with rate limiting"""
        if not self.check_rate_limit():
            return False
        
        # Color coding by alert type
        color_map = {
            'CRITICAL': 0xFF0000,  # Red
            'HIGH': 0xFF8C00,      # Orange  
            'MEDIUM': 0xFFD700,    # Yellow
            'INFO': 0x0066CC       # Blue
        }
        
        embed = {
            "title": alert_data['title'],
            "description": alert_data['message'][:4090],  # Discord limit
            "color": color_map.get(alert_data['type'], 0x0066CC),
            "timestamp": alert_data['timestamp'],
            "footer": {"text": f"SPX Trading System - {alert_data['type']}"}
        }
        
        payload = {"embeds": [embed]}
        
        try:
            response = requests.post(self.discord_webhook, json=payload, timeout=10)
            if response.status_code == 200:
                self.rate_limiter['requests_sent'] += 1
                print(f"Sent: {alert_data['title']}")
                return True
            else:
                print(f"Discord Error {response.status_code}: {response.text}")
                return False
                
        except requests.RequestException as e:
            print(f"Request failed: {e}")
            return False
    
    def process_queue(self):
        """Process alert queue with rate limiting"""
        while self.is_running:
            try:
                # Get next alert (blocks until available)
                priority, queued_time, alert_data = self.alert_queue.get(timeout=1.0)
                
                # Send if rate limit allows
                if self.send_to_discord(alert_data):
                    self.alert_queue.task_done()
                else:
                    # Re-queue if rate limited (back of queue)
                    print(f"Rate limited, re-queuing: {alert_data['title'][:30]}")
                    self.alert_queue.put((priority + 1, time.time(), alert_data))
                    time.sleep(2)  # Wait before retry
                
                # Minimum delay between requests
                time.sleep(2.5)  # 24 requests/minute max
                
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Queue processing error: {e}")
                time.sleep(1)
    
    def start(self):
        """Start the alert processing thread"""
        if self.is_running:
            return
            
        self.is_running = True
        self.worker_thread = threading.Thread(target=self.process_queue, daemon=True)
        self.worker_thread.start()
        print("Alert Manager started")
    
    def stop(self):
        """Stop the alert processing"""
        self.is_running = False
        if hasattr(self, 'worker_thread'):
            self.worker_thread.join(timeout=5)
        print("Alert Manager stopped")
    
    def market_open_batch(self, alerts: List[Dict]):
        """Handle batch of market open alerts"""
        print(f"Processing {len(alerts)} market open alerts...")
        
        for alert in alerts:
            priority = 1 if alert.get('type') == 'CRITICAL' else 2
            self.add_alert(
                priority=priority,
                title=alert['title'], 
                message=alert['message'],
                alert_type=alert.get('type', 'INFO')
            )

# Usage example
if __name__ == "__main__":
    # Initialize alert manager
    manager = AlertManager()
    manager.start()
    
    # Sample market open alerts
    market_alerts = [
        {
            'title': 'SPX Market Open Analysis',
            'message': 'SPX: $6,584 | Consensus: 245/275 | BULLISH bias confirmed',
            'type': 'HIGH'
        },
        {
            'title': 'NVDA Breakout Alert', 
            'message': 'NVDA breaking $180 resistance | Volume: 50M+',
            'type': 'CRITICAL'
        },
        {
            'title': 'MAG 7 Status Update',
            'message': '5/7 stocks above key support levels | Market correlation: 0.85',
            'type': 'MEDIUM'
        }
    ]
    
    # Process batch
    manager.market_open_batch(market_alerts)
    
    # Keep running for demo
    try:
        time.sleep(30)
    finally:
        manager.stop()