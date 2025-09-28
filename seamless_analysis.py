#!/usr/bin/env python3
"""
Seamless Analysis Engine - No Prompts, Auto-Save, Continuous Flow
Eliminates user interruptions and provides smooth trading analysis
"""

import os
import json
import requests
from datetime import datetime
import concurrent.futures
import time

class SeamlessAnalysisEngine:
    def __init__(self):
        self.api_key = "ZFL38ZY98GSN7E1S"
        self.base_url = "https://www.alphavantage.co/query"
        self.session_dir = ".spx"
        self.ensure_session_directory()
        
    def ensure_session_directory(self):
        """Create .spx directory if it doesn't exist"""
        os.makedirs(self.session_dir, exist_ok=True)
        
    def auto_save_analysis(self, analysis_type, data, key_findings):
        """Automatically save analysis results without user prompts"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Save to session log
        log_entry = f"{timestamp}: {analysis_type} completed\n"
        with open(f"{self.session_dir}/session_log.txt", "a") as f:
            f.write(log_entry)
            
        # Save analysis cache
        cache_data = {
            "timestamp": timestamp,
            "analysis_type": analysis_type,
            "data": data,
            "key_findings": key_findings
        }
        
        with open(f"{self.session_dir}/analysis_cache.json", "w") as f:
            json.dump(cache_data, f, indent=2)
            
        # Auto-update levels if provided
        if "support" in key_findings or "resistance" in key_findings:
            self.update_key_levels(key_findings)
            
    def update_key_levels(self, findings):
        """Auto-update support/resistance levels"""
        try:
            with open(f"{self.session_dir}/levels.json", "r") as f:
                levels = json.load(f)
        except FileNotFoundError:
            levels = {"support": [], "resistance": [], "last_updated": ""}
            
        levels["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if "support" in findings:
            levels["support"] = findings["support"]
        if "resistance" in findings:  
            levels["resistance"] = findings["resistance"]
            
        with open(f"{self.session_dir}/levels.json", "w") as f:
            json.dump(levels, f, indent=2)
    
    def batch_market_data(self, symbols):
        """Get multiple market data points simultaneously"""
        urls = []
        for symbol in symbols:
            urls.append(f"{self.base_url}?function=GLOBAL_QUOTE&symbol={symbol}&entitlement=realtime&apikey={self.api_key}")
            
        results = {}
        
        def fetch_data(url):
            try:
                response = requests.get(url, timeout=10)
                return response.json()
            except Exception as e:
                return {"error": str(e)}
        
        # Run API calls in parallel
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            future_to_symbol = {executor.submit(fetch_data, url): symbols[i] 
                               for i, url in enumerate(urls)}
            
            for future in concurrent.futures.as_completed(future_to_symbol):
                symbol = future_to_symbol[future]
                try:
                    data = future.result()
                    results[symbol] = data
                except Exception as e:
                    results[symbol] = {"error": str(e)}
                    
        return results
    
    def seamless_option_analysis(self, symbol, strike, option_type, entry_price):
        """Complete option analysis without user prompts"""
        print(f"🎯 SEAMLESS ANALYSIS: {symbol} {strike}{option_type} @ ${entry_price}")
        print("=" * 60)
        
        # Step 1: Get market data (no prompts)
        market_data = self.batch_market_data([symbol, "SPY"])
        
        # Step 2: Calculate metrics automatically
        current_price = self.extract_price(market_data, symbol)
        analysis = self.calculate_option_metrics(current_price, strike, option_type, entry_price)
        
        # Step 3: Generate recommendations
        recommendations = self.generate_recommendations(analysis)
        
        # Step 4: Auto-save results
        key_findings = {
            "symbol": symbol,
            "current_price": current_price,
            "probability": analysis["probability"],
            "risk_reward": analysis["risk_reward"],
            "recommendation": recommendations["action"]
        }
        
        self.auto_save_analysis("option_analysis", analysis, key_findings)
        
        # Step 5: Display results (no prompts to continue)
        self.display_seamless_results(analysis, recommendations)
        
        return analysis
    
    def extract_price(self, market_data, symbol):
        """Extract price from market data"""
        try:
            if symbol in market_data and "Global Quote" in market_data[symbol]:
                return float(market_data[symbol]["Global Quote"]["05. price"])
        except:
            pass
        return 0
    
    def calculate_option_metrics(self, current_price, strike, option_type, entry_price):
        """Calculate option metrics automatically"""
        if option_type.upper() == "P":  # PUT
            otm_distance = current_price - strike
            breakeven = strike - entry_price
        else:  # CALL
            otm_distance = strike - current_price  
            breakeven = strike + entry_price
            
        probability = max(5, min(95, 50 - (otm_distance * 2)))
        risk_reward = (entry_price * 2) / entry_price  # Simplified 2:1 target
        
        return {
            "current_price": current_price,
            "strike": strike,
            "entry_price": entry_price,
            "otm_distance": otm_distance,
            "breakeven": breakeven,
            "probability": probability,
            "risk_reward": risk_reward,
            "option_type": option_type
        }
    
    def generate_recommendations(self, analysis):
        """Generate trading recommendations"""
        prob = analysis["probability"]
        distance = abs(analysis["otm_distance"])
        
        if prob > 60 and distance < 10:
            action = "BUY"
            confidence = "HIGH"
        elif prob > 40 and distance < 20:
            action = "CONSIDER" 
            confidence = "MEDIUM"
        else:
            action = "AVOID"
            confidence = "LOW"
            
        return {
            "action": action,
            "confidence": confidence,
            "reasoning": f"{prob:.0f}% probability, {distance:.1f} points OTM"
        }
    
    def display_seamless_results(self, analysis, recommendations):
        """Display results without prompts"""
        print(f"📊 Current: ${analysis['current_price']:.2f}")
        print(f"🎯 Strike: ${analysis['strike']:.2f}")
        print(f"💰 Entry: ${analysis['entry_price']:.2f}")
        print(f"📏 Distance: {analysis['otm_distance']:.1f} points")
        print(f"⚖️ Breakeven: ${analysis['breakeven']:.2f}")
        print(f"📈 Probability: {analysis['probability']:.0f}%")
        print(f"🎲 Risk/Reward: {analysis['risk_reward']:.1f}:1")
        print(f"✅ Action: {recommendations['action']} ({recommendations['confidence']} confidence)")
        print(f"💡 Reasoning: {recommendations['reasoning']}")
        print("📁 Analysis auto-saved to .spx/ directory")
        print("=" * 60)

if __name__ == "__main__":
    engine = SeamlessAnalysisEngine()
    
    # Example usage - no prompts, continuous flow
    engine.seamless_option_analysis("ORCL", 320, "P", 12.50)
    engine.seamless_option_analysis("SPXW", 6550, "C", 0.60)