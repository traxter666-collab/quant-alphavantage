#!/usr/bin/env python3
"""
Enhanced Live Streaming - 1-10 Second Refresh
High-frequency updates for active trading
"""

import time
import threading
import subprocess
import json
import os
from datetime import datetime
from typing import Dict, Any

class EnhancedLiveStream:
    """Enhanced streaming with multiple refresh rates"""

    def __init__(self):
        self.running = False
        self.data_cache = {}
        self.last_updates = {}
        print("Enhanced Live Stream initialized")
        print("Multi-frequency streaming: 1s, 5s, 10s intervals")

    def get_quick_price_update(self) -> Dict[str, Any]:
        """Get quick price update (1-second capable)"""
        try:
            # Use fastest available method
            result = subprocess.run(
                ["python", "spx_live.py"],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                output = result.stdout
                # Extract price info
                price_info = {}
                for line in output.split('\n'):
                    if "SPX:" in line and "$" in line:
                        # Extract price from line like "SPX: $6618.20 (+37.70, +0.57%)"
                        parts = line.split("$")
                        if len(parts) > 1:
                            price_part = parts[1].split("(")[0].strip()
                            try:
                                price_info['price'] = float(price_part)
                                if "(" in line and "%" in line:
                                    # Extract change
                                    change_part = line.split("(")[1].split(")")[0]
                                    if "+" in change_part or "-" in change_part:
                                        price_info['change'] = change_part
                                break
                            except ValueError:
                                pass

                price_info['timestamp'] = datetime.now().strftime("%H:%M:%S")
                price_info['source'] = 'spx_live'
                return price_info

        except Exception as e:
            print(f"Quick update error: {e}")

        return {"error": "No price data", "timestamp": datetime.now().strftime("%H:%M:%S")}

    def get_smart_analysis(self, symbol="ES") -> Dict[str, Any]:
        """Get smart analysis (5-10 second refresh)"""
        try:
            result = subprocess.run(
                ["python", "trading_shortcuts.py", f"smart_{symbol.lower()}"],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                output = result.stdout
                analysis = {
                    'timestamp': datetime.now().strftime("%H:%M:%S"),
                    'symbol': symbol,
                    'raw_output': output
                }

                # Extract key metrics
                for line in output.split('\n'):
                    if "Action:" in line:
                        analysis['action'] = line.split("Action:")[1].strip()
                    elif "Confidence:" in line:
                        analysis['confidence'] = line.split("Confidence:")[1].strip()
                    elif "Score:" in line and "%" in line:
                        analysis['score'] = line.split("Score:")[1].strip()
                    elif "Current Price:" in line or symbol in line and "$" in line:
                        analysis['price_line'] = line.strip()

                return analysis

        except Exception as e:
            print(f"Smart analysis error: {e}")

        return {"error": "Analysis failed", "timestamp": datetime.now().strftime("%H:%M:%S")}

    def price_monitor_thread(self):
        """1-second price monitoring thread"""
        while self.running:
            try:
                price_data = self.get_quick_price_update()
                self.data_cache['price'] = price_data
                self.last_updates['price'] = datetime.now()

                # Display quick update
                if 'price' in price_data:
                    change = price_data.get('change', 'N/A')
                    print(f"⚡ {price_data['timestamp']} - SPX: ${price_data['price']:.2f} ({change})")

                time.sleep(1)  # 1-second refresh
            except Exception as e:
                print(f"Price monitor error: {e}")
                time.sleep(1)

    def analysis_monitor_thread(self, symbol="ES"):
        """5-second analysis monitoring thread"""
        while self.running:
            try:
                analysis_data = self.get_smart_analysis(symbol)
                self.data_cache['analysis'] = analysis_data
                self.last_updates['analysis'] = datetime.now()

                # Display analysis update
                if 'action' in analysis_data:
                    timestamp = analysis_data['timestamp']
                    action = analysis_data.get('action', 'N/A')
                    confidence = analysis_data.get('confidence', 'N/A')
                    print(f"🎯 {timestamp} - {symbol} Action: {action} | Confidence: {confidence}")

                time.sleep(5)  # 5-second refresh
            except Exception as e:
                print(f"Analysis monitor error: {e}")
                time.sleep(5)

    def start_enhanced_streaming(self, symbol="ES"):
        """Start enhanced multi-frequency streaming"""

        print(f"\n{'='*70}")
        print(f"ENHANCED LIVE STREAMING ACTIVATED")
        print(f"Symbol: {symbol}")
        print(f"Price Updates: Every 1 second")
        print(f"Analysis Updates: Every 5 seconds")
        print(f"Press Ctrl+C to stop")
        print(f"{'='*70}")

        self.running = True

        # Start monitoring threads
        price_thread = threading.Thread(target=self.price_monitor_thread, daemon=True)
        analysis_thread = threading.Thread(target=self.analysis_monitor_thread, args=(symbol,), daemon=True)

        try:
            price_thread.start()
            analysis_thread.start()

            # Main display loop
            while self.running:
                time.sleep(10)  # Display summary every 10 seconds

                print(f"\n📊 STREAMING SUMMARY - {datetime.now().strftime('%H:%M:%S')}")
                print(f"{'='*50}")

                # Show cached data
                if 'price' in self.data_cache:
                    price_data = self.data_cache['price']
                    if 'price' in price_data:
                        change = price_data.get('change', 'N/A')
                        print(f"Current SPX: ${price_data['price']:.2f} ({change})")

                if 'analysis' in self.data_cache:
                    analysis_data = self.data_cache['analysis']
                    if 'action' in analysis_data:
                        action = analysis_data.get('action', 'N/A')
                        confidence = analysis_data.get('confidence', 'N/A')
                        print(f"Current Signal: {action} | Confidence: {confidence}")

                print(f"{'='*50}")

        except KeyboardInterrupt:
            print(f"\n\n🛑 Enhanced streaming stopped by user")
            self.running = False
        except Exception as e:
            print(f"\n❌ Streaming error: {e}")
            self.running = False

def main():
    """Main enhanced streaming interface"""

    print("ENHANCED LIVE STREAMING OPTIONS:")
    print("1. ES Futures (1s price + 5s analysis)")
    print("2. NQ Futures (1s price + 5s analysis)")
    print("3. GC Futures (1s price + 5s analysis)")

    choice = input("\nSelect option (1-3): ").strip()

    stream = EnhancedLiveStream()

    if choice == "1":
        stream.start_enhanced_streaming("ES")
    elif choice == "2":
        stream.start_enhanced_streaming("NQ")
    elif choice == "3":
        stream.start_enhanced_streaming("GC")
    else:
        print("Invalid choice")

if __name__ == "__main__":
    main()