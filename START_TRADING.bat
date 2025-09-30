@echo off
REM ===================================================================
REM AUTOMATED TRADING SYSTEM LAUNCHER
REM Double-click this file to start the fully automated trading system
REM ===================================================================

echo.
echo ====================================================================
echo   AUTOMATED TRADING SYSTEM - STARTING
echo ====================================================================
echo.
echo   This will start the fully automated trading system:
echo.
echo   - Monitors SPX, SPY, QQQ, IWM, NDX automatically
echo   - Auto-starts at market open (9:30 AM ET)
echo   - Auto-stops at market close (4:00 PM ET)
echo   - Discord alerts for all trade setups
echo   - Auto-restart on crashes
echo   - Daily closing analysis
echo.
echo   Press Ctrl+C to stop the system
echo.
echo ====================================================================
echo.

cd /d "%~dp0"
python auto_trading_system.py

pause
