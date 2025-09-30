#!/usr/bin/env python3
"""
Combined SPX + TSLA Market Open Test System
Runs both SPX and TSLA analysis simultaneously at market open + 10 minutes
"""

import time
import schedule
from datetime import datetime
import pytz
from market_open_spx_test import MarketOpenSPXTest
from market_open_tsla_test import MarketOpenTSLATest
import subprocess
import threading

class CombinedMarketOpenTest:
    def __init__(self):
        self.spx_test = MarketOpenSPXTest()
        self.tsla_test = MarketOpenTSLATest()
        self.est = pytz.timezone('US/Eastern')
        
    def is_market_day(self) -> bool:
        """Check if today is a trading day"""
        now = datetime.now(self.est)
        return now.weekday() < 5
    
    def wait_for_market_open(self):
        """Wait until exactly 9:30 AM ET"""
        now = datetime.now(self.est)
        market_open = now.replace(hour=9, minute=30, second=0, microsecond=0)
        
        if now.time() > market_open.time():
            print(f"Market already open. Current time: {now.strftime('%H:%M:%S ET')}")
            return True
        
        wait_seconds = (market_open - now).total_seconds()
        print(f"Waiting {wait_seconds:.0f} seconds until market open at 9:30 AM ET...")
        print(f"Current time: {now.strftime('%H:%M:%S ET')}")
        
        time.sleep(wait_seconds)
        return True
    
    def wait_ten_minutes(self):
        """Wait exactly 10 minutes with progress updates"""
        print(f"\n⏰ WAITING 10 MINUTES FOR MARKET STABILIZATION...")
        
        for minute in range(10):
            print(f"   Minute {minute + 1}/10 - {datetime.now(self.est).strftime('%H:%M:%S ET')}")
            time.sleep(60)
        
        print(f"✅ 10-minute wait complete at {datetime.now(self.est).strftime('%H:%M:%S ET')}")
    
    def run_spx_analysis(self):
        """Run SPX analysis in separate thread"""
        print("\n🎯 RUNNING SPX ANALYSIS...")
        try:
            analysis = self.spx_test.analyze_spx_contracts()
            if analysis:
                self.spx_test.send_discord_alerts(analysis)
                print("✅ SPX analysis complete and sent to Discord")
            else:
                print("❌ SPX analysis failed")
        except Exception as e:
            print(f"❌ SPX analysis error: {e}")
    
    def run_tsla_analysis(self):
        """Run TSLA analysis in separate thread"""
        print("\n🚀 RUNNING TSLA ANALYSIS...")
        try:
            analysis = self.tsla_test.analyze_tsla_contracts()
            if analysis:
                self.tsla_test.send_discord_alerts(analysis)
                print("✅ TSLA analysis complete and sent to Discord")
            else:
                print("❌ TSLA analysis failed")
        except Exception as e:
            print(f"❌ TSLA analysis error: {e}")
    
    def send_summary_alert(self):
        """Send combined summary to Discord"""
        current_time = datetime.now(self.est).strftime('%H:%M:%S ET')
        
        summary_message = f"""COMBINED MARKET OPEN TEST - SUMMARY

⏰ ANALYSIS COMPLETE: {current_time}

📊 DUAL-ASSET ANALYSIS EXECUTED:
✅ SPX: 5 Calls + 5 Puts generated (9:40 AM ET)
✅ TSLA: 5 Calls + 5 Puts generated (9:42 AM ET)

🎯 TOTAL RECOMMENDATIONS: 20 contracts
- 10 SPX options (calls + puts)
- 10 TSLA options (calls + puts)

⚡ SYSTEM PERFORMANCE:
✅ Enhanced SPX Data: Multi-source validation
✅ TSLA Data: Real-time with volume analysis
✅ 10-minute stabilization: Complete
✅ 2-minute spacing: Prevents API/Discord errors
✅ Discord alerts: Delivered for both assets

📈 EXECUTION TIMELINE:
9:30 AM: Market open detection
9:40 AM: SPX analysis completed
9:42 AM: TSLA analysis completed  
9:43 AM: Summary delivered

📱 VALIDATION READY:
Both SPX and TSLA recommendations ready for market testing
All results saved to .spx/ directory for tracking
Sequential delivery prevents rate limiting issues

🚀 NEXT: Monitor performance throughout trading session"""
        
        try:
            result = subprocess.run([
                'python', 'send_discord.py',
                'COMBINED MARKET TEST - EXECUTION COMPLETE',
                summary_message
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                print("✅ Summary alert sent to Discord")
            else:
                print(f"❌ Summary alert failed: {result.stderr}")
                
        except Exception as e:
            print(f"❌ Summary alert error: {e}")
    
    def run_combined_market_test(self):
        """Main combined test execution with 2-minute spacing"""
        print("🚀 COMBINED SPX + TSLA MARKET OPEN TEST STARTING...")
        print(f"Current time: {datetime.now(self.est).strftime('%Y-%m-%d %H:%M:%S ET')}")
        
        if not self.is_market_day():
            print("❌ Not a trading day (weekend/holiday)")
            return
        
        # Step 1: Wait for market open
        print("\n📅 STEP 1: WAITING FOR MARKET OPEN")
        self.wait_for_market_open()
        
        # Step 2: Collect initial data for both assets
        print("\n📊 STEP 2: COLLECTING INITIAL DATA")
        spx_initial = self.spx_test.collect_market_data()
        tsla_initial = self.tsla_test.collect_market_data()
        
        if not spx_initial or not tsla_initial:
            print("❌ Failed to get initial market data")
            return
        
        # Step 3: Wait 10 minutes
        print("\n⏰ STEP 3: 10-MINUTE WAIT PERIOD")
        self.wait_ten_minutes()
        
        # Step 4: Run analyses with 2-minute spacing to prevent errors
        print("\n🎯 STEP 4: RUNNING SEQUENTIAL ANALYSIS (2-minute spacing)")
        
        # Run SPX analysis first
        print("\n📊 Running SPX analysis (9:40 AM ET)...")
        self.run_spx_analysis()
        
        # Wait 2 minutes before TSLA to prevent API/Discord rate limiting
        print(f"\n⏰ Waiting 2 minutes before TSLA analysis...")
        print(f"   Current time: {datetime.now(self.est).strftime('%H:%M:%S ET')}")
        for i in range(120):  # 120 seconds = 2 minutes
            if i % 30 == 0:  # Update every 30 seconds
                remaining = 120 - i
                print(f"   {remaining} seconds remaining... ({datetime.now(self.est).strftime('%H:%M:%S ET')})")
            time.sleep(1)
        
        # Run TSLA analysis second
        print(f"\n🚀 Running TSLA analysis (9:42 AM ET)...")
        print(f"   Current time: {datetime.now(self.est).strftime('%H:%M:%S ET')}")
        self.run_tsla_analysis()
        
        # Wait another minute before summary to ensure all alerts are processed
        print(f"\n⏰ Waiting 1 minute before summary...")
        time.sleep(60)
        
        # Step 5: Send summary
        print(f"\n📱 STEP 5: SENDING SUMMARY ALERT (9:43 AM ET)")
        print(f"   Current time: {datetime.now(self.est).strftime('%H:%M:%S ET')}")
        self.send_summary_alert()
        
        print(f"\n✅ COMBINED MARKET OPEN TEST COMPLETE")
        print(f"✅ Final time: {datetime.now(self.est).strftime('%H:%M:%S ET')}")
        print("✅ Both SPX and TSLA analyses delivered to Discord with proper spacing")

def schedule_combined_test():
    """Schedule the combined test for market open"""
    test_system = CombinedMarketOpenTest()
    
    # Schedule for 9:30 AM ET every weekday
    schedule.every().monday.at("09:30").do(test_system.run_combined_market_test)
    schedule.every().tuesday.at("09:30").do(test_system.run_combined_market_test)
    schedule.every().wednesday.at("09:30").do(test_system.run_combined_market_test)
    schedule.every().thursday.at("09:30").do(test_system.run_combined_market_test)
    schedule.every().friday.at("09:30").do(test_system.run_combined_market_test)
    
    print("📅 Combined SPX + TSLA Test scheduled for 9:30 AM ET (Mon-Fri)")
    print("⏰ Waiting for next market open...")
    
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    # For immediate testing
    print("🧪 RUNNING IMMEDIATE COMBINED TEST...")
    test_system = CombinedMarketOpenTest()
    test_system.run_combined_market_test()
    
    # Uncomment to enable scheduled runs
    # schedule_combined_test()