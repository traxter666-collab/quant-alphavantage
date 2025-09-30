# Discord Analysis Format Template

## 📱 Mobile-Optimized Line-by-Line Format

**Purpose:** Clean, professional analysis format optimized for phone and tablet viewing.

### **Template Structure:**

```
Title: "📊 {SYMBOL} • ${PRICE}"

Body:
**💰 PRICE**
Bid ${BID} / Ask ${ASK} / Spread ${SPREAD}

**🎯 KEY LEVELS**
🔴 Resistance: ${LEVEL} ← Testing NOW / Key Level
🟡 Current: ${CURRENT}
🟢 Support: ${SUPPORT_1}
🟢 Strong: ${SUPPORT_2}

**⚠️ STATUS** (if applicable)
Critical Support: ${CRITICAL_LEVEL}
Current Position: ${CURRENT}
Gap: ${GAP} (${PERCENT}%)
🔴 Status: {ABOVE/BELOW} critical level

**📈 BULLISH SCENARIO**
Trigger: {CONDITION}
Target 1: ${PRICE_1} (+{PERCENT}%)
Target 2: ${PRICE_2} (+{PERCENT}%)
Trade: {SYMBOL} {STRIKE}C or {STRIKE}C

**📉 BEARISH SCENARIO**
Trigger: {CONDITION}
Target 1: ${PRICE_1} (-{PERCENT}%)
Target 2: ${PRICE_2} (-{PERCENT}%)
Trade: {SYMBOL} {STRIKE}P or {STRIKE}P

**⏰ ACTION ITEM**
{WATCH_INSTRUCTION}
✅ {BULLISH_CONDITION} = Bullish → ${TARGET}
❌ {BEARISH_CONDITION} = Bearish → ${TARGET}

**📱 Next Update: {TIME}**
```

---

## 📋 Format Guidelines

### **Title Format:**
- Use emoji icon for visual appeal (📊, 🎯, 📈)
- Include symbol and current price
- Format: `"📊 SYMBOL • $PRICE"`

### **Section Headers:**
- Use emoji + bold for clear sections
- Keep headers concise (1-3 words)
- Common emojis:
  - 💰 PRICE
  - 🎯 KEY LEVELS
  - ⚠️ STATUS / ALERT
  - 📈 BULLISH SCENARIO
  - 📉 BEARISH SCENARIO
  - ⏰ ACTION ITEM
  - 📱 NEXT UPDATE

### **Color Coding:**
- 🔴 Red: Resistance, bearish, critical alerts
- 🟡 Yellow: Current price, neutral
- 🟢 Green: Support, bullish, good status
- ⚠️ Yellow Warning: Important status updates

### **Line-by-Line Structure:**
- Each data point gets its own line
- Format: `Label: Value` or `Label: Value (context)`
- Use arrows (←) to highlight important info
- Include percentages for targets

### **Mobile Optimization:**
- No horizontal scrolling needed
- Vertical flow for easy thumb scrolling
- Short lines (< 40 characters when possible)
- Clear visual hierarchy with emojis
- Minimal text, maximum info

---

## 🎯 Example: AMZN Analysis

```
Title: "📊 AMZN • $219.20"

Body:
**💰 PRICE**
Bid $219.19 / Ask $219.21 / Spread $0.02

**🎯 KEY LEVELS**
🔴 Resistance: $220.00 ← Testing NOW
🟡 Current: $219.20
🟢 Support: $217.50
🟢 Strong: $215.00

**⚠️ MAG 7 STATUS**
Critical Support: $231.90
Current Position: $219.20
Gap: -$12.70 (-5.5%)
🔴 Status: BELOW critical level

**📈 BULLISH SCENARIO**
Trigger: Break above $220.00 + volume
Target 1: $222.50 (+1.5%)
Target 2: $225.00 (+2.6%)
Trade: AMZN 220C or 222.5C

**📉 BEARISH SCENARIO**
Trigger: Rejection at $220.00
Target 1: $217.50 (-0.8%)
Target 2: $215.00 (-1.9%)
Trade: AMZN 217.5P or 215P

**⏰ ACTION ITEM**
Watch $220 level overnight
✅ Break = Bullish → $222.50
❌ Reject = Bearish → $217.50

**📱 Next Update: Market Open (9:30 AM ET)**
```

---

## 🚀 Usage Instructions

### **For Stock Analysis:**
1. Get current price with Polygon API
2. Identify key resistance and support levels
3. Determine bullish/bearish scenarios with triggers
4. Calculate percentage targets
5. Provide specific option trade recommendations
6. Include clear action item and watch levels

### **For Index Analysis (SPX, NDX):**
Same format, but add:
- Correlation with other indices
- VIX context if relevant
- Gamma/Delta exposure info

### **For Quick Updates:**
Can simplify to just:
- PRICE section
- KEY LEVELS section
- ACTION ITEM section

---

## ⚡ Python Implementation

```python
def send_stock_analysis_discord(symbol, price, bid, ask, resistance, support,
                                bullish_trigger, bullish_targets,
                                bearish_trigger, bearish_targets,
                                action_item):
    """
    Send formatted stock analysis to Discord

    Args:
        symbol: Stock ticker (e.g., "AMZN")
        price: Current price
        bid: Bid price
        ask: Ask price
        resistance: Resistance level(s)
        support: Support level(s)
        bullish_trigger: Condition for bullish scenario
        bullish_targets: List of [target, percent] pairs
        bearish_trigger: Condition for bearish scenario
        bearish_targets: List of [target, percent] pairs
        action_item: What to watch/do next
    """

    spread = ask - bid

    title = f"📊 {symbol} • ${price:.2f}"

    body = f"""**💰 PRICE**
Bid ${bid:.2f} / Ask ${ask:.2f} / Spread ${spread:.2f}

**🎯 KEY LEVELS**
🔴 Resistance: ${resistance} ← Testing NOW
🟡 Current: ${price:.2f}
🟢 Support: ${support}

**📈 BULLISH SCENARIO**
Trigger: {bullish_trigger}
Target 1: ${bullish_targets[0][0]} (+{bullish_targets[0][1]}%)
Target 2: ${bullish_targets[1][0]} (+{bullish_targets[1][1]}%)
Trade: {symbol} {bullish_targets[0][0]}C

**📉 BEARISH SCENARIO**
Trigger: {bearish_trigger}
Target 1: ${bearish_targets[0][0]} (-{bearish_targets[0][1]}%)
Target 2: ${bearish_targets[1][0]} (-{bearish_targets[1][1]}%)
Trade: {symbol} {bearish_targets[0][0]}P

**⏰ ACTION ITEM**
{action_item}
✅ Break = Bullish → ${bullish_targets[0][0]}
❌ Reject = Bearish → ${bearish_targets[0][0]}

**📱 Next Update: Market Open (9:30 AM ET)**"""

    # Send to Discord
    import subprocess
    subprocess.run(['python', 'send_discord.py', title, body])
```

---

## 📊 Format Variations

### **Quick Update Format:**
For rapid alerts during trading hours:
```
Title: "⚡ {SYMBOL} ALERT • ${PRICE}"

Body:
**LEVEL BREAK**
🔴 ${LEVEL} resistance BROKEN
🎯 Target: ${TARGET} (+{PERCENT}%)
⏰ Entry: NOW

Trade: {SYMBOL} {STRIKE}C
```

### **End of Day Format:**
For closing analysis:
```
Title: "📊 {SYMBOL} Daily Close • ${PRICE}"

Body:
**CLOSING PRICE**
Close: ${CLOSE} (+/-{CHANGE} / {PERCENT}%)
Range: ${LOW} - ${HIGH}
Volume: {VOLUME}M

**TOMORROW'S LEVELS**
Resistance: ${R1}, ${R2}
Support: ${S1}, ${S2}

**SETUP**
Watch for: {CONDITION}
Trade: {RECOMMENDATION}
```

---

## ✅ Best Practices

1. **Keep it scannable** - Use emojis and bold headers
2. **Be specific** - Exact prices, not ranges when possible
3. **Include context** - Why is this level important?
4. **Clear trades** - Exact strike and direction
5. **Action-oriented** - What should viewer do?
6. **Mobile-first** - Test on phone before sending
7. **Consistent format** - Use same template each time
8. **Percentages** - Always show % for targets
9. **Timestamps** - Include next update time
10. **Binary decisions** - Clear if/then scenarios

---

**Last Updated:** September 30, 2025
**Version:** 1.0 - Mobile-Optimized Line-by-Line Format
**Status:** ✅ APPROVED - Use this format for all Discord analysis
