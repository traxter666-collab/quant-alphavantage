#!/usr/bin/env python3
"""
Clean Trader - Essential Data Only
Saves only useful, reusable trading patterns and metrics
"""

import json
import requests
from datetime import datetime
import os

class CleanTrader:
    def __init__(self):
        self.api_key = "ZFL38ZY98GSN7E1S"
        self.data_file = ".spx/trading_patterns.json"
        os.makedirs(".spx", exist_ok=True)
        
    def analyze_option(self, symbol, strike, opt_type, entry):
        """Clean analysis - essential data only"""
        
        # Get current price
        current = self.get_price(symbol)
        if not current:
            return None
            
        # Core calculations
        if opt_type.upper() == 'P':
            distance = current - strike
            itm = distance < 0
        else:
            distance = strike - current
            itm = distance < 0
            
        # Key metrics only
        analysis = {
            'timestamp': datetime.now().strftime("%H:%M"),
            'setup': f"{symbol} {strike}{opt_type}",
            'current_price': round(current, 2),
            'entry_price': entry,
            'distance': round(distance, 1),
            'itm': itm,
            'probability': self.calc_probability(distance, itm),
            'value_score': self.calc_value(distance, entry, itm),
            'action': self.get_action(distance, entry, itm)
        }
        
        # Display clean results
        self.display_clean(analysis)
        
        # Save useful patterns only
        self.save_pattern(analysis)
        
        return analysis
    
    def get_price(self, symbol):
        """Get current price - SPY conversion for SPXW"""
        if symbol.upper() in ['SPXW', 'SPX']:
            symbol = 'SPY'
            multiplier = 10
        else:
            multiplier = 1
            
        try:
            url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&entitlement=realtime&apikey={self.api_key}"
            response = requests.get(url, timeout=8)
            data = response.json()
            price = float(data['Global Quote']['05. price'])
            return price * multiplier
        except:
            return None
    
    def calc_probability(self, distance, itm):
        """Simple probability calculation"""
        if itm:
            return min(85, 70 + abs(distance))
        else:
            return max(15, 55 - (distance * 1.5))
    
    def calc_value(self, distance, entry, itm):
        """Value score: good/fair/poor"""
        if itm and entry < abs(distance):
            return "excellent"
        elif abs(distance) < 10 and entry < 5:
            return "good" 
        elif abs(distance) < 20:
            return "fair"
        else:
            return "poor"
    
    def get_action(self, distance, entry, itm):
        """Simple action: buy/wait/avoid"""
        if itm and entry < abs(distance) * 0.8:
            return "BUY"
        elif abs(distance) < 15 and entry < 8:
            return "CONSIDER"
        else:
            return "AVOID"
    
    def display_clean(self, analysis):
        """Clean display - no clutter"""
        print(f"\n{analysis['setup']} @ ${analysis['entry_price']}")
        print(f"Current: ${analysis['current_price']} | Distance: {analysis['distance']}")
        print(f"Probability: {analysis['probability']:.0f}% | Value: {analysis['value_score']}")
        print(f"ACTION: {analysis['action']}")
        
    def save_pattern(self, analysis):
        """Save only useful reusable patterns"""
        
        # Load existing patterns
        try:
            with open(self.data_file, 'r') as f:
                patterns = json.load(f)
        except:
            patterns = {
                'high_probability': [],  # >70% setups
                'value_plays': [],       # Undervalued entries  
                'winning_patterns': [],  # Successful trade types
                'last_updated': ''
            }
        
        # Save high probability setups
        if analysis['probability'] >= 70:
            patterns['high_probability'].append({
                'setup_type': analysis['setup'],
                'distance': analysis['distance'],
                'entry_price': analysis['entry_price'],
                'probability': analysis['probability'],
                'time': analysis['timestamp']
            })
            
        # Save value plays
        if analysis['value_score'] in ['excellent', 'good']:
            patterns['value_plays'].append({
                'setup_type': analysis['setup'],
                'value_score': analysis['value_score'],
                'entry_price': analysis['entry_price'],
                'distance': analysis['distance']
            })
        
        # Keep only last 10 of each type
        patterns['high_probability'] = patterns['high_probability'][-10:]
        patterns['value_plays'] = patterns['value_plays'][-10:]
        patterns['last_updated'] = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        # Save back to file
        with open(self.data_file, 'w') as f:
            json.dump(patterns, f, indent=2)
        
        print(f"Saved to patterns database")
    
    def show_patterns(self):
        """Show saved useful patterns"""
        try:
            with open(self.data_file, 'r') as f:
                patterns = json.load(f)
                
            print("\nUSEFUL PATTERNS:")
            print("High Probability Setups:")
            for p in patterns['high_probability'][-3:]:
                print(f"  {p['setup_type']} | {p['distance']}pts | {p['probability']:.0f}%")
                
            print("Value Plays:")  
            for p in patterns['value_plays'][-3:]:
                print(f"  {p['setup_type']} | {p['value_score']} | ${p['entry_price']}")
                
        except:
            print("No patterns saved yet")

def quick_trade(symbol, strike, opt_type, entry):
    """One-line trade analysis"""
    trader = CleanTrader()
    return trader.analyze_option(symbol, strike, opt_type, entry)

if __name__ == "__main__":
    trader = CleanTrader()
    
    # Example usage
    trader.analyze_option("SPXW", 6525, "P", 4.30)
    trader.show_patterns()