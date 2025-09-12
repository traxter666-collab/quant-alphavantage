#!/usr/bin/env python3
"""
Single Discord Integration Script - Handles all content properly
Usage: python send_discord.py "title" "content"
"""
import requests
import json
import sys
from datetime import datetime, timezone

# Set UTF-8 encoding for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

WEBHOOK_URL = "https://discord.com/api/webhooks/1409686499745595432/BcxhXaFGMLy2rSPBMsN9Tb0wpKWxVYOnZnsfmETvHOeEJGsRep3N-lhZQcKxzrbMfHgk"

def send_to_discord(title, content):
    """Send message to Discord with proper formatting and error handling"""
    
    # Determine color based on title/content
    color = 3447003  # Default blue
    if "🚨" in title or "CRITICAL" in title.upper():
        color = 16711680  # Red
    elif "🟢" in content or "BUY" in content:
        color = 65280  # Green
    elif "🟡" in content or "CONSIDER" in content:
        color = 16776960  # Yellow
    elif "🔴" in content or "AVOID" in content:
        color = 16711680  # Red
    
    # Create embed payload
    embed = {
        "title": title[:256],  # Discord title limit
        "description": content[:4096],  # Discord description limit
        "color": color,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "footer": {
            "text": "SPX Trading System"
        }
    }
    
    payload = {
        "username": "Trading Analysis Bot",
        "embeds": [embed]
    }
    
    try:
        response = requests.post(
            WEBHOOK_URL,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 204:
            print("SUCCESS: Sent to Discord")
            return True
        else:
            print(f"ERROR: Discord {response.status_code} - {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"ERROR: Network {e}")
        return False
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def main():
    if len(sys.argv) != 3:
        print("Usage: python send_discord.py 'title' 'content'")
        print("Example: python send_discord.py 'SPX Analysis' 'Current: $6532.04...'")
        sys.exit(1)
    
    title = sys.argv[1]
    content = sys.argv[2]
    
    success = send_to_discord(title, content)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()