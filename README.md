# SPX 0DTE Trading System

Professional-grade SPX 0DTE options trading system with real-time alphavantage MCP integration and advanced probability-based position sizing.

## 🎯 Features

- **Real-time Market Data**: Alphavantage MCP integration for professional-grade data
- **Monte Carlo Analysis**: 50,000+ simulation option probability assessment
- **Advanced Position Sizing**: Kelly Criterion & coefficient management
- **Session Management**: Persistent context with `.spx/` directory structure
- **Risk Management**: Multi-factor probability-based protocols

## 📊 Key Components

### CLAUDE.md
Complete trading instructions and protocols:
- Alphavantage MCP data integration patterns
- SPX analysis shortcuts and commands
- Advanced position sizing with Kelly Criterion
- Risk management and coefficient targets
- Session management and context persistence

### Monte Carlo Analysis
- `monte_carlo_analysis.py`: Options probability assessment
- 4 volatility scenarios (Low/Base/High/Extreme)
- Win rate, expected value, and risk metrics
- Results saved to `.spx/monte_carlo_results.json`

### Session Management
- `.spx/session.json`: Current trading context
- `.spx/levels.json`: Key support/resistance levels  
- `.spx/notes.txt`: Timestamped trading notes
- `.spx/monte_carlo_summary.json`: Analysis results

## 🔧 Setup

1. **MCP Server Configuration**:
   ```bash
   claude mcp add -t http alphavantage https://mcp.alphavantage.co/mcp?apikey=YKNOT6EGFGF3T8D5
   ```

2. **Python Dependencies**:
   ```bash
   pip install numpy pandas scipy matplotlib
   ```

3. **Session Directory**:
   ```bash
   mkdir .spx
   ```

## 📈 Usage

### Core Analysis Commands
```bash
spx now              # Full analysis + auto-save context
spx structure        # Range/consolidation analysis
spx tactical         # Real-time execution
spx enhanced         # Institutional-grade analysis
```

### Monte Carlo Analysis
```bash
python monte_carlo_analysis.py
```

## 🎯 Position Sizing

Advanced probability-based sizing with:
- Kelly Criterion implementation (capped at 10%)
- Coefficient of Variation control (< 10.0)
- Beta management (portfolio beta < 1.0)
- Risk parity with probability weighting
- Dynamic probability adjustment

## 📊 Risk Management

**Coefficient Targets:**
- Kelly Fraction: < 0.10 (10% max)
- Coefficient of Variation: < 10.0
- Portfolio Beta: < 1.0
- Max Single Position: 5% of portfolio
- Risk Budget: 2-3% for 0DTE

## 🔄 Version Control

- **master**: Main development branch
- **claude-md-tracking**: Dedicated CLAUDE.md change tracking

Track CLAUDE.md changes over time:
```bash
git log --follow CLAUDE.md
git diff HEAD~1 CLAUDE.md  # Compare with previous version
```

## 📝 License

Private trading system - not for redistribution.

---
**⚠️ Risk Warning**: 0DTE options trading involves substantial risk of loss. Past performance does not guarantee future results.