#!/usr/bin/env python3
"""
Dynamic Exit Management System
Real-time profit/loss optimization with multiple exit triggers
"""

import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from enum import Enum

class ExitReason(Enum):
    PROFIT_TARGET = "PROFIT_TARGET"
    STOP_LOSS = "STOP_LOSS"
    TIME_DECAY = "TIME_DECAY"
    PATTERN_INVALIDATION = "PATTERN_INVALIDATION"
    CONSENSUS_DEGRADATION = "CONSENSUS_DEGRADATION"
    PORTFOLIO_HEAT = "PORTFOLIO_HEAT"
    VOLATILITY_SPIKE = "VOLATILITY_SPIKE"
    MANUAL_EXIT = "MANUAL_EXIT"

class PositionStatus(Enum):
    ACTIVE = "ACTIVE"
    MONITORING = "MONITORING"
    EXITED = "EXITED"
    EXPIRED = "EXPIRED"

class DynamicExitManager:
    def __init__(self):
        self.session_file = ".spx/exit_management_session.json"
        self.positions = {}
        self.exit_history = []

        # Exit parameters
        self.profit_targets = [0.50, 1.00, 2.00]  # 50%, 100%, 200% profit levels
        self.profit_allocations = [0.33, 0.33, 0.34]  # Partial exit percentages
        self.max_loss_threshold = 0.60  # 60% max loss before stop
        self.time_decay_threshold = 30  # Minutes before expiry for time exit
        self.consensus_drop_threshold = 30  # Point drop that triggers review

    def create_position(self,
                       position_id: str,
                       symbol: str,
                       strike: float,
                       option_type: str,
                       entry_price: float,
                       quantity: int,
                       entry_confidence: float,
                       expiration_time: datetime) -> Dict:
        """Create new position for exit management"""

        position = {
            'position_id': position_id,
            'symbol': symbol,
            'strike': strike,
            'option_type': option_type,  # 'CALL' or 'PUT'
            'entry_price': entry_price,
            'current_price': entry_price,
            'quantity': quantity,
            'remaining_quantity': quantity,
            'entry_time': datetime.now(),
            'expiration_time': expiration_time,
            'entry_confidence': entry_confidence,
            'current_confidence': entry_confidence,
            'status': PositionStatus.ACTIVE,
            'profit_targets_hit': [],
            'exit_triggers': self.calculate_exit_triggers(entry_price, entry_confidence),
            'pnl_history': [],
            'last_update': datetime.now()
        }

        self.positions[position_id] = position
        return position

    def calculate_exit_triggers(self, entry_price: float, confidence: float) -> Dict:
        """Calculate dynamic exit trigger levels"""

        # Profit targets based on entry price
        targets = {
            'profit_50': entry_price * (1 + self.profit_targets[0]),
            'profit_100': entry_price * (1 + self.profit_targets[1]),
            'profit_200': entry_price * (1 + self.profit_targets[2])
        }

        # Stop loss based on confidence (higher confidence = wider stop)
        confidence_multiplier = 0.5 + (confidence / 200)  # 0.5 to 1.0 range
        stop_loss = entry_price * (1 - self.max_loss_threshold * confidence_multiplier)

        # Time-based exits
        time_exit_cushion = max(15, 60 - (confidence / 2))  # 15-60 minutes before expiry

        return {
            'profit_targets': targets,
            'stop_loss': stop_loss,
            'time_exit_minutes': time_exit_cushion,
            'confidence_floor': confidence * 0.7  # 30% confidence drop triggers review
        }

    def update_position_price(self, position_id: str, current_price: float,
                            current_confidence: Optional[float] = None) -> Dict:
        """Update position with current market price and confidence"""

        if position_id not in self.positions:
            return {'error': f'Position {position_id} not found'}

        position = self.positions[position_id]

        if position['status'] != PositionStatus.ACTIVE:
            return {'error': f'Position {position_id} is not active'}

        # Update position data
        old_price = position['current_price']
        position['current_price'] = current_price
        position['last_update'] = datetime.now()

        if current_confidence:
            position['current_confidence'] = current_confidence

        # Calculate current P&L
        pnl_dollar = (current_price - position['entry_price']) * position['remaining_quantity'] * 100
        pnl_percentage = ((current_price - position['entry_price']) / position['entry_price']) * 100

        # Add to P&L history
        position['pnl_history'].append({
            'timestamp': datetime.now(),
            'price': current_price,
            'pnl_dollar': pnl_dollar,
            'pnl_percentage': pnl_percentage
        })

        # Check for exit triggers
        exit_signal = self.check_exit_triggers(position_id)

        return {
            'position_id': position_id,
            'price_change': current_price - old_price,
            'current_pnl_dollar': pnl_dollar,
            'current_pnl_percentage': pnl_percentage,
            'exit_signal': exit_signal,
            'position_status': position['status'].value
        }

    def check_exit_triggers(self, position_id: str) -> Optional[Dict]:
        """Check if any exit triggers are activated"""

        position = self.positions[position_id]
        current_price = position['current_price']
        entry_price = position['entry_price']
        triggers = position['exit_triggers']

        # Check profit targets
        pnl_percentage = ((current_price - entry_price) / entry_price) * 100

        for i, target_pct in enumerate(self.profit_targets):
            target_key = f'profit_{int(target_pct * 100)}'

            if (pnl_percentage >= target_pct * 100 and
                target_key not in position['profit_targets_hit']):

                position['profit_targets_hit'].append(target_key)

                return {
                    'trigger_type': ExitReason.PROFIT_TARGET,
                    'target_level': target_pct * 100,
                    'exit_percentage': self.profit_allocations[i],
                    'message': f"Profit target {target_pct * 100:.0f}% hit - exit {self.profit_allocations[i] * 100:.0f}% of position",
                    'urgency': 'MEDIUM'
                }

        # Check stop loss
        if current_price <= triggers['stop_loss']:
            return {
                'trigger_type': ExitReason.STOP_LOSS,
                'exit_percentage': 1.0,
                'message': f"Stop loss triggered at ${current_price:.2f} (target: ${triggers['stop_loss']:.2f})",
                'urgency': 'IMMEDIATE'
            }

        # Check time decay
        time_to_expiry = position['expiration_time'] - datetime.now()
        minutes_to_expiry = time_to_expiry.total_seconds() / 60

        if minutes_to_expiry <= triggers['time_exit_minutes']:
            return {
                'trigger_type': ExitReason.TIME_DECAY,
                'exit_percentage': 1.0,
                'message': f"Time decay exit - {minutes_to_expiry:.0f} minutes to expiry",
                'urgency': 'HIGH'
            }

        # Check confidence degradation
        confidence_drop = position['entry_confidence'] - position['current_confidence']
        if confidence_drop >= self.consensus_drop_threshold:
            return {
                'trigger_type': ExitReason.CONSENSUS_DEGRADATION,
                'exit_percentage': 0.5,  # Partial exit
                'message': f"Confidence dropped {confidence_drop:.0f} points - reduce position",
                'urgency': 'MEDIUM'
            }

        # Check pattern invalidation (simplified)
        if pnl_percentage < -30:  # 30% loss might indicate pattern failure
            return {
                'trigger_type': ExitReason.PATTERN_INVALIDATION,
                'exit_percentage': 1.0,
                'message': "Pattern appears invalidated - exit position",
                'urgency': 'HIGH'
            }

        return None

    def execute_exit(self, position_id: str, exit_percentage: float,
                    exit_reason: ExitReason, exit_price: Optional[float] = None) -> Dict:
        """Execute position exit"""

        if position_id not in self.positions:
            return {'error': f'Position {position_id} not found'}

        position = self.positions[position_id]

        if position['status'] != PositionStatus.ACTIVE:
            return {'error': f'Position {position_id} is not active'}

        # Calculate exit details
        exit_price = exit_price or position['current_price']
        contracts_to_exit = int(position['remaining_quantity'] * exit_percentage)

        if contracts_to_exit <= 0:
            return {'error': 'No contracts to exit'}

        # Calculate P&L
        pnl_per_contract = (exit_price - position['entry_price']) * 100
        total_pnl = pnl_per_contract * contracts_to_exit
        pnl_percentage = ((exit_price - position['entry_price']) / position['entry_price']) * 100

        # Create exit record
        exit_record = {
            'exit_id': f"{position_id}_exit_{len(position.get('exits', []))}",
            'position_id': position_id,
            'exit_time': datetime.now(),
            'exit_reason': exit_reason.value,
            'exit_price': exit_price,
            'entry_price': position['entry_price'],
            'contracts_exited': contracts_to_exit,
            'pnl_dollar': total_pnl,
            'pnl_percentage': pnl_percentage,
            'hold_time_minutes': (datetime.now() - position['entry_time']).total_seconds() / 60
        }

        # Update position
        position['remaining_quantity'] -= contracts_to_exit

        if not hasattr(position, 'exits'):
            position['exits'] = []
        position['exits'].append(exit_record)

        # Update position status
        if position['remaining_quantity'] <= 0:
            position['status'] = PositionStatus.EXITED

        # Add to exit history
        self.exit_history.append(exit_record)

        return {
            'success': True,
            'exit_record': exit_record,
            'remaining_quantity': position['remaining_quantity'],
            'position_status': position['status'].value,
            'total_pnl': total_pnl,
            'pnl_percentage': pnl_percentage
        }

    def monitor_all_positions(self, market_data: Dict) -> List[Dict]:
        """Monitor all active positions for exit signals"""

        alerts = []

        for position_id, position in self.positions.items():
            if position['status'] != PositionStatus.ACTIVE:
                continue

            # Update position price (simplified - would use real market data)
            symbol = position['symbol']
            if symbol in market_data:
                current_price = market_data[symbol].get('price', position['current_price'])
                confidence = market_data[symbol].get('confidence', position['current_confidence'])

                update_result = self.update_position_price(position_id, current_price, confidence)

                if update_result.get('exit_signal'):
                    exit_signal = update_result['exit_signal']
                    alerts.append({
                        'position_id': position_id,
                        'symbol': symbol,
                        'trigger_type': exit_signal['trigger_type'],
                        'message': exit_signal['message'],
                        'urgency': exit_signal['urgency'],
                        'recommended_action': f"Exit {exit_signal['exit_percentage'] * 100:.0f}% of position",
                        'current_pnl': update_result['current_pnl_percentage']
                    })

        return alerts

    def get_position_summary(self, position_id: str) -> Dict:
        """Get comprehensive position summary"""

        if position_id not in self.positions:
            return {'error': f'Position {position_id} not found'}

        position = self.positions[position_id]

        # Calculate current metrics
        current_pnl_dollar = ((position['current_price'] - position['entry_price']) *
                             position['remaining_quantity'] * 100)
        current_pnl_percentage = ((position['current_price'] - position['entry_price']) /
                                 position['entry_price']) * 100

        hold_time = datetime.now() - position['entry_time']
        time_to_expiry = position['expiration_time'] - datetime.now()

        # Calculate total realized P&L from exits
        realized_pnl = sum([exit_rec['pnl_dollar'] for exit_rec in position.get('exits', [])])

        return {
            'position_id': position_id,
            'symbol': position['symbol'],
            'strike': position['strike'],
            'option_type': position['option_type'],
            'status': position['status'].value,
            'entry_details': {
                'entry_price': position['entry_price'],
                'entry_time': position['entry_time'],
                'entry_confidence': position['entry_confidence'],
                'original_quantity': position['quantity']
            },
            'current_details': {
                'current_price': position['current_price'],
                'current_confidence': position['current_confidence'],
                'remaining_quantity': position['remaining_quantity'],
                'last_update': position['last_update']
            },
            'pnl_metrics': {
                'unrealized_pnl_dollar': current_pnl_dollar,
                'unrealized_pnl_percentage': current_pnl_percentage,
                'realized_pnl_dollar': realized_pnl,
                'total_pnl_dollar': current_pnl_dollar + realized_pnl
            },
            'time_metrics': {
                'hold_time_minutes': hold_time.total_seconds() / 60,
                'time_to_expiry_minutes': time_to_expiry.total_seconds() / 60,
                'expiration_time': position['expiration_time']
            },
            'exit_triggers': position['exit_triggers'],
            'targets_hit': position['profit_targets_hit'],
            'exit_history': position.get('exits', [])
        }

    def get_portfolio_summary(self) -> Dict:
        """Get comprehensive portfolio summary"""

        active_positions = [pos for pos in self.positions.values()
                           if pos['status'] == PositionStatus.ACTIVE]

        if not active_positions:
            return {
                'active_positions': 0,
                'total_unrealized_pnl': 0,
                'total_realized_pnl': 0,
                'portfolio_heat': 0,
                'positions': []
            }

        # Calculate portfolio metrics
        total_unrealized_pnl = 0
        total_realized_pnl = 0
        position_summaries = []

        for position in active_positions:
            current_pnl = ((position['current_price'] - position['entry_price']) *
                          position['remaining_quantity'] * 100)
            realized_pnl = sum([exit_rec['pnl_dollar'] for exit_rec in position.get('exits', [])])

            total_unrealized_pnl += current_pnl
            total_realized_pnl += realized_pnl

            position_summaries.append({
                'position_id': position['position_id'],
                'symbol': position['symbol'],
                'unrealized_pnl': current_pnl,
                'pnl_percentage': ((position['current_price'] - position['entry_price']) /
                                  position['entry_price']) * 100,
                'time_to_expiry': (position['expiration_time'] - datetime.now()).total_seconds() / 60
            })

        return {
            'active_positions': len(active_positions),
            'total_unrealized_pnl': total_unrealized_pnl,
            'total_realized_pnl': total_realized_pnl,
            'total_pnl': total_unrealized_pnl + total_realized_pnl,
            'portfolio_heat': len(active_positions) * 0.02,  # Simplified calculation
            'positions': position_summaries,
            'last_update': datetime.now()
        }

    def run_exit_management_cycle(self, market_data: Dict) -> str:
        """Run complete exit management cycle"""

        output = []

        output.append("DYNAMIC EXIT MANAGEMENT SYSTEM")
        output.append("=" * 40)
        output.append(f"Monitoring Time: {datetime.now().strftime('%H:%M:%S')}")
        output.append("")

        # Monitor all positions
        exit_alerts = self.monitor_all_positions(market_data)

        if exit_alerts:
            output.append("EXIT SIGNALS DETECTED:")
            output.append("-" * 25)

            for alert in exit_alerts:
                urgency_symbol = {"IMMEDIATE": "🚨", "HIGH": "⚠️", "MEDIUM": "📊"}.get(alert['urgency'], "📈")
                output.append(f"{urgency_symbol} {alert['symbol']} - {alert['trigger_type']}")
                output.append(f"   {alert['message']}")
                output.append(f"   Current P&L: {alert['current_pnl']:+.1f}%")
                output.append(f"   Action: {alert['recommended_action']}")
                output.append("")
        else:
            output.append("No exit signals detected - all positions within parameters")
            output.append("")

        # Portfolio summary
        portfolio = self.get_portfolio_summary()

        output.append("PORTFOLIO SUMMARY:")
        output.append(f"  Active Positions: {portfolio['active_positions']}")
        output.append(f"  Total Unrealized P&L: ${portfolio['total_unrealized_pnl']:,.0f}")
        output.append(f"  Portfolio Heat: {portfolio['portfolio_heat']:.1%}")

        if portfolio['positions']:
            output.append("")
            output.append("POSITION DETAILS:")
            for pos in portfolio['positions']:
                output.append(f"  {pos['symbol']}: {pos['pnl_percentage']:+.1f}% "
                            f"(${pos['unrealized_pnl']:,.0f}) - "
                            f"{pos['time_to_expiry']:.0f}min to expiry")

        # Save session
        session_data = {
            'timestamp': datetime.now().isoformat(),
            'positions': {k: {**v, 'status': v['status'].value} for k, v in self.positions.items()},
            'exit_alerts': exit_alerts,
            'portfolio_summary': portfolio
        }

        import os
        os.makedirs(os.path.dirname(self.session_file), exist_ok=True)
        with open(self.session_file, 'w') as f:
            json.dump(session_data, f, indent=2, default=str)

        output.append("")
        output.append("SESSION UPDATED: Exit management data saved to .spx/")

        return "\n".join(output)

def main():
    """Test dynamic exit management system"""
    exit_manager = DynamicExitManager()

    print("DYNAMIC EXIT MANAGEMENT SYSTEM TEST")
    print("=" * 40)

    # Create test position
    test_expiry = datetime.now() + timedelta(hours=2)
    position = exit_manager.create_position(
        position_id="TEST_SPXW_6650C",
        symbol="SPXW",
        strike=6650,
        option_type="CALL",
        entry_price=5.50,
        quantity=10,
        entry_confidence=85,
        expiration_time=test_expiry
    )

    print(f"Created test position: {position['position_id']}")
    print(f"Entry: ${position['entry_price']:.2f}")
    print(f"Quantity: {position['quantity']} contracts")
    print("")

    # Simulate market data update
    market_data = {
        'SPXW': {
            'price': 7.25,  # Profitable move
            'confidence': 82
        }
    }

    # Run monitoring cycle
    result = exit_manager.run_exit_management_cycle(market_data)
    print(result)

if __name__ == "__main__":
    main()