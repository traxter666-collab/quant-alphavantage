#!/usr/bin/env python3
"""
FULLY AUTOMATED TRADING SYSTEM
Complete automation with intelligent scheduling and monitoring
"""

import os
import sys
import time
import subprocess
from datetime import datetime, timedelta
import json
import signal

class AutomatedTradingSystem:
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.processes = {}
        self.running = True

        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self.shutdown)
        signal.signal(signal.SIGTERM, self.shutdown)

    def is_market_hours(self):
        """Check if market is open"""
        now = datetime.now()
        current_hour = now.hour
        current_minute = now.minute
        day_of_week = now.weekday()

        # Market closed on weekends
        if day_of_week >= 5:  # Saturday = 5, Sunday = 6
            return False

        # Market hours: 9:30 AM - 4:00 PM ET
        market_open_hour = 9
        market_open_minute = 30
        market_close_hour = 16
        market_close_minute = 0

        # Convert to minutes for easier comparison
        current_time = current_hour * 60 + current_minute
        market_open = market_open_hour * 60 + market_open_minute
        market_close = market_close_hour * 60 + market_close_minute

        return market_open <= current_time < market_close

    def time_until_market_open(self):
        """Calculate time until next market open"""
        now = datetime.now()

        # If it's weekend, calculate to next Monday
        if now.weekday() >= 5:
            days_until_monday = (7 - now.weekday()) % 7
            next_open = now + timedelta(days=days_until_monday)
            next_open = next_open.replace(hour=9, minute=30, second=0, microsecond=0)
        else:
            # Same day or next day
            next_open = now.replace(hour=9, minute=30, second=0, microsecond=0)
            if now.hour >= 16:  # After close, next day
                next_open += timedelta(days=1)
                # Skip weekend
                if next_open.weekday() >= 5:
                    days_until_monday = (7 - next_open.weekday()) % 7
                    next_open += timedelta(days=days_until_monday)

        return next_open - now

    def start_monitor(self):
        """Start the multi-asset trade monitor"""
        if 'monitor' not in self.processes or self.processes['monitor'].poll() is not None:
            print(f"[{datetime.now().strftime('%I:%M:%S %p')}] Starting multi-asset monitor...")

            process = subprocess.Popen(
                [sys.executable, 'multi_asset_trade_monitor.py'],
                cwd=self.base_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            self.processes['monitor'] = process
            print(f"✅ Monitor started (PID: {process.pid})")
            return True
        return False

    def stop_monitor(self):
        """Stop the monitor gracefully"""
        if 'monitor' in self.processes and self.processes['monitor'].poll() is None:
            print(f"[{datetime.now().strftime('%I:%M:%S %p')}] Stopping monitor...")
            self.processes['monitor'].terminate()

            # Wait up to 5 seconds for graceful shutdown
            try:
                self.processes['monitor'].wait(timeout=5)
                print("✅ Monitor stopped gracefully")
            except subprocess.TimeoutExpired:
                self.processes['monitor'].kill()
                print("⚠️  Monitor force-stopped")

            del self.processes['monitor']

    def check_processes(self):
        """Check if processes are still running"""
        for name, process in list(self.processes.items()):
            if process.poll() is not None:
                print(f"⚠️  {name} stopped unexpectedly (exit code: {process.returncode})")
                # Restart if during market hours
                if self.is_market_hours():
                    print(f"🔄 Restarting {name}...")
                    if name == 'monitor':
                        self.start_monitor()

    def daily_summary(self):
        """Generate end-of-day summary"""
        try:
            print("\n" + "="*70)
            print("📊 DAILY CLOSING SUMMARY")
            print("="*70)

            # Run daily closing analysis
            result = subprocess.run(
                [sys.executable, 'daily_closing_analysis.py'],
                cwd=self.base_dir,
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode == 0:
                print(result.stdout)
            else:
                print(f"⚠️  Summary generation failed: {result.stderr}")

        except Exception as e:
            print(f"❌ Summary error: {e}")

    def morning_startup(self):
        """Morning startup routine"""
        print("\n" + "="*70)
        print("🌅 MORNING STARTUP ROUTINE")
        print("="*70)

        # Test API connectivity
        print("\n1. Testing API connectivity...")
        try:
            result = subprocess.run(
                [sys.executable, 'dual_api_system.py'],
                cwd=self.base_dir,
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                print("✅ API connectivity verified")
            else:
                print("⚠️  API test failed - continuing anyway")
        except:
            print("⚠️  API test timeout - continuing anyway")

        # Start monitoring
        print("\n2. Starting multi-asset monitor...")
        self.start_monitor()

        print("\n✅ Startup complete - system is live")
        print("="*70)

    def shutdown(self, signum=None, frame=None):
        """Graceful shutdown"""
        print("\n\n🛑 SHUTTING DOWN AUTOMATED SYSTEM")
        self.running = False

        # Stop all processes
        for name, process in list(self.processes.items()):
            if process.poll() is None:
                print(f"Stopping {name}...")
                process.terminate()
                try:
                    process.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    process.kill()

        print("✅ All processes stopped")
        sys.exit(0)

    def run(self):
        """Main automation loop"""
        print("="*70)
        print("🤖 FULLY AUTOMATED TRADING SYSTEM")
        print("="*70)
        print()
        print("Features:")
        print("  • Automatic market hours detection")
        print("  • Intelligent startup/shutdown")
        print("  • Process monitoring and auto-restart")
        print("  • Daily closing analysis")
        print("  • Weekend awareness")
        print()
        print("Press Ctrl+C to stop")
        print("="*70)
        print()

        last_market_status = False
        last_check_time = datetime.now()

        while self.running:
            current_time = datetime.now()
            is_market_open = self.is_market_hours()

            # Status change handling
            if is_market_open != last_market_status:
                if is_market_open:
                    print(f"\n🔔 MARKET OPEN - {current_time.strftime('%I:%M %p ET')}")
                    self.morning_startup()
                else:
                    print(f"\n🔔 MARKET CLOSED - {current_time.strftime('%I:%M %p ET')}")
                    self.daily_summary()
                    self.stop_monitor()

                last_market_status = is_market_open

            # During market hours - monitor processes
            if is_market_open:
                # Check processes every 30 seconds
                if (current_time - last_check_time).total_seconds() >= 30:
                    self.check_processes()
                    last_check_time = current_time

            # Waiting status
            if not is_market_open:
                time_until = self.time_until_market_open()
                hours = int(time_until.total_seconds() // 3600)
                minutes = int((time_until.total_seconds() % 3600) // 60)

                print(f"[{current_time.strftime('%I:%M:%S %p')}] ⏰ Market opens in {hours}h {minutes}m", end='\r')
                time.sleep(60)  # Check every minute when market closed
            else:
                time.sleep(10)  # Check every 10 seconds during market hours

if __name__ == "__main__":
    system = AutomatedTradingSystem()
    try:
        system.run()
    except KeyboardInterrupt:
        system.shutdown()
