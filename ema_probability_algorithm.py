"""
EMA Probability Scoring Algorithm for SPX 0DTE Options Trading
Comprehensive scoring system combining EMA signals, momentum, and confluence
"""

import numpy as np
import pandas as pd
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional
from enum import Enum

class TimeFrame(Enum):
    """Timeframe definitions with weights"""
    MIN_30 = ("30min", 0.40)  # Primary trend
    MIN_15 = ("15min", 0.25)  # Secondary confirmation
    MIN_10 = ("10min", 0.15)  # Entry timing
    MIN_5 = ("5min", 0.10)    # Precision entry
    MIN_2 = ("2min", 0.05)    # Scalp timing
    MIN_1 = ("1min", 0.05)    # Tick precision

@dataclass
class EMAData:
    """EMA data structure for calculations"""
    ema_9: float
    ema_21: float
    ema_50: float
    ema_200: float
    price: float
    volume: float
    timestamp: str

@dataclass
class SMAData:
    """SMA data structure for confluence"""
    sma_20: float
    sma_50: float
    sma_100: float
    sma_200: float

class EMAProbabilityScorer:
    """Main class for EMA-based probability scoring"""
    
    def __init__(self):
        self.timeframes = list(TimeFrame)
        self.volume_ma_periods = 20
        
    def calculate_ema_alignment_score(self, ema_data: EMAData) -> Tuple[float, str]:
        """
        Calculate EMA alignment score (0-100)
        Returns: (score, direction)
        """
        price = ema_data.price
        ema_9 = ema_data.ema_9
        ema_21 = ema_data.ema_21
        ema_50 = ema_data.ema_50
        ema_200 = ema_data.ema_200
        
        # Base alignment scoring
        bullish_alignment = 0
        bearish_alignment = 0
        
        # Short-term momentum (EMA 9 vs 21) - 30 points
        if ema_9 > ema_21:
            bullish_alignment += 30
        else:
            bearish_alignment += 30
            
        # Medium-term trend (EMA 21 vs 50) - 25 points
        if ema_21 > ema_50:
            bullish_alignment += 25
        else:
            bearish_alignment += 25
            
        # Long-term trend (EMA 50 vs 200) - 25 points
        if ema_50 > ema_200:
            bullish_alignment += 25
        else:
            bearish_alignment += 25
            
        # Price position relative to EMAs - 20 points
        ema_levels = [ema_9, ema_21, ema_50, ema_200]
        emas_above_price = sum(1 for ema in ema_levels if price > ema)
        emas_below_price = 4 - emas_above_price
        
        bullish_alignment += (emas_above_price / 4) * 20
        bearish_alignment += (emas_below_price / 4) * 20
        
        # Determine direction and final score
        if bullish_alignment > bearish_alignment:
            return bullish_alignment, "BULLISH"
        else:
            return bearish_alignment, "BEARISH"
    
    def calculate_ema_momentum_score(self, current_ema: EMAData, 
                                   previous_ema: EMAData) -> float:
        """
        Calculate momentum acceleration score (0-100)
        """
        # Calculate slopes
        ema_9_slope = current_ema.ema_9 - previous_ema.ema_9
        ema_21_slope = current_ema.ema_21 - previous_ema.ema_21
        
        # Momentum differential
        momentum_diff = abs(ema_9_slope - ema_21_slope)
        
        # Price momentum
        price_momentum = current_ema.price - previous_ema.price
        
        # Normalize momentum (adjust these thresholds based on SPX volatility)
        momentum_score = min(100, (momentum_diff * 100) + abs(price_momentum * 10))
        
        return momentum_score
    
    def calculate_sma_confluence_score(self, ema_data: EMAData, 
                                     sma_data: SMAData) -> float:
        """
        Calculate SMA-EMA confluence score (0-100)
        """
        price = ema_data.price
        confluence_score = 0
        
        # Check EMA 50 vs SMA 50 alignment - 30 points
        if abs(ema_data.ema_50 - sma_data.sma_50) < (price * 0.001):  # Within 0.1%
            confluence_score += 30
        
        # Check support/resistance at SMA levels - 40 points
        sma_levels = [sma_data.sma_20, sma_data.sma_50, sma_data.sma_100, sma_data.sma_200]
        
        for sma_level in sma_levels:
            distance_pct = abs(price - sma_level) / price
            if distance_pct < 0.002:  # Within 0.2% of SMA level
                confluence_score += 10  # Max 40 points total
        
        # EMA 200 vs SMA 200 alignment - 30 points
        if abs(ema_data.ema_200 - sma_data.sma_200) < (price * 0.001):
            confluence_score += 30
            
        return min(100, confluence_score)
    
    def calculate_volume_score(self, current_volume: float, 
                             volume_history: List[float]) -> float:
        """
        Calculate volume confirmation score (0-100)
        """
        if len(volume_history) < self.volume_ma_periods:
            return 50  # Neutral if insufficient data
            
        avg_volume = np.mean(volume_history[-self.volume_ma_periods:])
        volume_ratio = current_volume / avg_volume
        
        # Score based on volume ratio
        if volume_ratio >= 2.0:
            return 100  # Very high volume
        elif volume_ratio >= 1.5:
            return 80   # High volume
        elif volume_ratio >= 1.2:
            return 65   # Above average
        elif volume_ratio >= 0.8:
            return 50   # Average
        else:
            return 25   # Below average
    
    def calculate_multi_timeframe_score(self, timeframe_data: Dict[str, EMAData],
                                      timeframe_history: Dict[str, List[EMAData]]) -> Dict:
        """
        Calculate multi-timeframe probability score
        """
        total_weighted_score = 0
        timeframe_scores = {}
        direction_votes = {"BULLISH": 0, "BEARISH": 0}
        
        for tf in self.timeframes:
            tf_name, weight = tf.value
            
            if tf_name not in timeframe_data:
                continue
                
            current_data = timeframe_data[tf_name]
            history = timeframe_history.get(tf_name, [])
            
            # EMA alignment score
            alignment_score, direction = self.calculate_ema_alignment_score(current_data)
            
            # Momentum score (if history available)
            momentum_score = 50  # Default neutral
            if len(history) > 0:
                momentum_score = self.calculate_ema_momentum_score(
                    current_data, history[-1]
                )
            
            # Combined timeframe score
            tf_score = (alignment_score * 0.7) + (momentum_score * 0.3)
            timeframe_scores[tf_name] = {
                'score': tf_score,
                'direction': direction,
                'alignment': alignment_score,
                'momentum': momentum_score
            }
            
            # Weight the score
            total_weighted_score += tf_score * weight
            direction_votes[direction] += weight
            
        # Determine overall direction
        overall_direction = "BULLISH" if direction_votes["BULLISH"] > direction_votes["BEARISH"] else "BEARISH"
        
        return {
            'total_score': round(total_weighted_score, 2),
            'direction': overall_direction,
            'timeframe_scores': timeframe_scores,
            'direction_confidence': max(direction_votes.values())
        }
    
    def calculate_final_probability(self, timeframe_data: Dict[str, EMAData],
                                  timeframe_history: Dict[str, List[EMAData]],
                                  sma_data: SMAData,
                                  volume_history: List[float]) -> Dict:
        """
        Calculate final entry probability combining all factors
        """
        # Multi-timeframe score (60% weight)
        mtf_result = self.calculate_multi_timeframe_score(timeframe_data, timeframe_history)
        mtf_score = mtf_result['total_score']
        
        # SMA confluence score (25% weight)
        primary_timeframe = "5min"  # Use 5min for confluence calculation
        confluence_score = 50  # Default neutral
        if primary_timeframe in timeframe_data:
            confluence_score = self.calculate_sma_confluence_score(
                timeframe_data[primary_timeframe], sma_data
            )
        
        # Volume score (15% weight)
        current_volume = timeframe_data.get("5min", EMAData(0,0,0,0,0,0,"")).volume
        volume_score = self.calculate_volume_score(current_volume, volume_history)
        
        # Final weighted score
        final_score = (
            (mtf_score * 0.60) +
            (confluence_score * 0.25) +
            (volume_score * 0.15)
        )
        
        # Probability classification
        if final_score >= 85:
            probability_class = "VERY_HIGH"
            recommendation = "STRONG BUY/SELL"
        elif final_score >= 75:
            probability_class = "HIGH"
            recommendation = "BUY/SELL"
        elif final_score >= 60:
            probability_class = "MODERATE"
            recommendation = "CONSIDER"
        elif final_score >= 45:
            probability_class = "LOW"
            recommendation = "WAIT"
        else:
            probability_class = "VERY_LOW"
            recommendation = "AVOID"
            
        return {
            'final_score': round(final_score, 2),
            'probability_class': probability_class,
            'recommendation': recommendation,
            'direction': mtf_result['direction'],
            'direction_confidence': mtf_result['direction_confidence'],
            'component_scores': {
                'multi_timeframe': round(mtf_score, 2),
                'sma_confluence': round(confluence_score, 2),
                'volume_confirmation': round(volume_score, 2)
            },
            'timeframe_breakdown': mtf_result['timeframe_scores']
        }

class ContractSelector:
    """Select optimal SPXW contract based on probability score"""
    
    def __init__(self):
        self.premium_range = (1.0, 4.0)  # $1-4 range as specified
        
    def select_optimal_contract(self, probability_result: Dict, 
                              current_spx_price: float,
                              available_strikes: List[Dict]) -> Dict:
        """
        Select best contract based on probability score
        """
        direction = probability_result['direction']
        score = probability_result['final_score']
        
        # Filter strikes by premium range
        valid_strikes = [
            strike for strike in available_strikes 
            if self.premium_range[0] <= strike['premium'] <= self.premium_range[1]
        ]
        
        if not valid_strikes:
            return {'error': 'No strikes available in $1-4 premium range'}
        
        # Select strategy based on probability score
        if score >= 75:
            # High probability: ATM or slightly ITM for higher delta
            target_delta = 0.6 if direction == "BULLISH" else -0.6
        elif score >= 60:
            # Moderate probability: Slightly OTM
            target_delta = 0.4 if direction == "BULLISH" else -0.4
        else:
            # Lower probability: OTM lottery ticket
            target_delta = 0.2 if direction == "BULLISH" else -0.2
            
        # Find strike closest to target delta
        best_strike = min(
            valid_strikes,
            key=lambda s: abs(s['delta'] - target_delta)
        )
        
        # Calculate position sizing based on score
        if score >= 85:
            max_risk_pct = 3.0  # Very high conviction
        elif score >= 75:
            max_risk_pct = 2.0  # High conviction
        elif score >= 60:
            max_risk_pct = 1.5  # Moderate conviction
        else:
            max_risk_pct = 1.0  # Low conviction
            
        return {
            'selected_strike': best_strike,
            'contract_type': 'CALL' if direction == 'BULLISH' else 'PUT',
            'max_risk_percentage': max_risk_pct,
            'entry_reason': f"{probability_result['probability_class']} probability {direction.lower()} setup",
            'target_profit': f"{50 if score < 60 else 75 if score < 80 else 100}%",
            'stop_loss': f"{30 if score >= 75 else 40 if score >= 60 else 50}%"
        }

# Example usage and testing
if __name__ == "__main__":
    scorer = EMAProbabilityScorer()
    selector = ContractSelector()
    
    # Example data structure
    sample_timeframe_data = {
        "30min": EMAData(6450.5, 6448.2, 6445.0, 6440.0, 6452.0, 1200000, "09:30:00"),
        "15min": EMAData(6451.2, 6449.0, 6446.5, 6441.0, 6452.0, 800000, "09:30:00"),
        "5min": EMAData(6452.8, 6450.5, 6448.0, 6443.0, 6452.0, 500000, "09:30:00")
    }
    
    sample_sma_data = SMAData(6449.0, 6446.0, 6442.0, 6438.0)
    sample_volume_history = [400000, 450000, 520000, 480000, 500000] * 4  # 20 periods
    
    # Calculate probability
    result = scorer.calculate_final_probability(
        sample_timeframe_data, {}, sample_sma_data, sample_volume_history
    )
    
    print("Probability Analysis Result:")
    print(f"Final Score: {result['final_score']}")
    print(f"Direction: {result['direction']}")
    print(f"Recommendation: {result['recommendation']}")
    print(f"Component Scores: {result['component_scores']}")
