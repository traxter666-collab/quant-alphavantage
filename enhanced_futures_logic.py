#!/usr/bin/env python3
"""
Enhanced Futures Trading Logic - Advanced Market Intelligence
Implements sophisticated futures trading logic with microstructure analysis
"""

import os
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import requests

class EnhancedFuturesLogic:
    """Advanced futures trading intelligence system"""

    def __init__(self):
        self.api_key = os.getenv('ALPHAVANTAGE_API_KEY')

        # Market sessions (Eastern Time)
        self.market_sessions = {
            'asian': {'start': 18, 'end': 24, 'characteristics': 'range_bound'},
            'european': {'start': 2, 'end': 8, 'characteristics': 'trending'},
            'us_premarket': {'start': 8, 'end': 9.5, 'characteristics': 'news_driven'},
            'us_regular': {'start': 9.5, 'end': 16, 'characteristics': 'high_liquidity'},
            'us_afterhours': {'start': 16, 'end': 18, 'characteristics': 'low_liquidity'}
        }

        # Volatility regimes
        self.volatility_regimes = {
            'ultra_low': {'threshold': 0.5, 'position_multiplier': 1.5, 'stop_multiplier': 0.7},
            'low': {'threshold': 1.0, 'position_multiplier': 1.2, 'stop_multiplier': 0.8},
            'normal': {'threshold': 2.0, 'position_multiplier': 1.0, 'stop_multiplier': 1.0},
            'high': {'threshold': 3.0, 'position_multiplier': 0.7, 'stop_multiplier': 1.3},
            'extreme': {'threshold': 5.0, 'position_multiplier': 0.3, 'stop_multiplier': 2.0}
        }

        # Economic events impact levels
        self.economic_events = {
            'FOMC': {'impact': 'extreme', 'reduce_hours_before': 2, 'position_reduction': 0.0},
            'NFP': {'impact': 'high', 'reduce_hours_before': 0.5, 'position_reduction': 0.5},
            'CPI': {'impact': 'high', 'reduce_hours_before': 0.5, 'position_reduction': 0.5},
            'GDP': {'impact': 'medium', 'reduce_hours_before': 0.25, 'position_reduction': 0.7},
            'PMI': {'impact': 'medium', 'reduce_hours_before': 0.25, 'position_reduction': 0.7}
        }

        print("Enhanced Futures Trading Logic initialized")
        print("Features: Session Analysis | Volatility Regimes | Cross-Market Correlation")

    def get_current_session(self) -> Dict[str, Any]:
        """Determine current trading session and characteristics"""

        current_hour = datetime.now().hour

        # Adjust for weekend (futures closed Saturday 6PM - Sunday 6PM ET)
        current_day = datetime.now().weekday()  # 0=Monday, 6=Sunday

        session_info = {
            'current_hour': current_hour,
            'current_day': current_day,
            'session': 'unknown',
            'characteristics': 'neutral',
            'recommended_strategy': 'standard',
            'position_multiplier': 1.0,
            'risk_adjustment': 1.0
        }

        # Weekend check (Saturday 6PM - Sunday 6PM, futures closed)
        if current_day == 5 and current_hour >= 18:  # Saturday after 6PM
            session_info.update({
                'session': 'weekend_closed',
                'characteristics': 'no_trading',
                'recommended_strategy': 'avoid',
                'position_multiplier': 0.0
            })
            return session_info

        if current_day == 6 and current_hour < 18:  # Sunday before 6PM
            session_info.update({
                'session': 'weekend_closed',
                'characteristics': 'no_trading',
                'recommended_strategy': 'avoid',
                'position_multiplier': 0.0
            })
            return session_info

        # Determine active session
        for session_name, session_data in self.market_sessions.items():
            start_hour = session_data['start']
            end_hour = session_data['end']

            # Handle overnight sessions (cross midnight)
            if start_hour > end_hour:  # e.g., Asian session 18-24, 0-2
                if current_hour >= start_hour or current_hour <= end_hour:
                    session_info.update({
                        'session': session_name,
                        'characteristics': session_data['characteristics'],
                        **self._get_session_strategy(session_name)
                    })
                    break
            else:  # Regular sessions
                if start_hour <= current_hour < end_hour:
                    session_info.update({
                        'session': session_name,
                        'characteristics': session_data['characteristics'],
                        **self._get_session_strategy(session_name)
                    })
                    break

        return session_info

    def _get_session_strategy(self, session: str) -> Dict[str, Any]:
        """Get recommended strategy for trading session"""

        strategies = {
            'asian': {
                'recommended_strategy': 'range_trading',
                'position_multiplier': 0.8,
                'risk_adjustment': 0.9,
                'preferred_style': 'fade_extremes'
            },
            'european': {
                'recommended_strategy': 'trend_following',
                'position_multiplier': 1.1,
                'risk_adjustment': 1.0,
                'preferred_style': 'momentum_breakouts'
            },
            'us_premarket': {
                'recommended_strategy': 'news_reaction',
                'position_multiplier': 0.7,
                'risk_adjustment': 1.2,
                'preferred_style': 'gap_analysis'
            },
            'us_regular': {
                'recommended_strategy': 'pattern_recognition',
                'position_multiplier': 1.0,
                'risk_adjustment': 1.0,
                'preferred_style': 'technical_patterns'
            },
            'us_afterhours': {
                'recommended_strategy': 'avoid_unless_news',
                'position_multiplier': 0.5,
                'risk_adjustment': 1.5,
                'preferred_style': 'minimal_activity'
            }
        }

        return strategies.get(session, {
            'recommended_strategy': 'standard',
            'position_multiplier': 1.0,
            'risk_adjustment': 1.0,
            'preferred_style': 'adaptive'
        })

    def detect_volatility_regime(self, price_data: Dict) -> Dict[str, Any]:
        """Detect current volatility regime and adjust trading parameters"""

        # Calculate daily volatility based on price change
        daily_change_pct = abs(price_data.get('change_percent', 0))

        # Determine regime
        regime_name = 'normal'
        regime_data = self.volatility_regimes['normal']

        for regime, data in self.volatility_regimes.items():
            if daily_change_pct <= data['threshold']:
                regime_name = regime
                regime_data = data
                break

        # Calculate ATR-based volatility (simplified)
        price = price_data.get('price', 6700)
        estimated_atr = price * (daily_change_pct / 100) * 1.5  # Rough ATR estimate

        return {
            'regime': regime_name,
            'daily_change_pct': daily_change_pct,
            'estimated_atr': estimated_atr,
            'position_multiplier': regime_data['position_multiplier'],
            'stop_multiplier': regime_data['stop_multiplier'],
            'risk_level': self._categorize_risk_level(daily_change_pct),
            'recommended_stops': {
                'tight': estimated_atr * 0.5,
                'normal': estimated_atr * 1.0,
                'wide': estimated_atr * 1.5
            }
        }

    def _categorize_risk_level(self, change_pct: float) -> str:
        """Categorize risk level based on volatility"""
        if change_pct <= 0.5:
            return 'LOW'
        elif change_pct <= 1.5:
            return 'MEDIUM'
        elif change_pct <= 3.0:
            return 'HIGH'
        else:
            return 'EXTREME'

    def analyze_cross_market_correlation(self) -> Dict[str, Any]:
        """Analyze cross-market correlations for futures intelligence"""

        correlations = {}

        try:
            # Get key market data
            symbols = ['SPY', 'QQQ', 'IWM', 'TLT', 'GLD', 'DXY']  # VIX not available via API
            market_data = {}

            for symbol in symbols:
                try:
                    url = "https://www.alphavantage.co/query"
                    params = {
                        'function': 'GLOBAL_QUOTE',
                        'symbol': symbol,
                        'apikey': self.api_key
                    }

                    response = requests.get(url, params=params, timeout=10)
                    data = response.json()

                    if 'Global Quote' in data:
                        quote = data['Global Quote']
                        market_data[symbol] = {
                            'price': float(quote['05. price']),
                            'change_pct': float(quote['10. change percent'].replace('%', ''))
                        }

                    time.sleep(0.2)  # Rate limiting

                except Exception as e:
                    print(f"Failed to get {symbol}: {e}")
                    market_data[symbol] = {'price': 0, 'change_pct': 0}

            # Analyze correlations
            spy_change = market_data.get('SPY', {}).get('change_pct', 0)
            qqq_change = market_data.get('QQQ', {}).get('change_pct', 0)

            correlations = {
                'spy_qqq_correlation': self._calculate_correlation_strength(spy_change, qqq_change),
                'tech_leadership': 'QQQ' if abs(qqq_change) > abs(spy_change) else 'SPY',
                'market_breadth': self._analyze_market_breadth(market_data),
                'risk_regime': self._determine_risk_regime(market_data),
                'flight_to_quality': self._detect_flight_to_quality(market_data),
                'dollar_impact': self._analyze_dollar_impact(market_data)
            }

        except Exception as e:
            print(f"Cross-market analysis failed: {e}")
            correlations = {'error': 'Could not analyze cross-market correlations'}

        return correlations

    def _calculate_correlation_strength(self, change1: float, change2: float) -> Dict[str, Any]:
        """Calculate correlation strength between two assets"""

        diff = abs(change1 - change2)

        if diff <= 0.1:
            strength = 'VERY_HIGH'
            score = 95
        elif diff <= 0.3:
            strength = 'HIGH'
            score = 85
        elif diff <= 0.5:
            strength = 'MEDIUM'
            score = 70
        else:
            strength = 'LOW'
            score = 50

        same_direction = (change1 > 0) == (change2 > 0)

        return {
            'strength': strength,
            'score': score,
            'same_direction': same_direction,
            'divergence': diff
        }

    def _analyze_market_breadth(self, market_data: Dict) -> Dict[str, Any]:
        """Analyze market breadth across asset classes"""

        equity_symbols = ['SPY', 'QQQ', 'IWM']
        positive_count = 0
        total_count = 0

        for symbol in equity_symbols:
            if symbol in market_data:
                change = market_data[symbol]['change_pct']
                if change > 0:
                    positive_count += 1
                total_count += 1

        if total_count == 0:
            breadth_pct = 50
        else:
            breadth_pct = (positive_count / total_count) * 100

        if breadth_pct >= 80:
            breadth_status = 'STRONG_BULLISH'
        elif breadth_pct >= 60:
            breadth_status = 'BULLISH'
        elif breadth_pct >= 40:
            breadth_status = 'NEUTRAL'
        elif breadth_pct >= 20:
            breadth_status = 'BEARISH'
        else:
            breadth_status = 'STRONG_BEARISH'

        return {
            'positive_count': positive_count,
            'total_count': total_count,
            'breadth_percentage': breadth_pct,
            'status': breadth_status
        }

    def _determine_risk_regime(self, market_data: Dict) -> str:
        """Determine current risk-on vs risk-off regime"""

        # Risk-on assets: SPY, QQQ (should be positive)
        # Risk-off assets: TLT, GLD (should be positive in risk-off)

        spy_change = market_data.get('SPY', {}).get('change_pct', 0)
        qqq_change = market_data.get('QQQ', {}).get('change_pct', 0)
        tlt_change = market_data.get('TLT', {}).get('change_pct', 0)
        gld_change = market_data.get('GLD', {}).get('change_pct', 0)

        risk_on_score = 0
        risk_off_score = 0

        # Equity performance (risk-on)
        if spy_change > 0.2:
            risk_on_score += 2
        elif spy_change > 0:
            risk_on_score += 1

        if qqq_change > 0.2:
            risk_on_score += 2
        elif qqq_change > 0:
            risk_on_score += 1

        # Safe haven performance (risk-off)
        if tlt_change > 0.2:
            risk_off_score += 2
        elif tlt_change > 0:
            risk_off_score += 1

        if gld_change > 0.5:
            risk_off_score += 2
        elif gld_change > 0:
            risk_off_score += 1

        if risk_on_score > risk_off_score + 1:
            return 'RISK_ON'
        elif risk_off_score > risk_on_score + 1:
            return 'RISK_OFF'
        else:
            return 'NEUTRAL'

    def _detect_flight_to_quality(self, market_data: Dict) -> bool:
        """Detect flight-to-quality scenarios"""

        spy_change = market_data.get('SPY', {}).get('change_pct', 0)
        tlt_change = market_data.get('TLT', {}).get('change_pct', 0)

        # Flight to quality: Stocks down significantly, bonds up significantly
        return spy_change < -1.0 and tlt_change > 0.5

    def _analyze_dollar_impact(self, market_data: Dict) -> Dict[str, Any]:
        """Analyze dollar strength impact on markets"""

        dxy_change = market_data.get('DXY', {}).get('change_pct', 0)

        if abs(dxy_change) < 0.2:
            impact = 'MINIMAL'
            equity_pressure = 'NEUTRAL'
        elif dxy_change > 0.5:
            impact = 'STRONG_DOLLAR'
            equity_pressure = 'NEGATIVE'
        elif dxy_change < -0.5:
            impact = 'WEAK_DOLLAR'
            equity_pressure = 'POSITIVE'
        else:
            impact = 'MODERATE'
            equity_pressure = 'SLIGHT'

        return {
            'dxy_change': dxy_change,
            'impact': impact,
            'equity_pressure': equity_pressure
        }

    def calculate_enhanced_position_size(self, base_analysis: Dict, account_size: float = 25000) -> Dict[str, Any]:
        """Calculate position size using enhanced logic"""

        # Get session info
        session_info = self.get_current_session()

        # Get volatility regime
        volatility_info = self.detect_volatility_regime(base_analysis)

        # Get cross-market analysis
        correlation_info = self.analyze_cross_market_correlation()

        # Base position size (1% of account)
        base_position_pct = 0.01

        # Apply session multiplier
        session_multiplier = session_info.get('position_multiplier', 1.0)

        # Apply volatility multiplier
        volatility_multiplier = volatility_info.get('position_multiplier', 1.0)

        # Apply correlation adjustment
        correlation_adjustment = 1.0
        if correlation_info.get('risk_regime') == 'RISK_OFF':
            correlation_adjustment = 0.7  # Reduce positions in risk-off
        elif correlation_info.get('flight_to_quality'):
            correlation_adjustment = 0.5  # Significantly reduce in flight-to-quality

        # Final position calculation
        final_position_pct = (base_position_pct *
                             session_multiplier *
                             volatility_multiplier *
                             correlation_adjustment)

        # Convert to dollar amount and contracts
        position_dollars = account_size * final_position_pct

        # For ES: $50 per point, typical margin $12,500
        es_margin_per_contract = 12500
        max_contracts_by_margin = int(position_dollars / es_margin_per_contract)
        recommended_contracts = max(1, max_contracts_by_margin)

        # Calculate risk metrics
        current_price = base_analysis.get('price', 6700)
        stop_distance = volatility_info['recommended_stops']['normal']
        risk_per_contract = stop_distance * 50  # $50 per point
        max_risk_dollars = recommended_contracts * risk_per_contract

        return {
            'base_position_pct': base_position_pct * 100,
            'session_multiplier': session_multiplier,
            'volatility_multiplier': volatility_multiplier,
            'correlation_adjustment': correlation_adjustment,
            'final_position_pct': final_position_pct * 100,
            'position_dollars': position_dollars,
            'recommended_contracts': recommended_contracts,
            'max_risk_dollars': max_risk_dollars,
            'risk_percent_of_account': (max_risk_dollars / account_size) * 100,
            'stop_distance_points': stop_distance,
            'session_info': session_info,
            'volatility_info': volatility_info,
            'correlation_info': correlation_info
        }

    def generate_enhanced_trading_signals(self, symbol: str, price_data: Dict) -> Dict[str, Any]:
        """Generate enhanced trading signals with advanced logic"""

        print(f"\nENHANCED {symbol} TRADING ANALYSIS")
        print("=" * 50)

        # Enhanced position sizing
        enhanced_sizing = self.calculate_enhanced_position_size(price_data)

        # Session analysis
        session = enhanced_sizing['session_info']
        volatility = enhanced_sizing['volatility_info']
        correlation = enhanced_sizing['correlation_info']

        # Generate signal based on enhanced logic
        signal_strength = self._calculate_signal_strength(price_data, session, volatility, correlation)

        # Trading recommendation
        recommendation = self._generate_recommendation(signal_strength, enhanced_sizing)

        result = {
            'symbol': symbol,
            'current_price': price_data.get('price', 0),
            'change_percent': price_data.get('change_percent', 0),
            'enhanced_analysis': {
                'session': session,
                'volatility': volatility,
                'correlation': correlation,
                'signal_strength': signal_strength
            },
            'position_sizing': enhanced_sizing,
            'recommendation': recommendation,
            'timestamp': datetime.now().isoformat()
        }

        return result

    def _calculate_signal_strength(self, price_data: Dict, session: Dict, volatility: Dict, correlation: Dict) -> Dict[str, Any]:
        """Calculate overall signal strength using enhanced factors"""

        strength_score = 0
        max_score = 100

        # Session appropriateness (25 points)
        if session['session'] in ['us_regular', 'european']:
            strength_score += 25
        elif session['session'] in ['asian', 'us_premarket']:
            strength_score += 15
        else:
            strength_score += 5

        # Volatility regime (25 points)
        vol_regime = volatility['regime']
        if vol_regime in ['low', 'normal']:
            strength_score += 25
        elif vol_regime in ['ultra_low', 'high']:
            strength_score += 15
        else:
            strength_score += 5

        # Cross-market correlation (25 points)
        if not correlation.get('error'):
            risk_regime = correlation.get('risk_regime', 'NEUTRAL')
            if risk_regime == 'RISK_ON':
                strength_score += 25
            elif risk_regime == 'NEUTRAL':
                strength_score += 15
            else:
                strength_score += 5

        # Price momentum (25 points)
        change_pct = abs(price_data.get('change_percent', 0))
        if 0.2 <= change_pct <= 2.0:  # Ideal momentum range
            strength_score += 25
        elif change_pct <= 0.2:  # Low momentum
            strength_score += 10
        else:  # Too volatile
            strength_score += 5

        strength_percentage = (strength_score / max_score) * 100

        if strength_percentage >= 80:
            strength_category = 'VERY_HIGH'
        elif strength_percentage >= 65:
            strength_category = 'HIGH'
        elif strength_percentage >= 50:
            strength_category = 'MEDIUM'
        else:
            strength_category = 'LOW'

        return {
            'score': strength_score,
            'max_score': max_score,
            'percentage': strength_percentage,
            'category': strength_category,
            'components': {
                'session_score': min(25, strength_score),
                'volatility_score': min(25, strength_score - 25) if strength_score > 25 else 0,
                'correlation_score': min(25, strength_score - 50) if strength_score > 50 else 0,
                'momentum_score': min(25, strength_score - 75) if strength_score > 75 else 0
            }
        }

    def _generate_recommendation(self, signal_strength: Dict, enhanced_sizing: Dict) -> Dict[str, Any]:
        """Generate final trading recommendation"""

        strength_pct = signal_strength['percentage']
        contracts = enhanced_sizing['recommended_contracts']
        session_strategy = enhanced_sizing['session_info']['recommended_strategy']

        # Determine action based on signal strength
        if strength_pct >= 70 and contracts >= 1:
            action = 'STRONG_BUY'
            confidence = 'HIGH'
        elif strength_pct >= 55 and contracts >= 1:
            action = 'BUY'
            confidence = 'MEDIUM'
        elif strength_pct >= 40:
            action = 'CONSIDER'
            confidence = 'LOW'
        else:
            action = 'AVOID'
            confidence = 'VERY_LOW'

        # Session-specific adjustments
        if session_strategy in ['avoid_unless_news', 'minimal_activity']:
            if action in ['STRONG_BUY', 'BUY']:
                action = 'CONSIDER'
                confidence = 'LOW'

        return {
            'action': action,
            'confidence': confidence,
            'contracts': contracts if action != 'AVOID' else 0,
            'session_strategy': session_strategy,
            'reasoning': f'{signal_strength["category"]} signal strength ({strength_pct:.1f}%) during {enhanced_sizing["session_info"]["session"]} session',
            'risk_percent': enhanced_sizing['risk_percent_of_account'],
            'stop_distance': enhanced_sizing['stop_distance_points']
        }

def main():
    """Test enhanced futures logic"""

    enhancer = EnhancedFuturesLogic()

    print("ENHANCED FUTURES TRADING LOGIC TEST")
    print("=" * 60)

    # Test with sample ES data
    sample_es_data = {
        'price': 6704.0,
        'change': 38.19,
        'change_percent': 0.57
    }

    # Generate enhanced analysis
    enhanced_analysis = enhancer.generate_enhanced_trading_signals('ES', sample_es_data)

    # Display results
    print(f"\nCURRENT PRICE: ${sample_es_data['price']:.2f} ({sample_es_data['change_percent']:+.2f}%)")

    session = enhanced_analysis['enhanced_analysis']['session']
    print(f"\nSESSION ANALYSIS:")
    print(f"Current Session: {session['session'].upper()}")
    print(f"Characteristics: {session['characteristics']}")
    print(f"Strategy: {session['recommended_strategy']}")
    print(f"Position Multiplier: {session['position_multiplier']:.2f}x")

    volatility = enhanced_analysis['enhanced_analysis']['volatility']
    print(f"\nVOLATILITY ANALYSIS:")
    print(f"Regime: {volatility['regime'].upper()}")
    print(f"Daily Change: {volatility['daily_change_pct']:.2f}%")
    print(f"Risk Level: {volatility['risk_level']}")
    print(f"Position Multiplier: {volatility['position_multiplier']:.2f}x")

    signal = enhanced_analysis['enhanced_analysis']['signal_strength']
    print(f"\nSIGNAL STRENGTH:")
    print(f"Overall: {signal['category']} ({signal['percentage']:.1f}%)")
    print(f"Score: {signal['score']}/{signal['max_score']}")

    recommendation = enhanced_analysis['recommendation']
    print(f"\nFINAL RECOMMENDATION:")
    print(f"Action: {recommendation['action']}")
    print(f"Confidence: {recommendation['confidence']}")
    print(f"Contracts: {recommendation['contracts']}")
    print(f"Risk: {recommendation['risk_percent']:.1f}% of account")
    print(f"Reasoning: {recommendation['reasoning']}")

    # Save results
    try:
        os.makedirs('.spx', exist_ok=True)
        with open('.spx/enhanced_futures_analysis.json', 'w') as f:
            json.dump(enhanced_analysis, f, indent=2)
        print(f"\nEnhanced analysis saved to .spx/enhanced_futures_analysis.json")
    except Exception as e:
        print(f"Warning: Could not save results: {e}")

if __name__ == "__main__":
    main()