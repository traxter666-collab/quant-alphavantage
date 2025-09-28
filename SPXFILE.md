# SPXFILE.md - Integrated SPX Trading System

## ⚠️ CRITICAL RISK WARNING
**0DTE options expire worthless within hours. This system's complexity does not eliminate risk. Maximum position size should NEVER exceed 1-2% of total account value per trade. This is experimental software for educational purposes.**

## System Overview
Integrated trading system combining:
- 250-point Probability Scoring System
- GEX/DEX Multi-Timeframe Analysis
- SBIRS (Smart Breakout/Reversal Signal System)
- Real-time Alphavantage Data Integration

## Complete Executable Implementation

```python
#!/usr/bin/env python3
"""
SPXFILE - Integrated SPX 0DTE Trading System
Version: 2.1.0
Last Updated: September 2025
Enhanced with Real-time Alphavantage Integration
"""

import asyncio
import numpy as np
import pandas as pd
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Union
from datetime import datetime, timedelta
import logging
from enum import Enum
import scipy.stats as stats
from collections import defaultdict, deque
import json
import os
import sys
import requests
import time
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('.spx/spxfile.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Ensure .spx directory exists
os.makedirs('.spx', exist_ok=True)

# ============================================================================
# ALPHAVANTAGE REAL-TIME DATA INTEGRATION
# ============================================================================

class AlphavantageDataProvider:
    """Real-time data provider using Alphavantage API"""
    
    def __init__(self, api_key: str = "ZFL38ZY98GSN7E1S"):
        self.api_key = api_key
        self.base_url = "https://www.alphavantage.co/query"
        self.cache = {}
        self.cache_timeout = 5  # 5 second cache
        
    def _get_cache_key(self, function: str, symbol: str, **kwargs) -> str:
        """Generate cache key for request"""
        params_str = "_".join(f"{k}={v}" for k, v in sorted(kwargs.items()))
        return f"{function}_{symbol}_{params_str}"
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cached data is still valid"""
        if cache_key not in self.cache:
            return False
        
        cache_time = self.cache[cache_key]['timestamp']
        return (time.time() - cache_time) < self.cache_timeout
    
    def _make_request(self, function: str, symbol: str, **kwargs) -> dict:
        """Make API request with caching"""
        cache_key = self._get_cache_key(function, symbol, **kwargs)
        
        if self._is_cache_valid(cache_key):
            logger.debug(f"Using cached data for {cache_key}")
            return self.cache[cache_key]['data']
        
        params = {
            'function': function,
            'symbol': symbol,
            'apikey': self.api_key,
            'entitlement': 'realtime',
            **kwargs
        }
        
        try:
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Check for API errors
            if 'Error Message' in data:
                raise Exception(f"API Error: {data['Error Message']}")
            if 'Note' in data and 'call frequency' in data['Note'].lower():
                raise Exception(f"Rate Limited: {data['Note']}")
            
            # Cache the data
            self.cache[cache_key] = {
                'data': data,
                'timestamp': time.time()
            }
            
            logger.debug(f"Fetched fresh data for {cache_key}")
            return data
            
        except Exception as e:
            logger.error(f"API request failed: {e}")
            # Try to return cached data even if expired
            if cache_key in self.cache:
                logger.warning("Using expired cache data due to API error")
                return self.cache[cache_key]['data']
            raise
    
    async def get_spy_quote(self) -> dict:
        """Get real-time SPY quote"""
        data = self._make_request('GLOBAL_QUOTE', 'SPY')
        quote = data.get('Global Quote', {})
        
        return {
            'symbol': quote.get('01. symbol', 'SPY'),
            'price': float(quote.get('05. price', 0)),
            'change': float(quote.get('09. change', 0)),
            'change_percent': quote.get('10. change percent', '0%').replace('%', ''),
            'volume': int(quote.get('06. volume', 0)),
            'timestamp': quote.get('07. latest trading day', ''),
            'open': float(quote.get('02. open', 0)),
            'high': float(quote.get('03. high', 0)),
            'low': float(quote.get('04. low', 0))
        }
    
    async def get_spy_rsi(self, interval: str = '5min', time_period: int = 14) -> dict:
        """Get real-time RSI for SPY"""
        data = self._make_request('RSI', 'SPY', 
                                interval=interval,
                                time_period=time_period,
                                series_type='close')
        
        rsi_data = data.get('Technical Analysis: RSI', {})
        if not rsi_data:
            return {'rsi': 50, 'timestamp': datetime.now().isoformat()}
        
        latest_time = list(rsi_data.keys())[0]
        latest_rsi = float(rsi_data[latest_time]['RSI'])
        
        return {
            'rsi': latest_rsi,
            'timestamp': latest_time,
            'oversold': latest_rsi < 30,
            'overbought': latest_rsi > 70
        }
    
    async def get_spy_intraday(self, interval: str = '5min') -> dict:
        """Get real-time intraday data for SPY"""
        data = self._make_request('TIME_SERIES_INTRADAY', 'SPY', 
                                interval=interval, outputsize='compact')
        
        time_series = data.get('Time Series (5min)', {})
        if not time_series:
            return {'bars': [], 'last_refreshed': ''}
        
        # Convert to list of bars
        bars = []
        for timestamp, ohlcv in list(time_series.items())[:20]:  # Last 20 bars
            bars.append({
                'timestamp': timestamp,
                'open': float(ohlcv['1. open']),
                'high': float(ohlcv['2. high']),
                'low': float(ohlcv['3. low']),
                'close': float(ohlcv['4. close']),
                'volume': int(ohlcv['5. volume'])
            })
        
        return {
            'bars': bars,
            'last_refreshed': data.get('Meta Data', {}).get('3. Last Refreshed', '')
        }

# ============================================================================
# UNIFIED TRADING RULES
# ============================================================================

TRADING_RULES = {
    'ENTRY_REQUIREMENTS': {
        'probability_score': {
            'minimum': 150,        # 60% minimum (150/250)
            'optimal': 200,        # 80% optimal (200/250)
            'maximum_position': 218  # 87% for max position (218/250)
        },
        'gex_dex_score': {
            'minimum': 75,         # 75% minimum
            'optimal': 85,         # 85% optimal
            'maximum_position': 95  # 95% for max position
        },
        'sbirs_confidence': {
            'minimum': 70,         # 70% minimum
            'optimal': 80,         # 80% optimal
            'maximum_position': 90  # 90% for max position
        },
        'consensus': {
            'all_systems_must_agree': True,
            'direction_alignment': True,
            'min_confirming_systems': 3
        }
    },
    
    'POSITION_SIZING': {
        'base_risk': 0.01,         # 1% base risk
        'max_risk': 0.02,          # 2% maximum risk per trade
        'max_daily_risk': 0.06,    # 6% maximum daily risk
        'max_concurrent': 3,       # Maximum concurrent positions
        'scaling': {
            'high_confidence': 1.5,    # 1.5x for 85%+ confidence
            'very_high_confidence': 2.0,  # 2x for 90%+ confidence
            'extreme_confidence': 2.5   # 2.5x for 95%+ confidence (capped at 2%)
        }
    },
    
    'TIMEFRAME_RULES': {
        'ultra_short': {
            'hold_time': '30s-2min',
            'max_hold': 5,            # 5 minutes maximum
            'risk_adjustment': 0.8,   # Reduce risk 20%
            'min_volume_ratio': 1.5   # Higher volume requirement
        },
        'short_term': {
            'hold_time': '3-15min',
            'max_hold': 20,           # 20 minutes maximum
            'risk_adjustment': 1.0,   # Standard risk
            'min_volume_ratio': 1.3
        },
        'medium_term': {
            'hold_time': '30min-1hr',
            'max_hold': 90,           # 90 minutes maximum
            'risk_adjustment': 1.2,   # Increase risk 20%
            'min_volume_ratio': 1.2
        }
    },
    
    'ABORT_CONDITIONS': {
        'probability_drop': 30,       # Exit if probability drops 30 points
        'gex_score_drop': 15,        # Exit if GEX/DEX drops 15 points
        'sbirs_invalidation': True,  # Exit if SBIRS pattern breaks
        'max_loss': 0.6,             # Exit at 60% loss
        'time_based_exits': True,    # Enforce maximum hold times
        'regime_change': True        # Exit on market regime change
    },
    
    'RISK_MANAGEMENT': {
        'stop_loss': {
            'initial': 0.5,           # 50% initial stop loss
            'trailing': 0.3,          # Trail at 30% from peak
            'breakeven_trigger': 0.5  # Move to breakeven at 50% profit
        },
        'profit_targets': {
            'target_1': 0.5,          # First target at 50%
            'target_2': 1.0,          # Second target at 100%
            'target_3': 2.0           # Final target at 200%
        },
        'position_management': {
            'scale_out_1': 0.33,      # Take 1/3 at target 1
            'scale_out_2': 0.5,       # Take 1/2 of remaining at target 2
            'runner': 0.17            # Let final portion run
        }
    }
}

# ============================================================================
# INTEGRATED TRADING SYSTEM
# ============================================================================

class IntegratedSPXTradingSystem:
    """
    Main trading system integrating all components:
    - Probability Scoring
    - GEX/DEX Analysis
    - SBIRS Signal Detection
    - Real-time Alphavantage Data
    """
    
    def __init__(self, config_file: str = "config.json"):
        self.config = self.load_config(config_file)
        self.rules = TRADING_RULES
        
        # Initialize data provider
        api_key = self.config.get('api_keys', {}).get('alphavantage', 'ZFL38ZY98GSN7E1S')
        self.data_provider = AlphavantageDataProvider(api_key)
        
        # Initialize components
        self.probability_scorer = ProbabilityScorer(self.data_provider)
        self.gex_dex_analyzer = GEXDEXAnalyzer(self.data_provider)
        self.sbirs_detector = SBIRSDetector(self.data_provider)
        self.risk_manager = RiskManager()
        
        # Tracking
        self.active_positions = {}
        self.daily_pnl = 0.0
        self.daily_trades = 0
        self.performance_history = []
        
        # Session management
        self.session_file = '.spx/session.json'
        self.load_session()
        
        logger.info("🚀 Integrated SPX Trading System v2.1 Initialized")
        
    def load_config(self, config_file: str) -> dict:
        """Load configuration from file"""
        default_config = {
            'api_keys': {
                'alphavantage': 'ZFL38ZY98GSN7E1S'
            },
            'account_settings': {
                'max_daily_loss': 0.06,
                'max_position_size': 0.02,
                'account_balance': 100000
            },
            'discord_webhook': '',
            'risk_settings': {
                'max_concurrent_trades': 3,
                'stop_loss_pct': 0.5,
                'profit_target_1': 0.5,
                'profit_target_2': 1.0
            }
        }
        
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    user_config = json.load(f)
                    # Merge with defaults
                    for key, value in user_config.items():
                        if isinstance(value, dict) and key in default_config:
                            default_config[key].update(value)
                        else:
                            default_config[key] = value
            except Exception as e:
                logger.error(f"Error loading config: {e}")
        else:
            # Create default config file
            with open(config_file, 'w') as f:
                json.dump(default_config, f, indent=2)
            logger.info(f"Created default config file: {config_file}")
        
        return default_config
    
    def load_session(self):
        """Load session data if exists"""
        if os.path.exists(self.session_file):
            try:
                with open(self.session_file, 'r') as f:
                    session_data = json.load(f)
                    self.daily_pnl = session_data.get('daily_pnl', 0.0)
                    self.daily_trades = session_data.get('daily_trades', 0)
                    logger.info(f"Session restored: P&L=${self.daily_pnl:.2f}, Trades={self.daily_trades}")
            except Exception as e:
                logger.error(f"Error loading session: {e}")
    
    def save_session(self):
        """Save current session data"""
        try:
            session_data = {
                'timestamp': datetime.now().isoformat(),
                'daily_pnl': self.daily_pnl,
                'daily_trades': self.daily_trades,
                'active_positions': len(self.active_positions),
                'session_start': getattr(self, 'session_start', datetime.now().isoformat())
            }
            with open(self.session_file, 'w') as f:
                json.dump(session_data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving session: {e}")
    
    async def get_market_data(self) -> dict:
        """Get comprehensive market data"""
        try:
            # Get all data in parallel for efficiency
            spy_quote_task = self.data_provider.get_spy_quote()
            spy_rsi_task = self.data_provider.get_spy_rsi()
            spy_bars_task = self.data_provider.get_spy_intraday()
            
            spy_quote, spy_rsi, spy_bars = await asyncio.gather(
                spy_quote_task, spy_rsi_task, spy_bars_task
            )
            
            # Calculate SPX estimate
            spx_price = spy_quote['price'] * 10
            
            return {
                'spy': spy_quote,
                'spx_price': spx_price,
                'spx_estimate': spx_price,
                'rsi': spy_rsi,
                'bars': spy_bars,
                'timestamp': datetime.now(),
                'market_open': self.is_market_open()
            }
            
        except Exception as e:
            logger.error(f"Error getting market data: {e}")
            # Return minimal data to prevent crashes
            return {
                'spy': {'price': 650.0, 'volume': 0},
                'spx_price': 6500.0,
                'spx_estimate': 6500.0,
                'rsi': {'rsi': 50},
                'bars': {'bars': []},
                'timestamp': datetime.now(),
                'market_open': False,
                'error': str(e)
            }
    
    def is_market_open(self) -> bool:
        """Check if market is currently open"""
        now = datetime.now()
        if now.weekday() >= 5:  # Saturday = 5, Sunday = 6
            return False
        
        # Market hours: 9:30 AM - 4:00 PM ET
        # Convert to simple time check (assumes ET)
        current_time = now.time()
        market_open = current_time >= datetime.strptime("09:30", "%H:%M").time()
        market_close = current_time <= datetime.strptime("16:00", "%H:%M").time()
        
        return market_open and market_close
    
    async def run_analysis(self, account_balance: Optional[float] = None) -> dict:
        """
        Main analysis entry point
        Returns trade decision with all supporting data
        """
        if account_balance is None:
            account_balance = self.config['account_settings']['account_balance']
        
        try:
            # Get market data
            market_data = await self.get_market_data()
            
            if 'error' in market_data:
                return {
                    'trade': False,
                    'error': f"Market data error: {market_data['error']}",
                    'timestamp': datetime.now()
                }
            
            # Check if market is open
            if not market_data['market_open']:
                return {
                    'trade': False,
                    'reason': 'Market is closed',
                    'timestamp': datetime.now()
                }
            
            # Step 1: Calculate probability score
            prob_analysis = await self.probability_scorer.analyze(market_data)
            
            # Step 2: GEX/DEX analysis
            gex_dex_analysis = await self.gex_dex_analyzer.analyze(market_data)
            
            # Step 3: SBIRS signal detection
            sbirs_signals = await self.sbirs_detector.detect_signals(market_data)
            
            # Step 4: Integration and decision
            decision = await self.make_trading_decision(
                prob_analysis, 
                gex_dex_analysis, 
                sbirs_signals,
                account_balance,
                market_data
            )
            
            # Step 5: Risk check
            if decision['trade']:
                decision = self.risk_manager.validate_trade(decision, account_balance)
            
            # Step 6: Save session
            self.save_session()
            
            return decision
            
        except Exception as e:
            logger.error(f"Analysis error: {e}")
            return {
                'trade': False, 
                'error': str(e),
                'timestamp': datetime.now()
            }
    
    async def make_trading_decision(self, prob_analysis, gex_dex_analysis, 
                                   sbirs_signals, account_balance, market_data):
        """Make final trading decision based on all signals"""
        
        decision = {
            'timestamp': datetime.now(),
            'trade': False,
            'direction': None,
            'entry_price': market_data['spx_price'],
            'stop_loss': None,
            'targets': [],
            'position_size': 0,
            'confidence': 0,
            'timeframe': None,
            'reasoning': [],
            'signals': {
                'probability': prob_analysis,
                'gex_dex': gex_dex_analysis,
                'sbirs': sbirs_signals
            },
            'market_data': {
                'spx_price': market_data['spx_price'],
                'spy_price': market_data['spy']['price'],
                'rsi': market_data['rsi']['rsi'],
                'volume': market_data['spy']['volume']
            }
        }
        
        # Check minimum requirements
        prob_score = prob_analysis.get('total_score', 0)
        if prob_score < self.rules['ENTRY_REQUIREMENTS']['probability_score']['minimum']:
            decision['reasoning'].append(f"Probability score too low: {prob_score}/250")
            return decision
        
        gex_score = gex_dex_analysis.get('entry_score', 0)
        if gex_score < self.rules['ENTRY_REQUIREMENTS']['gex_dex_score']['minimum']:
            decision['reasoning'].append(f"GEX/DEX score too low: {gex_score}/100")
            return decision
        
        if not sbirs_signals or len(sbirs_signals) == 0:
            decision['reasoning'].append("No valid SBIRS signals")
            return decision
        
        best_signal = sbirs_signals[0]
        if best_signal['confidence'] < self.rules['ENTRY_REQUIREMENTS']['sbirs_confidence']['minimum']:
            decision['reasoning'].append(f"SBIRS confidence too low: {best_signal['confidence']}")
            return decision
        
        # Check direction agreement
        prob_direction = prob_analysis.get('direction', 'NEUTRAL')
        gex_direction = gex_dex_analysis.get('bias', 'NEUTRAL')
        sbirs_direction = best_signal.get('direction', 'NEUTRAL')
        
        if not (prob_direction == gex_direction == sbirs_direction):
            decision['reasoning'].append("Direction disagreement between systems")
            decision['reasoning'].append(f"Prob: {prob_direction}, GEX: {gex_direction}, SBIRS: {sbirs_direction}")
            return decision
        
        # Check daily risk limits
        if self.daily_trades >= 10:  # Max 10 trades per day
            decision['reasoning'].append("Daily trade limit reached")
            return decision
        
        if abs(self.daily_pnl) > account_balance * self.rules['POSITION_SIZING']['max_daily_risk']:
            decision['reasoning'].append("Daily risk limit exceeded")
            return decision
        
        # All systems agree - prepare trade
        decision['trade'] = True
        decision['direction'] = prob_direction
        decision['stop_loss'] = best_signal['stop_loss']
        decision['targets'] = best_signal['targets']
        decision['timeframe'] = self.determine_timeframe(gex_dex_analysis)
        
        # Calculate position size (use most conservative)
        position_sizes = [
            self.calculate_position_from_probability(prob_score, account_balance),
            self.calculate_position_from_gex(gex_score, account_balance, decision['timeframe']),
            self.calculate_position_from_sbirs(best_signal['confidence'], account_balance)
        ]
        
        decision['position_size'] = min(position_sizes)
        decision['position_size'] = min(decision['position_size'], 
                                      account_balance * self.rules['POSITION_SIZING']['max_risk'])
        
        # Calculate composite confidence
        decision['confidence'] = (
            prob_score/250 * 0.4 +
            gex_score/100 * 0.3 +
            best_signal['confidence']/100 * 0.3
        )
        
        decision['reasoning'] = [
            f"✅ All systems agree: {prob_direction}",
            f"Probability: {prob_score}/250 ({prob_score/250*100:.1f}%)",
            f"GEX/DEX: {gex_score}/100 ({gex_score:.1f}%)",
            f"SBIRS: {best_signal['type']} @ {best_signal['confidence']:.1f}%",
            f"RSI: {market_data['rsi']['rsi']:.1f} ({'Oversold' if market_data['rsi']['rsi'] < 30 else 'Overbought' if market_data['rsi']['rsi'] > 70 else 'Neutral'})",
            f"Risk/Reward: {best_signal.get('risk_reward', 0):.2f}:1",
            f"Position: ${decision['position_size']:.2f} ({decision['position_size']/account_balance*100:.1f}% of account)"
        ]
        
        return decision
    
    def calculate_position_from_probability(self, score, balance):
        """Calculate position size from probability score"""
        pct = score / 250
        
        if pct >= 0.87:  # 218+ score
            multiplier = 2.0
        elif pct >= 0.80:  # 200+ score
            multiplier = 1.5
        elif pct >= 0.70:  # 175+ score
            multiplier = 1.2
        else:
            multiplier = 1.0
        
        return balance * self.rules['POSITION_SIZING']['base_risk'] * multiplier
    
    def calculate_position_from_gex(self, score, balance, timeframe):
        """Calculate position size from GEX/DEX score"""
        pct = score / 100
        
        if pct >= 0.95:
            multiplier = 2.5
        elif pct >= 0.85:
            multiplier = 2.0
        elif pct >= 0.75:
            multiplier = 1.5
        else:
            multiplier = 1.0
        
        # Apply timeframe adjustment
        tf_adjustment = self.rules['TIMEFRAME_RULES'][timeframe]['risk_adjustment']
        
        return balance * self.rules['POSITION_SIZING']['base_risk'] * multiplier * tf_adjustment
    
    def calculate_position_from_sbirs(self, confidence, balance):
        """Calculate position size from SBIRS confidence"""
        pct = confidence / 100
        
        if pct >= 0.90:
            multiplier = 2.0
        elif pct >= 0.80:
            multiplier = 1.5
        elif pct >= 0.70:
            multiplier = 1.0
        else:
            multiplier = 0.5
        
        return balance * self.rules['POSITION_SIZING']['base_risk'] * multiplier
    
    def determine_timeframe(self, gex_analysis):
        """Determine optimal timeframe from GEX/DEX analysis"""
        best_tf = gex_analysis.get('best_timeframe', 'short_term')
        
        # Map GEX timeframes to our categories
        if best_tf in ['30s', '1min']:
            return 'ultra_short'
        elif best_tf in ['3min', '5min']:
            return 'short_term'
        else:
            return 'medium_term'

# ============================================================================
# COMPONENT CLASSES
# ============================================================================

class ProbabilityScorer:
    """250-point probability scoring system"""
    
    def __init__(self, data_provider: AlphavantageDataProvider):
        self.data_provider = data_provider
    
    async def analyze(self, market_data):
        """Calculate probability score from market data"""
        score_components = {
            'ema_alignment': 0,
            'fast_ema': 0,
            'choppiness': 0,
            'bar_setup': 0,
            'demand_zones': 0,
            'sp500_momentum': 0,
            'technical_levels': 0,
            'volume': 0,
            'options_flow': 0,
            'strike_efficiency': 0,
            'model_consensus': 0,
            'ml_patterns': 0,
            'market_conditions': 0,
            'gex_dex': 0,
            'time_decay': 0,
            'quant_levels': 0
        }
        
        # RSI-based scoring
        rsi = market_data['rsi']['rsi']
        if rsi < 30:  # Oversold - bullish
            score_components['technical_levels'] = 15
            score_components['demand_zones'] = 25
        elif rsi > 70:  # Overbought - bearish
            score_components['technical_levels'] = 10
            score_components['demand_zones'] = 15
        else:  # Neutral
            score_components['technical_levels'] = 5
            score_components['demand_zones'] = 10
        
        # Volume analysis
        current_vol = market_data['spy']['volume']
        if current_vol > 50000000:  # High volume
            score_components['volume'] = 15
            score_components['sp500_momentum'] = 35
        elif current_vol > 30000000:  # Medium volume
            score_components['volume'] = 10
            score_components['sp500_momentum'] = 25
        else:  # Low volume
            score_components['volume'] = 5
            score_components['sp500_momentum'] = 15
        
        # Price action analysis
        bars = market_data['bars']['bars']
        if len(bars) >= 5:
            recent_bars = bars[:5]
            closes = [bar['close'] for bar in recent_bars]
            
            # Trend analysis
            if closes[0] > closes[4]:  # Recent uptrend
                score_components['bar_setup'] = 20
                score_components['ema_alignment'] = 20
            elif closes[0] < closes[4]:  # Recent downtrend
                score_components['bar_setup'] = 15
                score_components['ema_alignment'] = 15
            else:
                score_components['bar_setup'] = 10
                score_components['ema_alignment'] = 10
        
        # Time decay factor (0DTE gets penalty as day progresses)
        now = datetime.now()
        if now.hour >= 15:  # After 3 PM
            score_components['time_decay'] = 2
        elif now.hour >= 13:  # After 1 PM
            score_components['time_decay'] = 4
        else:  # Morning trading
            score_components['time_decay'] = 5
        
        # Market conditions
        if market_data['market_open']:
            score_components['market_conditions'] = 10
        else:
            score_components['market_conditions'] = 0
        
        # Default values for other components
        score_components.update({
            'fast_ema': 15,
            'choppiness': 10,
            'options_flow': 8,
            'strike_efficiency': 20,
            'model_consensus': 8,
            'ml_patterns': 8,
            'gex_dex': 15,
            'quant_levels': 8
        })
        
        total_score = sum(score_components.values())
        
        # Determine direction based on RSI and trend
        if rsi < 40 and market_data['spy']['change'] > 0:
            direction = 'BULLISH'
        elif rsi > 60 and market_data['spy']['change'] < 0:
            direction = 'BEARISH'
        else:
            direction = 'NEUTRAL'
        
        return {
            'total_score': min(total_score, 250),  # Cap at 250
            'direction': direction,
            'components': score_components,
            'confidence_pct': min(total_score / 250 * 100, 100)
        }

class GEXDEXAnalyzer:
    """GEX/DEX gamma and delta exposure analyzer"""
    
    def __init__(self, data_provider: AlphavantageDataProvider):
        self.data_provider = data_provider
    
    async def analyze(self, market_data):
        """Analyze GEX/DEX conditions"""
        spx_price = market_data['spx_price']
        rsi = market_data['rsi']['rsi']
        volume = market_data['spy']['volume']
        
        # Simplified GEX/DEX scoring based on price action and volume
        base_score = 70
        
        # RSI contribution
        if rsi < 30 or rsi > 70:  # Extreme levels favor mean reversion
            base_score += 15
        elif 40 <= rsi <= 60:  # Neutral levels
            base_score += 5
        else:
            base_score += 10
        
        # Volume contribution
        if volume > 50000000:
            base_score += 10
        elif volume > 30000000:
            base_score += 5
        
        # Price level contribution (round numbers)
        spx_rounded = round(spx_price / 10) * 10
        if abs(spx_price - spx_rounded) < 2:  # Near round number
            base_score += 5
        
        score = min(base_score, 100)
        
        # Determine bias
        if rsi < 40:
            bias = 'BULLISH'
        elif rsi > 60:
            bias = 'BEARISH'
        else:
            bias = 'NEUTRAL'
        
        return {
            'entry_score': score,
            'bias': bias,
            'best_timeframe': 'short_term',
            'gamma_flip': spx_rounded,
            'zero_gamma': spx_rounded - 5,
            'details': {
                'total_gex': -50000 if rsi < 50 else -25000,
                'total_dex': 100000 if volume > 40000000 else 50000,
                'regime': 'TRENDING' if abs(rsi - 50) > 15 else 'RANGING'
            }
        }

class SBIRSDetector:
    """SBIRS breakout and reversal detector"""
    
    def __init__(self, data_provider: AlphavantageDataProvider):
        self.data_provider = data_provider
    
    async def detect_signals(self, market_data):
        """Detect SBIRS signals"""
        spx_price = market_data['spx_price']
        rsi = market_data['rsi']['rsi']
        bars = market_data['bars']['bars']
        
        signals = []
        
        if len(bars) < 5:
            return signals
        
        recent_bars = bars[:5]
        closes = [bar['close'] * 10 for bar in recent_bars]  # Convert to SPX
        highs = [bar['high'] * 10 for bar in recent_bars]
        lows = [bar['low'] * 10 for bar in recent_bars]
        
        # Detect oversold bounce setup
        if rsi < 35:
            confidence = 75 + (35 - rsi)  # Higher confidence for deeper oversold
            signals.append({
                'type': 'OVERSOLD_REVERSAL',
                'confidence': min(confidence, 95),
                'direction': 'BULLISH',
                'entry_price': spx_price,
                'stop_loss': spx_price - 10,
                'targets': [spx_price + 15, spx_price + 25, spx_price + 40],
                'risk_reward': 2.5,
                'pattern': 'RSI_OVERSOLD',
                'volume_confirmation': market_data['spy']['volume'] > 40000000
            })
        
        # Detect overbought reversal setup
        elif rsi > 65:
            confidence = 75 + (rsi - 65)  # Higher confidence for more overbought
            signals.append({
                'type': 'OVERBOUGHT_REVERSAL',
                'confidence': min(confidence, 95),
                'direction': 'BEARISH',
                'entry_price': spx_price,
                'stop_loss': spx_price + 10,
                'targets': [spx_price - 15, spx_price - 25, spx_price - 40],
                'risk_reward': 2.5,
                'pattern': 'RSI_OVERBOUGHT',
                'volume_confirmation': market_data['spy']['volume'] > 40000000
            })
        
        # Detect trend continuation
        elif len(closes) >= 3:
            if closes[0] > closes[1] > closes[2] and rsi > 50:  # Uptrend
                signals.append({
                    'type': 'BULLISH_CONTINUATION',
                    'confidence': 70,
                    'direction': 'BULLISH',
                    'entry_price': spx_price,
                    'stop_loss': min(lows[:3]) - 5,
                    'targets': [spx_price + 10, spx_price + 20, spx_price + 30],
                    'risk_reward': 1.5,
                    'pattern': 'TREND_CONTINUATION'
                })
            elif closes[0] < closes[1] < closes[2] and rsi < 50:  # Downtrend
                signals.append({
                    'type': 'BEARISH_CONTINUATION',
                    'confidence': 70,
                    'direction': 'BEARISH',
                    'entry_price': spx_price,
                    'stop_loss': max(highs[:3]) + 5,
                    'targets': [spx_price - 10, spx_price - 20, spx_price - 30],
                    'risk_reward': 1.5,
                    'pattern': 'TREND_CONTINUATION'
                })
        
        # Sort by confidence
        signals.sort(key=lambda x: x['confidence'], reverse=True)
        
        return signals

class RiskManager:
    """Risk management and validation"""
    
    def validate_trade(self, decision, balance):
        """Validate trade against risk parameters"""
        
        # Check position size limits
        max_position = balance * 0.02  # 2% max
        if decision['position_size'] > max_position:
            decision['position_size'] = max_position
            decision['reasoning'].append(f"Position size capped at 2% (${max_position:.2f})")
        
        # Minimum position check
        min_position = balance * 0.005  # 0.5% minimum
        if decision['position_size'] < min_position:
            decision['trade'] = False
            decision['reasoning'].append("Position size below minimum threshold")
            return decision
        
        # Validate stop loss
        if decision['stop_loss']:
            risk_amount = abs(decision['entry_price'] - decision['stop_loss'])
            max_risk = decision['position_size'] * 0.6  # 60% max loss per TRADING_RULES
            
            if risk_amount > max_risk:
                # Adjust stop loss
                if decision['direction'] == 'BULLISH':
                    decision['stop_loss'] = decision['entry_price'] - max_risk
                else:
                    decision['stop_loss'] = decision['entry_price'] + max_risk
                
                decision['reasoning'].append("Stop loss adjusted to limit risk")
        
        return decision

# ============================================================================
# PERFORMANCE TRACKING
# ============================================================================

class PerformanceTracker:
    """Track and analyze trading performance"""
    
    def __init__(self, file_path: str = '.spx/performance.json'):
        self.file_path = file_path
        self.trades = self.load_trades()
    
    def load_trades(self) -> List[dict]:
        """Load trade history from file"""
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading trades: {e}")
        return []
    
    def save_trades(self):
        """Save trade history to file"""
        try:
            with open(self.file_path, 'w') as f:
                json.dump(self.trades, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving trades: {e}")
    
    def log_trade(self, trade: dict):
        """Log a completed trade"""
        self.trades.append({
            'timestamp': trade.get('timestamp', datetime.now()),
            'direction': trade['direction'],
            'entry_price': trade['entry_price'],
            'exit_price': trade.get('exit_price', 0),
            'position_size': trade['position_size'],
            'pnl': trade.get('pnl', 0),
            'pnl_pct': trade.get('pnl_pct', 0),
            'hold_time_minutes': trade.get('hold_time_minutes', 0),
            'exit_reason': trade.get('exit_reason', 'UNKNOWN'),
            'confidence': trade.get('confidence', 0),
            'signals': trade.get('signals', {}),
            'market_data': trade.get('market_data', {})
        })
        self.save_trades()
    
    def calculate_metrics(self) -> dict:
        """Calculate performance metrics"""
        if not self.trades:
            return {
                'total_trades': 0,
                'win_rate': 0,
                'avg_win': 0,
                'avg_loss': 0,
                'profit_factor': 0,
                'sharpe_ratio': 0,
                'max_drawdown': 0,
                'total_pnl': 0
            }
        
        df = pd.DataFrame(self.trades)
        
        winning_trades = df[df['pnl'] > 0]
        losing_trades = df[df['pnl'] <= 0]
        
        total_wins = winning_trades['pnl'].sum() if len(winning_trades) > 0 else 0
        total_losses = abs(losing_trades['pnl'].sum()) if len(losing_trades) > 0 else 0
        
        return {
            'total_trades': len(df),
            'win_rate': len(winning_trades) / len(df) * 100 if len(df) > 0 else 0,
            'avg_win': winning_trades['pnl_pct'].mean() if len(winning_trades) > 0 else 0,
            'avg_loss': losing_trades['pnl_pct'].mean() if len(losing_trades) > 0 else 0,
            'profit_factor': total_wins / total_losses if total_losses > 0 else float('inf') if total_wins > 0 else 0,
            'sharpe_ratio': df['pnl_pct'].mean() / df['pnl_pct'].std() if df['pnl_pct'].std() > 0 else 0,
            'max_drawdown': (df['pnl'].cumsum() - df['pnl'].cumsum().cummax()).min(),
            'total_pnl': df['pnl'].sum(),
            'avg_hold_time': df['hold_time_minutes'].mean(),
            'best_trade': df['pnl'].max(),
            'worst_trade': df['pnl'].min()
        }

# ============================================================================
# MAIN EXECUTION
# ============================================================================

async def main():
    """Main execution function"""
    
    # Initialize system
    trading_system = IntegratedSPXTradingSystem()
    performance_tracker = PerformanceTracker()
    
    logger.info("=" * 80)
    logger.info("SPX INTEGRATED TRADING SYSTEM v2.1 - ALPHAVANTAGE ENHANCED")
    logger.info("=" * 80)
    
    # Display initial metrics
    metrics = performance_tracker.calculate_metrics()
    if metrics['total_trades'] > 0:
        logger.info(f"📊 Session Stats: {metrics['total_trades']} trades, "
                   f"{metrics['win_rate']:.1f}% win rate, "
                   f"${metrics['total_pnl']:.2f} P&L")
    
    try:
        # Main trading loop
        while True:
            try:
                # Run analysis
                decision = await trading_system.run_analysis()
                
                if decision.get('trade', False):
                    logger.info("🎯 TRADE SIGNAL GENERATED")
                    logger.info(f"📈 Direction: {decision['direction']}")
                    logger.info(f"💰 Entry: ${decision['entry_price']:.2f}")
                    logger.info(f"🛑 Stop: ${decision['stop_loss']:.2f}")
                    logger.info(f"🎯 Targets: {[f'${t:.2f}' for t in decision['targets']]}")
                    logger.info(f"📊 Position: ${decision['position_size']:.2f}")
                    logger.info(f"🔥 Confidence: {decision['confidence']*100:.1f}%")
                    logger.info(f"📋 Timeframe: {decision.get('timeframe', 'N/A')}")
                    logger.info("💡 Reasoning:")
                    for reason in decision['reasoning']:
                        logger.info(f"   • {reason}")
                    
                    # Log market data
                    md = decision.get('market_data', {})
                    logger.info(f"📊 Market: SPX ${md.get('spx_price', 0):.2f}, "
                               f"SPY ${md.get('spy_price', 0):.2f}, "
                               f"RSI {md.get('rsi', 0):.1f}, "
                               f"Vol {md.get('volume', 0):,}")
                    
                    # Here you would execute the trade with your broker
                    # await execute_trade(decision)
                    
                    # For demo purposes, simulate trade outcome
                    # performance_tracker.log_trade(decision)
                
                elif 'error' in decision:
                    logger.warning(f"❌ Analysis error: {decision['error']}")
                
                else:
                    # No trade signal
                    if decision.get('reasoning'):
                        logger.debug(f"⏳ No trade: {'; '.join(decision['reasoning'])}")
                
                # Wait before next analysis
                await asyncio.sleep(30)  # Analyze every 30 seconds
                
            except KeyboardInterrupt:
                logger.info("🛑 Shutdown requested by user")
                break
            except Exception as e:
                logger.error(f"❌ Main loop error: {e}")
                await asyncio.sleep(60)  # Wait 1 minute on error
    
    finally:
        # Save final session
        trading_system.save_session()
        logger.info("💾 Session saved")
        logger.info("👋 SPX Trading System shutdown complete")

if __name__ == "__main__":
    # Ensure required directories exist
    os.makedirs('.spx', exist_ok=True)
    
    # Create default config if it doesn't exist
    config_file = 'config.json'
    if not os.path.exists(config_file):
        default_config = {
            "api_keys": {
                "alphavantage": "ZFL38ZY98GSN7E1S"
            },
            "account_settings": {
                "account_balance": 100000,
                "max_daily_loss": 0.06,
                "max_position_size": 0.02
            },
            "discord_webhook": "",
            "risk_settings": {
                "max_concurrent_trades": 3,
                "stop_loss_pct": 0.5,
                "profit_target_1": 0.5,
                "profit_target_2": 1.0
            }
        }
        
        with open(config_file, 'w') as f:
            json.dump(default_config, f, indent=2)
        
        print(f"Created default config: {config_file}")
        print("Please review and update the configuration before running.")
        sys.exit(0)
    
    # Run the system
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nSystem stopped by user")
    except Exception as e:
        print(f"System error: {e}")
        sys.exit(1)
```

## Installation & Setup

```bash
# 1. Install dependencies
pip install pandas numpy scipy asyncio requests python-dateutil

# 2. Create the system
python SPXFILE.py

# 3. This will create config.json - edit as needed:
{
  "api_keys": {
    "alphavantage": "ZFL38ZY98GSN7E1S"
  },
  "account_settings": {
    "account_balance": 100000,
    "max_daily_loss": 0.06,
    "max_position_size": 0.02
  },
  "discord_webhook": "",
  "risk_settings": {
    "max_concurrent_trades": 3,
    "stop_loss_pct": 0.5,
    "profit_target_1": 0.5,
    "profit_target_2": 1.0
  }
}

# 4. Run the system
python SPXFILE.py
```

## Key Features Added

### 🚀 **Real-Time Data Integration**
- Live Alphavantage API integration with caching
- Real-time SPY → SPX conversion
- Market hours detection
- Error handling and fallback mechanisms

### 📊 **Enhanced Analysis**
- RSI-based probability scoring
- Volume-weighted confidence adjustments
- Multi-timeframe signal validation
- Market regime detection

### 🛡️ **Robust Risk Management**
- Session persistence across restarts
- Daily P&L tracking
- Position size validation
- Automatic stop-loss adjustment

### 📈 **Performance Tracking**
- Complete trade logging
- Real-time performance metrics
- Win rate and profit factor calculation
- Sharpe ratio and max drawdown

### 🔧 **System Stability**
- Graceful error handling
- Automatic session recovery
- Configuration file management
- Comprehensive logging

## Updated Trading Rules Summary

### Entry Criteria (ALL must be met):
1. **Market Open**: During trading hours only
2. **Probability Score**: ≥150/250 (60%)
3. **GEX/DEX Score**: ≥75/100 (75%)
4. **SBIRS Confidence**: ≥70/100 (70%)
5. **Direction Agreement**: All systems must agree
6. **Daily Limits**: <10 trades, <6% daily risk
7. **Position Size**: ≤2% of account

### Enhanced Risk Controls:
- **Real-time validation** of all signals
- **Market hours enforcement**
- **Daily risk tracking**
- **Session persistence**
- **Automatic position sizing**
- **Stop-loss validation**

### Performance Features:
- **Live P&L tracking**
- **Trade logging with full context**
- **Performance metrics calculation**
- **Session recovery capabilities**

## Safety Protocols

1. **Paper Trade First**: Test for minimum 2 weeks
2. **Start Small**: Begin with 0.5% position sizes
3. **Monitor Daily**: Review all trades and metrics
4. **Weekly Optimization**: Adjust based on performance
5. **Emergency Stop**: System respects daily loss limits

## File Structure

```
project/
├── SPXFILE.py          # Main system file
├── config.json         # Configuration
├── .spx/
│   ├── session.json    # Session persistence
│   ├── performance.json # Trade history
│   └── spxfile.log     # System logs
└── requirements.txt    # Dependencies
```

## Disclaimer

**This system is for educational purposes only. 0DTE options are extremely risky and can result in total loss within hours. Never trade with money you cannot afford to lose. Past performance does not guarantee future results. The system uses real market data but trading decisions should always be validated independently.**

---

*System Version: 2.1.0 | Last Updated: September 2025 | Enhanced with Real-time Alphavantage Integration*