@echo off
echo SPX Market Open Test System
echo ===========================
echo.
echo This will run tomorrow at 9:30 AM ET and wait 10 minutes
echo Then generate 5 calls and 5 puts with Discord alerts
echo.
echo Starting scheduler...
python market_open_spx_test.py
pause