#!/usr/bin/env python3
"""
MARKET OPEN AUTO-LAUNCHER
Automatically starts monitoring when market opens
Runs in background, zero intervention required
"""

import time
import subprocess
import os
from datetime import datetime, timedelta

class MarketOpenLauncher:
    def __init__(self):
        self.base_path = os.path.dirname(os.path.abspath(__file__))
        self.monitoring_started = False

    def is_market_open(self):
        """Check if market is currently open"""
        now = datetime.now()
        market_open = now.replace(hour=9, minute=30, second=0, microsecond=0)
        market_close = now.replace(hour=16, minute=0, second=0, microsecond=0)

        return market_open <= now < market_close

    def time_until_open(self):
        """Calculate minutes until market open"""
        now = datetime.now()
        market_open = now.replace(hour=9, minute=30, second=0, microsecond=0)

        if now > market_open:
            # Market already opened or after hours
            return 0

        diff = market_open - now
        return diff.total_seconds() / 60

    def run_pre_market_prep(self):
        """Execute pre-market preparation"""
        print(f"\n{'='*60}")
        print(f"⏰ {datetime.now().strftime('%I:%M %p ET')}")
        print(f"🔄 Running pre-market preparation...")
        print(f"{'='*60}\n")

        subprocess.run(['python', os.path.join(self.base_path, 'seamless_market_system.py')])

    def start_monitoring(self):
        """Start continuous monitoring"""
        print(f"\n{'='*60}")
        print(f"🚀 MARKET OPEN - Starting continuous monitoring")
        print(f"⏰ {datetime.now().strftime('%I:%M %p ET')}")
        print(f"{'='*60}\n")

        # Start seamless monitoring in continuous mode
        subprocess.run([
            'python',
            os.path.join(self.base_path, 'seamless_market_system.py'),
            'monitor',
            '30'
        ])

    def wait_for_market_open(self):
        """Wait for market open and auto-launch monitoring"""
        print("🔄 MARKET OPEN AUTO-LAUNCHER")
        print("="*60)
        print("Waiting for market open...")
        print("Will automatically start monitoring at 9:30 AM ET")
        print("="*60)

        while True:
            minutes_to_open = self.time_until_open()

            if self.is_market_open() and not self.monitoring_started:
                self.monitoring_started = True
                self.start_monitoring()
                break

            elif minutes_to_open > 0:
                if minutes_to_open <= 60 and minutes_to_open > 55:
                    # Run pre-market prep at 60 minutes
                    self.run_pre_market_prep()

                if minutes_to_open <= 10:
                    print(f"⏰ Market opens in {int(minutes_to_open)} minutes...")
                    time.sleep(60)  # Check every minute when close
                else:
                    print(f"⏰ Market opens in {int(minutes_to_open)} minutes...")
                    time.sleep(300)  # Check every 5 minutes when far
            else:
                # After hours
                print("📊 Market closed - waiting for next trading day")
                time.sleep(3600)  # Check hourly

def main():
    launcher = MarketOpenLauncher()

    if launcher.is_market_open():
        # Market already open - start monitoring immediately
        launcher.start_monitoring()
    else:
        minutes = launcher.time_until_open()
        if minutes > 0 and minutes <= 60:
            # Within 1 hour of open - run prep now
            launcher.run_pre_market_prep()
            print(f"\n⏳ Waiting {int(minutes)} minutes until market open...")
            print("   (Auto-monitoring will start at 9:30 AM ET)")
        else:
            # Wait for market open
            launcher.wait_for_market_open()

if __name__ == "__main__":
    main()