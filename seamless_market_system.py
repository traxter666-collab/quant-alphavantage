#!/usr/bin/env python3
"""
SEAMLESS MARKET SYSTEM
One command does everything - zero prompts, maximum intelligence
"""

import os
import sys
import time
import subprocess
import requests
from datetime import datetime, timedelta
import json

class SeamlessMarketSystem:
    def __init__(self):
        self.api_key = 'ZFL38ZY98GSN7E1S'
        self.base_path = os.path.dirname(os.path.abspath(__file__))
        self.spx_path = os.path.join(self.base_path, '.spx')

        # Ensure .spx directory exists
        os.makedirs(self.spx_path, exist_ok=True)

    def get_market_time(self):
        """Check current market time and status"""
        now = datetime.now()
        market_open = now.replace(hour=9, minute=30, second=0, microsecond=0)
        market_close = now.replace(hour=16, minute=0, second=0, microsecond=0)

        minutes_to_open = (market_open - now).total_seconds() / 60
        minutes_to_close = (market_close - now).total_seconds() / 60

        if now.hour < 9 or (now.hour == 9 and now.minute < 30):
            status = "PRE_MARKET"
        elif now.hour >= 16:
            status = "AFTER_HOURS"
        else:
            status = "MARKET_HOURS"

        return {
            'status': status,
            'minutes_to_open': minutes_to_open,
            'minutes_to_close': minutes_to_close,
            'current_time': now.strftime('%I:%M %p ET')
        }

    def quick_api_check(self):
        """Quick API validation - no output unless failure"""
        try:
            url = f'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=SPY&apikey={self.api_key}'
            r = requests.get(url, timeout=10)
            if r.status_code == 200 and 'Global Quote' in r.text:
                return {'status': 'OK', 'api': 'alphavantage'}
            return {'status': 'FAIL', 'error': 'API response invalid'}
        except:
            return {'status': 'FAIL', 'error': 'Connection failed'}

    def get_current_analysis(self):
        """Run analysis based on market time - seamless execution"""
        market_time = self.get_market_time()

        print(f"\n⏰ {market_time['current_time']} - {market_time['status']}")

        if market_time['status'] == 'PRE_MARKET':
            if market_time['minutes_to_open'] <= 60:
                print(f"📊 Market opens in {int(market_time['minutes_to_open'])} minutes")
                print("🔄 Running pre-market validation...")
                return self.run_pre_market_prep()
            else:
                print("📊 After-hours analysis...")
                return self.run_after_hours_analysis()

        elif market_time['status'] == 'MARKET_HOURS':
            print(f"📈 Market open - {int(market_time['minutes_to_close'])} minutes until close")
            return self.run_live_analysis()

        else:  # AFTER_HOURS
            print("📊 After-hours analysis...")
            return self.run_after_hours_analysis()

    def run_pre_market_prep(self):
        """Execute pre-market preparation seamlessly"""
        results = {
            'timestamp': datetime.now().isoformat(),
            'mode': 'PRE_MARKET_PREP',
            'systems': {}
        }

        # Quick API check
        api_status = self.quick_api_check()
        results['systems']['api'] = api_status
        if api_status['status'] == 'OK':
            print("✅ API Connected")

        # Run system validation
        print("🔄 Validating systems...")
        try:
            result = subprocess.run(
                ['python', 'system_validation.py'],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=self.base_path
            )

            if "100.0%" in result.stdout:
                print("✅ All Systems Operational (100%)")
                results['systems']['validation'] = 'PASS'
            else:
                print("⚠️  System health check completed")
                results['systems']['validation'] = 'PARTIAL'

        except Exception as e:
            print(f"⚠️  Validation warning: {str(e)[:50]}")
            results['systems']['validation'] = 'ERROR'

        # Get current market snapshot
        print("📊 Getting market snapshot...")
        snapshot = self.get_market_snapshot()
        results['market_data'] = snapshot

        # Save results
        self.save_results(results, 'pre_market_prep.json')

        print("\n🚀 READY FOR MARKET OPEN")
        print(f"   SPX: ${snapshot['spx']:.2f}")
        print(f"   SPY: ${snapshot['spy']:.2f}")
        print(f"   QQQ: ${snapshot['qqq']:.2f}")
        print(f"   IWM: ${snapshot['iwm']:.2f}")

        return results

    def run_live_analysis(self):
        """Execute live market analysis seamlessly"""
        results = {
            'timestamp': datetime.now().isoformat(),
            'mode': 'LIVE_MARKET',
            'analysis': {}
        }

        print("🔄 Running unified analysis...")

        try:
            result = subprocess.run(
                ['python', 'unified_spx_data.py'],
                capture_output=True,
                text=True,
                timeout=20,
                cwd=self.base_path
            )

            # Parse output for key metrics
            if "UNIFIED TRADING RECOMMENDATION" in result.stdout:
                print("✅ Analysis Complete")
                results['analysis']['status'] = 'SUCCESS'

                # Extract key info
                for line in result.stdout.split('\n'):
                    if 'SPX Price:' in line:
                        print(f"   {line.strip()}")
                    elif 'Consensus:' in line:
                        print(f"   {line.strip()}")
                    elif 'Direction:' in line:
                        print(f"   {line.strip()}")
                    elif 'Action:' in line:
                        print(f"   {line.strip()}")
            else:
                print("⚠️  Analysis completed with warnings")
                results['analysis']['status'] = 'PARTIAL'

        except Exception as e:
            print(f"⚠️  Analysis error: {str(e)[:50]}")
            results['analysis']['status'] = 'ERROR'

        # Get quick market snapshot
        snapshot = self.get_market_snapshot()
        results['market_data'] = snapshot

        self.save_results(results, 'live_market_analysis.json')

        return results

    def run_after_hours_analysis(self):
        """Execute after-hours analysis seamlessly"""
        results = {
            'timestamp': datetime.now().isoformat(),
            'mode': 'AFTER_HOURS',
            'analysis': {}
        }

        print("🔄 Getting after-hours data...")

        # Get market snapshot
        snapshot = self.get_market_snapshot()
        results['market_data'] = snapshot

        print(f"📊 After-Hours Status:")
        print(f"   SPX: ${snapshot['spx']:.2f}")
        print(f"   SPY: ${snapshot['spy']:.2f} (proxy)")
        print(f"   QQQ: ${snapshot['qqq']:.2f}")
        print(f"   IWM: ${snapshot['iwm']:.2f}")

        self.save_results(results, 'after_hours_analysis.json')

        return results

    def get_market_snapshot(self):
        """Get current prices for all major assets"""
        snapshot = {
            'timestamp': datetime.now().isoformat(),
            'spy': 0.0,
            'qqq': 0.0,
            'iwm': 0.0,
            'spx': 0.0
        }

        symbols = ['SPY', 'QQQ', 'IWM']

        for symbol in symbols:
            try:
                url = f'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={self.api_key}'
                r = requests.get(url, timeout=10)
                data = r.json()

                if 'Global Quote' in data and '05. price' in data['Global Quote']:
                    price = float(data['Global Quote']['05. price'])
                    snapshot[symbol.lower()] = price

                time.sleep(0.3)  # Rate limiting

            except:
                pass

        # Get accurate SPX from SPXW options using put-call parity
        # CRITICAL: Follow CLAUDE.md rules - use mcp__alphavantage__REALTIME_OPTIONS
        # This requires Claude MCP integration, fallback to unified_spx_data.py
        try:
            result = subprocess.run(
                ['python', os.path.join(self.base_path, 'unified_spx_data.py')],
                capture_output=True,
                text=True,
                timeout=10
            )
            for line in result.stdout.split('\n'):
                if 'Current:' in line and '$' in line:
                    # Extract SPX price from "Current: $6661.21"
                    price_str = line.split('$')[1].split()[0]
                    snapshot['spx'] = float(price_str.replace(',', ''))
                    break
        except:
            # Fallback only if unified script fails
            if snapshot['spy'] > 0:
                snapshot['spx'] = snapshot['spy'] * 10

        return snapshot

    def save_results(self, results, filename):
        """Save results to .spx directory"""
        filepath = os.path.join(self.spx_path, filename)
        try:
            with open(filepath, 'w') as f:
                json.dump(results, f, indent=2)
        except:
            pass

    def continuous_monitoring(self, interval=30):
        """Continuous monitoring mode - updates every N seconds"""
        print(f"\n🔄 CONTINUOUS MONITORING MODE")
        print(f"   Updates every {interval} seconds")
        print(f"   Press Ctrl+C to stop\n")

        try:
            while True:
                print("=" * 60)
                self.get_current_analysis()
                print(f"\n⏱️  Next update in {interval} seconds...")
                time.sleep(interval)

        except KeyboardInterrupt:
            print("\n\n✅ Monitoring stopped")
            return

def main():
    """Main entry point - seamless execution"""
    system = SeamlessMarketSystem()

    if len(sys.argv) > 1:
        if sys.argv[1] == 'monitor':
            # Continuous monitoring mode
            interval = int(sys.argv[2]) if len(sys.argv) > 2 else 30
            system.continuous_monitoring(interval)
        elif sys.argv[1] == 'quick':
            # Quick snapshot only
            snapshot = system.get_market_snapshot()
            print(f"SPX: ${snapshot['spx']:.2f} | SPY: ${snapshot['spy']:.2f} | QQQ: ${snapshot['qqq']:.2f} | IWM: ${snapshot['iwm']:.2f}")
        else:
            print("Usage: python seamless_market_system.py [monitor|quick]")
    else:
        # Default: Run appropriate analysis based on market time
        system.get_current_analysis()

if __name__ == "__main__":
    main()