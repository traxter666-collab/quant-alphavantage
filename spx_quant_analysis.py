import os
import requests
from datetime import datetime

def spx_quant_levels_analysis():
    """SPX analysis with today's quant levels integrated"""
    
    api_key = os.getenv('ALPHAVANTAGE_API_KEY', 'ZFL38ZY98GSN7E1S')
    base_url = "https://www.alphavantage.co/query"
    
    print("SPX QUANT LEVELS ANALYSIS - September 10, 2025")
    print("=" * 55)
    
    # Today's Quant Levels
    quant_levels = {
        'resistance_high': [6578, 6567],
        'reversal_high': 6560,
        'resistance_zone': [6538, 6542],
        'current_resistance': 6510,
        'strong_support': 6498,
        'support_zone_upper': [6488, 6498],
        'support_zone_lower': [6465, 6470],
        'reversal_low': 6465,
        'lower_levels': [6455, 6430]
    }
    
    # Get current market data
    spy_response = requests.get(f"{base_url}?function=GLOBAL_QUOTE&symbol=SPY&entitlement=realtime&apikey={api_key}")
    spy_data = spy_response.json()
    
    if "Global Quote" not in spy_data:
        print("Error getting market data")
        return
    
    spy_quote = spy_data["Global Quote"]
    spy_price = float(spy_quote["05. price"])
    spy_high = float(spy_quote["03. high"])
    spy_low = float(spy_quote["04. low"])
    spy_change = float(spy_quote["09. change"])
    
    spx_current = spy_price * 10
    spx_high = spy_high * 10
    spx_low = spy_low * 10
    
    print(f"CURRENT MARKET STATUS:")
    print(f"SPX: ${spx_current:.2f} ({spy_change * 10:+.2f} pts)")
    print(f"Session Range: ${spx_low:.2f} - ${spx_high:.2f}")
    
    # Determine current position relative to quant levels
    print(f"\nQUANT LEVEL ANALYSIS:")
    
    # Find nearest levels
    above_levels = []
    below_levels = []
    
    all_levels = [6578, 6567, 6560, 6542, 6538, 6510, 6498, 6488, 6482, 6470, 6465, 6455, 6430]
    
    for level in all_levels:
        if level > spx_current:
            above_levels.append(level)
        else:
            below_levels.append(level)
    
    # Sort levels
    above_levels.sort()
    below_levels.sort(reverse=True)
    
    print(f"Current Position: ${spx_current:.2f}")
    
    if above_levels:
        next_resistance = above_levels[0]
        print(f"Next Resistance: {next_resistance} (+{next_resistance - spx_current:.1f} pts)")
        
        # Identify what type of level it is
        if next_resistance == 6560:
            level_type = "HIGH REVERSAL PROBABILITY"
        elif next_resistance in [6538, 6542]:
            level_type = "RESISTANCE ZONE"
        elif next_resistance == 6510:
            level_type = "KEY RESISTANCE"
        else:
            level_type = "RESISTANCE"
        print(f"Level Type: {level_type}")
    
    if below_levels:
        next_support = below_levels[0]
        print(f"Next Support: {next_support} ({next_support - spx_current:.1f} pts)")
        
        # Identify support type
        if next_support == 6498:
            support_type = "STRONG SUPPORT"
        elif next_support in [6488, 6498]:
            support_type = "SUPPORT ZONE UPPER"
        elif next_support in [6465, 6470]:
            support_type = "HIGH REVERSAL PROBABILITY / SUPPORT ZONE LOWER"
        else:
            support_type = "SUPPORT"
        print(f"Support Type: {support_type}")
    
    # Trading strategy based on current position
    print(f"\nTRADING STRATEGY:")
    
    if spx_current < 6510:
        print(f"BELOW 6510 RESISTANCE:")
        print(f"• Bias: BEARISH until reclaim 6510")
        print(f"• Target: 6498 strong support (-{spx_current - 6498:.1f} pts)")
        print(f"• Extended Target: 6488-6498 support zone")
        print(f"• Major Target: 6465-6470 high reversal zone")
        
        put_strike = 6495 if spx_current > 6500 else 6485
        print(f"\nPUT PLAY:")
        print(f"SPXW250910P{put_strike}.0")
        print(f"Entry: Current levels")
        print(f"Target 1: 6498 (+{(spx_current - 6498) / 6498 * 100:.1f}% move)")
        print(f"Target 2: 6475 (+{(spx_current - 6475) / 6475 * 100:.1f}% move)")
        print(f"Stop: Above 6515")
        
    elif 6510 <= spx_current < 6538:
        print(f"BETWEEN 6510-6538:")
        print(f"• Status: Above key resistance, below resistance zone")
        print(f"• Bias: CAUTIOUSLY BULLISH")
        print(f"• Target: 6538-6542 resistance zone")
        print(f"• Major Target: 6560 high reversal level")
        
        call_strike = 6520 if spx_current > 6515 else 6515
        print(f"\nCALL PLAY:")
        print(f"SPXW250910C{call_strike}.0")
        print(f"Entry: Hold above 6510")
        print(f"Target 1: 6540 (+{(6540 - spx_current) / spx_current * 100:.1f}% move)")
        print(f"Target 2: 6560 (+{(6560 - spx_current) / spx_current * 100:.1f}% move)")
        print(f"Stop: Below 6505")
        
    elif 6538 <= spx_current < 6560:
        print(f"IN RESISTANCE ZONE (6538-6560):")
        print(f"• Status: CRITICAL AREA - High reversal probability at 6560")
        print(f"• Bias: NEUTRAL to BEARISH near 6560")
        print(f"• Strategy: FADE rallies near 6560")
        
        print(f"\nFADE STRATEGY:")
        print(f"SPXW250910P6550.0 - if approaches 6560")
        print(f"Target: Back to 6510-6520")
        print(f"Stop: Above 6565")
        
    # Risk-based position sizing
    print(f"\nRISK MANAGEMENT:")
    if spx_current < 6498:
        print(f"• Position: OVERSOLD - larger size OK near strong support")
        print(f"• Max Risk: 2-3% (strong quant support)")
    elif 6498 <= spx_current <= 6542:
        print(f"• Position: NORMAL - standard 1-2% risk")
        print(f"• Risk: Moderate (between key levels)")
    else:
        print(f"• Position: REDUCED - smaller size near resistance")
        print(f"• Max Risk: 1% (high reversal probability above)")
    
    # Key levels summary
    print(f"\nKEY LEVELS SUMMARY:")
    print(f"High Reversal: 6560 (sell zone)")
    print(f"Resistance Zone: 6538-6542")
    print(f"Key Resistance: 6510")
    print(f"Strong Support: 6498")
    print(f"Support Zone: 6488-6498")
    print(f"High Reversal: 6465-6470 (buy zone)")

if __name__ == "__main__":
    spx_quant_levels_analysis()