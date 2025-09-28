#!/usr/bin/env python3
"""
Auto Trader - Seamless Analysis with Zero Prompts
Batch processing, auto-save, continuous flow
"""

import requests
import json
import os
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import time

class AutoTrader:
    def __init__(self):
        self.api_key = "ZFL38ZY98GSN7E1S"
        self.base_url = "https://www.alphavantage.co/query"
        self.session_dir = ".spx"
        os.makedirs(self.session_dir, exist_ok=True)
        
    def batch_analysis(self, trades):
        """Process multiple trades simultaneously without prompts"""
        print("AUTO TRADER - BATCH PROCESSING")
        print("=" * 50)
        
        results = []
        
        # Process all trades in parallel
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = []
            for trade in trades:
                future = executor.submit(self.analyze_trade, trade)
                futures.append(future)
            
            # Collect results as they complete
            for i, future in enumerate(futures):
                try:
                    result = future.result(timeout=30)
                    results.append(result)
                    print(f"Trade {i+1} analyzed: {result['symbol']} {result['recommendation']}")
                except Exception as e:
                    print(f"Trade {i+1} failed: {str(e)}")
                    
        # Auto-save batch results
        self.save_batch_results(results)
        return results
    
    def analyze_trade(self, trade):
        """Single trade analysis - no user interaction"""
        symbol = trade['symbol']
        strike = trade['strike'] 
        option_type = trade['type']
        entry = trade['entry']
        
        # Get market data
        market_data = self.get_market_data(symbol)
        
        # Calculate metrics
        current_price = self.extract_price(market_data)
        analysis = self.calculate_metrics(current_price, strike, option_type, entry)
        
        # Generate recommendation
        recommendation = self.get_recommendation(analysis)
        
        # Auto-save individual trade
        self.save_trade_analysis(symbol, analysis, recommendation)
        
        return {
            'symbol': symbol,
            'current_price': current_price,
            'strike': strike,
            'entry': entry,
            'probability': analysis['probability'],
            'recommendation': recommendation,
            'timestamp': datetime.now().strftime("%H:%M:%S")
        }
    
    def get_market_data(self, symbol):
        """Get market data without prompts"""
        try:
            url = f"{self.base_url}?function=GLOBAL_QUOTE&symbol={symbol}&entitlement=realtime&apikey={self.api_key}"
            response = requests.get(url, timeout=10)
            return response.json()
        except:
            return {}
    
    def extract_price(self, data):
        """Extract price from API response"""
        try:
            return float(data['Global Quote']['05. price'])
        except:
            return 0
    
    def calculate_metrics(self, current, strike, opt_type, entry):
        """Calculate option metrics"""
        if opt_type.upper() == 'P':
            distance = current - strike
            breakeven = strike - entry
        else:
            distance = strike - current
            breakeven = strike + entry
            
        probability = max(10, min(90, 50 - distance))
        
        return {
            'current': current,
            'distance': distance,
            'breakeven': breakeven,
            'probability': probability
        }
    
    def get_recommendation(self, analysis):
        """Generate recommendation"""
        prob = analysis['probability']
        if prob > 60:
            return "BUY"
        elif prob > 35:
            return "CONSIDER"
        else:
            return "AVOID"
    
    def save_trade_analysis(self, symbol, analysis, rec):
        """Auto-save trade analysis"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        trade_log = {
            'symbol': symbol,
            'analysis': analysis,
            'recommendation': rec,
            'timestamp': timestamp
        }
        
        # Append to trade log
        log_file = f"{self.session_dir}/trade_log.jsonl"
        with open(log_file, "a") as f:
            f.write(json.dumps(trade_log) + "\n")
    
    def save_batch_results(self, results):
        """Save batch results"""
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"{self.session_dir}/batch_analysis_{timestamp}.json"
        
        with open(filename, "w") as f:
            json.dump(results, f, indent=2)
        
        print(f"Batch results saved to {filename}")
    
    def quick_analysis(self, symbol, strike, opt_type, entry):
        """Single quick analysis - no prompts, immediate results"""
        print(f"QUICK ANALYSIS: {symbol} {strike}{opt_type} @ ${entry}")
        
        # Get data and analyze in one shot
        market_data = self.get_market_data(symbol)
        current = self.extract_price(market_data)
        
        if opt_type.upper() == 'P':
            distance = current - strike
            breakeven = strike - entry
        else:
            distance = strike - current  
            breakeven = strike + entry
            
        prob = max(10, min(90, 50 - distance))
        
        if prob > 60:
            rec = "BUY"
        elif prob > 35:
            rec = "CONSIDER"
        else:
            rec = "AVOID"
        
        print(f"Current: ${current:.2f} | Distance: {distance:.1f} | Prob: {prob:.0f}% | {rec}")
        
        # Auto-save
        self.save_trade_analysis(symbol, {
            'current': current, 
            'distance': distance,
            'probability': prob
        }, rec)
        
        return rec

def main():
    """Example usage - seamless execution"""
    trader = AutoTrader()
    
    # Batch analysis - no prompts
    trades = [
        {'symbol': 'ORCL', 'strike': 320, 'type': 'P', 'entry': 12.50},
        {'symbol': 'SPXW', 'strike': 6550, 'type': 'C', 'entry': 0.60},
        {'symbol': 'SPXW', 'strike': 6510, 'type': 'P', 'entry': 0.90}
    ]
    
    results = trader.batch_analysis(trades)
    
    # Quick individual analysis
    trader.quick_analysis('AAPL', 225, 'P', 3.50)

if __name__ == "__main__":
    main()