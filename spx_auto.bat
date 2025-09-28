@echo off
REM SPX Auto Analysis - One-Click Trading Interface
REM Runs complete market analysis with all enhanced systems

echo 🎯 SPX AUTO ANALYSIS - Starting...
echo =====================================

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found. Please install Python 3.8+
    pause
    exit /b 1
)

REM Run SPX Auto analysis
echo 📊 Running comprehensive analysis...
python spx_auto.py %*

REM Check if analysis was successful
if errorlevel 1 (
    echo ❌ Analysis failed. Check error messages above.
) else (
    echo ✅ Analysis completed successfully!
)

echo.
echo 📁 Results saved to .spx\auto_analysis_results.json
echo 💡 Run with "spx_auto.bat discord" to send alerts to Discord
echo.
pause