@echo off
REM UNIFIED TRADING SYSTEM - WINDOWS LAUNCHER
REM No .py scripts needed - just run commands

if "%1"=="" (
    REM Default: Auto-analysis based on market time
    python seamless_market_system.py
) else if "%1"=="now" (
    python seamless_market_system.py
) else if "%1"=="monitor" (
    REM Continuous monitoring 30s
    python seamless_market_system.py monitor 30
) else if "%1"=="fast" (
    REM Fast monitoring 10s
    python seamless_market_system.py monitor 10
) else if "%1"=="stream" (
    REM Alias for monitor
    python seamless_market_system.py monitor 30
) else if "%1"=="auto" (
    REM Auto-launcher - waits for market open
    python market_open_auto_launcher.py
) else if "%1"=="health" (
    REM System health check
    python system_validation.py
) else if "%1"=="quick" (
    REM Quick snapshot
    python seamless_market_system.py quick
) else (
    echo UNIFIED TRADING SYSTEM
    echo =====================
    echo.
    echo USAGE:
    echo   trade              Auto-analysis (adapts to market time)
    echo   trade now          Current market analysis
    echo   trade monitor      Continuous updates (30s)
    echo   trade fast         Fast updates (10s)
    echo   trade stream       Streaming mode (30s)
    echo   trade auto         Auto-start at market open
    echo   trade health       System health check
    echo   trade quick        Quick snapshot
    echo.
)