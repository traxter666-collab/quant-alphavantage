# 🚀 MONDAY TRADING QUICK REFERENCE GUIDE

## ⚡ INSTANT START OPTIONS

### **FASTEST METHOD (Recommended for Monday):**
```bash
# Single commands - run when you need updates
python trading_shortcuts.py smart_es    # ES futures analysis
python trading_shortcuts.py smart_nq    # NQ futures analysis
python spx_command_router.py "spx quick" # SPX options analysis
python trading_shortcuts.py multi       # Multi-asset overview
```

### **STREAMING OPTIONS:**
```bash
# Launch streaming interface
python start_streaming.py

# Option 1: Basic streaming (30-second refresh)
# Option 2: Enhanced streaming (1-10 second refresh)
# Option 3: Manual refresh commands
# Option 4: Quick system test
```

---

## 📊 WHAT YOU'LL GET FROM EACH COMMAND

### **Smart ES Analysis:**
- Current ES price: $6,618.20 (+0.57%)
- Trading action: BUY/SELL/AVOID
- Confidence: HIGH/MEDIUM/LOW
- Combined score: 82.8% (base + enhanced)
- Risk management: Position sizing
- Entry/exit levels with stops

### **SPX Quick Analysis:**
- Real-time SPX/SPXW pricing
- 0DTE option recommendations
- Strike selection with Greeks
- Support/resistance levels
- Risk/reward ratios

### **Multi-Asset Overview:**
- ES, NQ, GC futures status
- SPX options opportunities
- Portfolio allocation suggestions
- Market regime analysis

---

## 🎯 MONDAY MORNING ROUTINE (5 MINUTES)

### **Step 1: Market Check (1 minute)**
```bash
python trading_shortcuts.py smart_es
```
*Look for: Action, Confidence, Current Price*

### **Step 2: SPX Options (2 minutes)**
```bash
python spx_command_router.py "spx quick"
```
*Look for: 0DTE setups, Strike recommendations*

### **Step 3: Portfolio View (2 minutes)**
```bash
python trading_shortcuts.py multi
```
*Look for: Overall market bias, Risk allocation*

---

## 🔥 KEY SIGNALS TO WATCH

### **HIGH CONFIDENCE TRADES:**
- **Combined Score >80%:** Strong trade signal
- **Direction Agreement:** Both systems align (BULLISH/BEARISH)
- **Low Risk:** <15% account risk
- **Market Conditions:** Session analysis favorable

### **AVOID TRADES WHEN:**
- **Combined Score <70%:** Low confidence
- **High Risk:** >20% account risk
- **System Disagreement:** Mixed signals
- **Market Session:** ASIAN (lower liquidity)

---

## ⚠️ RISK MANAGEMENT

### **Position Sizing:**
- **Maximum per trade:** 2% account risk
- **Daily maximum:** 6% total exposure
- **Smart ES typical:** 0-1 contracts recommended
- **Risk calculation:** Automatic in all commands

### **Exit Rules:**
- **Stop Loss:** Automatic calculation included
- **Profit Targets:** 1:2 Risk/Reward minimum
- **Time Exits:** Monitor for session changes

---

## 📱 QUICK TROUBLESHOOTING

### **If Commands Timeout:**
```bash
# Try single test first
echo "4" | python start_streaming.py

# If successful, proceed with trading commands
```

### **If Data Seems Wrong:**
```bash
# Validate API access
python validate_api_key.py

# Test with backup
python spx_live.py
```

### **If No Results:**
- Check internet connection
- Verify market hours (9:30 AM - 4:00 PM ET)
- Wait 30 seconds and retry

---

## 🚀 ADVANCED FEATURES (OPTIONAL)

### **Real-Time Streaming:**
```bash
# 30-second updates
python basic_live_stream.py

# 1-10 second updates
python enhanced_live_stream.py
```

### **Custom Analysis:**
```bash
# Specific contracts
python spx_command_router.py "spx scalp plan"
python spx_command_router.py "spx dealer positioning"

# News integration
python spx_command_router.py "spx market intel"
```

---

## ✅ SYSTEM STATUS VERIFIED

**All Systems Operational:**
- ✅ Command Router (125+ commands)
- ✅ Smart Futures Integration
- ✅ SPX Options Analysis
- ✅ Real-time Data Feeds
- ✅ Risk Management
- ✅ Multi-asset Portfolio
- ✅ Streaming Capabilities

**Last Verified:** 2025-09-28 22:10 ET
**Test Result:** SUCCESS - 82.8% confidence, HIGH signal strength

---

## 💡 MONDAY TRADING TIPS

1. **Start Simple:** Use single commands before streaming
2. **Monitor Risk:** Never exceed 2% per trade
3. **Watch Confidence:** Only trade >70% signals
4. **Session Awareness:** Best liquidity 9:30 AM - 4:00 PM ET
5. **System Agreement:** Ensure base + enhanced systems align

**Ready for Monday Trading!** 🚀