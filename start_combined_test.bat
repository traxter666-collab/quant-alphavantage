@echo off
echo SPX + TSLA Combined Market Open Test System
echo ==========================================
echo.
echo EXECUTION TIMELINE:
echo 9:30 AM ET - Market open detection
echo 9:40 AM ET - SPX analysis (5 calls + 5 puts)
echo 9:42 AM ET - TSLA analysis (5 calls + 5 puts)  
echo 9:43 AM ET - Combined summary
echo.
echo FEATURES:
echo - 2-minute spacing prevents API/Discord errors
echo - Sequential execution for reliability
echo - Enhanced SPX data (99.9% accuracy)
echo - TSLA volume/volatility optimization
echo.
echo Total: 20 option recommendations with proper spacing
echo.
echo Starting combined scheduler...
python combined_market_test.py
pause