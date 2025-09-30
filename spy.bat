@echo off
cd /d "C:\Users\traxt\quant-alphavantage"
python -c "
import requests
try:
    r = requests.get('https://query1.finance.yahoo.com/v8/finance/chart/SPY', timeout=2)
    price = r.json()['chart']['result'][0]['meta']['regularMarketPrice']
    print(f'SPY: ${price:.2f} | SPX: ${price*10:.0f}')
except:
    print('SPY: Data unavailable')
"