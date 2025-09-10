# Claude Instructions for Quant Trading (Alpha)

## Alphavantage MCP Integration

**CRITICAL: All market data now comes from alphavantage MCP - professional-grade real-time data**

### Market Data Protocol
```bash
# Real-time Price Data
mcp__alphavantage__GLOBAL_QUOTE(symbol="SPY")           # Current price, volume, change
mcp__alphavantage__TIME_SERIES_INTRADAY(symbol, interval) # 1min, 5min, 15min, 30min, 60min bars

# Technical Indicators (Built-in calculations)
mcp__alphavantage__RSI(symbol, interval, time_period, series_type)  # RSI calculations
mcp__alphavantage__EMA(symbol, interval, time_period, series_type)  # EMA calculations  
mcp__alphavantage__SMA(symbol, interval, time_period, series_type)  # SMA calculations
mcp__alphavantage__MACD(symbol, interval, series_type)              # MACD calculations

# Market Context
mcp__alphavantage__NEWS_SENTIMENT()                     # Market news and sentiment
mcp__alphavantage__TOP_GAINERS_LOSERS()                # Market movers
mcp__alphavantage__MARKET_STATUS()                     # Market open/closed status
```

### SPX Data Conversion Protocol
```bash
# SPY to SPX Conversion (SPY × 10 ≈ SPX)
SPY_PRICE = mcp__alphavantage__GLOBAL_QUOTE("SPY")["Global Quote"]["05. price"]
SPX_ESTIMATE = float(SPY_PRICE) * 10

# Example: SPY $650.33 → SPX ~6503.30
# Use SPY technical indicators directly for SPX analysis
# SPY volume and sentiment = SPX market context
```

### MANDATORY Data Verification Protocol
```bash
# STEP 0: ALWAYS GET REAL MARKET DATA FIRST - NO EXCEPTIONS
# Before ANY SPX analysis, MUST call:
market_status = mcp__alphavantage__MARKET_STATUS()
spy_quote = mcp__alphavantage__GLOBAL_QUOTE("SPY")
spy_rsi = mcp__alphavantage__RSI("SPY", "5min", 14, "close")

# NEVER estimate prices - use actual data from alphavantage MCP
# Verify market is open before real-time analysis
# Use SPY data as direct proxy for SPX analysis
```

## Simple Session Management Protocol

**File-based persistence for seamless context continuity**

### File-Based Session System
```bash
./.spx/                  # Local to current directory (portable)
├── session.json         # Current session context
├── levels.json          # Key support/resistance levels  
├── notes.txt           # Session notes with timestamps
├── quant_levels.json   # Daily quant levels
└── last_analysis.json  # Most recent analysis for continuity
```

### Session Management Commands
```bash
spx session start      # Load existing ./.spx/session.json or create new
spx session save       # Write current context to ./.spx/session.json  
spx session restore    # Load from ./.spx/session.json and display status
spx session clear      # Clear all ./.spx/ files (fresh start)
spx key levels save    # Save S/R levels to ./.spx/levels.json
spx session notes     # Add timestamped note to ./.spx/notes.txt
spx quant levels      # Save daily quant levels to ./.spx/quant_levels.json
```

### Enhanced Analysis Commands (with alphavantage + file-based auto-save)
```bash
spx now              # Full analysis + auto-save context
spx tactical         # Real-time execution + session update  
spx strategic        # Full context + persistent key levels
spx context          # Full day analysis + restore gaps if needed
```

## NEW: Institutional-Grade Analysis Commands

**Professional-level multi-factor analysis with alphavantage MCP + local calculations:**

```bash
spx enhanced         # Complete institutional-grade multi-factor analysis
spx multi confirm    # Multi-timeframe confirmation (30s-1hr alignment)
spx cost analysis    # Realistic transaction cost breakdown + impact
spx smart size       # Dynamic position sizing (volatility + confidence)
spx gex entry        # GEX/DEX optimized entry analysis with scoring
spx cisd detect      # Institutional supply/demand patterns (5m + 4h)
spx sbirs signal     # Smart breakout/reversal detection with filtering
spx consensus        # Multi-factor consensus scoring (0-100 scale)
```

## Multi-Timeframe Confirmation Protocol

**ALPHAVANTAGE MCP: Professional multi-timeframe analysis with real market data**

### Multi-Timeframe Analysis Framework:
```bash
# Alphavantage MCP calls for comprehensive timeframe analysis
timeframes = ["1min", "5min", "15min", "30min", "60min"]
for tf in timeframes:
    bars = mcp__alphavantage__TIME_SERIES_INTRADAY("SPY", tf)
    rsi = mcp__alphavantage__RSI("SPY", tf, 14, "close")
    ema_9 = mcp__alphavantage__EMA("SPY", tf, 9, "close")
    ema_21 = mcp__alphavantage__EMA("SPY", tf, 21, "close")
    
    # Determine signal from real market data
    signal = "BULL" if (rsi > 50 and ema_9 > ema_21) else "BEAR" if (rsi < 50 and ema_9 < ema_21) else "NEUT"
    
consensus_score = count_bullish_signals - count_bearish_signals  # -5 to +5
alignment_strength = abs(consensus_score) / 5 * 100            # 0-100%
```

### Consensus Interpretation:
```bash
# Calculated from real alphavantage data:
STRONG_CONSENSUS (80-100%): 4-5 timeframes aligned → 30min-1h holds (15% win rate boost)
MEDIUM_CONSENSUS (60-79%): 3 timeframes aligned → 5min-30min holds (10% win rate boost)
WEAK_CONSENSUS (40-59%): 2-3 timeframes aligned → 1min-5min holds (5% win rate boost)
CONFLICTED (≤39%): 1 or fewer aligned → ultra-quick or avoid (0% boost)
```

## Realistic Cost Analysis Engine

**LOCAL CALCULATION: Transaction cost calculations with real option pricing**

### Transaction Cost Analysis (Enhanced for Real Data):
```bash
# Enhanced cost calculation with market data validation
def calculate_enhanced_transaction_costs(contracts, bid, ask, theta=0, days=1):
    # Validate prices make sense
    if bid <= 0 or ask <= 0 or ask < bid:
        return {"error": "Invalid option pricing data"}
    
    commission = contracts * 0.65
    spread_cost = (ask - bid) * contracts
    slippage = contracts * 0.02 if contracts <= 10 else contracts * 0.05
    theta_cost = abs(theta) * days * contracts if theta else 0
    
    total_cost = commission + spread_cost + slippage + theta_cost
    breakeven_pct = (total_cost / (bid * contracts)) * 100
    
    return {
        "total_cost": total_cost,
        "breakeven_move": breakeven_pct,
        "cost_warning": total_cost > (bid * contracts * 0.15),
        "difficult_trade": breakeven_pct > 2.0,
        "spread_pct": ((ask - bid) / bid) * 100
    }
```

### Cost-Based Decision Making:
```bash
# Enhanced cost decision framework:
if cost_warning: "HIGH COST TRADE - Consider smaller size"
if difficult_trade: "DIFFICULT BREAKEVEN - Requires >2% move" 
if spread_pct > 5%: "WIDE SPREAD - Wait for better pricing"
if breakeven_move > 1.5%: "Adjust targets upward for cost impact"
```

## Dynamic Position Sizing Framework  

**ALPHAVANTAGE ENHANCED: VIX-based intelligent scaling**

### Position Sizing with Real Market Data:
```bash
# Get real VIX data for volatility adjustment
def calculate_vix_adjusted_position_size(base_size, confidence, max_drawdown):
    # Get actual VIX from market (or use SPY volatility as proxy)
    spy_bars = mcp__alphavantage__TIME_SERIES_INTRADAY("SPY", "5min")
    # Calculate realized volatility from SPY as VIX proxy
    vix_proxy = calculate_realized_volatility(spy_bars)
    
    # VIX/Volatility adjustment
    if vix_proxy < 15:
        vol_adj = 0.75     # Low vol = smaller size
    elif vix_proxy <= 25:
        vol_adj = 1.0      # Normal vol = base size  
    else:
        vol_adj = min(1.5, 1.0 + ((vix_proxy - 25) * 0.02))  # High vol = larger size
    
    # Confidence adjustment (0-100 → 0-1)
    conf_adj = confidence / 100
    
    # Drawdown protection
    drawdown_adj = max(0.5, 1.0 - (max_drawdown * 0.5))
    
    optimal_size = base_size * vol_adj * conf_adj * drawdown_adj
    return round(max(1, min(50, optimal_size)))
```

## Advanced Position Sizing Protocol (Probability-Based)

**KELLY CRITERION & COEFFICIENT MANAGEMENT: Professional risk optimization**

### Kelly Criterion Implementation
```bash
def calculate_kelly_position_size(win_prob, avg_win, avg_loss, max_kelly=0.10):
    """
    Kelly Criterion: f = (bp - q) / b
    Where: b = odds received, p = probability of winning, q = probability of losing
    """
    # Calculate odds ratio
    b = avg_win / avg_loss if avg_loss > 0 else 0
    p = win_prob  # probability of winning
    q = 1 - win_prob  # probability of losing
    
    # Kelly fraction calculation
    kelly_fraction = (b * p - q) / b if b > 0 else 0
    
    # Conservative fractional Kelly (25% of full Kelly for safety)
    fractional_kelly = kelly_fraction * 0.25
    
    # Cap at maximum Kelly threshold (10% max)
    return max(0, min(fractional_kelly, max_kelly))

def probability_weighted_position_size(signal_confidence, expected_return, volatility):
    """
    Signal Confidence Weighting with Risk-Adjusted Sizing
    """
    # Expected Return = (Win Rate × Average Win) - (Loss Rate × Average Loss)
    # Risk-Adjusted Size = Expected Return / Standard Deviation
    
    if volatility <= 0:
        return 0
    
    # Base size calculation
    risk_adjusted_return = expected_return / volatility
    base_size = (signal_confidence * risk_adjusted_return) * 0.01  # 1% base
    
    # Cap at 5% of portfolio regardless of probability
    return min(base_size, 0.05)
```

### Coefficient Management Strategies
```bash
def coefficient_of_variation_control(returns_series, target_cv=10.0):
    """
    Coefficient of Variation Control: CV = Standard Deviation / Mean Return < 10
    """
    mean_return = np.mean(returns_series)
    std_return = np.std(returns_series)
    
    current_cv = std_return / mean_return if mean_return > 0 else float('inf')
    
    # Position size adjustment factor
    if current_cv > target_cv:
        adjustment_factor = target_cv / current_cv
        return min(adjustment_factor, 1.0)
    
    return 1.0

def beta_coefficient_management(portfolio_beta, target_beta=1.0):
    """
    Keep portfolio beta relative to market under 1.0
    """
    if portfolio_beta > target_beta:
        # Reduce position sizes when beta exceeds target
        beta_adjustment = target_beta / portfolio_beta
        return beta_adjustment
    
    return 1.0

def risk_parity_with_probability(probability, expected_return, volatility, total_risk_budget=0.10):
    """
    Risk Parity with Probability Weighting
    Weight positions by: (Probability × Expected Return) / Volatility
    """
    if volatility <= 0:
        return 0
    
    # Risk parity calculation
    risk_weighted_size = (probability * expected_return) / volatility
    
    # Normalize to risk budget (ensure no single position exceeds 10% of total risk)
    normalized_size = (risk_weighted_size * total_risk_budget) / 10
    
    return min(normalized_size, total_risk_budget)
```

### Practical Implementation Framework
```bash
def advanced_position_sizing(trade_setup):
    """
    Integrated Advanced Position Sizing with Multiple Constraints
    """
    # Extract trade parameters
    win_prob = trade_setup['win_probability']
    avg_win = trade_setup['average_win']
    avg_loss = trade_setup['average_loss']
    signal_confidence = trade_setup['confidence_score']  # 0-1
    volatility = trade_setup['volatility']
    
    # Calculate Expected Return
    expected_return = (win_prob * avg_win) - ((1 - win_prob) * avg_loss)
    
    # Kelly Criterion sizing
    kelly_size = calculate_kelly_position_size(win_prob, avg_win, avg_loss)
    
    # Probability-weighted sizing
    prob_weighted_size = probability_weighted_position_size(
        signal_confidence, expected_return, volatility
    )
    
    # Take conservative minimum of both methods
    base_position_size = min(kelly_size, prob_weighted_size)
    
    # Apply coefficient management constraints
    cv_adjustment = coefficient_of_variation_control(recent_returns)
    beta_adjustment = beta_coefficient_management(current_portfolio_beta)
    
    # Final position size with all constraints
    final_size = base_position_size * cv_adjustment * beta_adjustment
    
    # Absolute maximum caps
    final_size = min(final_size, 0.05)  # 5% portfolio max
    final_size = max(final_size, 0.001) # 0.1% minimum
    
    return {
        'position_size_pct': final_size,
        'kelly_component': kelly_size,
        'prob_weighted_component': prob_weighted_size,
        'cv_adjustment': cv_adjustment,
        'beta_adjustment': beta_adjustment,
        'expected_return': expected_return
    }
```

### Dynamic Probability Adjustment Protocol
```bash
def update_probability_estimates(trade_history, lookback_periods=20):
    """
    Update probabilities based on recent performance
    Reduce position sizes when hit rates fall below expected
    """
    recent_trades = trade_history[-lookback_periods:]
    
    if len(recent_trades) < 5:  # Insufficient data
        return 1.0
    
    # Calculate actual vs expected performance
    actual_win_rate = sum(1 for trade in recent_trades if trade['pnl'] > 0) / len(recent_trades)
    expected_win_rate = np.mean([trade['expected_win_rate'] for trade in recent_trades])
    
    # Performance ratio adjustment
    performance_ratio = actual_win_rate / expected_win_rate if expected_win_rate > 0 else 1.0
    
    # Conservative adjustment (cap between 0.5 and 1.5)
    adjustment_factor = max(0.5, min(1.5, performance_ratio))
    
    return adjustment_factor
```

### Integration with SPX Analysis
```bash
# Apply to SPX option setups from Monte Carlo analysis
def apply_advanced_sizing_to_spx_setup(monte_carlo_results, confidence_score):
    """
    Apply advanced position sizing to SPX option plays
    """
    # Extract Monte Carlo probabilities
    win_prob = monte_carlo_results['base_case_win_rate'] / 100
    expected_return = monte_carlo_results['expected_value']
    
    trade_setup = {
        'win_probability': win_prob,
        'average_win': expected_return if expected_return > 0 else 3.0,
        'average_loss': 3.0,  # Premium paid
        'confidence_score': confidence_score,
        'volatility': 0.15  # 15% daily vol estimate
    }
    
    sizing_result = advanced_position_sizing(trade_setup)
    
    return sizing_result
```

**COEFFICIENT TARGETS:**
- **Kelly Fraction:** < 0.10 (10% max)
- **Coefficient of Variation:** < 10.0
- **Portfolio Beta:** < 1.0
- **Maximum Single Position:** 5% of portfolio
- **Risk Budget per Position:** 2-3% for 0DTE, 1-2% for longer-term

## Integrated Trading System Framework (SPXFILE v2.0)

**⚠️ CRITICAL RISK WARNING: 0DTE options expire worthless within hours. Maximum position size NEVER exceeds 1-2% of account per trade.**

### 250-Point Probability Scoring System
```bash
def calculate_probability_score(market_data):
    """
    Comprehensive 250-point scoring system for trade probability assessment
    """
    score_components = {
        'ema_alignment': 25,        # EMA structure alignment
        'fast_ema': 20,            # 9/21 EMA positioning
        'choppiness': 15,          # Market regime clarity
        'bar_setup': 25,           # Candlestick patterns
        'demand_zones': 30,        # Supply/demand levels
        'sp500_momentum': 40,      # Broader market context
        'technical_levels': 15,    # Key S/R levels
        'volume': 15,              # Volume confirmation
        'options_flow': 10,        # Unusual options activity
        'strike_efficiency': 25,   # Strike selection quality
        'model_consensus': 10,     # Model agreement
        'ml_patterns': 10,         # Machine learning signals
        'market_conditions': 10,   # Market regime factor
        'gex_dex': 20,            # Gamma/delta exposure
        'time_decay': 5,          # Time value consideration
        'quant_levels': 10         # Quantitative level proximity
    }
    
    # Calculate individual scores (implement scoring logic)
    total_score = sum(component_scores.values())
    
    return {
        'total_score': total_score,
        'direction': 'BULLISH' if total_score > 150 else 'BEARISH',
        'confidence_pct': total_score / 250 * 100,
        'components': score_components
    }

# MINIMUM REQUIREMENTS:
# Entry: ≥150/250 (60%)
# Optimal: ≥200/250 (80%) 
# Maximum Position: ≥218/250 (87%)
```

### SBIRS (Smart Breakout/Reversal Signal System)
```bash
def detect_sbirs_signals(market_data, timeframe='5min'):
    """
    Advanced breakout and reversal pattern detection
    """
    signals = []
    
    # Breakout Detection
    breakout_signal = {
        'type': 'BULLISH_BREAKOUT',
        'confidence': 85,           # 0-100 confidence score
        'direction': 'BULLISH',
        'entry_price': 6455,
        'stop_loss': 6445,
        'targets': [6465, 6475, 6485],
        'risk_reward': 2.0,
        'pattern': 'FLAG_BREAKOUT',
        'volume_confirmation': True,
        'ema_alignment': True
    }
    
    # Reversal Detection  
    reversal_signal = {
        'type': 'BEARISH_REVERSAL',
        'confidence': 78,
        'direction': 'BEARISH', 
        'entry_price': 6485,
        'stop_loss': 6495,
        'targets': [6475, 6465, 6455],
        'risk_reward': 1.8,
        'pattern': 'DOUBLE_TOP',
        'divergence': True,
        'momentum_shift': True
    }
    
    return signals

# MINIMUM REQUIREMENTS:
# SBIRS Confidence: ≥70%
# Pattern Validation: TRUE
# Risk/Reward: ≥1.5:1
```

### Unified Trading Rules Framework
```bash
INTEGRATED_TRADING_RULES = {
    'ENTRY_REQUIREMENTS': {
        'probability_score': {
            'minimum': 150,        # 60% minimum (150/250)
            'optimal': 200,        # 80% optimal (200/250)
            'maximum_position': 218 # 87% for max position (218/250)
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
        'consensus_required': {
            'all_systems_agree': True,     # ALL systems must agree on direction
            'direction_alignment': True,   # BULLISH/BEARISH alignment required
            'min_confirming_systems': 3    # Minimum 3 systems confirming
        }
    },
    
    'POSITION_SIZING_ENHANCED': {
        'base_risk': 0.01,         # 1% base risk
        'max_risk': 0.02,          # 2% maximum risk per trade
        'max_daily_risk': 0.06,    # 6% maximum daily risk
        'max_concurrent': 3,       # Maximum concurrent positions
        'confidence_scaling': {
            'high_confidence': 1.5,    # 1.5x for 85%+ confidence
            'very_high': 2.0,          # 2x for 90%+ confidence
            'extreme': 2.5             # 2.5x for 95%+ (capped at 2%)
        }
    },
    
    'ABORT_CONDITIONS_STRICT': {
        'probability_drop': 30,       # Exit if probability drops 30 points
        'gex_score_drop': 15,        # Exit if GEX/DEX drops 15 points
        'sbirs_invalidation': True,  # Exit if SBIRS pattern breaks
        'max_loss': 0.6,             # Exit at 60% loss
        'consensus_break': True,     # Exit if systems disagree
        'regime_change': True        # Exit on market regime change
    }
}
```

### Multi-System Integration Protocol
```bash
def integrated_trading_decision(market_data, account_balance):
    """
    Multi-system consensus decision making
    """
    # Step 1: Calculate all scores
    prob_analysis = calculate_probability_score(market_data)
    gex_dex_analysis = analyze_gex_dex(market_data)
    sbirs_signals = detect_sbirs_signals(market_data)
    
    # Step 2: Check minimum requirements
    if prob_analysis['total_score'] < 150:
        return {'trade': False, 'reason': 'Probability score too low'}
    
    if gex_dex_analysis['entry_score'] < 75:
        return {'trade': False, 'reason': 'GEX/DEX score too low'}
    
    if not sbirs_signals or sbirs_signals[0]['confidence'] < 70:
        return {'trade': False, 'reason': 'SBIRS confidence insufficient'}
    
    # Step 3: Check direction consensus
    prob_direction = prob_analysis['direction']
    gex_direction = gex_dex_analysis['bias']
    sbirs_direction = sbirs_signals[0]['direction']
    
    if not (prob_direction == gex_direction == sbirs_direction):
        return {'trade': False, 'reason': 'Direction disagreement'}
    
    # Step 4: Calculate position size (use most conservative)
    position_sizes = [
        calculate_position_from_probability(prob_analysis['total_score'], account_balance),
        calculate_position_from_gex(gex_dex_analysis['entry_score'], account_balance),
        calculate_position_from_sbirs(sbirs_signals[0]['confidence'], account_balance)
    ]
    
    position_size = min(position_sizes)
    position_size = min(position_size, account_balance * 0.02)  # 2% hard cap
    
    # Step 5: Generate trade decision
    return {
        'trade': True,
        'direction': prob_direction,
        'entry_price': sbirs_signals[0]['entry_price'],
        'stop_loss': sbirs_signals[0]['stop_loss'],
        'targets': sbirs_signals[0]['targets'],
        'position_size': position_size,
        'confidence': (prob_analysis['total_score']/250 + 
                      gex_dex_analysis['entry_score']/100 + 
                      sbirs_signals[0]['confidence']/100) / 3,
        'systems_consensus': f"Prob:{prob_analysis['total_score']}/250, GEX:{gex_dex_analysis['entry_score']}/100, SBIRS:{sbirs_signals[0]['confidence']}/100"
    }
```

### Performance Tracking Integration
```bash
def track_performance(trade_result):
    """
    Comprehensive performance tracking for integrated system
    """
    performance_metrics = {
        'trade_data': {
            'timestamp': trade_result['timestamp'],
            'direction': trade_result['direction'],
            'entry_price': trade_result['entry_price'],
            'exit_price': trade_result['exit_price'],
            'pnl': trade_result['pnl'],
            'pnl_pct': trade_result['pnl_pct'],
            'hold_time_minutes': trade_result['hold_time'],
            'exit_reason': trade_result['exit_reason']
        },
        'system_scores': {
            'probability_score': trade_result['entry_probability_score'],
            'gex_dex_score': trade_result['entry_gex_score'],
            'sbirs_confidence': trade_result['entry_sbirs_confidence'],
            'consensus_strength': trade_result['consensus_strength']
        },
        'risk_metrics': {
            'position_size_pct': trade_result['position_size_pct'],
            'max_drawdown': trade_result['max_drawdown'],
            'risk_reward_actual': trade_result['actual_risk_reward']
        }
    }
    
    # Save to .spx/performance_log.json
    save_performance_data(performance_metrics)
    
    return calculate_running_metrics()

def calculate_running_metrics():
    """Calculate real-time performance metrics"""
    trades = load_performance_data()
    
    if not trades:
        return {}
    
    df = pd.DataFrame(trades)
    
    return {
        'total_trades': len(df),
        'win_rate': (df['pnl'] > 0).mean() * 100,
        'avg_win_pct': df[df['pnl'] > 0]['pnl_pct'].mean(),
        'avg_loss_pct': df[df['pnl'] <= 0]['pnl_pct'].mean(),
        'profit_factor': abs(df[df['pnl'] > 0]['pnl'].sum() / 
                           df[df['pnl'] <= 0]['pnl'].sum()) if df[df['pnl'] <= 0]['pnl'].sum() != 0 else float('inf'),
        'sharpe_ratio': df['pnl_pct'].mean() / df['pnl_pct'].std() if df['pnl_pct'].std() > 0 else 0,
        'max_drawdown_pct': (df['pnl'].cumsum() - df['pnl'].cumsum().cummax()).min(),
        'system_accuracy': {
            'probability_system': calculate_system_accuracy(df, 'probability_score'),
            'gex_dex_system': calculate_system_accuracy(df, 'gex_dex_score'),
            'sbirs_system': calculate_system_accuracy(df, 'sbirs_confidence')
        }
    }
```

### Integration Commands for SPX Analysis
```bash
spx integrated        # Run full integrated system analysis (250pt + GEX/DEX + SBIRS)
spx consensus        # Multi-system consensus check with detailed scoring
spx sbirs           # SBIRS breakout/reversal signal detection only
spx score250        # 250-point probability scoring breakdown
spx performance     # Show running performance metrics
spx systems check   # Verify all systems operational and aligned
```

**CRITICAL INTEGRATION RULES:**
- **ALL SYSTEMS MUST AGREE** on direction before trade entry
- **Minimum Scores:** Probability ≥150, GEX/DEX ≥75, SBIRS ≥70
- **Maximum Risk:** 2% per trade, 6% daily, never exceed hard caps
- **Consensus Breaking:** Immediate exit if systems disagree post-entry
- **Performance Tracking:** Every trade logged with full system context

## Discord Webhook Integration

**Auto-Send Triggers:** Automatically send to Discord when user uses these phrases:
- "spx [analysis] discord" - Send analysis directly to Discord
- "discord spx [analysis]" - Send analysis directly to Discord  
- "[analysis] and send discord" - Send analysis and Discord simultaneously

**Manual Send:** When user says "send to discord" or "discord it", use one of these methods:

### Method 1: Discord Helper Script (Recommended)
```bash
./discord_helper.sh "Analysis Title" "Analysis content here"
```

### Method 2: Python Helper (For complex content)
```bash
python3 send_discord.py "Analysis Title" "Analysis content here"
```

### Method 3: Direct curl (Fallback)
```bash
curl -H "Content-Type: application/json" -X POST -d '{
  "username": "Trading Analysis Bot",
  "embeds": [{
    "title": "Analysis Title Here",
    "description": "Analysis content here",
    "color": 3447003,
    "timestamp": "'$(date -u +%Y-%m-%dT%H:%M:%S.000Z)'"
  }]
}' "https://discord.com/api/webhooks/1413434367853990019/QBe2jVMUDxt5x42ZNlWWxzHrexyq2oxW1OwT1-xwXbg5fY9CDIeYNDWfCYg7Vqxfdbtr"
```

**Helper Scripts Created:**
- `discord_helper.sh` - Bash wrapper for fast sending
- `send_discord.py` - Python wrapper with error handling

## SPX 0DTE Trading Instructions with Alphavantage MCP

**CRITICAL OPTION PRICE PROTOCOL - ZERO TOLERANCE FOR ERRORS:**

### MANDATORY Market Data Verification
```bash
# STEP 0: ALWAYS GET REAL MARKET DATA FIRST - NO EXCEPTIONS
# Before ANY SPX analysis, MUST call:
market_status = mcp__alphavantage__MARKET_STATUS()
spy_quote = mcp__alphavantage__GLOBAL_QUOTE("SPY")
spy_rsi_5m = mcp__alphavantage__RSI("SPY", "5min", 14, "close")

# SPY to SPX conversion: SPY × 10 ≈ SPX
spx_estimate = float(spy_quote["Global Quote"]["05. price"]) * 10

# NEVER estimate prices - use actual data from alphavantage MCP
# Verify market is open before real-time analysis
# Use SPY data as direct proxy for SPX analysis
```

**WORKFLOW PROTOCOL:** Every SPX analysis command must follow this sequence:

### Pre-Analysis Checks (MANDATORY)
```bash
# Step 1: Market Status & Session Check
market_status = mcp__alphavantage__MARKET_STATUS()
IF first_command_of_session:
    IF ./.spx/session.json exists:
        LOAD session_context()
        DISPLAY session_continuity_info()
    ENDIF
ENDIF

# Step 2: Real Market Data Integration
spy_data = mcp__alphavantage__GLOBAL_QUOTE("SPY")
spy_bars_5m = mcp__alphavantage__TIME_SERIES_INTRADAY("SPY", "5min")
spy_rsi = mcp__alphavantage__RSI("SPY", "5min", 14, "close")
LOAD key_levels from ./.spx/levels.json
REFERENCE previous_analysis for continuity
```

### Analysis Execution
During market hours, when user requests SPX analysis:

1. **Get fresh data from alphavantage MCP**:
   - SPY quote and convert to SPX estimate (×10)
   - SPY technical indicators (RSI, EMA, SMA, MACD)
   - SPY intraday bars for volume/momentum analysis
   - Market status and news sentiment

2. **Analysis requirements**:
   - Technical analysis with real RSI, support/resistance levels
   - Momentum indicators from alphavantage calculations
   - Identify high-confidence scalp and lotto opportunities
   - **Reference restored context** for continuity

3. **Option setup criteria**:
   - **CRITICAL: Get REAL option prices from market data sources**
   - Entry range: $1-10 per contract (based on actual market prices)
   - 0DTE expiration focus
   - High delta for scalps, low delta for lottos
   - Liquidity check via volume analysis
   - **VERIFY: ATM options typically $5-15, not $25-50**

4. **Format output as**:
   - Current SPX level (derived from SPY × 10) and key technicals
   - **Context continuity** with previous analysis
   - Recommended option strikes and realistic premiums
   - Entry/exit levels with risk management
   - Confidence rating and rationale

### Post-Analysis Auto-Save (MANDATORY)
```bash
# Step 3: Context Persistence  
SAVE session_context to ./.spx/session.json with:
    - Updated key levels
    - Analysis results from alphavantage data
    - Significant findings as session notes
    - Trading plan updates

# Step 4: Session Management
APPEND significant_findings to ./.spx/notes.txt
UPDATE ./.spx/levels.json with new support/resistance
DISPLAY "SESSION UPDATED" confirmation
```

## SPX 0DTE Analysis Template (Alphavantage Enhanced)

```
[Session context auto-load from ./.spx/ files if they exist]

🎯 SPX 0DTE SCALP & LOTTO SETUPS - ALPHAVANTAGE POWERED

📊 CURRENT vs SESSION CONTEXT:
SPX: $X,XXX.XX (SPY $XXX.XX × 10) (+/-XX.XX from last session)
Key Levels: [LOAD FROM ./.spx/levels.json]
Session Notes: [LAST 3 ENTRIES FROM ./.spx/notes.txt]
Trading Plan: [FROM ./.spx/session.json]

📊 CURRENT LEVELS (ALPHAVANTAGE MCP):
SPY: $XXX.XX (+X.XX, +X.XX%) - mcp__alphavantage__GLOBAL_QUOTE("SPY")
SPX Estimate: $X,XXX.XX (SPY × 10)
Volume: X.XM shares - Real volume data
Market Status: [OPEN/CLOSED] - mcp__alphavantage__MARKET_STATUS()

📈 TECHNICAL ANALYSIS (REAL-TIME ALPHAVANTAGE):
5min RSI: XX (oversold/neutral/overbought) - mcp__alphavantage__RSI("SPY", "5min", 14, "close")
15min RSI: XX (trend direction) - mcp__alphavantage__RSI("SPY", "15min", 14, "close")
Support: $X,XXX | Resistance: $X,XXX (from technical analysis)
Volume Profile: [High/Normal/Low] (vs 20-day average)

📊 EMA DEMAND ZONES (ALPHAVANTAGE CALCULATED):
EMA 9/21: [BULLISH/BEARISH] - mcp__alphavantage__EMA("SPY", "5min", 9, "close") vs EMA21
EMA 50/200: [Above/Below] - mcp__alphavantage__EMA("SPY", "15min", 50, "close") demand zone
SMA Structure: [Confirming/Diverging] - mcp__alphavantage__SMA crossover analysis

⚡ LIVE MARKET SIGNALS (ALPHAVANTAGE REAL-TIME):
SPY Stream: $XXX.XX (mcp__alphavantage__TIME_SERIES_INTRADAY 1min data)
EMA 9/21: [BULLISH/BEARISH] cross detected from real calculations
EMA 50/200: [Above/Below] - institutional demand zone active
MACD: [BULLISH/BEARISH] - mcp__alphavantage__MACD("SPY", "5min", "close")

🎯 SCALP OPPORTUNITIES (High Delta):
**MANDATORY: Get REAL option prices from market data - NEVER estimate**
Strike: $X,XXX Call/Put (based on SPX estimate)
Last: $X.XX | Bid: $X.XX | Ask: $X.XX (ACTUAL market prices)
Delta: X.XX (XX% chance ITM)
Entry: Based on real bid/ask spread and alphavantage signals
Target: +50-100% | Stop: -50%
Confidence: [HIGH/MEDIUM/LOW] - [Based on multi-timeframe alphavantage data]
Volume: X,XXX (liquidity check from SPY volume analysis)

🎲 LOTTO OPPORTUNITIES (Low Delta):  
**MANDATORY: Get REAL option prices from market data - NEVER estimate**
Strike: $X,XXX Call/Put (OTM based on SPX estimate)
Last: $X.XX | Bid: $X.XX | Ask: $X.XX (ACTUAL market prices)
Delta: 0.XX (X% chance ITM)
Entry: Strong momentum break confirmed by alphavantage signals
Target: +200-500% | Risk: 100%
Confidence: [HIGH/MEDIUM/LOW] - [Based on EMA/RSI confluence]
Volume: X,XXX (liquidity check)

⚠️ RISK MANAGEMENT:
• Position size: X% of account per trade (based on alphavantage volatility)
• Time decay: Exit 30min before close if flat
• Momentum stops: Exit on RSI reversal (real RSI from alphavantage)

📱 TRADINGVIEW CODES:
**MANDATORY: Verify option symbols exist with real market data first**
SCALP: SPXW 250908C6XXX.0 (use actual strikes with real prices)
LOTTO: SPXW 250908C6XXX.0 (use actual strikes with real prices)
**Format: "SPXW 250908C6495.0" NOT "SPXWXXXXXXCXXXX.0"**

SESSION UPDATED: Analysis and context saved to ./.spx/ using alphavantage data
```

**Important: Always include TradingView shortcodes ending in .0 for SPX/option analyses**
**For Discord: Wrap codes with backticks for mobile clickability**
**Also provide full TV URL in non-auto-expanding format: <https://www.tradingview.com/chart/?symbol=SYMBOLHERE.0>**

## Time Zone and Market Hours Protocol

**CRITICAL REMINDER:** ALWAYS check current time before making ANY time-related statements.

**Market Hours Reference:**
- **Market Open:** 6:30 AM PT / 9:30 AM ET
- **Market Close:** 1:00 PM PT / 4:00 PM ET  
- **User Location:** Pacific Time (PT)
- **Market Time:** Eastern Time (ET)

**MANDATORY TIME PROTOCOL RULES:**
1. **ALWAYS** check current time before ANY time references - NO EXCEPTIONS
2. **ALWAYS** calculate time remaining to market close using CURRENT TIME
3. **ALWAYS** show both PT and ET when discussing market timing
4. **NEVER** assume or estimate time - ALWAYS verify current time
5. Account for 3-hour difference: ET = PT + 3 hours
6. **CRITICAL:** Market closes at 1:00 PM PT / 4:00 PM ET

**TIME CHECK INTEGRATION:** 
- Combine with mcp__alphavantage__MARKET_STATUS() for market open verification
- Use available time checking mechanisms before market hour calculations
- Format: getCurrentTime() → validate market hours → calculate remaining time

**MANDATORY FORMAT:** 
"Current time: X:XX AM/PM PT (X:XX AM/PM ET) - X hours XX minutes until market close at 1:00 PM PT"

## Real-Time Streaming Protocol Framework

**ALPHAVANTAGE MCP: Real-time analysis integration patterns**

### Streaming Data Integration Framework:
```bash
**ALPHAVANTAGE STREAMING INTEGRATION:**
# Real-time data refresh patterns using alphavantage MCP:

⚡ LIVE MARKET SIGNALS (Alphavantage real-time):
SPY Price: $XXX.XX (mcp__alphavantage__GLOBAL_QUOTE("SPY"))
EMA 9/21: [BULLISH/BEARISH] cross (mcp__alphavantage__EMA calculations)
EMA 50/200: [Above/Below] - demand zone (mcp__alphavantage__EMA analysis)
RSI: XX (mcp__alphavantage__RSI("SPY", "5min", 14, "close"))
MACD: [BULLISH/BEARISH] (mcp__alphavantage__MACD("SPY", "5min", "close"))

**DATA REFRESH PROTOCOL:**
- Price updates: mcp__alphavantage__GLOBAL_QUOTE every analysis
- Technical updates: mcp__alphavantage__RSI/EMA/MACD for signals
- Volume context: mcp__alphavantage__TIME_SERIES_INTRADAY for flow
- Market sentiment: mcp__alphavantage__NEWS_SENTIMENT for context
```

### Live Analysis Template Integration:
```bash
⚡ LIVE SCALP SIGNALS (ALPHAVANTAGE POWERED):
SPY Stream: $XXX.XX (live data via mcp__alphavantage__GLOBAL_QUOTE)
EMA Analysis: [CROSS/DIVERGENCE] detected (mcp__alphavantage__EMA calculations)
RSI Momentum: XX - [BULLISH/BEARISH] bias (mcp__alphavantage__RSI real-time)
Volume Flow: [HIGH/NORMAL/LOW] vs average (alphavantage volume data)
```

## Last Hour of Trading Template

When user asks for "last hour of trading", use this format:

```
**TIME CHECK: [Current time from available source] - Market closes 1:00 PM PT**

SPX Current Status: X,XXX.XX (SPY $XXX.XX × 10) (last hour of trading)
Position: [Near session highs/lows] at X,XXX.XX
Range: XXXX-XXXX (from alphavantage intraday data)
Momentum: [Trend description] from alphavantage technical analysis

0DTE Scalp Plays (based on real market data):

Bullish (if continues [direction]):
XXXX calls @ $X.XX-X.XX - [Setup description], [Greeks], needs move above XXXX
XXXX calls @ $X.XX-X.XX - [Setup type] if breaks XXXX [level]

Bearish (if reverses):
XXXX puts @ $X.XX-X.XX - [Setup description], delta -X.XX
XXXX puts @ $X.XX-X.XX - [Target description]

Best Risk/Reward: [Primary setup] if SPX [condition]. [Theta warning] but [gamma/momentum benefit] for final hour [context].

📱 Primary: `SPXWXXXXXXCXXXX.0` | Alt: `SPXWXXXXXXPXXXX.0`

SESSION UPDATED: Last hour analysis saved to ./.spx/
```

**Focus for Last Hour Trading:**
- Current position relative to session range (from alphavantage data)
- Both bullish and bearish 0DTE setups with real pricing
- Greeks analysis and market data verification
- Risk/reward assessment for final hour
- Specific trigger levels based on technical analysis
- TradingView codes for quick access

## SPX Play by Play Template

When user asks for "spx play by play", use this concise real-time format:

```
**REAL-TIME: [Time check] - [Market status from mcp__alphavantage__MARKET_STATUS()]**

SPX: X,XXX.XX (SPY $XXX.XX × 10) (+/-XX.XX, +/-X.XX%) - [Current action description] with [key level] at X,XXX.
SPY Data: $XXX.XX (+/-$X.XX, +/-X.XX%) - Volume: X.XM vs avg. [RSI/EMA analysis] shows [bullish/bearish] flow supporting SPX thesis.
```

**Focus for SPX Play by Play:**
- Real-time SPX price action (derived from alphavantage SPY data)
- Key resistance/support levels ahead
- SPY confirmation with volume and technical indicators
- Alphavantage-based momentum analysis for direction
- Keep it concise and actionable for live trading

## SPX Order Book Analysis Template

When user asks for "spx order book", use this format:

```
**SPY Order Book Analysis (SPX Proxy via Alphavantage):**
Current: $XXX.XX (mcp__alphavantage__GLOBAL_QUOTE)

Volume Analysis: XXM shares (mcp__alphavantage volume data)
vs Average: [HIGH/NORMAL/LOW] (compared to 20-day average)
Price Action: [BULLISH/BEARISH] momentum from alphavantage technicals

Supporting SPX Thesis:
RSI: XX ([oversold/neutral/overbought]) - mcp__alphavantage__RSI
EMA Status: [Above/Below key levels] - mcp__alphavantage__EMA
MACD: [BULLISH/BEARISH] signal - mcp__alphavantage__MACD
Range: $XXX.XX-$XXX.XX ([pattern description])

Market Flow Analysis:
[Volume/momentum description from alphavantage data]
[Technical confirmation/contradiction] 
Last Move: [Direction based on alphavantage bars] ([buying/selling] pressure)

SPY action [confirms/contradicts] SPX [pattern] - [summary based on alphavantage analysis]
```

**Focus for SPX Order Book:**
- SPY volume and momentum analysis via alphavantage
- Technical indicator confirmation from real calculations
- Volume patterns and market context
- Correlation between SPY technical action and SPX thesis
- Real-time market participation indicators

## MAG 7 Support Levels - SPX Correlation Map

**MAG 7 Critical Support Levels:**
- **AAPL:** 238.60 support
- **GOOGL:** 231.90 support  
- **AMZN:** 231.90 support
- **NVDA:** 164.00 support 🚨 (Primary SPX catalyst)
- **MSFT:** 494.50 support
- **TSLA:** 344.70 support
- **META:** 745.00 support

**SPX Breakdown Triggers:**
- **6450:** Triple MAG 7 support break (3+ stocks break support)
- **6440:** Mass MAG 7 breakdown (5+ stocks break support)  
- **6430:** Full MAG 7 collapse scenario (6-7 stocks break support)

**Alphavantage Integration:**
- Use mcp__alphavantage__GLOBAL_QUOTE for each MAG 7 stock
- Monitor real-time distance to support levels
- Combine with mcp__alphavantage__NEWS_SENTIMENT for correlation analysis
- 3+ simultaneous breaks = major SPX downside potential

**Usage:** Reference MAG 7 support levels in all SPX analysis enhanced with real-time alphavantage data

## Full SPX Market Report Template

When user asks for "full spx market report", use this format with MAG 7 analysis:

```
SPXW 0DTE SCALP - UPDATED WITH MAG 7 ANALYSIS 🎯

📊 MAG 7 LEVEL 2 & 5MIN ANALYSIS
🔴 AAPL: $XXX.XX (-X.XX%) | Bid: XXX.XX (XXX) Ask: XXX.XX (XXX) - WEAK
🔴 GOOGL: $XXX.XX (-X.XX%) | Bid: XXX.XX (XXX) Ask: XXX.XX (XXX) - VERY WEAK
🟢 AMZN: $XXX.XX (+X.XX%) | Bid: XXX.XX (XXX) Ask: XXX.XX (XXX) - STRONG
🟡 NVDA: $XXX.XX (+X.XX%) | Bid: XXX.XX (XXX) Ask: XXX.XX (XXX) - FLAT
🟡 MSFT: $XXX.XX (-X.XX%) | Bid: XXX.XX (XXX) Ask: XXX.XX (XXX) - FLAT
🔴 TSLA: $XXX.XX (-X.XX%) | Bid: XXX.XX (XXX) Ask: XXX.XX (XXX) - WEAK
🟢 META: $XXX.XX (+X.XX%) | Bid: XXX.XX (XXX) Ask: XXX.XX (XXX) - STRONG

🔥 KEY 5MIN INSIGHTS:
[Individual stock momentum analysis]

📈 MAG 7 SENTIMENT: [BULLISH/BEARISH/MIXED]
✅ X Strong ([symbols])
❌ X Weak ([symbols]) 
🟡 X Flat ([symbols])

🎯 REVISED RECOMMENDATION: [CALL/PUT] CONVICTION

Trade: `SPXWXXXXXXPXXXX.0` (XXXX Put/Call)
💰 Entry: $X.XX-X.XX
📈 Target 1: $X.XX (XX% to level)
📈 Target 2: $X.XX+ (XX% to key level)
🛑 Stop: $X.XX (XX% loss)
📊 Volume: XXXX ✅

🔥 ENHANCED RATIONALE:
✅ [Key technical levels]
✅ [MAG 7 supporting factors]
✅ [Volume/momentum confirmations]

⚡ EXECUTION PLAN:
Entry: [timing and levels]
Watch: [key breakout/breakdown levels]  
Key Target: [major technical level]
Exit: [time-based exit strategy]

🚨 [Summary of setup conviction]
```

**MAG 7 Symbols to check**: AAPL, GOOGL, AMZN, NVDA, MSFT, TSLA, META
**Use color coding**: 🔴 Weak (down >0.5%), 🟢 Strong (up >0.5%), 🟡 Flat (±0.5%)

## SPX Scalp Plan Template

When user asks for "spx scalp plan", use this tactical format for 0DTE SPXW contracts:

```
SPXW 0DTE Scalping Analysis - [Date]
Current: $X,XXX.XX (+/-XX.XX, +/-X.XX%)
Range: $X,XXX.XX - $X,XXX.XX

⚡ STREAMING EMA/SMA ANALYSIS (1-10sec refresh):
EMA 9/21 Cross: [BULLISH/BEARISH] at $X,XXX.XX (streamBars 1min)
EMA 50/200 Demand Zone: [ACTIVE/INACTIVE] - [timeframe confirmation]
SMA Structure: [Aligned/Diverging] with momentum
Live Contract Pricing: SPXWXXXXXX @ $X.XX (streamOptionChains)

Key Levels Status
XXXX resistance: [BROKEN/HOLDING] ([bullish/bearish] signal)
Next target: XXXX-XXXX (immediate resistance/support)
Major resistance/support: XXXX-XXXX (XX-XX points away)
Support/Resistance: XXXX-XXXX (now key [fallback/target] level)

BEST SCALP SETUPS:
CALLS - Momentum Play Above XXXX

XXXX Calls @ $X.XX - [Tactical reasoning for level]
Delta: X.XXX, Gamma: X.XXX, Volume: XXK+ ([liquidity assessment])
EMA Entry Signal: [STRONG/WEAK] - EMA 9>21 + SMA structure aligned
Target: [Specific breakout scenario]

XXXX Calls @ $X.XX - [Secondary setup description]  
Delta: X.XXX, Gamma: X.XXX, Volume: XXK ([liquidity assessment])
EMA Confluence: [HIGH/MEDIUM/LOW] probability based on 50/200 demand zone
Target: [Specific target reasoning]

PUTS - Reversal Play at [Key Level]

XXXX Puts @ $X.XX - [High probability setup reasoning]
Delta: -X.XXX, Gamma: X.XXX, Volume: X.XK
[Perfect for specific scenario as predicted]

XXXX Puts @ $X.XX - [Secondary reversal description]
Delta: -X.XXX, Gamma: X.XXX, Volume: XXK ([liquidity assessment])

Market Context
Mag 7 [Mixed/Bullish/Bearish]: [Individual performances]
Volume: [Analysis of key strike volumes]

Trade Plan
Primary: [Primary setup with rationale]
Target: $X-X (XX-XX% gain) | Stop: $X.XX (XX% loss)

Risk: [Key risks - theta, resistance levels, etc.]

Watch: [Key timing and exit criteria]

📱 TradingView Codes:
Primary: `SPXWXXXXXXCXXXX.0` or `SPXWXXXXXXPXXXX.0`
Alt: `SPXWXXXXXXCXXXX.0` or `SPXWXXXXXXPXXXX.0`
```

**Data Sources for SPX Scalp Plan:**
- Use $SPXW.X for option chains (0DTE focus)
- Use $SPX.X for price/bars/technical analysis
- Use SPY for volume/order book context
- Check MAG 7 for market sentiment
- Focus on $1-4 premium range for scalp setups

**Streaming Protocol for 1-10 Second Refresh:**
- streamQuotes(["SPX.X", "SPY"]) - Live tick data for price action
- streamBars("SPX.X", "1min") - Real-time 1min bars for EMA calculations
- streamOptionChains("SPXW.X") - Live option contract pricing
- EMA 50/200 calculated on 1min-30min base intervals for demand zones
- EMA 9/21 fast alerts for scalp entry signals with SMA structure confirmation

## SPX Quick Update Template

When user asks for "spx quick", use this fast tactical format:

```
SPX Update:

Current: $X,XXX.XX (+/-XX.XX, +/-X.XX%)
5min Action: [Brief momentum description, recent high/low]
Momentum: [Strong/Weak] [bullish/bearish], [tick analysis]

⚡ LIVE EMA SCALP SIGNALS (1-10sec refresh):
EMA 9/21: [BUY/SELL] signal triggered at $X,XXX.XX
EMA 50/200 Zone: [Above/Below] demand - [bullish/bearish] bias
Optimal Entry: [contract] @ $X.XX (EMA confluence + SMA structure)
Stream Status: [ACTIVE] - Live pricing via streamQuotes/streamOptionChains

Quick Play:

SPXW XXXXXXCXXXX still valid at $X.XX-X.XX
SPX only X points from XXXX strike
Entry Probability: [HIGH/MEDIUM/LOW] based on EMA/SMA alignment

📱 `SPXWXXXXXXCXXXX.0`
```

**Focus for SPX Quick:**
- Current price and immediate momentum
- 5-minute action and recent levels
- Single best quick play opportunity
- Distance to strike analysis
- TradingView code for instant access

## SPX Structure Analysis Template

When user asks for "spx structure", use this format:

```
SPX Structure Analysis:

Range: [Consolidation description with timeframe]
Support: [Strength assessment] at XXXX-XXXX, [test analysis]
Resistance: XXXX-XXXX [description] capping [direction]
Volume: [Pattern description], [context]
Pattern: [Technical pattern], [catalyst requirement]

Single Options Play:

XXXX puts @ $X.XX - if breaks below XXXX support
XXXX calls @ $X.XX - if breaks above XXXX resistance

📱 Put: `SPXWXXXXXXPXXXX.0` | Call: `SPXWXXXXXXCXXXX.0`
```

**Focus for SPX Structure:**
- Current range and consolidation patterns
- Support/resistance strength and test history
- Volume patterns and market context
- Technical pattern identification
- Binary breakout/breakdown setups with specific triggers
- TradingView codes for both scenarios

## SPX Momentum Analysis Template

When user asks for "spx momentum", use this format:

```
Current Momentum: [BULLISH/BEARISH]
Key Changes:

Drop/Rise: XXXX.XX → XXXX.XX (+/-X.XX pts)
Break: [Broke above/below] XXXX [support/resistance] level
Volume: [Up/Down] ticks dominating (XXX vs XXX [opposite])
Pattern: [Failed at/Broke through] XXXX [resistance/support], now [action]

Momentum Shift:

XX:XX: XXXX.XX ([initial condition])
XX:XX: XXXX.XX ([first change])
XX:XX: XXXX.XX ([development])
XX:XX: XXXX.XX ([key break])
Now: XXXX.XX ([current state])

Options Play:
XXXX [puts/calls] @ $X.XX - momentum now [bullish/bearish], targeting XXXX [break/test]

Next [support/resistance] at XXXX, then XXXX

📱 `SPXWXXXXXXPXXXX.0` or `SPXWXXXXXXCXXXX.0`
```

**Focus for SPX Momentum:**
- Current directional bias and strength
- Specific price changes and level breaks
- Tick volume analysis (up vs down ticks)
- Time-stamped momentum shifts
- Single directional play aligned with momentum
- Next key levels to watch

## SPX Order Book Analysis Template

When user asks for "spx order book", use this format:

```
SPY Order Book Analysis:
Current: $XXX.XX

Bid: $XXX.XX (XXX shares)
Ask: $XXX.XX (XXX shares)
Spread: $X.XX ([tight/wide description])

Supporting SPX Thesis:

Volume: XXM shares ([strength assessment])
VWAP: $XXX.XX - trading [above/below] VWAP ([bullish/bearish])
Range: $XXX.XX-$XXX.XX ([pattern description])
Momentum: +/-X.XX (+/-X.XX%) - [confirming/contradicting] SPX [strength/weakness]

Order Flow:

[Spread analysis]: [Flow type], [liquidity assessment]
[Size comparison]: [Pressure description]
Last trade: XXX shares at [bid/ask] ([buying/selling] aggression)

SPY action [confirms/contradicts] SPX [pattern] - [summary of alignment with volume and spread analysis]
```

**Focus for SPX Order Book:**
- SPY bid/ask spreads and sizes for liquidity assessment
- Volume and VWAP relationship for institutional flow
- Order flow patterns (buying vs selling aggression)
- Correlation between SPY action and SPX thesis
- Institutional participation indicators

## SPX Play by Play Template

When user asks for "spx play by play", use this concise real-time format:

```
$SPX.X: X,XXX.XX (+/-XX.XX, +/-X.XX%) - [Current action description] with [key level] at X,XXX.
SPY: $XXX.XX (+/-$X.XX, +/-X.XX%) - [Spread info], volume [status]. [Bid/ask analysis] shows [bullish/bearish] flow.
```

**Focus for SPX Play by Play:**
- Real-time SPX price action and momentum
- Key resistance/support levels ahead
- SPY confirmation with spread and volume
- Bid/ask depth analysis for flow direction
- Keep it concise and actionable for live trading

## MAG 7 Support Levels - SPX Correlation Map

**MAG 7 Critical Support Levels:**
- **AAPL:** 238.60 support
- **GOOGL:** 231.90 support  
- **AMZN:** 231.90 support
- **NVDA:** 164.00 support 🚨 (Primary SPX catalyst)
- **MSFT:** 494.50 support
- **TSLA:** 344.70 support
- **META:** 745.00 support

**SPX Breakdown Triggers:**
- **6450:** Triple MAG 7 support break (3+ stocks break support)
- **6440:** Mass MAG 7 breakdown (5+ stocks break support)  
- **6430:** Full MAG 7 collapse scenario (6-7 stocks break support)

**Key Correlation Rules:**
1. NVDA breaking 164.00 = SPX 6450 breakdown catalyst
2. MSFT + NVDA breaking together = SPX 6440 target
3. Monitor distance to support for each stock
4. 3+ simultaneous breaks = major SPX downside
5. Use MAG 7 support proximity for SPX risk assessment

**Usage:** Reference MAG 7 support levels in all SPX analysis for enhanced correlation insights

## Time Zone and Market Hours Protocol

**CRITICAL REMINDER:** ALWAYS check current time using MCP getCurrentDateTime tool before making ANY time-related statements.

**Market Hours Reference:**
- **Market Open:** 6:30 AM PT / 9:30 AM ET
- **Market Close:** 1:00 PM PT / 4:00 PM ET  
- **User Location:** Pacific Time (PT)
- **Market Time:** Eastern Time (ET)

**Time Protocol Rules:**
1. Use getCurrentDateTime MCP tool before ANY time references
2. Always convert market time (ET) to user time (PT) 
3. Never assume time remaining without checking current time
4. Reference both PT and ET when discussing market timing
5. Account for 3-hour difference: ET = PT + 3 hours

**Example Format:** 
"Current time: 9:05 AM PT (12:05 PM ET) - 3 hours 55 minutes until market close"

## Last Hour of Trading Template

When user asks for "last hour of trading", use this format:

```
SPX Current Status: X,XXX.XX (last hour of trading)
Position: [Near session highs/lows] at X,XXX.XX
Range: XXXX-XXXX
Momentum: [Trend description] from [timeframe context]

0DTE Scalp Plays ($1-4 range):

Bullish (if continues [direction]):
XXXX calls @ $X.XX-X.XX - [Setup description], [Greeks], needs move above XXXX
XXXX calls @ $X.XX-X.XX - [Setup type] if breaks XXXX [level]

Bearish (if reverses):
XXXX puts @ $X.XX-X.XX - [Setup description], delta -X.XX
XXXX puts @ $X.XX-X.XX - [Target description]

Best Risk/Reward: [Primary setup] if SPX [condition]. [Theta warning] but [gamma/momentum benefit] for final hour [context].

📱 Primary: `SPXWXXXXXXCXXXX.0` | Alt: `SPXWXXXXXXPXXXX.0`
```

**Focus for Last Hour Trading:**
- Current position relative to session range
- Both bullish and bearish 0DTE setups within $1-4 range
- Greeks analysis (gamma, theta, delta)
- Risk/reward assessment for final hour
- Specific trigger levels for each setup
- TradingView codes for quick access

## Quant Levels Integration

**IMPORTANT: For ALL SPX analysis shortcuts, incorporate user-provided quant levels when available:**

### Daily Quant Levels Format:
```
Quant Levels Integration:

Iron Condor: XXXX-XXXX and XXXX-XXXX (increasing resistance throughout session)
High Probability Reversals: XXXX, XXXX
Gamma Flip: XXXX (major directional shift level)  
Pivot Zone: XXXX-XXXX (key decision area)

Key Levels:
XXXX: [specific level significance]
XXXX: [specific level significance]
XXXX: [specific level significance]

Support Range: XXXX-XXXX
Resistance Range: XXXX-XXXX
```

### Backtest Integration:
- **Historical validation**: Reference how price previously reacted at these quant levels
- **Supply/Demand context**: Align option setups with proven supply/demand zones
- **Probability enhancement**: Use quant levels to improve entry/exit timing
- **Risk management**: Position sizing based on distance to key quant levels

### Implementation Rules:
1. **Always reference quant levels** in analysis when provided by user
2. **Align option strikes** near high-probability reversal levels
3. **Use gamma flip levels** for directional bias changes
4. **Respect iron condor zones** as increasing resistance/support
5. **Incorporate pivot zones** for range-bound strategies

**Note: User will provide fresh quant levels each trading day. Always ask for current levels if not provided.**

## Trading Analysis Format

Format trading analysis with:
- Current price and volume
- Technical indicators (RSI, support/resistance)
- Recommendation details
- Risk management notes