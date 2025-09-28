#!/usr/bin/env python3
"""
Heatseeker Touch Probability Tracking System
Implements the official Heatseeker touch probability model with historical tracking
"""

import json
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
from pathlib import Path

@dataclass
class TouchEvent:
    """Records a touch event at a specific level"""
    timestamp: str
    price_level: float
    touch_type: str  # 'EXACT', 'NEAR' (within 0.5%), 'PENETRATION'
    hold_result: bool  # True if level held, False if broken
    volume_confirmation: bool
    subsequent_move: float  # Points moved after touch
    timeframe: str  # '1min', '5min', '15min', etc.

@dataclass
class LevelStats:
    """Statistics for a specific price level"""
    level: float
    total_touches: int
    successful_holds: int
    failed_breaks: int
    hold_percentage: float
    last_touch_date: Optional[str]
    avg_reaction_size: float
    volume_weighted_success: float
    node_classification: str  # 'KING_NODE', 'GATEKEEPER', 'MINOR', 'UNCLASSIFIED'

class HeatSeekerTouchTracker:
    """
    Official Heatseeker Touch Probability System

    Implements the touch model:
    - 1st Touch: 90% hold probability
    - 2nd Touch: 66% hold probability
    - 3rd Touch: 33% hold probability
    - 4th+ Touch: 20% hold probability
    """

    def __init__(self, data_file: str = ".spx/touch_history.json"):
        self.data_file = Path(data_file)
        self.touch_history: Dict[float, List[TouchEvent]] = {}
        self.level_stats: Dict[float, LevelStats] = {}
        self.load_history()

    def load_history(self):
        """Load touch history from file"""
        if self.data_file.exists():
            try:
                with open(self.data_file, 'r') as f:
                    data = json.load(f)

                # Reconstruct touch events
                for level_str, events_data in data.get('touch_history', {}).items():
                    level = float(level_str)
                    self.touch_history[level] = [
                        TouchEvent(**event) for event in events_data
                    ]

                # Reconstruct level stats
                for level_str, stats_data in data.get('level_stats', {}).items():
                    level = float(level_str)
                    self.level_stats[level] = LevelStats(**stats_data)

            except Exception as e:
                print(f"Warning: Could not load touch history: {e}")
                self.touch_history = {}
                self.level_stats = {}

    def save_history(self):
        """Save touch history to file"""
        try:
            # Ensure directory exists
            self.data_file.parent.mkdir(exist_ok=True)

            # Convert to serializable format
            data = {
                'touch_history': {
                    str(level): [asdict(event) for event in events]
                    for level, events in self.touch_history.items()
                },
                'level_stats': {
                    str(level): asdict(stats)
                    for level, stats in self.level_stats.items()
                },
                'last_updated': datetime.now().isoformat()
            }

            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=2)

        except Exception as e:
            print(f"Warning: Could not save touch history: {e}")

    def record_touch(self, price: float, current_level: float,
                    volume_confirmed: bool = False, timeframe: str = "5min",
                    node_type: str = "UNCLASSIFIED") -> TouchEvent:
        """
        Record a touch event at a specific level

        Args:
            price: Current market price
            current_level: The level being tested (support/resistance)
            volume_confirmed: Whether volume confirmed the test
            timeframe: Timeframe of the touch
            node_type: Heatseeker node classification
        """
        # Determine touch type
        distance_pct = abs(price - current_level) / current_level * 100

        if distance_pct <= 0.05:  # Within 0.05%
            touch_type = "EXACT"
        elif distance_pct <= 0.5:  # Within 0.5%
            touch_type = "NEAR"
        else:
            touch_type = "PENETRATION"

        # Create touch event (hold_result and subsequent_move will be updated later)
        touch_event = TouchEvent(
            timestamp=datetime.now().isoformat(),
            price_level=current_level,
            touch_type=touch_type,
            hold_result=True,  # Assume hold initially
            volume_confirmation=volume_confirmed,
            subsequent_move=0.0,  # Will be updated
            timeframe=timeframe
        )

        # Add to history
        if current_level not in self.touch_history:
            self.touch_history[current_level] = []

        self.touch_history[current_level].append(touch_event)

        # Update level statistics
        self._update_level_stats(current_level, node_type)

        # Save to file
        self.save_history()

        return touch_event

    def update_touch_result(self, level: float, hold_result: bool,
                           subsequent_move: float):
        """Update the result of the most recent touch at a level"""
        if level in self.touch_history and self.touch_history[level]:
            # Update most recent touch
            latest_touch = self.touch_history[level][-1]
            latest_touch.hold_result = hold_result
            latest_touch.subsequent_move = subsequent_move

            # Update statistics
            self._update_level_stats(level)
            self.save_history()

    def get_touch_probability(self, level: float) -> Dict:
        """
        Get Heatseeker touch probability for a specific level

        Returns probability analysis based on touch history
        """
        if level not in self.touch_history:
            return {
                'touch_count': 0,
                'probability': 0.90,  # 1st touch default
                'confidence': 'HIGH',
                'classification': 'FRESH_LEVEL',
                'last_touch': None,
                'historical_success_rate': None
            }

        touches = self.touch_history[level]
        touch_count = len(touches)

        # Apply Heatseeker probability model
        if touch_count == 1:
            base_probability = 0.66  # 2nd touch
        elif touch_count == 2:
            base_probability = 0.33  # 3rd touch
        else:
            base_probability = 0.20  # 4th+ touch

        # Calculate historical success rate
        successful_holds = sum(1 for touch in touches if touch.hold_result)
        historical_rate = successful_holds / touch_count if touch_count > 0 else 0

        # Weight recent vs historical (70% model, 30% historical)
        final_probability = (base_probability * 0.7) + (historical_rate * 0.3)

        # Determine confidence
        if touch_count <= 1:
            confidence = 'HIGH'
        elif touch_count <= 3:
            confidence = 'MEDIUM'
        else:
            confidence = 'LOW'

        # Get last touch info
        last_touch = touches[-1] if touches else None

        return {
            'touch_count': touch_count + 1,  # +1 for current approaching touch
            'probability': final_probability,
            'confidence': confidence,
            'classification': self._classify_level_age(level),
            'last_touch': last_touch.timestamp if last_touch else None,
            'historical_success_rate': historical_rate,
            'model_probability': base_probability,
            'volume_factor': self._calculate_volume_factor(level)
        }

    def _update_level_stats(self, level: float, node_type: str = None):
        """Update statistics for a specific level"""
        if level not in self.touch_history:
            return

        touches = self.touch_history[level]
        if not touches:
            return

        successful_holds = sum(1 for touch in touches if touch.hold_result)
        failed_breaks = len(touches) - successful_holds
        hold_percentage = (successful_holds / len(touches)) * 100

        # Calculate average reaction size
        reactions = [abs(touch.subsequent_move) for touch in touches if touch.subsequent_move != 0]
        avg_reaction = sum(reactions) / len(reactions) if reactions else 0

        # Volume weighted success
        volume_confirmed_touches = [t for t in touches if t.volume_confirmation]
        volume_success = 0
        if volume_confirmed_touches:
            volume_holds = sum(1 for t in volume_confirmed_touches if t.hold_result)
            volume_success = (volume_holds / len(volume_confirmed_touches)) * 100

        # Update or create stats
        self.level_stats[level] = LevelStats(
            level=level,
            total_touches=len(touches),
            successful_holds=successful_holds,
            failed_breaks=failed_breaks,
            hold_percentage=hold_percentage,
            last_touch_date=touches[-1].timestamp,
            avg_reaction_size=avg_reaction,
            volume_weighted_success=volume_success,
            node_classification=node_type or self.level_stats.get(level, LevelStats(level, 0, 0, 0, 0, None, 0, 0, "UNCLASSIFIED")).node_classification
        )

    def _classify_level_age(self, level: float) -> str:
        """Classify level based on touch history and age"""
        if level not in self.touch_history:
            return "FRESH_LEVEL"

        touches = self.touch_history[level]
        touch_count = len(touches)

        if touch_count == 0:
            return "FRESH_LEVEL"
        elif touch_count == 1:
            return "TESTED_ONCE"
        elif touch_count <= 3:
            return "ESTABLISHED_LEVEL"
        else:
            return "HEAVILY_TESTED"

    def _calculate_volume_factor(self, level: float) -> float:
        """Calculate volume confirmation factor for probability adjustment"""
        if level not in self.touch_history:
            return 1.0

        touches = self.touch_history[level]
        if not touches:
            return 1.0

        volume_touches = sum(1 for touch in touches if touch.volume_confirmation)
        volume_ratio = volume_touches / len(touches)

        # Volume confirmation increases probability
        return 1.0 + (volume_ratio * 0.2)  # Up to 20% boost

    def get_level_ranking(self, current_price: float, max_distance: float = 50) -> List[Dict]:
        """
        Get ranked list of nearby levels by probability and significance
        """
        nearby_levels = []

        for level, stats in self.level_stats.items():
            distance = abs(level - current_price)
            if distance <= max_distance:
                prob_data = self.get_touch_probability(level)

                # Calculate significance score
                significance = (
                    stats.hold_percentage * 0.4 +  # Historical success
                    prob_data['probability'] * 100 * 0.3 +  # Model probability
                    (stats.avg_reaction_size / distance if distance > 0 else 0) * 0.2 +  # Reaction/distance ratio
                    (100 - stats.total_touches * 10) * 0.1  # Freshness factor
                )

                nearby_levels.append({
                    'level': level,
                    'distance': distance,
                    'probability': prob_data['probability'],
                    'significance': significance,
                    'classification': stats.node_classification,
                    'touch_count': stats.total_touches,
                    'last_touch': stats.last_touch_date
                })

        # Sort by significance score
        return sorted(nearby_levels, key=lambda x: x['significance'], reverse=True)

    def generate_probability_report(self, current_price: float) -> Dict:
        """Generate comprehensive probability report for current market conditions"""
        nearby_levels = self.get_level_ranking(current_price)

        # Find key levels
        resistance_levels = [l for l in nearby_levels if l['level'] > current_price][:3]
        support_levels = [l for l in nearby_levels if l['level'] < current_price][:3]

        return {
            'current_price': current_price,
            'timestamp': datetime.now().isoformat(),
            'resistance_levels': resistance_levels,
            'support_levels': support_levels,
            'total_tracked_levels': len(self.level_stats),
            'summary': {
                'nearest_resistance': resistance_levels[0] if resistance_levels else None,
                'nearest_support': support_levels[0] if support_levels else None,
                'high_probability_levels': [l for l in nearby_levels if l['probability'] > 0.7],
                'fresh_levels': [l for l in nearby_levels if l['touch_count'] <= 1]
            }
        }

def test_touch_tracker():
    """Test the touch tracking system"""
    tracker = HeatSeekerTouchTracker(".spx/test_touch_history.json")

    print("🔥 TESTING HEATSEEKER TOUCH TRACKER")
    print("=" * 50)

    # Test recording touches
    current_price = 6645.0

    # Record some test touches
    levels_to_test = [6650.0, 6625.0, 6645.0, 6630.0]

    for level in levels_to_test:
        # Simulate touch
        touch = tracker.record_touch(
            price=current_price,
            current_level=level,
            volume_confirmed=True,
            node_type="GATEKEEPER" if level == 6650 else "KING_NODE" if level == 6625 else "MINOR"
        )
        print(f"✅ Recorded touch at {level}: {touch.touch_type}")

        # Simulate result (randomly for test)
        import random
        hold_result = random.choice([True, True, False])  # 66% hold rate
        subsequent_move = random.uniform(-5, 10)

        tracker.update_touch_result(level, hold_result, subsequent_move)
        print(f"   Result: {'HELD' if hold_result else 'BROKE'} ({subsequent_move:+.1f} points)")

    # Test probability calculation
    print("\n🎯 PROBABILITY ANALYSIS:")
    for level in levels_to_test:
        prob_data = tracker.get_touch_probability(level)
        print(f"{level}: {prob_data['probability']:.1%} probability ({prob_data['confidence']} confidence)")
        print(f"   Touch #{prob_data['touch_count']} | {prob_data['classification']}")

    # Generate report
    print("\n📊 COMPREHENSIVE REPORT:")
    report = tracker.generate_probability_report(current_price)

    if report['summary']['nearest_resistance']:
        res = report['summary']['nearest_resistance']
        print(f"Next Resistance: {res['level']} ({res['probability']:.1%} hold probability)")

    if report['summary']['nearest_support']:
        sup = report['summary']['nearest_support']
        print(f"Next Support: {sup['level']} ({sup['probability']:.1%} hold probability)")

    print(f"High Probability Levels: {len(report['summary']['high_probability_levels'])}")
    print(f"Fresh Levels: {len(report['summary']['fresh_levels'])}")

    return tracker

if __name__ == "__main__":
    test_touch_tracker()