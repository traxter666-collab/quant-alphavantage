#!/usr/bin/env python3
"""
Basic Live Streaming - 30 Second Refresh
Simple continuous updates for Monday trading
"""

import time
import subprocess
import os
from datetime import datetime

class BasicLiveStream:
    """Simple live streaming with 30-second updates"""

    def __init__(self, refresh_interval=30):
        self.refresh_interval = refresh_interval
        self.running = False
        print("Basic Live Stream initialized")
        print(f"Refresh interval: {refresh_interval} seconds")

    def start_streaming(self, command="smart_es"):
        """Start basic live streaming"""

        print(f"\n{'='*60}")
        print(f"STARTING BASIC LIVE STREAM")
        print(f"Command: {command}")
        print(f"Refresh: Every {self.refresh_interval} seconds")
        print(f"Press Ctrl+C to stop")
        print(f"{'='*60}")

        self.running = True
        update_count = 0

        try:
            while self.running:
                update_count += 1
                current_time = datetime.now().strftime("%H:%M:%S")

                print(f"\nUPDATE #{update_count} - {current_time}")
                print(f"{'='*50}")

                # Run the trading command
                try:
                    if command == "smart_es":
                        result = subprocess.run(
                            ["python", "trading_shortcuts.py", "smart_es"],
                            capture_output=True,
                            text=True,
                            timeout=60
                        )
                    elif command == "spx_quick":
                        result = subprocess.run(
                            ["python", "spx_command_router.py", "spx quick"],
                            capture_output=True,
                            text=True,
                            timeout=60
                        )
                    elif command == "multi":
                        result = subprocess.run(
                            ["python", "trading_shortcuts.py", "multi"],
                            capture_output=True,
                            text=True,
                            timeout=60
                        )
                    else:
                        print(f"Unknown command: {command}")
                        break

                    if result.returncode == 0:
                        # Extract key info from output
                        output = result.stdout
                        if "Current Price:" in output:
                            # Extract price line
                            for line in output.split('\n'):
                                if "Current Price:" in line or "ES Current:" in line:
                                    print(f"PRICE: {line}")
                                if "Action:" in line:
                                    print(f"ACTION: {line}")
                                if "Confidence:" in line:
                                    print(f"CONFIDENCE: {line}")
                        else:
                            # Show first few lines if no price found
                            lines = output.split('\n')[:5]
                            for line in lines:
                                if line.strip():
                                    print(line)
                    else:
                        print(f"ERROR: Command failed: {result.stderr}")

                except subprocess.TimeoutExpired:
                    print("TIMEOUT: Command timed out")
                except Exception as e:
                    print(f"ERROR: {e}")

                # Wait for next update
                print(f"\nNext update in {self.refresh_interval} seconds...")
                time.sleep(self.refresh_interval)

        except KeyboardInterrupt:
            print(f"\n\nSTOPPED: Streaming stopped by user")
            self.running = False
        except Exception as e:
            print(f"\nERROR: Streaming error: {e}")
            self.running = False

def main():
    """Main streaming interface"""

    print("BASIC LIVE STREAMING OPTIONS:")
    print("1. Smart ES Analysis (30s refresh)")
    print("2. SPX Quick Updates (30s refresh)")
    print("3. Multi-Asset View (30s refresh)")
    print("4. Custom interval")

    choice = input("\nSelect option (1-4): ").strip()

    if choice == "1":
        stream = BasicLiveStream(30)
        stream.start_streaming("smart_es")
    elif choice == "2":
        stream = BasicLiveStream(30)
        stream.start_streaming("spx_quick")
    elif choice == "3":
        stream = BasicLiveStream(30)
        stream.start_streaming("multi")
    elif choice == "4":
        interval = int(input("Enter refresh interval (seconds): "))
        command = input("Enter command (smart_es/spx_quick/multi): ")
        stream = BasicLiveStream(interval)
        stream.start_streaming(command)
    else:
        print("Invalid choice")

if __name__ == "__main__":
    main()