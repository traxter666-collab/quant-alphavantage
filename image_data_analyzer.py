"""
SPX Image Data Analyzer
Captures and analyzes screenshots for real-time market data
"""

import os
from datetime import datetime

def analyze_screenshot_instructions():
    """Instructions for using image analysis for SPX data"""
    
    print("SPX IMAGE DATA ANALYSIS SETUP")
    print("=" * 40)
    
    print("\n1. SCREENSHOT CAPTURE:")
    print("   - Take screenshot of your trading platform")
    print("   - Include SPX price, volume, and key indicators")
    print("   - Save to this directory or provide path")
    print("   - Supported formats: PNG, JPG, JPEG")
    
    print("\n2. WHAT TO CAPTURE:")
    print("   ✓ Current SPX price (large, clear)")
    print("   ✓ Daily change (+/- points and %)")
    print("   ✓ Session high/low")
    print("   ✓ Volume if visible")
    print("   ✓ Time/timestamp")
    print("   ✓ RSI or other indicators")
    
    print("\n3. BEST SOURCES TO SCREENSHOT:")
    print("   - TradingView SPX chart")
    print("   - Think or Swim SPX")
    print("   - TD Ameritrade SPX")
    print("   - Interactive Brokers")
    print("   - Yahoo Finance S&P 500")
    print("   - Bloomberg Terminal")
    
    print("\n4. HOW TO USE:")
    print("   - Take screenshot")
    print("   - Upload/provide image path")
    print("   - I'll extract SPX data visually")
    print("   - Update analysis with real numbers")
    
    print("\n5. EXAMPLE WORKFLOW:")
    print("   You: 'Here's my TradingView screenshot'")
    print("   Me: 'I see SPX at 6543.20, +40.15 (+0.62%)'")
    print("   Me: Updates all analysis with real data")
    
    print("\nREADY TO ANALYZE!")
    print("Send me a screenshot of your SPX data.")

def create_screenshot_template():
    """Create a template for what to capture"""
    
    template = """
SPX SCREENSHOT CHECKLIST:
========================

□ Current SPX Price (main number)
□ Daily Change (+ or - points)  
□ Percentage Change (+ or - %)
□ Session High
□ Session Low
□ Current Time/Timestamp
□ Volume (if available)
□ RSI (if visible)
□ Key support/resistance levels

IDEAL SCREENSHOT LAYOUT:
[SPX PRICE: 6543.20]
[CHANGE: +40.15 (+0.62%)]
[HIGH: 6545.80]
[LOW: 6501.40] 
[TIME: 12:45 PM ET]
[RSI: 67.3]

TIPS:
- Make text as large as possible
- Good contrast (dark text on light background)
- Clear, unobstructed view
- Include multiple data points in one shot
- Avoid blurry or pixelated images
"""
    
    return template

if __name__ == "__main__":
    analyze_screenshot_instructions()
    print("\n" + "=" * 40)
    print(create_screenshot_template())