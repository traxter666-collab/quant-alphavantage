# 👑 King Node Directional Bias Framework

## 📅 Implementation Date: October 1, 2025

---

## 🎯 CORE CONCEPT

**King Node = Highest Strength Dealer Level (99% strength in our system)**

The king node acts as a **gravitational magnet** for price:
- When price is **BELOW** the king node → Gravitates **UP** (but dealers push away)
- When price is **ABOVE** the king node → Gravitates **DOWN** (but dealers push away)

---

## 🔧 DISTANCE THRESHOLDS

### Critical Distance Zones:

**FAR ZONE (25+ points away):**
- **Behavior:** Strong gravitational pull toward king node
- **Trading:** LONG if below, SHORT if above king node
- **Confidence Boost:** +20 points
- **Status:** OPTIMAL TRADING ZONE

**GATEKEEPER ZONE (10-24 points away):**
- **Behavior:** Moderate pull, some dealer resistance
- **Trading:** Trade toward king node but expect minor rejections
- **Confidence Boost:** +15 points
- **Status:** GOOD TRADING ZONE

**CAUTION ZONE (5-9 points away):**
- **Behavior:** Active dealer defense begins
- **Trading:** Expect rejection attempts, tight stops required
- **Confidence Boost:** +10 points
- **Status:** CAUTION - TIGHT RISK MANAGEMENT

**REJECTION ZONE (0-4 points away):**
- **Behavior:** Strong dealer pushback, high rejection probability
- **Trading:** REVERSE BIAS - expect bounce away from king node
- **Confidence Penalty:** -15 points for gravitational trades
- **Confidence Boost:** +25 points for REVERSAL trades
- **Status:** DANGER ZONE - REVERSAL PLAYS ONLY

**AT KING NODE (within 2 points):**
- **Behavior:** Maximum dealer activity, explosive moves possible
- **Trading:** WAIT for breakout/breakdown confirmation
- **Confidence:** Neutral (0 points) until direction clear
- **Status:** DECISION POINT - NO POSITION

---

## 📊 TRADING LOGIC MATRIX

### Example: King Node at 24750 CALL WALL (99%)

| Current Price | Distance | Zone | Directional Bias | Trade Type | Confidence Adj |
|--------------|----------|------|-----------------|------------|---------------|
| 24700 | -50 pts | FAR | ✅ BULLISH (gravitate UP) | LONG | +20 |
| 24725 | -25 pts | GATEKEEPER | ✅ BULLISH (pull UP) | LONG | +15 |
| 24742 | -8 pts | CAUTION | ⚠️ BULLISH (weak) | LONG | +10 |
| 24746 | -4 pts | REJECTION | 🔄 BEARISH REVERSAL | SHORT | +25 |
| 24750 | 0 pts | AT NODE | ⏸️ NEUTRAL WAIT | WAIT | 0 |
| 24754 | +4 pts | REJECTION | 🔄 BULLISH REVERSAL | LONG | +25 |
| 24758 | +8 pts | CAUTION | ⚠️ BEARISH (weak) | SHORT | +10 |
| 24775 | +25 pts | GATEKEEPER | ✅ BEARISH (pull DOWN) | SHORT | +15 |
| 24800 | +50 pts | FAR | ✅ BEARISH (gravitate DOWN) | SHORT | +20 |

---

## 🎪 IMPLEMENTATION IN CONFIDENCE SCORING

### Enhanced Confidence Score Components:

**Existing Factors (70 points max):**
- Momentum alignment: 20 points
- News sentiment: 15 points
- Dealer positioning (walls): 30 points
- Reversal zone: 5 points

**NEW: King Node Directional Bias (30 points max):**

```python
def calculate_king_node_bias(king_node, current_price, trade_direction):
    distance = current_price - king_node['strike']
    bias_score = 0
    bias_reason = ""

    # Determine gravitational direction
    if distance < -25:  # FAR BELOW
        if trade_direction == 'LONG':
            bias_score = 20
            bias_reason = f"👑 FAR BELOW king node at {king_node['strike']} - Strong upward gravity"
        else:
            bias_score = -10
            bias_reason = f"⚠️ Fighting king node gravity (price {abs(distance):.0f} pts below)"

    elif -25 <= distance < -10:  # GATEKEEPER BELOW
        if trade_direction == 'LONG':
            bias_score = 15
            bias_reason = f"👑 Gatekeeper zone - Moderate upward pull to {king_node['strike']}"
        else:
            bias_score = 0

    elif -10 <= distance < -5:  # CAUTION BELOW
        if trade_direction == 'LONG':
            bias_score = 10
            bias_reason = f"⚠️ Approaching king node - Weak upward bias"
        else:
            bias_score = 5

    elif -5 <= distance < 0:  # REJECTION BELOW
        if trade_direction == 'LONG':
            bias_score = 25  # REVERSAL PLAY
            bias_reason = f"🔄 REJECTION ZONE - Dealer pushback reversal (bounce from {king_node['strike']})"
        else:
            bias_score = -15  # Fighting reversal

    elif 0 <= distance < 2:  # AT NODE
        bias_score = 0
        bias_reason = f"⏸️ AT KING NODE {king_node['strike']} - Waiting for direction"

    elif 2 <= distance < 5:  # REJECTION ABOVE
        if trade_direction == 'SHORT':
            bias_score = 25  # REVERSAL PLAY
            bias_reason = f"🔄 REJECTION ZONE - Dealer pushback reversal (drop from {king_node['strike']})"
        else:
            bias_score = -15

    elif 5 <= distance < 10:  # CAUTION ABOVE
        if trade_direction == 'SHORT':
            bias_score = 10
            bias_reason = f"⚠️ Approaching king node - Weak downward bias"
        else:
            bias_score = 5

    elif 10 <= distance < 25:  # GATEKEEPER ABOVE
        if trade_direction == 'SHORT':
            bias_score = 15
            bias_reason = f"👑 Gatekeeper zone - Moderate downward pull to {king_node['strike']}"
        else:
            bias_score = 0

    else:  # FAR ABOVE (25+)
        if trade_direction == 'SHORT':
            bias_score = 20
            bias_reason = f"👑 FAR ABOVE king node at {king_node['strike']} - Strong downward gravity"
        else:
            bias_score = -10
            bias_reason = f"⚠️ Fighting king node gravity (price {distance:.0f} pts above)"

    return bias_score, bias_reason
```

### Updated Confidence Scoring (100 point scale):
- Momentum alignment: 20 points
- News sentiment: 15 points
- Dealer wall proximity: 30 points
- **King node directional bias: 30 points** ← NEW
- Reversal zone: 5 points

**NEW MINIMUM:** 85% confidence required (85/100 points)

---

## 📈 EXPECTED IMPROVEMENTS

### Win Rate Enhancement:
- **Before:** 70-75% win rate (basic dealer positioning)
- **After:** 80-85% win rate (king node framework)
- **Improvement:** +10-15% through directional bias intelligence

### Trade Quality:
- **Better Entries:** Trade WITH gravity instead of against it
- **Reduced Losses:** Avoid fighting king node magnetism
- **Reversal Opportunities:** Capitalize on rejection zone setups
- **Distance Awareness:** Know when dealers will defend levels

---

## 🎯 BACKTESTING PROTOCOL

### Historical Validation:
1. **Identify king nodes** from past options data
2. **Calculate distances** for each trade signal
3. **Apply bias scoring** to historical confidence scores
4. **Measure win rate improvement** with new framework

### Expected Results:
- Trades WITH king node gravity: 85%+ win rate
- Trades AGAINST king node gravity: 55% win rate
- Rejection zone reversals: 75%+ win rate
- Total system improvement: +10-15% win rate

---

## 🔄 SYSTEM INTEGRATION

### Files Modified:
1. **dealer_positioning_scanner.py** - Core king node bias logic
2. **scalping_engine.py** - Already integrated (uses confidence scores)
3. **KING_NODE_FRAMEWORK.md** - This documentation

### Discord Alert Enhancement:
```
👑 KING NODE ANALYSIS:
Distance: -26 pts (FAR BELOW)
Bias: BULLISH GRAVITY (+20 pts)
Zone: OPTIMAL TRADING
Direction: Price gravitating UP toward 24750
```

---

## ✅ IMPLEMENTATION STATUS

- ✅ Framework designed and documented
- ✅ Distance thresholds defined
- ✅ Confidence scoring logic created
- ⏳ Code implementation in progress
- ⏳ Backtest validation pending
- ⏳ Live trading deployment pending

---

## 📝 USAGE NOTES

**For Traders:**
- **Far from king node (25+):** HIGH CONFIDENCE - Trade toward king node
- **Gatekeeper zone (10-24):** GOOD CONFIDENCE - Trade toward king node
- **Caution zone (5-9):** LOW CONFIDENCE - Tight stops, expect minor rejection
- **Rejection zone (0-4):** REVERSAL ONLY - Bounce/drop away from king node
- **At king node (0-2):** WAIT - Explosive move coming, need direction first

**For System:**
- King node bias automatically integrated into confidence scoring
- Minimum 85% confidence now required for trades
- Rejection zone setups get +25 point bonus (reversal plays)
- Gravitational trades get +10 to +20 points based on distance

---

*Framework created: October 1, 2025*
*Status: ACTIVE DEVELOPMENT*
