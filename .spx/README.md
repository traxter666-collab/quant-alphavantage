# Session Management Directory

This directory contains session persistence and analysis results for the Four-Asset Trading System.

## Directory Structure

```
.spx/
├── session.json              # Current session context and state
├── levels.json               # Key support/resistance levels
├── performance_log.json      # Trading performance tracking
├── system_health_report.json # Latest system health results
├── iwm_analysis_results.json # IWM (Russell 2000) analysis
├── spy_analysis_results.json # SPY (S&P 500 ETF) analysis
├── qqq_analysis_results.json # QQQ (Nasdaq ETF) analysis
├── multi_asset_results.json  # Combined multi-asset analysis
└── unified_analysis.json     # Unified system analysis results
```

## File Purposes

- **session.json**: Maintains trading session context across conversation resets
- **levels.json**: Preserves critical support/resistance levels for continuity
- **performance_log.json**: Tracks system performance and accuracy metrics
- **analysis_results.json**: Latest analysis for each asset (SPX, SPY, QQQ, IWM)
- **system_health_report.json**: 100% system health achievement tracking

## Session Recovery

The system automatically saves and restores context from this directory to maintain:
- Trading session continuity
- Key market levels
- System performance metrics
- Analysis results history
- Risk management parameters

## Data Persistence

All analysis results are automatically saved to ensure no loss of critical trading information between sessions or system restarts.