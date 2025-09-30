#!/usr/bin/env python3
"""
TRADE SIGNAL ENGINE
Auto-generates trade ideas when conditions align
Sends Discord notifications for high-probability setups
"""

import os
import json
import subprocess
from datetime import datetime
from typing import Dict, List, Optional

class TradeSignalEngine:
    def __init__(self):
        self.base_path = os.path.dirname(os.path.abspath(__file__))
        self.signals_file = '.spx/trade_signals.json'
        self.last_signal_time = None
        self.min_signal_interval = 300  # 5 minutes between same signals

    def analyze_trade_setup(self, market_data: Dict) -> Optional[Dict]:
        """Analyze market data and generate trade signal if conditions met"""

        signal = {
            'timestamp': datetime.now().isoformat(),
            'type': None,
            'symbol': None,
            'strike': None,
            'direction': None,
            'entry': None,
            'target': None,
            'stop': None,
            'size': None,
            'confidence': 0,
            'reasoning': []
        }

        spx_price = market_data.get('spx', 0)
        spy_price = market_data.get('spy', 0)

        if spx_price == 0 or spy_price == 0:
            return None

        # Load today's levels
        try:
            with open(os.path.join(self.base_path, '.spx/todays_levels.json'), 'r') as f:
                levels = json.load(f)
        except:
            levels = None

        # Get dealer positioning
        dealer_pos = market_data.get('dealer_positioning')

        # TRADE IDEA 1: King Node Magnet Play
        if dealer_pos and dealer_pos['spx'].get('primary_magnet'):
            king_node = dealer_pos['spx']['primary_magnet']
            distance = king_node - spx_price
            distance_pct = abs(distance / spx_price * 100)

            # If within 0.5% of King Node - high probability setup
            if distance_pct < 0.5:
                signal['type'] = 'KING_NODE_MAGNET'
                signal['confidence'] = 85  # UNTESTED level probability
                signal['reasoning'].append(f'Price within 0.5% of King Node at ${king_node:.2f}')

                if distance > 0:  # King Node above
                    signal['direction'] = 'CALL'
                    signal['symbol'] = 'SPY'
                    signal['strike'] = int(king_node / 10)  # SPY strike
                    signal['entry'] = spy_price
                    signal['target'] = signal['strike'] + 2
                    signal['stop'] = spy_price - 2
                    signal['reasoning'].append('Price being pulled UP to King Node')
                else:  # King Node below
                    signal['direction'] = 'PUT'
                    signal['symbol'] = 'SPY'
                    signal['strike'] = int(king_node / 10)
                    signal['entry'] = spy_price
                    signal['target'] = signal['strike'] - 2
                    signal['stop'] = spy_price + 2
                    signal['reasoning'].append('Price being pulled DOWN to King Node')

                signal['size'] = '1-2%'

        # TRADE IDEA 2: Resistance Zone Rejection
        if levels and spx_price >= 6680:  # At resistance zone
            resistance_upper = 6694
            if spx_price >= 6680 and spx_price <= resistance_upper:
                signal['type'] = 'RESISTANCE_REJECTION'
                signal['confidence'] = 75
                signal['direction'] = 'PUT'
                signal['symbol'] = 'SPY'
                signal['strike'] = int(spy_price)
                signal['entry'] = spy_price
                signal['target'] = 662  # Support zone
                signal['stop'] = spy_price + 2
                signal['size'] = '1-2%'
                signal['reasoning'].append(f'Price at resistance zone 6680-6694')
                signal['reasoning'].append('High probability reversal zone')

        # TRADE IDEA 3: Support Zone Bounce
        if levels and spx_price <= 6626:  # At support zone
            support_lower = 6620
            if spx_price >= support_lower and spx_price <= 6626:
                signal['type'] = 'SUPPORT_BOUNCE'
                signal['confidence'] = 75
                signal['direction'] = 'CALL'
                signal['symbol'] = 'SPY'
                signal['strike'] = int(spy_price) + 1
                signal['entry'] = spy_price
                signal['target'] = 668  # Resistance zone
                signal['stop'] = spy_price - 2
                signal['size'] = '1-2%'
                signal['reasoning'].append(f'Price at support zone 6620-6626')
                signal['reasoning'].append('High probability bounce zone')

        # TRADE IDEA 4: Gamma Flip Reversal
        if levels and spx_price <= 6610 and spx_price >= 6607:
            signal['type'] = 'GAMMA_FLIP_REVERSAL'
            signal['confidence'] = 85  # Very high probability
            signal['direction'] = 'CALL'
            signal['symbol'] = 'SPY'
            signal['strike'] = int(spy_price) + 1
            signal['entry'] = spy_price
            signal['target'] = 665
            signal['stop'] = spy_price - 1.5
            signal['size'] = '2-3%'
            signal['reasoning'].append('Price at gamma flip zone 6607-6610')
            signal['reasoning'].append('VERY HIGH reversal probability')
            signal['reasoning'].append('Dealer positioning supports reversal')

        # Only return signal if confidence >= 75%
        if signal['confidence'] >= 75 and signal['type']:
            return signal

        return None

    def format_signal_for_display(self, signal: Dict) -> str:
        """Format trade signal for terminal display"""
        output = [
            "\n" + "="*70,
            "🚨 TRADE SIGNAL DETECTED",
            "="*70,
            f"\n📊 SETUP: {signal['type']}",
            f"⏰ Time: {datetime.now().strftime('%I:%M:%S %p ET')}",
            f"🎯 Confidence: {signal['confidence']}%",
            f"\n💡 TRADE IDEA:",
            f"   Symbol: {signal['symbol']} {signal['strike']} {signal['direction']}",
            f"   Entry: ${signal['entry']:.2f}",
            f"   Target: ${signal['target']:.2f}",
            f"   Stop: ${signal['stop']:.2f}",
            f"   Size: {signal['size']} position",
            f"\n📋 REASONING:"
        ]

        for reason in signal['reasoning']:
            output.append(f"   • {reason}")

        output.extend([
            f"\n⚠️  RISK MANAGEMENT:",
            f"   - Use stop loss at ${signal['stop']:.2f}",
            f"   - Take profits at ${signal['target']:.2f}",
            f"   - Max position size: {signal['size']}",
            "="*70 + "\n"
        ])

        return "\n".join(output)

    def format_signal_for_discord(self, signal: Dict) -> tuple:
        """Format trade signal for Discord notification"""
        title = f"🚨 TRADE SIGNAL: {signal['type']}"

        message = f"""
⏰ TIME: {datetime.now().strftime('%I:%M:%S %p ET')}
🎯 CONFIDENCE: {signal['confidence']}%

💡 TRADE IDEA
Symbol: {signal['symbol']} {signal['strike']} {signal['direction']}
Entry: ${signal['entry']:.2f}
Target: ${signal['target']:.2f}
Stop: ${signal['stop']:.2f}
Size: {signal['size']} position

📋 REASONING
""" + "\n".join([f"• {r}" for r in signal['reasoning']]) + f"""

⚠️ RISK MANAGEMENT
- Stop loss: ${signal['stop']:.2f}
- Take profit: ${signal['target']:.2f}
- Max size: {signal['size']}

🔥 HIGH PROBABILITY SETUP - ACT QUICKLY
"""

        return (title, message)

    def send_to_discord(self, signal: Dict):
        """Send trade signal to Discord"""
        try:
            title, message = self.format_signal_for_discord(signal)
            subprocess.run([
                'python',
                os.path.join(self.base_path, 'send_discord.py'),
                title,
                message
            ], timeout=10)
        except Exception as e:
            print(f"Discord notification failed: {e}")

    def save_signal(self, signal: Dict):
        """Save signal to history file"""
        try:
            # Load existing signals
            if os.path.exists(self.signals_file):
                with open(self.signals_file, 'r') as f:
                    history = json.load(f)
            else:
                history = {'signals': []}

            # Add new signal
            history['signals'].append(signal)

            # Keep only last 50 signals
            history['signals'] = history['signals'][-50:]

            # Save
            with open(self.signals_file, 'w') as f:
                json.dump(history, f, indent=2)

        except Exception as e:
            print(f"Failed to save signal: {e}")

if __name__ == "__main__":
    # Test the signal engine
    engine = TradeSignalEngine()

    # Test with sample data
    test_data = {
        'spx': 6661.21,
        'spy': 666.12,
        'qqq': 598.73,
        'dealer_positioning': {
            'spx': {'primary_magnet': 6659.0},
            'spy': {'primary_magnet': 665.9},
            'qqq': {'primary_magnet': 594.0}
        }
    }

    signal = engine.analyze_trade_setup(test_data)
    if signal:
        print(engine.format_signal_for_display(signal))
    else:
        print("No trade signals at current price levels")