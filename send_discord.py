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
    if "🚨" in title or "CRITICAL" in title.upper() or "ACTIVE" in title.upper():
        color = 16711680  # Red for active alerts
    elif "🟢" in content or "BUY" in content or "CALL" in content:
        color = 65280  # Green for bullish
    elif "🟡" in content or "CONSIDER" in content or "STANDBY" in title.upper():
        color = 16776960  # Yellow for standby
    elif "🔴" in content or "AVOID" in content or "PUT" in content:
        color = 16711680  # Red for bearish

    # Create embed payload
    embed = {
        "title": title[:256],  # Discord title limit
        "description": content[:4096],  # Discord description limit
        "color": color,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "footer": {
            "text": "🤖 Powered by TraxterAI"
        }
    }

    payload = {
        "username": "Trading Monitor Bot",
        "embeds": [embed]
    }

    # Retry logic with exponential backoff
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = requests.post(
                WEBHOOK_URL,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=15  # Increased timeout
            )

            if response.status_code == 204:
                print("SUCCESS: Sent to Discord")
                return True
            elif response.status_code == 429:  # Rate limited
                retry_after = int(response.headers.get('Retry-After', 5))
                print(f"RATE LIMITED: Retry after {retry_after}s (attempt {attempt + 1})")
                if attempt < max_retries - 1:
                    import time
                    time.sleep(retry_after)
                    continue
            else:
                print(f"ERROR: Discord {response.status_code} - {response.text}")
                if attempt < max_retries - 1:
                    import time
                    time.sleep(2 * (attempt + 1))  # Exponential backoff
                    continue
                return False

        except requests.exceptions.Timeout:
            print(f"TIMEOUT: Attempt {attempt + 1} (15s timeout exceeded)")
            if attempt < max_retries - 1:
                import time
                time.sleep(2 * (attempt + 1))
                continue
            return False

        except requests.exceptions.RequestException as e:
            print(f"NETWORK ERROR: {e} (attempt {attempt + 1})")
            if attempt < max_retries - 1:
                import time
                time.sleep(2 * (attempt + 1))
                continue
            return False

        except Exception as e:
            print(f"ERROR: {e} (attempt {attempt + 1})")
            if attempt < max_retries - 1:
                import time
                time.sleep(2 * (attempt + 1))
                continue
            return False

    print(f"FAILED: All {max_retries} attempts exhausted")
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