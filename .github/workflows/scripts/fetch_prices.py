#!/usr/bin/env python3
"""
Fetch live prices from financial APIs
Used by GitHub Actions to auto-update prices.json daily
"""

import json
import sys
from datetime import datetime
import requests

def fetch_crypto(symbol):
    """Fetch crypto prices from CoinGecko (free, no auth)"""
    try:
        crypto_map = {'BTC': 'bitcoin'}
        crypto_id = crypto_map.get(symbol)
        if not crypto_id:
            return None
        
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={crypto_id}&vs_currencies=usd"
        response = requests.get(url, timeout=10)
        data = response.json()
        return data[crypto_id]['usd']
    except Exception as e:
        print(f"Error fetching {symbol}: {e}")
        return None

def fetch_stock_yahoo(ticker):
    """Fetch stock price from Yahoo Finance"""
    try:
        url = f"https://query2.finance.yahoo.com/v10/finance/quoteSummary/{ticker}?modules=price"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data['quoteSummary']['result'][0]['price']['regularMarketPrice']['raw']
    except Exception as e:
        print(f"Error fetching {ticker}: {e}")
    return None

def fetch_stock_finnhub(ticker):
    """Fetch stock price from Finnhub (free tier)"""
    try:
        url = f"https://finnhub.io/api/v1/quote?symbol={ticker}&token=demo"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data.get('c')
    except Exception as e:
        print(f"Error fetching {ticker}: {e}")
    return None

def fetch_stock(ticker):
    """Try multiple sources for stock prices"""
    sources = [fetch_stock_yahoo, fetch_stock_finnhub]
    
    for source in sources:
        try:
            price = source(ticker)
            if price and price > 0:
                return price
        except:
            continue
    
    return None

def main():
    holdings = {
        'MSTY': 'stock',
        'TSLY': 'stock',
        'MSTR': 'stock',
        'SWC': 'stock',
        'MPJPY': 'stock',
        'ASST': 'stock',
        'BTC': 'crypto',
        'STRD': 'stock',
        'STRK': 'stock',
        'STRC': 'stock',
        'SATA': 'stock',
    }
    
    prices = {}
    errors = []
    
    print(f"Fetching prices at {datetime.utcnow().isoformat()}Z\n")
    
    for ticker, asset_type in holdings.items():
        print(f"  {ticker}...", end=" ", flush=True)
        
        price = None
        if asset_type == 'crypto':
            price = fetch_crypto(ticker)
        else:
            price = fetch_stock(ticker)
        
        if price and price > 0:
            prices[ticker] = round(price, 2)
            print(f"✓ ${price:.2f}")
        else:
            errors.append(f"{ticker}: Could not fetch")
            print("✗")
    
    # Save to prices.json
    output = {
        "prices": prices,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "errors": errors
    }
    
    with open('prices.json', 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\n✓ Prices updated: {len(prices)}/{len(holdings)}")
    return 0 if len(prices) >= 8 else 1

if __name__ == '__main__':
    sys.exit(main())
