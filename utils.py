import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import re

def create_buy_sell_chart(df):
    if df.empty:
        return go.Figure().add_annotation(
            text="No data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
    
    trade_summary = df.groupby('Trade Type')['Value'].sum().reset_index()
    
    fig = px.bar(
        trade_summary,
        x='Trade Type',
        y='Value',
        color='Trade Type',
        color_discrete_map={'Buy': '#00ff88', 'Sell': '#ff6b6b'},
        title='Total Buy vs Sell Value',
        labels={'Value': 'Total Value ($)', 'Trade Type': 'Trade Type'}
    )
    
    fig.update_layout(
        xaxis_title="Trade Type",
        yaxis_title="Total Value ($)",
        showlegend=False,
        height=400,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#e0e0e0'),
        title_font_color='#00d4ff'
    )
    
    fig.update_yaxes(tickformat=",.0f", gridcolor='rgba(0,212,255,0.1)')
    fig.update_xaxes(gridcolor='rgba(0,212,255,0.1)')
    
    return fig

def create_volume_chart(df):
    if df.empty:
        return go.Figure().add_annotation(
            text="No data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
    
    daily_volume = df.groupby(df['Date'].dt.date)['Value'].sum().reset_index()
    daily_volume['Date'] = pd.to_datetime(daily_volume['Date'])
    
    fig = px.line(
        daily_volume,
        x='Date',
        y='Value',
        title='Insider Trading Volume Over Time',
        labels={'Value': 'Total Value ($)', 'Date': 'Date'}
    )
    
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Total Value ($)",
        height=400,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#e0e0e0'),
        title_font_color='#00d4ff'
    )
    
    fig.update_yaxes(tickformat=",.0f", gridcolor='rgba(0,212,255,0.1)')
    fig.update_xaxes(gridcolor='rgba(0,212,255,0.1)')
    
    return fig

def create_ticker_chart(df):
    if df.empty:
        return go.Figure().add_annotation(
            text="No data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
    
    ticker_volume = df.groupby('Ticker')['Value'].sum().sort_values(ascending=False).head(10).reset_index()
    
    fig = px.bar(
        ticker_volume,
        x='Ticker',
        y='Value',
        title='Top 10 Tickers by Trading Volume',
        labels={'Value': 'Total Value ($)', 'Ticker': 'Ticker Symbol'}
    )
    
    fig.update_layout(
        xaxis_title="Ticker Symbol",
        yaxis_title="Total Value ($)",
        height=400,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#e0e0e0'),
        title_font_color='#00d4ff'
    )
    
    fig.update_yaxes(tickformat=",.0f", gridcolor='rgba(0,212,255,0.1)')
    fig.update_xaxes(gridcolor='rgba(0,212,255,0.1)')
    
    return fig

def create_trade_type_distribution(df):
    if df.empty:
        return go.Figure().add_annotation(
            text="No data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
    
    trade_counts = df['Trade Type'].value_counts().reset_index()
    trade_counts.columns = ['Trade Type', 'Count']
    
    fig = px.pie(
        trade_counts,
        values='Count',
        names='Trade Type',
        title='Distribution of Buy vs Sell Trades',
        color_discrete_map={'Buy': '#00ff88', 'Sell': '#ff6b6b'}
    )
    
    fig.update_layout(
        height=400,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#e0e0e0'),
        title_font_color='#00d4ff'
    )
    
    return fig

def format_currency(value):
    if pd.isna(value) or value == 0:
        return "$0"
    
    if value >= 1e9:
        return f"${value/1e9:.2f}B"
    elif value >= 1e6:
        return f"${value/1e6:.2f}M"
    elif value >= 1e3:
        return f"${value/1e3:.2f}K"
    else:
        return f"${value:,.0f}"

def format_number(value):
    if pd.isna(value):
        return "0"
    return f"{value:,.0f}"

def parse_date_string(date_str):
    if not date_str:
        return None
    
    date_formats = [
        '%m/%d/%Y',
        '%Y-%m-%d',
        '%m/%d/%y',
        '%b %d, %Y',
        '%B %d, %Y',
        '%Y-%m-%d %H:%M:%S',
        '%m/%d/%Y %H:%M:%S'
    ]
    
    for fmt in date_formats:
        try:
            return datetime.strptime(date_str.strip(), fmt)
        except:
            continue
    
    return None

def clean_ticker(ticker):
    if not ticker:
        return ''
    
    cleaned = ticker.strip().upper()
    cleaned = re.sub(r'[^A-Z]', '', cleaned)
    return cleaned[:5]

def validate_trade_data(row):
    required_fields = ['Ticker', 'Trade Type', 'Shares', 'Price', 'Value', 'Date']
    
    for field in required_fields:
        if field not in row or pd.isna(row[field]):
            return False
    
    if row['Trade Type'] not in ['Buy', 'Sell']:
        return False
    
    try:
        float(row['Shares'])
        float(row['Price'])
        float(row['Value'])
    except:
        return False
    
    return True

def get_date_range(df, days=30):
    if df.empty:
        return datetime.now() - timedelta(days=days), datetime.now()
    
    min_date = df['Date'].min()
    max_date = df['Date'].max()
    
    if (max_date - min_date).days > days:
        min_date = max_date - timedelta(days=days)
    
    return min_date, max_date

def calculate_statistics(df):
    if df.empty:
        return {}
    
    stats = {
        'total_trades': len(df),
        'total_value': df['Value'].sum(),
        'avg_trade_value': df['Value'].mean(),
        'buy_trades': len(df[df['Trade Type'] == 'Buy']),
        'sell_trades': len(df[df['Trade Type'] == 'Sell']),
        'buy_value': df[df['Trade Type'] == 'Buy']['Value'].sum(),
        'sell_value': df[df['Trade Type'] == 'Sell']['Value'].sum(),
        'unique_tickers': df['Ticker'].nunique(),
        'date_range': f"{df['Date'].min().strftime('%Y-%m-%d')} to {df['Date'].max().strftime('%Y-%m-%d')}"
    }
    
    return stats

def filter_data(df, tickers=None, trade_types=None, start_date=None, end_date=None):
    filtered_df = df.copy()
    
    if tickers and 'All' not in tickers:
        filtered_df = filtered_df[filtered_df['Ticker'].isin(tickers)]
    
    if trade_types and 'All' not in trade_types:
        filtered_df = filtered_df[filtered_df['Trade Type'].isin(trade_types)]
    
    if start_date:
        filtered_df = filtered_df[filtered_df['Date'].dt.date >= start_date]
    
    if end_date:
        filtered_df = filtered_df[filtered_df['Date'].dt.date <= end_date]
    
    return filtered_df 