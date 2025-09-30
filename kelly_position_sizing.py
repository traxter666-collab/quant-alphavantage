#!/usr/bin/env python3
"""
Kelly Criterion Position Sizing System
Mathematical risk optimization for SPX options trading
"""

import json
import math
from datetime import datetime
from typing import Dict, List, Optional, Tuple

class KellyPositionSizer:
    def __init__(self):
        self.session_file = ".spx/kelly_session.json"
        self.trade_history = []
        self.performance_metrics = {}

        # Default parameters (will be updated with actual data)
        self.default_win_rate = 0.65        # 65% default win rate
        self.default_avg_win = 0.75         # 75% average win
        self.default_avg_loss = 0.50        # 50% average loss (stop loss)
        self.max_kelly_fraction = 0.25      # Never risk more than 25% of Kelly
        self.min_position_size = 0.005      # 0.5% minimum position
        self.max_position_size = 0.05       # 5% maximum position

    def calculate_kelly_fraction(self, win_prob: float, avg_win: float, avg_loss: float) -> float:
        """Calculate Kelly Criterion fraction"""
        if avg_loss <= 0:
            return 0

        # Kelly formula: f = (bp - q) / b
        # where b = odds received on win (avg_win/avg_loss)
        # p = probability of win
        # q = probability of loss (1-p)

        b = avg_win / avg_loss  # Odds ratio
        p = win_prob
        q = 1 - win_prob

        kelly_fraction = (b * p - q) / b

        # Ensure reasonable bounds
        kelly_fraction = max(0, min(kelly_fraction, 1.0))

        return kelly_fraction

    def calculate_position_size(self,
                              confidence_score: float,
                              trade_type: str = "0DTE",
                              historical_performance: Optional[Dict] = None,
                              volatility_adjustment: float = 1.0) -> Dict:
        """Calculate optimal position size using Kelly Criterion"""

        # Use historical performance if available, otherwise defaults
        if historical_performance:
            win_rate = historical_performance.get('win_rate', self.default_win_rate)
            avg_win = historical_performance.get('avg_win', self.default_avg_win)
            avg_loss = historical_performance.get('avg_loss', self.default_avg_loss)
            trade_count = historical_performance.get('trade_count', 0)
        else:
            win_rate = self.default_win_rate
            avg_win = self.default_avg_win
            avg_loss = self.default_avg_loss
            trade_count = 0

        # Adjust win rate based on confidence score
        confidence_adjustment = (confidence_score / 100) ** 0.5  # Square root for smoothing
        adjusted_win_rate = win_rate * confidence_adjustment

        # Adjust for trade type
        if trade_type == "0DTE":
            # 0DTE options have higher risk but potentially higher rewards
            avg_win *= 1.2  # 20% higher potential wins
            avg_loss *= 1.1  # 10% higher potential losses
        elif trade_type == "WEEKLY":
            # Weekly options more conservative
            avg_win *= 0.9
            avg_loss *= 0.9

        # Calculate base Kelly fraction
        kelly_fraction = self.calculate_kelly_fraction(adjusted_win_rate, avg_win, avg_loss)

        # Apply fractional Kelly (conservative)
        fractional_kelly = kelly_fraction * self.max_kelly_fraction

        # Volatility adjustment
        vol_adjusted_size = fractional_kelly * volatility_adjustment

        # Confidence scaling
        confidence_scaled_size = vol_adjusted_size * (confidence_score / 100)

        # Apply hard limits
        final_position_size = max(self.min_position_size,
                                 min(confidence_scaled_size, self.max_position_size))

        # Sample size adjustment (reduce size with limited data)
        if trade_count < 20:
            sample_adjustment = min(1.0, trade_count / 20)
            final_position_size *= sample_adjustment

        return {
            'kelly_fraction': kelly_fraction,
            'fractional_kelly': fractional_kelly,
            'confidence_adjusted': confidence_scaled_size,
            'final_position_size': final_position_size,
            'position_percentage': final_position_size * 100,
            'input_parameters': {
                'confidence_score': confidence_score,
                'adjusted_win_rate': adjusted_win_rate,
                'avg_win': avg_win,
                'avg_loss': avg_loss,
                'trade_type': trade_type,
                'volatility_adjustment': volatility_adjustment,
                'trade_count': trade_count
            },
            'risk_metrics': {
                'expected_return': (adjusted_win_rate * avg_win) - ((1 - adjusted_win_rate) * avg_loss),
                'maximum_risk': final_position_size,
                'risk_per_dollar': final_position_size,
                'optimal_leverage': 1 / final_position_size if final_position_size > 0 else 0
            }
        }

    def calculate_contract_quantity(self,
                                  position_size: float,
                                  account_value: float,
                                  option_premium: float,
                                  min_contracts: int = 1) -> Dict:
        """Calculate number of contracts to trade"""

        if option_premium <= 0:
            return {'error': 'Invalid option premium'}

        # Calculate dollar amount to risk
        risk_amount = account_value * position_size

        # Calculate number of contracts
        # Each contract controls 100 shares, premium is per share
        contract_cost = option_premium * 100
        num_contracts = max(min_contracts, int(risk_amount / contract_cost))

        # Actual cost and position size
        actual_cost = num_contracts * contract_cost
        actual_position_size = actual_cost / account_value

        return {
            'recommended_contracts': num_contracts,
            'cost_per_contract': contract_cost,
            'total_cost': actual_cost,
            'actual_position_size': actual_position_size,
            'actual_percentage': actual_position_size * 100,
            'contracts_affordable': int(account_value * 0.05 / contract_cost),  # 5% max
            'risk_amount': risk_amount
        }

    def analyze_portfolio_heat(self,
                             current_positions: List[Dict],
                             new_position_size: float) -> Dict:
        """Analyze total portfolio heat including new position"""

        current_heat = sum([pos.get('position_size', 0) for pos in current_positions])
        total_heat = current_heat + new_position_size

        # Risk limits
        max_total_heat = 0.15      # 15% maximum total exposure
        max_single_direction = 0.08 # 8% maximum same direction
        max_correlated_heat = 0.10  # 10% maximum correlated positions

        # Direction analysis
        bullish_heat = sum([pos.get('position_size', 0) for pos in current_positions
                           if pos.get('direction') == 'BULLISH'])
        bearish_heat = sum([pos.get('position_size', 0) for pos in current_positions
                           if pos.get('direction') == 'BEARISH'])

        # Correlation analysis (simplified)
        spx_heat = sum([pos.get('position_size', 0) for pos in current_positions
                       if 'SPX' in pos.get('symbol', '')])
        tech_heat = sum([pos.get('position_size', 0) for pos in current_positions
                        if pos.get('symbol') in ['QQQ', 'XLK']])

        return {
            'current_heat': current_heat,
            'new_position_size': new_position_size,
            'total_heat': total_heat,
            'heat_percentage': total_heat * 100,
            'limits': {
                'max_total_heat': max_total_heat,
                'max_single_direction': max_single_direction,
                'max_correlated_heat': max_correlated_heat
            },
            'directional_exposure': {
                'bullish_heat': bullish_heat,
                'bearish_heat': bearish_heat,
                'net_exposure': bullish_heat - bearish_heat
            },
            'correlation_exposure': {
                'spx_heat': spx_heat,
                'tech_heat': tech_heat
            },
            'risk_warnings': self.generate_risk_warnings(total_heat, bullish_heat, bearish_heat, spx_heat),
            'position_allowed': total_heat <= max_total_heat,
            'recommended_adjustment': max(0, total_heat - max_total_heat) if total_heat > max_total_heat else 0
        }

    def generate_risk_warnings(self, total_heat: float, bullish_heat: float,
                             bearish_heat: float, spx_heat: float) -> List[str]:
        """Generate risk management warnings"""
        warnings = []

        if total_heat > 0.12:
            warnings.append("HIGH PORTFOLIO HEAT: Consider reducing position sizes")

        if bullish_heat > 0.08:
            warnings.append("EXCESSIVE BULLISH EXPOSURE: Diversify directional risk")

        if bearish_heat > 0.08:
            warnings.append("EXCESSIVE BEARISH EXPOSURE: Diversify directional risk")

        if spx_heat > 0.10:
            warnings.append("HIGH SPX CONCENTRATION: Consider other asset classes")

        if total_heat > 0.15:
            warnings.append("CRITICAL: Portfolio heat exceeds maximum limits")

        return warnings

    def update_performance_metrics(self, trade_result: Dict) -> None:
        """Update performance metrics with completed trade"""
        self.trade_history.append({
            'timestamp': datetime.now().isoformat(),
            'trade_result': trade_result
        })

        # Recalculate metrics
        self.calculate_historical_performance()

    def calculate_historical_performance(self) -> Dict:
        """Calculate historical performance metrics"""
        if not self.trade_history:
            return {
                'trade_count': 0,
                'win_rate': self.default_win_rate,
                'avg_win': self.default_avg_win,
                'avg_loss': self.default_avg_loss
            }

        trades = [t['trade_result'] for t in self.trade_history]
        winning_trades = [t for t in trades if t.get('pnl', 0) > 0]
        losing_trades = [t for t in trades if t.get('pnl', 0) <= 0]

        win_rate = len(winning_trades) / len(trades) if trades else 0
        avg_win = sum([t.get('pnl', 0) for t in winning_trades]) / len(winning_trades) if winning_trades else 0
        avg_loss = abs(sum([t.get('pnl', 0) for t in losing_trades]) / len(losing_trades)) if losing_trades else 0

        self.performance_metrics = {
            'trade_count': len(trades),
            'win_rate': win_rate,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'total_pnl': sum([t.get('pnl', 0) for t in trades]),
            'largest_win': max([t.get('pnl', 0) for t in trades]) if trades else 0,
            'largest_loss': min([t.get('pnl', 0) for t in trades]) if trades else 0
        }

        return self.performance_metrics

    def run_kelly_analysis(self,
                          confidence_score: float,
                          account_value: float = 50000,
                          option_premium: float = 2.50,
                          trade_type: str = "0DTE",
                          current_positions: List[Dict] = None) -> str:
        """Run complete Kelly Criterion analysis"""

        if current_positions is None:
            current_positions = []

        output = []

        output.append("KELLY CRITERION POSITION SIZING")
        output.append("=" * 40)
        output.append(f"Analysis Time: {datetime.now().strftime('%H:%M:%S')}")
        output.append(f"Confidence Score: {confidence_score}/100")
        output.append(f"Account Value: ${account_value:,}")
        output.append(f"Option Premium: ${option_premium:.2f}")
        output.append("")

        # Get historical performance
        historical = self.calculate_historical_performance()

        # Calculate position size
        sizing_result = self.calculate_position_size(
            confidence_score=confidence_score,
            trade_type=trade_type,
            historical_performance=historical
        )

        # Calculate contracts
        contract_result = self.calculate_contract_quantity(
            position_size=sizing_result['final_position_size'],
            account_value=account_value,
            option_premium=option_premium
        )

        # Portfolio heat analysis
        portfolio_analysis = self.analyze_portfolio_heat(
            current_positions=current_positions,
            new_position_size=sizing_result['final_position_size']
        )

        # Display results
        output.append("KELLY CALCULATION RESULTS:")
        output.append(f"  Raw Kelly Fraction: {sizing_result['kelly_fraction']:.3f}")
        output.append(f"  Fractional Kelly (25%): {sizing_result['fractional_kelly']:.3f}")
        output.append(f"  Final Position Size: {sizing_result['position_percentage']:.2f}%")
        output.append("")

        output.append("POSITION RECOMMENDATION:")
        output.append(f"  Recommended Contracts: {contract_result['recommended_contracts']}")
        output.append(f"  Total Cost: ${contract_result['total_cost']:,.0f}")
        output.append(f"  Actual Position Size: {contract_result['actual_percentage']:.2f}%")
        output.append("")

        output.append("RISK METRICS:")
        output.append(f"  Expected Return: {sizing_result['risk_metrics']['expected_return']:.3f}")
        output.append(f"  Maximum Risk: {sizing_result['risk_metrics']['maximum_risk']:.3f}")
        output.append(f"  Portfolio Heat: {portfolio_analysis['heat_percentage']:.2f}%")
        output.append("")

        # Risk warnings
        if portfolio_analysis['risk_warnings']:
            output.append("RISK WARNINGS:")
            for warning in portfolio_analysis['risk_warnings']:
                output.append(f"  WARNING: {warning}")
            output.append("")

        # Historical performance
        output.append("HISTORICAL PERFORMANCE:")
        output.append(f"  Trade Count: {historical['trade_count']}")
        output.append(f"  Win Rate: {historical['win_rate']:.1%}")
        output.append(f"  Avg Win: {historical['avg_win']:.2f}")
        output.append(f"  Avg Loss: {historical['avg_loss']:.2f}")
        output.append("")

        # Recommendation
        if portfolio_analysis['position_allowed']:
            output.append("RECOMMENDATION: POSITION APPROVED")
        else:
            output.append("RECOMMENDATION: REDUCE POSITION SIZE")
            output.append(f"  Suggested Reduction: {portfolio_analysis['recommended_adjustment']:.3f}")

        # Save session
        session_data = {
            'timestamp': datetime.now().isoformat(),
            'confidence_score': confidence_score,
            'sizing_result': sizing_result,
            'contract_result': contract_result,
            'portfolio_analysis': portfolio_analysis,
            'historical_performance': historical
        }

        import os
        os.makedirs(os.path.dirname(self.session_file), exist_ok=True)
        with open(self.session_file, 'w') as f:
            json.dump(session_data, f, indent=2, default=str)

        output.append("SESSION UPDATED: Kelly analysis saved to .spx/")

        return "\n".join(output)

def main():
    """Test Kelly Criterion position sizing"""
    kelly = KellyPositionSizer()

    print("KELLY CRITERION POSITION SIZING SYSTEM")
    print("=" * 45)

    # Test with high confidence trade
    result = kelly.run_kelly_analysis(
        confidence_score=85,
        account_value=50000,
        option_premium=2.50,
        trade_type="0DTE"
    )
    print(result)

if __name__ == "__main__":
    main()