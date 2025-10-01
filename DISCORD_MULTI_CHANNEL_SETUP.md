# Discord Multi-Channel Setup Guide

## 📱 Quick Start

You now have a multi-channel Discord system! Here's how to use it:

### **Basic Usage:**
```bash
# Send to default channel (alerts)
python send_discord_multi.py "Title" "Message"

# Send to specific channel
python send_discord_multi.py "Title" "Message" alerts
python send_discord_multi.py "Title" "Message" performance
python send_discord_multi.py "Title" "Message" research
python send_discord_multi.py "Title" "Message" system
```

---

## 🔧 Setup Instructions

### **Step 1: Create Discord Webhooks**

For each channel you want to use, create a webhook in Discord:

1. Go to your Discord server
2. Right-click the channel (e.g., #trading-performance)
3. Click "Edit Channel" → "Integrations" → "Webhooks"
4. Click "New Webhook"
5. Copy the webhook URL

### **Step 2: Update Configuration**

Edit `discord_config.json` and replace the placeholder webhooks:

```json
{
  "channels": {
    "alerts": {
      "webhook": "YOUR_CURRENT_WEBHOOK_HERE",
      "description": "Main trading alerts and market updates",
      "username": "Trading Monitor Bot"
    },
    "performance": {
      "webhook": "PASTE_PERFORMANCE_WEBHOOK_HERE",
      "description": "Trade performance, P&L, analytics",
      "username": "Performance Tracker"
    },
    "research": {
      "webhook": "PASTE_RESEARCH_WEBHOOK_HERE",
      "description": "Market research, backtest results, strategy optimization",
      "username": "Research Bot"
    },
    "system": {
      "webhook": "PASTE_SYSTEM_WEBHOOK_HERE",
      "description": "System status, errors, testing results",
      "username": "System Monitor"
    }
  },
  "default_channel": "alerts"
}
```

---

## 📊 Channel Recommendations

### **#trading-alerts** (alerts channel)
- Real-time SPX/SPY/QQQ/IWM/NDX price alerts
- VIX regime changes
- Volume surge detection
- Correlation breakdowns
- Trading signal generation

**Color Coding:**
- 🔴 Red: Critical alerts, bearish signals
- 🟢 Green: Bullish signals, buy opportunities
- 🟡 Yellow: Neutral, consider positions
- 🔵 Blue: General market updates

### **#trading-performance** (performance channel)
- Trade execution confirmations
- Profit/loss updates
- Daily/weekly/monthly performance summaries
- Win rate tracking
- Strategy effectiveness metrics

**Color Coding:**
- 🟢 Green: Profitable trades, wins
- 🔴 Red: Losing trades, losses
- 🔵 Blue: Neutral performance updates

### **#market-research** (research channel)
- Backtest results
- Strategy optimization reports
- Historical analysis
- Pattern recognition findings
- Correlation studies

**Color Coding:**
- 🟣 Purple: Research reports
- 🔵 Blue: Analysis results

### **#system-status** (system channel)
- System startup/shutdown
- Error notifications
- Test results
- Component status updates
- API health checks

**Color Coding:**
- 🟢 Green: Success, operational
- 🟡 Yellow: Warnings
- 🔴 Red: Errors, failures

---

## 💡 Usage Examples

### **Trading Alerts:**
```bash
python send_discord_multi.py "🚨 SPX Breakout" "SPX broke above 6680 resistance with volume confirmation" alerts
```

### **Performance Updates:**
```bash
python send_discord_multi.py "✅ Trade Closed - PROFIT" "SPY 665C closed at +125% gain" performance
```

### **Research Results:**
```bash
python send_discord_multi.py "📊 September Backtest Complete" "Strategy optimization: 37.5% win rate, 25 combinations tested" research
```

### **System Status:**
```bash
python send_discord_multi.py "✅ System Testing Complete" "All 5 components validated - zero errors" system
```

---

## 🔄 Integration with Existing Scripts

Update your scripts to use the new multi-channel system:

```python
import subprocess

# Send to alerts channel (trading signals)
subprocess.run([
    'python', 'send_discord_multi.py',
    'SPX Alert', 'Current: $6651.20',
    'alerts'
])

# Send to performance channel (trade results)
subprocess.run([
    'python', 'send_discord_multi.py',
    'Trade Closed', 'Profit: +$1,250',
    'performance'
])

# Send to research channel (backtest results)
subprocess.run([
    'python', 'send_discord_multi.py',
    'Backtest Complete', 'Win rate: 75%',
    'research'
])

# Send to system channel (errors/status)
subprocess.run([
    'python', 'send_discord_multi.py',
    'System Ready', 'All tests passed',
    'system'
])
```

---

## 🎯 Automatic Channel Selection

The system automatically:
- Routes trading alerts to `alerts` channel by default
- Uses color coding based on message type and channel
- Includes channel name in footer for clarity
- Falls back to default channel if webhook not configured
- Validates channel names before sending

---

## 🔒 Security Notes

- Keep `discord_config.json` private (don't commit to public repos)
- Each webhook can be revoked independently if compromised
- Different webhooks allow granular permission control
- Consider separate servers for production vs testing

---

## 📈 Future Enhancements

Planned features:
- Priority-based routing (critical → alerts, info → system)
- Message templates by channel type
- Rate limiting per channel
- Channel-specific retry logic
- Webhook health monitoring

---

**Created:** September 30, 2025
**Status:** Production Ready
**Compatibility:** Backward compatible with send_discord.py

🤖 Powered by TraxterAI
