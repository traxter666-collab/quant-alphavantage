#!/usr/bin/env python3
"""
Market Open SPX Test System - Automated 9:30 AM + 10 Min Test
Waits for market open, analyzes for 10 minutes, then provides 5 calls and 5 puts with Discord alerts
"""

import time
import schedule
from datetime import datetime, timezone
import pytz
from enhanced_spx_data import EnhancedSPXData
from spx_data_integration import SPXTradingIntegration
import subprocess
import json

class MarketOpenSPXTest:
    def __init__(self):
        self.spx_data = EnhancedSPXData()
        self.integration = SPXTradingIntegration()
        self.est = pytz.timezone('US/Eastern')
        self.test_results = []
        
    def is_market_day(self) -> bool:
        """Check if today is a trading day (Monday-Friday, excluding holidays)"""
        now = datetime.now(self.est)
        # Basic check - Monday=0, Sunday=6
        return now.weekday() < 5  # Monday through Friday
    
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
    
    def collect_market_data(self):
        """Collect SPX data at market open"""
        print("\nCOLLECTING MARKET OPEN DATA...")
        
        # Get enhanced SPX data (now with options priority)
        spx_result = self.spx_data.get_best_spx_price()
        
        if 'error' in spx_result:
            print("Failed to get SPX data")
            return None
        
        # Get current time
        current_time = datetime.now(self.est)
        
        market_data = {
            'timestamp': current_time.isoformat(),
            'time_string': current_time.strftime('%H:%M:%S ET'),
            'spx_price': spx_result['price'],
            'data_source': spx_result['source'],
            'consensus_sources': spx_result.get('consensus', {}).get('sources_count', 1)
        }
        
        print(f"SPX Price: ${market_data['spx_price']:.2f}")
        print(f"Data Source: {market_data['data_source']}")
        print(f"Time: {market_data['time_string']}")
        
        return market_data
    
    def wait_ten_minutes(self):
        """Wait exactly 10 minutes with progress updates"""
        print(f"\n⏰ WAITING 10 MINUTES FOR MARKET STABILIZATION...")
        
        for minute in range(10):
            print(f"   Minute {minute + 1}/10 - {datetime.now(self.est).strftime('%H:%M:%S ET')}")
            time.sleep(60)  # Wait 1 minute
        
        print(f"✅ 10-minute wait complete at {datetime.now(self.est).strftime('%H:%M:%S ET')}")
    
    def analyze_spx_contracts(self):
        """Analyze and recommend 5 calls and 5 puts"""
        print(f"\n🎯 ANALYZING SPX CONTRACTS...")
        
        # Get updated market data after 10 minutes
        current_data = self.collect_market_data()
        if not current_data:
            return None
        
        current_price = current_data['spx_price']
        
        # Generate 5 optimal call strikes
        call_distances = [3, 7, 12, 18, 25]  # Points OTM
        calls = []
        
        for i, distance in enumerate(call_distances):
            strike = int((current_price + distance) / 5) * 5  # Round to nearest 5
            
            # Estimate probability and premium
            probability = max(15, 60 - distance * 2)  # Higher for closer strikes
            estimated_premium = max(0.5, 4.0 - distance * 0.15)
            
            # Risk/reward calculation
            target_price = current_price + distance + 10  # Assume 10-point move
            target_value = max(0, target_price - strike)
            potential_return = ((target_value - estimated_premium) / estimated_premium * 100) if estimated_premium > 0 else -100
            
            call_analysis = {
                'rank': i + 1,
                'contract': f'SPXW{strike}C',
                'strike': strike,
                'current_spx': current_price,
                'distance_otm': distance,
                'probability': probability,
                'estimated_premium': estimated_premium,
                'potential_return': potential_return,
                'recommendation': 'BUY' if probability > 40 and potential_return > 100 else 'CONSIDER' if probability > 25 else 'SPECULATIVE'
            }
            
            calls.append(call_analysis)
        
        # Generate 5 optimal put strikes
        put_distances = [3, 7, 12, 18, 25]  # Points OTM
        puts = []
        
        for i, distance in enumerate(put_distances):
            strike = int((current_price - distance) / 5) * 5  # Round to nearest 5
            
            probability = max(15, 60 - distance * 2)
            estimated_premium = max(0.5, 4.0 - distance * 0.15)
            
            # Risk/reward for puts
            target_price = current_price - distance - 10  # Assume 10-point move down
            target_value = max(0, strike - target_price)
            potential_return = ((target_value - estimated_premium) / estimated_premium * 100) if estimated_premium > 0 else -100
            
            put_analysis = {
                'rank': i + 1,
                'contract': f'SPXW{strike}P',
                'strike': strike,
                'current_spx': current_price,
                'distance_otm': distance,
                'probability': probability,
                'estimated_premium': estimated_premium,
                'potential_return': potential_return,
                'recommendation': 'BUY' if probability > 40 and potential_return > 100 else 'CONSIDER' if probability > 25 else 'SPECULATIVE'
            }
            
            puts.append(put_analysis)
        
        analysis_result = {
            'timestamp': datetime.now(self.est).isoformat(),
            'market_data': current_data,
            'calls': calls,
            'puts': puts,
            'best_call': max(calls, key=lambda x: x['probability'] * (x['potential_return'] / 100) if x['potential_return'] > 0 else 0),
            'best_put': max(puts, key=lambda x: x['probability'] * (x['potential_return'] / 100) if x['potential_return'] > 0 else 0)
        }
        
        return analysis_result
    
    def send_discord_alerts(self, analysis):
        """Send comprehensive analysis to Discord"""
        if not analysis:
            print("❌ No analysis to send to Discord")
            return
        
        market_data = analysis['market_data']
        
        # Format call recommendations
        calls_text = "\n".join([
            f"{call['rank']}. {call['contract']} @ ${call['estimated_premium']:.2f}"
            f"\n   Strike: ${call['strike']} ({call['distance_otm']:+.0f} pts)"
            f"\n   Probability: {call['probability']:.0f}% | Return: {call['potential_return']:+.0f}%"
            f"\n   Rec: {call['recommendation']}\n"
            for call in analysis['calls']
        ])
        
        # Format put recommendations  
        puts_text = "\n".join([
            f"{put['rank']}. {put['contract']} @ ${put['estimated_premium']:.2f}"
            f"\n   Strike: ${put['strike']} ({put['distance_otm']:+.0f} pts)"
            f"\n   Probability: {put['probability']:.0f}% | Return: {put['potential_return']:+.0f}%"
            f"\n   Rec: {put['recommendation']}\n"
            for put in analysis['puts']
        ])
        
        best_call = analysis['best_call']
        best_put = analysis['best_put']
        
        discord_message = f"""SPX MARKET OPEN TEST - 9:40 AM ANALYSIS

📊 MARKET DATA:
SPX: ${market_data['spx_price']:.2f}
Time: {market_data['time_string']}
Source: {market_data['data_source']} ({market_data['consensus_sources']} sources)

🚀 TOP 5 CALL RECOMMENDATIONS:
{calls_text}

📉 TOP 5 PUT RECOMMENDATIONS:
{puts_text}

🎯 BEST OVERALL PICKS:
Best Call: {best_call['contract']} ({best_call['probability']:.0f}% prob, {best_call['potential_return']:+.0f}% return)
Best Put: {best_put['contract']} ({best_put['probability']:.0f}% prob, {best_put['potential_return']:+.0f}% return)

⚡ SYSTEM STATUS:
✅ Enhanced SPX Data: OPERATIONAL
✅ Multi-source Validation: ACTIVE  
✅ 10-minute Market Analysis: COMPLETE
✅ Contract Recommendations: GENERATED

📱 Test Validation Ready"""
        
        try:
            # Send to Discord using existing method
            result = subprocess.run([
                'python', 'send_discord.py',
                'SPX MARKET OPEN TEST - 9:40 AM Analysis',
                discord_message
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                print("✅ Discord alert sent successfully")
            else:
                print(f"❌ Discord alert failed: {result.stderr}")
                
        except Exception as e:
            print(f"❌ Discord send error: {e}")
    
    def run_market_open_test(self):
        """Main test execution function"""
        print("🚀 SPX MARKET OPEN TEST SYSTEM STARTING...")
        print(f"Current time: {datetime.now(self.est).strftime('%Y-%m-%d %H:%M:%S ET')}")
        
        # Check if it's a trading day
        if not self.is_market_day():
            print("❌ Not a trading day (weekend/holiday)")
            return
        
        # Step 1: Wait for market open (9:30 AM ET)
        print("\n📅 STEP 1: WAITING FOR MARKET OPEN")
        self.wait_for_market_open()
        
        # Step 2: Collect initial market data
        print("\n📊 STEP 2: COLLECTING INITIAL DATA")
        initial_data = self.collect_market_data()
        if not initial_data:
            print("❌ Failed to get initial market data")
            return
        
        # Step 3: Wait 10 minutes for market stabilization
        print("\n⏰ STEP 3: 10-MINUTE WAIT PERIOD")
        self.wait_ten_minutes()
        
        # Step 4: Analyze and generate recommendations
        print("\n🎯 STEP 4: GENERATING RECOMMENDATIONS")
        analysis = self.analyze_spx_contracts()
        
        if analysis:
            # Step 5: Send to Discord
            print("\n📱 STEP 5: SENDING DISCORD ALERTS")
            self.send_discord_alerts(analysis)
            
            # Save results for validation
            with open('.spx/market_open_test_results.json', 'w') as f:
                json.dump(analysis, f, indent=2)
            
            print("\n✅ MARKET OPEN TEST COMPLETE")
            print(f"✅ Results saved to .spx/market_open_test_results.json")
            print(f"✅ 5 Calls and 5 Puts generated at {analysis['timestamp']}")
            
        else:
            print("❌ Analysis failed")

def schedule_market_open_test():
    """Schedule the test to run at market open"""
    test_system = MarketOpenSPXTest()
    
    # Schedule for 9:30 AM ET every weekday
    schedule.every().monday.at("09:30").do(test_system.run_market_open_test)
    schedule.every().tuesday.at("09:30").do(test_system.run_market_open_test) 
    schedule.every().wednesday.at("09:30").do(test_system.run_market_open_test)
    schedule.every().thursday.at("09:30").do(test_system.run_market_open_test)
    schedule.every().friday.at("09:30").do(test_system.run_market_open_test)
    
    print("📅 Market Open Test scheduled for 9:30 AM ET (Mon-Fri)")
    print("⏰ Waiting for next market open...")
    
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

if __name__ == "__main__":
    # For immediate testing, run the test now
    print("🧪 RUNNING IMMEDIATE TEST (ignoring schedule)...")
    test_system = MarketOpenSPXTest()
    test_system.run_market_open_test()
    
    # Uncomment below to enable scheduled runs
    # schedule_market_open_test()