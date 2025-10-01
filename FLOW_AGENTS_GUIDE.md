# Options Flow Analysis Agents System

**Specialized subagents for comprehensive options flow analysis with entry prices and ATR-based targets**

---

## 🎯 Agent Overview

Three specialized agents work together to provide complete options flow analysis:

### 1. **Flow Chart Reader**
**Agent:** `@flow-chart-reader`
**Purpose:** Extract ALL data from PDFs/images
**Output:** Complete structured flow data

### 2. **Flow Entry Analyzer**
**Agent:** `@flow-entry-analyzer`
**Purpose:** Calculate optimal entry prices using ATR
**Output:** Entry zones, ATR-based targets, stop losses

### 3. **Flow Risk Manager**
**Agent:** `@flow-risk-manager`
**Purpose:** Position sizing, risk limits, portfolio impact
**Output:** Approved position sizes, risk warnings

---

## 🚀 Quick Start

### Single-Agent Usage

**Extract data from flow PDF/image:**
```
@flow-chart-reader analyze this flow report [attach PDF/image]
```

**Get entry prices for specific ticker:**
```
@flow-entry-analyzer
BABA $220 calls bought, $5.1M premium, exp 11/21/25
What are the optimal entry prices and ATR targets?
```

**Calculate position sizing:**
```
@flow-risk-manager
Account: $25,000
BABA entry $167.50, stop $163.30
Calculate position size and risk
```

### Multi-Agent Workflow (Complete Analysis)

**Step 1: Extract Flow Data**
```
@flow-chart-reader
Please extract all flow data from this PDF and provide complete details
[attach flow PDF]
```

**Step 2: Get Entry Analysis for Top Plays**
```
@flow-entry-analyzer
Based on this extracted flow data, provide entry analysis for the top 3 bullish plays:
1. BABA $220 calls, $5.1M, exp 11/21/25
2. CRWV $150 calls, $4.0M, exp 12/20/25
3. SMCI $55 calls, $3.9M, exp 11/15/25
```

**Step 3: Risk Management**
```
@flow-risk-manager
Account size: $50,000
Please calculate position sizing for these three entries:
[paste entry analysis from step 2]
```

---

## 📊 Agent Capabilities

### Flow Chart Reader

**What it does:**
- ✅ Reads PDFs, PNGs, JPEGs, screenshots
- ✅ Extracts ticker, strike, expiration, premium, %OTM
- ✅ Calculates DTE (days to expiration)
- ✅ Identifies unusual sizes (whale trades)
- ✅ Flags earnings proximity
- ✅ Provides bullish/bearish bias summary

**Input:** Flow report PDF or image

**Output:**
```
📊 FLOW EXTRACTION RESULTS
Date: September 30, 2025
Total Entries: 43

🟢 CALLS BOUGHT (19)
1. BABA $220.00 | Exp: 11/21/25 (52 DTE)
   Premium: $5,100,000 (5.1M)
   Distance: 23% OTM
   Size: MASSIVE PREMIUM

[Complete extraction of all entries...]

🎯 KEY OBSERVATIONS
- Largest trade: BABA $220C - $5.1M
- Most active: Tech sector (12 trades)
- Bullish bias: 73%
```

### Flow Entry Analyzer

**What it does:**
- ✅ Calculates current price and ATR
- ✅ Identifies optimal entry zones (pullbacks/bounces)
- ✅ Sets ATR-based profit targets (1.5x, 2.5x, 4.0x ATR)
- ✅ Calculates stop losses (1.0x ATR)
- ✅ Analyzes support/resistance levels
- ✅ Provides R:R ratios

**Input:** Ticker, option details from flow

**Output:**
```
📊 ENTRY ANALYSIS: BABA

Current Price: $169.50
ATR (14-day): $4.20

🎯 OPTIMAL ENTRY PRICES:
Entry Zone: $166.80 - $168.50
Best Entry: $167.50 (EMA 21 bounce + support)
Entry Logic: Wait for pullback to EMA 21

📈 ATR-BASED TARGETS:
T1 (1.5 ATR): $173.80 | +3.8% | R:R 1.5:1
T2 (2.5 ATR): $178.00 | +6.3% | R:R 2.5:1
T3 (4.0 ATR): $184.30 | +10.0% | R:R 4.0:1

🛡️ RISK MANAGEMENT:
Stop Loss: $163.30 | -2.5%
Max Risk: 1-2% of account
```

### Flow Risk Manager

**What it does:**
- ✅ Calculates max position size for 1-2% account risk
- ✅ Estimates Greeks exposure (delta, gamma, theta, vega)
- ✅ Assesses portfolio heat and correlation
- ✅ Checks sector concentration limits
- ✅ Approves/rejects/reduces position sizes
- ✅ Provides scaling rules (partial exits at T1/T2/T3)

**Input:** Account size, entry, stop, ticker details

**Output:**
```
🛡️ RISK ANALYSIS: BABA

Account Size: $25,000
Risk Tolerance: 2% per trade

💰 POSITION SIZING
Max Contracts: 1 contract
Position Value: $16,750
Max Loss: $420 (1.68% of account) ✅

📊 GREEKS EXPOSURE
Delta: 0.45 | Directional exposure: Moderate
Theta: -$12/day | Time decay impact

⚠️ PORTFOLIO IMPACT
Current Heat: 3.2%
This Trade: 1.68%
Total Heat: 4.88% / 15% max ✅

✅ RISK APPROVAL
Final: APPROVED - 1 contract maximum
```

---

## 💡 Usage Patterns

### Pattern 1: Quick Entry Analysis
**Use when:** You see a ticker in flow and want fast entry prices

```
@flow-entry-analyzer
Quick analysis needed:
NVDA $180 calls, exp 11/15/25, $3M premium
```

### Pattern 2: Complete Flow Report
**Use when:** Daily flow PDF arrives

```
Step 1: @flow-chart-reader [attach PDF]
Step 2: @flow-entry-analyzer [paste top 5 tickers from step 1]
Step 3: @flow-risk-manager [paste entries + your account size]
```

### Pattern 3: Portfolio Check
**Use when:** Want to add new position to existing portfolio

```
@flow-risk-manager
Current positions:
- AAPL $180 calls (2% heat)
- MSFT $420 calls (1.5% heat)

New position:
- BABA $220 calls, entry $167.50, stop $163.30

Account: $50,000
Check correlation and total heat
```

### Pattern 4: Image Analysis
**Use when:** Screenshot of single trade

```
@flow-chart-reader
What are the details of this trade?
[attach screenshot]
```

---

## 🎯 ATR-Based Targeting System

### Why ATR?

ATR (Average True Range) measures volatility and provides realistic, achievable targets based on stock's actual movement.

**Benefits:**
- ✅ Scales with volatility (more volatile = wider targets)
- ✅ Avoids arbitrary round numbers
- ✅ Realistic based on stock behavior
- ✅ Adapts to market conditions

### Standard ATR Targets

| Target | ATR Multiplier | Typical R:R | Use Case |
|--------|----------------|-------------|-----------|
| T1 | 1.5× ATR | 1.5:1 | Quick profits, scale out 33% |
| T2 | 2.5× ATR | 2.5:1 | Primary target, scale out 33% |
| T3 | 4.0× ATR | 4.0:1 | Runner position, final 34% |
| Stop | 1.0× ATR | - | Max loss limit |

### Example Calculation

**Stock:** BABA
**Current Price:** $169.50
**ATR (14-day):** $4.20
**Entry:** $167.50

**Targets:**
- T1: $167.50 + (1.5 × $4.20) = $173.80
- T2: $167.50 + (2.5 × $4.20) = $178.00
- T3: $167.50 + (4.0 × $4.20) = $184.30
- Stop: $167.50 - (1.0 × $4.20) = $163.30

**Why these work:**
- BABA moves $4.20/day on average
- T1 is 1.5 days of movement (very achievable)
- T2 is 2.5 days of movement (normal swing)
- T3 is 4 days of movement (strong trend)

---

## 🔄 Integration with Existing System

### Combine with TA Engine

**Old way (basic flow):**
```bash
python flow.py "flow.pdf" --send
```

**New way (agents + TA):**
```
1. @flow-chart-reader [extract PDF data]
2. Run: python flow_enhanced.py "flow.pdf" --min-score 70
3. @flow-entry-analyzer [top TA-filtered plays from step 2]
4. @flow-risk-manager [calculate sizing]
```

### Agent + Python Hybrid

**Agents for:** Analysis, planning, entry calculation
**Python for:** Batch processing, Discord posting, automation

```bash
# Get agent analysis first
# Then format for Discord
python send_discord_multi.py "Entry Analysis" "[paste agent output]" alerts
```

---

## 📋 Complete Workflow Example

### Morning Flow Routine

**9:30 AM - Flow PDF arrives**

```
@flow-chart-reader
Extract all data from today's flow report
[attach flow PDF]
```

**9:35 AM - Identify best setups**

Run TA filter:
```bash
python flow_enhanced.py "flow.pdf" --min-score 75
```

**9:40 AM - Get entries for top plays**

```
@flow-entry-analyzer
Provide entry analysis for these high TA score plays:
1. BABA $220C (TA: 78)
2. CRWV $150C (TA: 82)
3. SMCI $55C (TA: 76)
```

**9:45 AM - Risk management**

```
@flow-risk-manager
Account: $100,000
Current heat: 8.5%

Check these three positions:
[paste entry analysis]
```

**9:50 AM - Execute approved trades**

Set alerts at entry zones from agent analysis

**Result:** Complete institutional-grade analysis in 20 minutes

---

## 🎪 Agent Advantages

### vs. Basic Flow Parser
| Feature | Basic Parser | With Agents |
|---------|-------------|-------------|
| Data extraction | ✅ | ✅ |
| Entry prices | ❌ | ✅ ATR-based |
| Profit targets | ❌ | ✅ T1/T2/T3 |
| Stop losses | ❌ | ✅ ATR-based |
| Position sizing | ❌ | ✅ Risk-calculated |
| Greeks analysis | ❌ | ✅ Full exposure |
| Portfolio impact | ❌ | ✅ Heat tracking |
| Risk approval | ❌ | ✅ Automated |

### vs. Manual Analysis
| Task | Manual Time | Agent Time |
|------|-------------|------------|
| Extract PDF | 10 min | 30 sec |
| Calculate ATR | 5 min | 10 sec |
| Find entry zones | 15 min | 20 sec |
| Set targets | 10 min | instant |
| Size position | 5 min | 15 sec |
| **Total** | **45 min** | **~2 min** |

---

## 🚨 Important Notes

### Agent Limitations

**Flow Chart Reader:**
- Requires clear, readable PDFs/images
- May struggle with handwritten notes
- Best with standard flow report formats

**Flow Entry Analyzer:**
- Needs AlphaVantage API for ATR/price data
- ATR targets assume normal market conditions
- Entry zones require discretion based on market structure

**Flow Risk Manager:**
- Assumes standard option pricing (100 shares/contract)
- Greeks are estimates without actual option chain data
- Portfolio heat requires you to track existing positions

### Best Practices

1. **Always verify agent output** - Especially price data
2. **Use discretion on entries** - Agents provide zones, you pick exact entry
3. **Monitor correlations** - Agent warns, but you track all positions
4. **Adjust for catalysts** - Agent doesn't know about surprise earnings
5. **Scale position sizes** - Use partial positions if uncertain

---

## 🔧 Advanced Customization

### Modify ATR Multipliers

Edit `flow-entry-analyzer.md` to change target multipliers:

```
Default:
T1 (1.5 ATR) | T2 (2.5 ATR) | T3 (4.0 ATR)

Aggressive:
T1 (1.0 ATR) | T2 (2.0 ATR) | T3 (3.0 ATR)

Conservative:
T1 (2.0 ATR) | T2 (3.5 ATR) | T3 (5.0 ATR)
```

### Adjust Risk Limits

Edit `flow-risk-manager.md` to change defaults:

```
Default: 1-2% risk per trade, 15% portfolio heat

Aggressive: 2-3% risk, 20% heat

Conservative: 0.5-1% risk, 10% heat
```

---

## 📚 Quick Reference

### Agent Invocation
```
@flow-chart-reader [for PDF/image extraction]
@flow-entry-analyzer [for entry prices + ATR targets]
@flow-risk-manager [for position sizing + risk]
```

### Common Commands
```bash
# Run TA filter first
python flow_enhanced.py "flow.pdf" --min-score 70

# Get agent analysis
@flow-entry-analyzer [top tickers from TA filter]

# Calculate sizing
@flow-risk-manager [with your account size]

# Send to Discord
python send_discord_multi.py "Analysis" "[agent output]" alerts
```

### File Locations
```
.claude/agents/
├── flow-chart-reader.md      # PDF/image extraction
├── flow-entry-analyzer.md     # Entry prices + ATR
└── flow-risk-manager.md       # Position sizing + risk

quant-alphavantage/
├── flow_enhanced.py           # TA-filtered flow
├── flow_ta_engine.py          # Technical analysis
└── FLOW_AGENTS_GUIDE.md       # This guide
```

---

**🤖 Powered by TraxterAI Agent System**

Each agent has its own context window and specialized expertise - no context pollution, maximum efficiency!

Last Updated: September 30, 2025
