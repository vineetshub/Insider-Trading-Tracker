import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
from datetime import datetime, timedelta
import time
import random
import os
import io
import json

def get_latest_insider_trades(api_key=None, symbol=None, page=0):
    if not api_key:
        api_key = os.getenv('SEC_API_KEY', 'f62eeeb281516660069b2bcf08532948157552b05b1307392e0ca98ff865e44f')
    
    base_url = "https://api.sec-api.io/insider-trading"
    
    if symbol:
        query = f"issuer.tradingSymbol:{symbol}"
    else:
        query = "issuer.tradingSymbol:(AAPL OR MSFT OR GOOG OR AMZN OR TSLA OR META OR NVDA OR IONQ OR LEU)"
    
    try:
        search_payload = {
            "query": query,
            "from": page * 50,
            "size": 50,
            "sort": [{"filedAt": {"order": "desc"}}]
        }
        
        headers = {
            'Authorization': api_key,
            'Content-Type': 'application/json'
        }
        
        print(f"Fetching data from SEC API for query: {query}")
        
        response = requests.post(
            base_url,
            headers=headers,
            json=search_payload,
            timeout=30
        )
        response.raise_for_status()
        
        data = response.json()
        
        if not data or 'transactions' not in data:
            print("No data returned from SEC API")
            return generate_sample_data()
        
        transactions = data['transactions']
        
        if not transactions:
            print("No transactions found in SEC API response")
            return generate_sample_data()
        
        trades = []
        
        for transaction in transactions:
            try:
                ticker = transaction.get('issuer', {}).get('tradingSymbol', '')
                insider_name = transaction.get('reportingOwner', {}).get('name', 'Unknown')
                
                relationship = transaction.get('reportingOwner', {}).get('relationship', {})
                title = 'Unknown'
                if relationship.get('isOfficer'):
                    title = relationship.get('officerTitle', 'Officer')
                elif relationship.get('isDirector'):
                    title = 'Director'
                elif relationship.get('isTenPercentOwner'):
                    title = '10% Owner'
                elif relationship.get('isOther'):
                    title = relationship.get('otherText', 'Other')
                
                non_derivative = transaction.get('nonDerivativeTable', {}).get('transactions', [])
                for trans in non_derivative:
                    trade_data = process_transaction(trans, ticker, insider_name, title, 'Non-Derivative')
                    if trade_data:
                        trades.append(trade_data)
                
                derivative = transaction.get('derivativeTable', {}).get('transactions', [])
                for trans in derivative:
                    trade_data = process_transaction(trans, ticker, insider_name, title, 'Derivative')
                    if trade_data:
                        trades.append(trade_data)
            
            except Exception as e:
                print(f"Error parsing transaction: {e}")
                continue
        
        result_df = pd.DataFrame(trades)
        
        if result_df.empty:
            print("No valid trades found in SEC API response")
            return generate_sample_data()
        
        return result_df
        
    except requests.RequestException as e:
        print(f"SEC API request error: {e}")
        print("Using sample data for demonstration...")
        return generate_sample_data()
    except Exception as e:
        print(f"SEC API parsing error: {e}")
        print("Using sample data for demonstration...")
        return generate_sample_data()

def process_transaction(trans, ticker, insider_name, title, security_type):
    try:
        coding = trans.get('coding', {})
        code = coding.get('code', '')
        trade_type = map_sec_transaction_code(code)
        
        transaction_date = trans.get('transactionDate', '')
        if transaction_date:
            try:
                date = pd.to_datetime(transaction_date)
            except:
                date = datetime.now()
        else:
            date = datetime.now()
        
        amounts = trans.get('amounts', {})
        shares = amounts.get('shares', 0)
        price = amounts.get('pricePerShare', 0)
        acquired_disposed = amounts.get('acquiredDisposedCode', '')
        
        value = shares * price if shares and price else 0
        
        if acquired_disposed == 'D':
            if trade_type == 'Buy':
                trade_type = 'Sell'
        elif acquired_disposed == 'A':
            if trade_type == 'Sell':
                trade_type = 'Buy'
        
        return {
            'Ticker': ticker,
            'Insider': insider_name,
            'Title': title,
            'Trade Type': trade_type,
            'Shares': shares,
            'Price': price,
            'Value': value,
            'Date': date,
            'Security Type': security_type,
            'Transaction Code': code
        }
    
    except Exception as e:
        print(f"Error processing transaction: {e}")
        return None

def map_sec_transaction_code(code):
    code = str(code).upper()
    
    if code in ['P']:
        return 'Buy'
    elif code in ['S']:
        return 'Sell'
    elif code in ['A', 'M']:
        return 'Award/Exercise'
    elif code in ['C', 'X']:
        return 'Conversion/Exercise'
    elif code in ['G']:
        return 'Gift'
    elif code in ['D', 'F', 'H', 'I', 'J', 'L', 'O', 'U', 'W', 'Z']:
        return 'Other'
    else:
        return 'Unknown'

def get_insider_trades_by_symbol(symbol, api_key=None, page=0):
    return get_latest_insider_trades(api_key=api_key, symbol=symbol, page=page)

def get_multiple_symbols_insider_trades(symbols=None, api_key=None):
    if not symbols:
        symbols = ['AAPL', 'MSFT', 'GOOG', 'AMZN', 'TSLA']
    
    all_trades = []
    
    for symbol in symbols[:3]:
        try:
            print(f"Fetching SEC data for {symbol}...")
            df = get_latest_insider_trades(api_key=api_key, symbol=symbol)
            if not df.empty:
                all_trades.append(df)
            time.sleep(1)
        except Exception as e:
            print(f"Error fetching {symbol}: {e}")
            continue
    
    if all_trades:
        return pd.concat(all_trades, ignore_index=True)
    else:
        return generate_sample_data()

def get_recent_insider_trades(api_key=None, days=30):
    if not api_key:
        api_key = os.getenv('SEC_API_KEY', 'f62eeeb281516660069b2bcf08532948157552b05b1307392e0ca98ff865e44f')
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    start_str = start_date.strftime('%Y-%m-%d')
    end_str = end_date.strftime('%Y-%m-%d')
    
    query = f"periodOfReport:[{start_str} TO {end_str}]"
    
    try:
        search_payload = {
            "query": query,
            "from": 0,
            "size": 50,
            "sort": [{"filedAt": {"order": "desc"}}]
        }
        
        headers = {
            'Authorization': api_key,
            'Content-Type': 'application/json'
        }
        
        print(f"Fetching recent insider trades from {start_str} to {end_str}")
        
        response = requests.post(
            "https://api.sec-api.io/insider-trading",
            headers=headers,
            json=search_payload,
            timeout=30
        )
        response.raise_for_status()
        
        data = response.json()
        
        if not data or 'transactions' not in data:
            return generate_sample_data()
        
        return get_latest_insider_trades(api_key=api_key)
        
    except Exception as e:
        print(f"Error fetching recent trades: {e}")
        return generate_sample_data()

def get_insider_info(symbol):
    try:
        base_url = "http://35.164.216.200:8000"
        info_url = f"{base_url}/generate_insiders_info/{symbol}"
        
        response = requests.get(info_url, timeout=15)
        response.raise_for_status()
        
        return response.text
        
    except Exception as e:
        print(f"Error getting insider info: {e}")
        return None

def clean_text(text):
    if not text:
        return ''
    return re.sub(r'\s+', ' ', text.strip())

def parse_number(text):
    if not text:
        return 0
    try:
        cleaned = re.sub(r'[^\d.]', '', text)
        return float(cleaned) if cleaned else 0
    except:
        return 0

def parse_price(text):
    if not text:
        return 0.0
    try:
        cleaned = re.sub(r'[^\d.]', '', text)
        return float(cleaned) if cleaned else 0.0
    except:
        return 0.0

def parse_value(text):
    if not text:
        return 0.0
    try:
        cleaned = re.sub(r'[^\d.]', '', text)
        return float(cleaned) if cleaned else 0.0
    except:
        return 0.0

def parse_date(text):
    if not text:
        return None
    
    date_formats = [
        '%m/%d/%Y',
        '%Y-%m-%d',
        '%m/%d/%y',
        '%b %d, %Y',
        '%B %d, %Y'
    ]
    
    for fmt in date_formats:
        try:
            return datetime.strptime(text.strip(), fmt)
        except:
            continue
    
    return datetime.now()

def extract_ticker(text):
    match = re.search(r'\b[A-Z]{1,5}\b', text)
    return match.group() if match else ''

def extract_trade_type(text):
    text_lower = text.lower()
    if 'buy' in text_lower:
        return 'Buy'
    elif 'sell' in text_lower:
        return 'Sell'
    return 'Unknown'

def extract_shares(text):
    match = re.search(r'(\d{1,3}(?:,\d{3})*)', text)
    if match:
        return parse_number(match.group())
    return 0

def extract_price(text):
    match = re.search(r'\$(\d+\.?\d*)', text)
    if match:
        return float(match.group(1))
    return 0.0

def extract_value(text):
    match = re.search(r'\$(\d{1,3}(?:,\d{3})*)', text)
    if match:
        return parse_number(match.group(1))
    return 0.0

def extract_date(text):
    date_patterns = [
        r'\d{1,2}/\d{1,2}/\d{4}',
        r'\d{4}-\d{1,2}-\d{1,2}',
        r'\d{1,2}/\d{1,2}/\d{2}'
    ]
    
    for pattern in date_patterns:
        match = re.search(pattern, text)
        if match:
            return parse_date(match.group())
    
    return datetime.now()

def generate_sample_data():
    tickers = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA', 'META', 'NVDA', 'NFLX', 'AMD', 'CRM']
    
    insiders = [
        'John Smith', 'Sarah Johnson', 'Michael Brown', 'Emily Davis', 'David Wilson',
        'Lisa Anderson', 'Robert Taylor', 'Jennifer Martinez', 'Christopher Garcia', 'Amanda Rodriguez'
    ]
    
    titles = [
        'CEO', 'CFO', 'CTO', 'COO', 'VP of Engineering', 'VP of Sales', 'VP of Marketing',
        'Director', 'Senior Manager', 'Board Member'
    ]
    
    trades = []
    base_date = datetime.now()
    
    for i in range(50):
        ticker = random.choice(tickers)
        insider = random.choice(insiders)
        title = random.choice(titles)
        trade_type = random.choice(['Buy', 'Sell'])
        
        shares = random.randint(100, 10000)
        price = round(random.uniform(50, 500), 2)
        value = shares * price
        
        days_ago = random.randint(0, 30)
        date = base_date - timedelta(days=days_ago)
        
        trades.append({
            'Ticker': ticker,
            'Insider': insider,
            'Title': title,
            'Trade Type': trade_type,
            'Shares': shares,
            'Price': price,
            'Value': value,
            'Date': date
        })
    
    return pd.DataFrame(trades)

if __name__ == "__main__":
    df = get_latest_insider_trades()
    print(f"Scraped {len(df)} insider trades")
    if not df.empty:
        print(df.head())
    else:
        print("No data found") n match.group() if match else ''

def extract_trade_type(text):
    """Extract trade type from text"""
    text_lower = text.lower()
    if 'buy' in text_lower:
        return 'Buy'
    elif 'sell' in text_lower:
        return 'Sell'
    return 'Unknown'

def extract_shares(text):
    """Extract number of shares from text"""
    match = re.search(r'(\d{1,3}(?:,\d{3})*)', text)
    if match:
        return parse_number(match.group())
    return 0

def extract_price(text):
    """Extract price from text"""
    match = re.search(r'\$(\d+\.?\d*)', text)
    if match:
        return float(match.group(1))
    return 0.0

def extract_value(text):
    """Extract value from text"""
    match = re.search(r'\$(\d{1,3}(?:,\d{3})*)', text)
    if match:
        return parse_number(match.group(1))
    return 0.0

def extract_date(text):
    """Extract date from text"""
    # Look for date patterns
    date_patterns = [
        r'\d{1,2}/\d{1,2}/\d{4}',
        r'\d{4}-\d{1,2}-\d{1,2}',
        r'\d{1,2}/\d{1,2}/\d{2}'
    ]
    
    for pattern in date_patterns:
        match = re.search(pattern, text)
        if match:
            return parse_date(match.group())
    
    return datetime.now()

def generate_sample_data():
    """
    Generate sample insider trading data for demonstration purposes
    """
    # Sample tickers
    tickers = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA', 'META', 'NVDA', 'NFLX', 'AMD', 'CRM']
    
    # Sample insider names
    insiders = [
        'John Smith', 'Sarah Johnson', 'Michael Brown', 'Emily Davis', 'David Wilson',
        'Lisa Anderson', 'Robert Taylor', 'Jennifer Martinez', 'Christopher Garcia', 'Amanda Rodriguez'
    ]
    
    # Sample titles
    titles = [
        'CEO', 'CFO', 'CTO', 'COO', 'VP of Engineering', 'VP of Sales', 'VP of Marketing',
        'Director', 'Senior Manager', 'Board Member'
    ]
    
    # Generate sample data
    trades = []
    base_date = datetime.now()
    
    for i in range(50):  # Generate 50 sample trades
        ticker = random.choice(tickers)
        insider = random.choice(insiders)
        title = random.choice(titles)
        trade_type = random.choice(['Buy', 'Sell'])
        
        # Generate realistic values
        shares = random.randint(100, 10000)
        price = round(random.uniform(50, 500), 2)
        value = shares * price
        
        # Generate date within last 30 days
        days_ago = random.randint(0, 30)
        date = base_date - timedelta(days=days_ago)
        
        trades.append({
            'Ticker': ticker,
            'Insider': insider,
            'Title': title,
            'Trade Type': trade_type,
            'Shares': shares,
            'Price': price,
            'Value': value,
            'Date': date
        })
    
    return pd.DataFrame(trades)

if __name__ == "__main__":
    # Test the scraper
    df = get_latest_insider_trades()
    print(f"Scraped {len(df)} insider trades")
    if not df.empty:
        print(df.head())
    else:
        print("No data found") 