# Discord Options Flow Analysis Template

**PURPOSE:** Mobile-optimized format for options flow analysis with clean, readable strike prices and formatting.

---

## **Template Structure:**

```
📊 INSTITUTIONAL OPTIONS FLOW (Date)

**XX CALLS BOUGHT | XX PUTS SOLD | XX PUTS BOUGHT | XX CALLS SOLD**

━━━━━━━━━━━━━━━━━━━━━━━━━━━
🟢 **TOP BULLISH PLAYS**
━━━━━━━━━━━━━━━━━━━━━━━━━━━

**#1 TICKER - CONVICTION LEVEL**
Calls Bought: $XXX strike
Expiration: MM/DD/YY
Premium: $X.XM
Distance: +X% OTM
Strategy: $XXX/$XXX call spread
Win Rate: XX%

**#2 TICKER - DESCRIPTOR**
Calls Bought: $XXX strike
Expiration: MM/DD/YY
Premium: $X.XM
Distance: +X% OTM
Strategy: $XXX/$XXX call spread
Win Rate: XX%

━━━━━━━━━━━━━━━━━━━━━━━━━━━
🛡️ **BULLISH PUTS SOLD**
━━━━━━━━━━━━━━━━━━━━━━━━━━━

**#X TICKER - IMPLICATION**
Puts Sold: $XXX strike
Expiration: MM/DD/YY
Premium: $X.XM
Distance: -X% OTM
Implication: $XXX is institutional floor
Action: STAY BULLISH above $XXX

━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔴 **BEARISH WARNINGS**
━━━━━━━━━━━━━━━━━━━━━━━━━━━

**#X TICKER - WARNING TYPE 🚨**
Puts Bought: $XXX strike
Expiration: MM/DD/YY
Premium: $X.XM
Distance: -X% OTM
Warning: ACTION TO AVOID
Risk: RISK DESCRIPTION

━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 **BEST TRADES RANKED**
━━━━━━━━━━━━━━━━━━━━━━━━━━━

1️⃣ TICKER $XXX/$XXX Exp Calls (XX% win)
2️⃣ TICKER $XXX/$XXX Exp Calls (XX% win)
3️⃣ TICKER $XXX/$XXX Exp Calls (XX% win)
4️⃣ TICKER $XXX/$XXX Exp Calls (XX% win)
5️⃣ TICKER $XXX/$XXX Exp Calls (XX% win)

━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️ **DO NOT TRADE**
━━━━━━━━━━━━━━━━━━━━━━━━━━━

❌ TICKER - $X.XM puts bought
❌ TICKER - $X.XM puts bought
❌ TICKER - $X.XM calls SOLD
❌ TICKER - $X.XM calls SOLD

━━━━━━━━━━━━━━━━━━━━━━━━━━━
💡 **QUICK REFERENCE**
━━━━━━━━━━━━━━━━━━━━━━━━━━━

**URGENT (Expires Soon):**
TICKER - MM/DD/YY (X days)
TICKER - MM/DD/YY (X days)

**High Premium (>$XM):**
TICKER: $X.XM
TICKER: $X.XM
TICKER: $X.XM

**Position Sizing:**
1-2% per trade
Enter on pullbacks
Exit at 50-100% profit
30 days before expiration

🤖 Powered by TraxterAI
```

---

## **Formatting Rules:**

### **Strike Prices:**
✅ CORRECT: "Calls Bought: $220 strike"
✅ CORRECT: "Puts Sold: $730 strike"
❌ WRONG: "$220 Calls" (confusing on mobile)
❌ WRONG: "220.00 (23%)" (numbers run together)

### **Line Breaks:**
- Use `━━━━━━━━━` separator between sections
- Blank line after each ticker analysis
- Group related info together (strike, exp, premium, strategy)

### **Labels:**
- **Calls Bought:** for bullish call buying
- **Puts Sold:** for bullish put selling (support level)
- **Puts Bought:** for bearish put buying (hedging)
- **Calls Sold:** for bearish call selling

### **Distance Labels:**
- **+X% OTM** for out-of-the-money (needs price to move UP)
- **-X% OTM** for out-of-the-money (strike BELOW current price)
- **ATM** for at-the-money

### **Premium Format:**
- **$5.1M** for millions
- **$644K** for thousands
- Always include M or K suffix

### **Win Rate Format:**
- **Win Rate: 72%** on separate line
- Always include percentage sign
- Round to whole numbers

### **Expiration Format:**
- **Expiration: 11/21/25** (MM/DD/YY)
- Include urgency note if <14 days

---

## **Color Coding (Discord Embeds):**

### **Green (Bullish):**
- Calls bought
- Puts sold (support)
- Win rates >70%

### **Red (Bearish):**
- Puts bought (hedging)
- Calls sold
- Warning signals

### **Yellow (Neutral):**
- Consider/standby signals
- Mixed signals

### **Blue (Default):**
- General information
- Quick reference sections

---

## **Mobile Optimization:**

### **DO:**
✅ Use line breaks between each data point
✅ Keep lines under 40 characters when possible
✅ Use emojis sparingly for visual breaks
✅ Bold key information
✅ Use separators between sections

### **DON'T:**
❌ Cram multiple data points on one line
❌ Use complex tables (they break on mobile)
❌ Write long paragraphs (use bullets)
❌ Use special characters that don't render
❌ Mix strike price with percentage in same field

---

## **Priority Sorting:**

1. **Highest Premium First** (largest institutional bets)
2. **Highest Win Rate** (most confident plays)
3. **Urgency** (soonest expiration)
4. **Concentration** (most activity in single name)

---

## **Quick Command Reference:**

```bash
# Send options flow analysis
python send_discord.py "🔥 Options Flow - CLEAN FORMAT" "[FORMATTED CONTENT]"

# Send to specific channel
python send_discord_multi.py "🔥 Options Flow" "[CONTENT]" alerts
python send_discord_multi.py "📊 Research" "[CONTENT]" research
```

---

## **Example Usage:**

### **Single Trade Format:**
```
**#1 BABA - HIGHEST CONVICTION**
Calls Bought: $220 strike
Expiration: 11/21/25
Premium: $5.1M (LARGEST)
Distance: +23% OTM
Strategy: $190/$220 call spread
Win Rate: 70%
```

### **Puts Sold (Bullish) Format:**
```
**#5 META - FLOOR PROTECTION**
Puts Sold: $730 strike
Expiration: 10/31/25
Premium: $16.9M (MASSIVE)
Distance: -1% OTM
Implication: $730 is institutional floor
Action: STAY BULLISH above $730
```

### **Warning Format:**
```
**#8 GOOG - MASSIVE HEDGING 🚨**
Puts Bought: $230 strike
Expiration: 3/20/26
Premium: $13.9M (LARGEST PUT)
Distance: -6% OTM
Warning: AVOID ALL BULLISH GOOG TRADES
Risk: Major institutional fear
```

---

## **Testing Checklist:**

Before sending, verify:
- [ ] All strike prices visible and clear
- [ ] Expiration dates formatted correctly
- [ ] Premium amounts include M or K
- [ ] Win rates included where applicable
- [ ] Sections separated with dividers
- [ ] Mobile-friendly (test on phone preview)
- [ ] No text cutoff or overflow
- [ ] Emojis render correctly
- [ ] Footer includes TraxterAI branding

---

**Last Updated:** September 30, 2025
**Status:** Production Template - Mobile Optimized
**Use For:** Options flow analysis, unusual activity alerts, daily flow summaries

🤖 Powered by TraxterAI
