import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import io
import os

from scraper import get_latest_insider_trades, get_multiple_symbols_insider_trades, get_recent_insider_trades
from utils import create_buy_sell_chart, create_volume_chart

# Page configuration
st.set_page_config(
    page_title="Insider Trading Tracker",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for sharp, modern design
st.markdown("""
<style>
    /* Global styles */
    .main {
        background: linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 50%, #0f0f0f 100%);
    }
    
    .main-header {
        background: linear-gradient(90deg, #0a0a0a 0%, #1a1a1a 50%, #0f0f0f 100%);
        padding: 2.5rem;
        border-radius: 0;
        margin-bottom: 2rem;
        border: 2px solid #00d4ff;
        box-shadow: 0 0 30px rgba(0, 212, 255, 0.2);
        position: relative;
        overflow: hidden;
    }
    
    .main-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 2px;
        background: linear-gradient(90deg, #00d4ff, #00ff88, #00d4ff);
        animation: glow 2s ease-in-out infinite alternate;
    }
    
    @keyframes glow {
        from { opacity: 0.7; }
        to { opacity: 1; }
    }
    
    .metric-card {
        background: linear-gradient(135deg, #1a1a1a 0%, #0f0f0f 100%);
        padding: 1.8rem;
        border-radius: 0;
        border: 1px solid #00d4ff;
        box-shadow: 0 4px 20px rgba(0, 212, 255, 0.15);
        margin: 0.5rem 0;
        position: relative;
        overflow: hidden;
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 4px;
        height: 100%;
        background: linear-gradient(180deg, #00d4ff, #00ff88);
    }
    
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #0a0a0a 0%, #1a1a1a 100%);
        border-right: 2px solid #00d4ff;
    }
    
    /* Sharp input styling */
    .stSelectbox > div > div, .stTextInput > div > div > input {
        background: #1a1a1a !important;
        border: 2px solid #00d4ff !important;
        border-radius: 0 !important;
        color: #ffffff !important;
        font-weight: 500 !important;
        padding: 12px 16px !important;
        transition: all 0.3s ease !important;
    }
    
    .stSelectbox > div > div:hover, .stTextInput > div > div > input:hover {
        border-color: #00ff88 !important;
        box-shadow: 0 0 15px rgba(0, 255, 136, 0.3) !important;
        background: #0f0f0f !important;
    }
    
    .stSelectbox > div > div:focus, .stTextInput > div > div > input:focus {
        border-color: #00ff88 !important;
        box-shadow: 0 0 20px rgba(0, 255, 136, 0.4) !important;
        background: #0f0f0f !important;
    }
    
    /* Sharp multiselect styling */
    .stMultiSelect > div > div {
        background: #1a1a1a !important;
        border: 2px solid #00d4ff !important;
        border-radius: 0 !important;
        color: #ffffff !important;
        min-height: 48px !important;
        padding: 12px 16px !important;
        transition: all 0.3s ease !important;
    }
    
    .stMultiSelect > div > div:hover {
        border-color: #00ff88 !important;
        box-shadow: 0 0 20px rgba(0, 255, 136, 0.3) !important;
        background: #0f0f0f !important;
    }
    
    .stMultiSelect > div > div > div {
        background: #1a1a1a !important;
        color: #ffffff !important;
        border: 1px solid #00d4ff !important;
        border-radius: 0 !important;
        margin: 2px !important;
        padding: 6px 12px !important;
        font-weight: 500 !important;
    }
    
    .stMultiSelect > div > div > div:hover {
        background: #00d4ff !important;
        color: #0a0a0a !important;
        border-color: #00ff88 !important;
        transform: translateY(-1px) !important;
    }
    
    /* Sharp slider styling */
    .stSlider > div > div > div > div {
        background: #00d4ff !important;
        border-radius: 0 !important;
    }
    
    .stSlider > div > div > div > div > div {
        background: #00ff88 !important;
        border-radius: 0 !important;
        box-shadow: 0 0 10px rgba(0, 255, 136, 0.5) !important;
    }
    
    /* Sharp button styling */
    .stButton > button {
        background: linear-gradient(90deg, #00d4ff 0%, #00ff88 100%) !important;
        border: none !important;
        border-radius: 0 !important;
        color: #0a0a0a !important;
        font-weight: bold !important;
        padding: 12px 24px !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(0, 212, 255, 0.4) !important;
    }
    
    /* Sharp dataframe styling */
    .stDataFrame {
        background: #1a1a1a !important;
        border: 2px solid #00d4ff !important;
        border-radius: 0 !important;
        box-shadow: 0 4px 20px rgba(0, 212, 255, 0.1) !important;
    }
    
    /* Sharp typography */
    h1, h2, h3 {
        color: #00d4ff !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 2px !important;
        text-shadow: 0 0 10px rgba(0, 212, 255, 0.3) !important;
    }
    
    .stMarkdown {
        color: #e0e0e0 !important;
        font-weight: 400 !important;
    }
    
    /* Sharp filter section */
    .filter-section {
        background: linear-gradient(135deg, #1a1a1a 0%, #0f0f0f 100%);
        padding: 1.5rem;
        border-radius: 0;
        border: 2px solid #00d4ff;
        margin: 1rem 0;
        position: relative;
        overflow: hidden;
    }
    
    .filter-section::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 2px;
        background: linear-gradient(90deg, #00d4ff, #00ff88, #00d4ff);
    }
    
    .filter-section h3 {
        color: #00d4ff;
        margin: 0 0 1.5rem 0;
        font-size: 1.2rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Sharp date input styling */
    .stDateInput > div > div {
        background: #1a1a1a !important;
        border: 2px solid #00d4ff !important;
        border-radius: 0 !important;
        color: #ffffff !important;
        padding: 12px 16px !important;
    }
    
    /* Chart styling */
    .js-plotly-plot {
        background: #1a1a1a !important;
        border: 1px solid #00d4ff !important;
        border-radius: 0 !important;
    }
    
    /* Success/Error messages */
    .stSuccess {
        background: linear-gradient(90deg, #00ff88, #00d4ff) !important;
        color: #0a0a0a !important;
        border-radius: 0 !important;
        border: none !important;
        padding: 1rem !important;
        font-weight: 600 !important;
    }
    
    .stWarning {
        background: linear-gradient(90deg, #ff6b6b, #ff8e8e) !important;
        color: #ffffff !important;
        border-radius: 0 !important;
        border: none !important;
        padding: 1rem !important;
        font-weight: 600 !important;
    }
    
    .stInfo {
        background: linear-gradient(90deg, #00d4ff, #0099cc) !important;
        color: #ffffff !important;
        border-radius: 0 !important;
        border: none !important;
        padding: 1rem !important;
        font-weight: 600 !important;
    }
    
    /* Remove rounded corners from all elements */
    * {
        border-radius: 0 !important;
    }
</style>
""", unsafe_allow_html=True)

# Main header
st.markdown("""
<div class="main-header">
    <h1 style="text-align: center; margin: 0; font-size: 2.5rem; font-weight: 700; color: #00d4ff; text-transform: uppercase; letter-spacing: 3px;">
        COMPANY INSIDER TRADES
    </h1>
    <p style="text-align: center; margin: 1rem 0 0 0; color: #e0e0e0; font-size: 1rem; font-weight: 400; letter-spacing: 1px;">
        Real-time SEC data analysis platform
    </p>
</div>
""", unsafe_allow_html=True)

# Sidebar configuration
st.sidebar.markdown("""
<div style="background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); padding: 1rem; border-radius: 10px; border: 1px solid #00d4ff; margin-bottom: 1rem;">
    <h3 style="color: #00d4ff; margin: 0;">CONFIGURATION</h3>
</div>
""", unsafe_allow_html=True)

# API Key configuration
api_key = st.sidebar.text_input(
    "SEC API Key",
    value="f62eeeb281516660069b2bcf08532948157552b05b1307392e0ca98ff865e44f",
    type="password",
    help="SEC API key for real insider trading data"
)

# Available major company symbols
available_symbols = [
    'AAPL', 'MSFT', 'GOOG', 'AMZN', 'TSLA', 'META', 'NVDA', 'NFLX', 'CRM',
    'VZ', 'PFE', 'PEP', 'WMT', 'CVX', 'INTC', 'MA', 'HD', 'MRK', 'JNJ',
    'BAC', 'FB', 'COST', 'TMO', 'ABBV', 'MCD', 'ACN', 'T', 'PYPL', 'PG',
    'XOM', 'ABT', 'AMGN', 'UNH', 'DIS', 'CSCO', 'KO', 'ADBE', 'V', 'JPM',
    'IONQ', 'LEU'
]

# Data type selection
data_type = st.sidebar.selectbox(
    "Data Type",
    ["Recent Trades", "Company Specific", "Multiple Companies"],
    help="Choose the type of data to fetch"
)

if data_type == "Recent Trades":
    days_back = st.sidebar.slider(
        "Days Back",
        min_value=7,
        max_value=90,
        value=30,
        help="Number of days to look back for recent trades"
    )
    symbols_to_fetch = None
elif data_type == "Company Specific":
    selected_symbol = st.sidebar.selectbox(
        "Company Symbol",
        available_symbols,
        index=0,
        help="Select a company to analyze"
    )
    symbols_to_fetch = [selected_symbol]
else:
    # Multiple companies selection
    selected_symbols = st.sidebar.multiselect(
        "Company Symbols (Max 3)",
        available_symbols,
        default=['AAPL', 'MSFT'],
        max_selections=3,
        help="Select up to 3 companies to analyze"
    )
    symbols_to_fetch = selected_symbols if selected_symbols else ['AAPL']

# Load data
@st.cache_data(ttl=300)
def load_data(api_key=None, symbols=None, data_type="Recent Trades", days_back=30):
    try:
        if data_type == "Recent Trades":
            data = get_recent_insider_trades(api_key=api_key, days=days_back)
        elif data_type == "Multiple Companies" and len(symbols) > 1:
            data = get_multiple_symbols_insider_trades(symbols=symbols, api_key=api_key)
        else:
            data = get_latest_insider_trades(api_key=api_key, symbol=symbols[0])
        
        return data
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

# Load the data
with st.spinner("Loading insider trading data..."):
    df = load_data(
        api_key=api_key, 
        symbols=symbols_to_fetch,
        data_type=data_type,
        days_back=days_back if data_type == "Recent Trades" else 30
    )

if df.empty:
    st.error("No data available. Please check your configuration.")
    st.stop()

# Convert date column to datetime
df['Date'] = pd.to_datetime(df['Date'])

# Display data source info
if api_key:
    if data_type == "Recent Trades":
        st.success(f"Using real SEC insider trading data from the last {days_back} days")
    elif data_type == "Company Specific":
        st.success(f"Using real SEC insider trading data for: {symbols_to_fetch[0]}")
    else:
        st.success(f"Using real SEC insider trading data for: {', '.join(symbols_to_fetch)}")
else:
    st.warning("No API key provided. Using limited API access")

# Filters section
st.sidebar.markdown("""
<div class="filter-section">
    <h3>FILTERS</h3>
</div>
""", unsafe_allow_html=True)

# Filters
col1, col2 = st.sidebar.columns(2)

with col1:
    # Ticker filter with better visibility
    tickers = ['All'] + sorted(df['Ticker'].unique().tolist())
    selected_tickers = st.multiselect(
        "Ticker Symbols",
        options=tickers,
        default=['All'],
        help="Select ticker symbols to filter"
    )
    
    # Simplified trade type filter - only Buy/Sell
    trade_types = ['All', 'Buy', 'Sell']
    selected_trade_types = st.multiselect(
        "Trade Type",
        options=trade_types,
        default=['All'],
        help="Select trade types to filter"
    )

with col2:
    # Date range filter
    min_date = df['Date'].min()
    max_date = df['Date'].max()
    
    start_date = st.date_input(
        "Start Date",
        value=min_date.date(),
        min_value=min_date.date(),
        max_value=max_date.date()
    )
    
    end_date = st.date_input(
        "End Date",
        value=max_date.date(),
        min_value=min_date.date(),
        max_value=max_date.date()
    )

# Apply filters
filtered_df = df.copy()

# Filter by ticker
if 'All' not in selected_tickers:
    filtered_df = filtered_df[filtered_df['Ticker'].isin(selected_tickers)]

# Filter by trade type - only Buy/Sell
if 'All' not in selected_trade_types:
    filtered_df = filtered_df[filtered_df['Trade Type'].isin(selected_trade_types)]

# Filter by date range
filtered_df = filtered_df[
    (filtered_df['Date'].dt.date >= start_date) &
    (filtered_df['Date'].dt.date <= end_date)
]

# Display summary metrics
st.markdown("""
<div style="background: linear-gradient(135deg, #1a1a1a 0%, #0f0f0f 100%); padding: 1.5rem; border-radius: 0; border: 2px solid #00d4ff; margin: 2rem 0; position: relative; overflow: hidden;">
    <div style="position: absolute; top: 0; left: 0; width: 100%; height: 2px; background: linear-gradient(90deg, #00d4ff, #00ff88, #00d4ff);"></div>
    <h2 style="color: #00d4ff; margin: 0; text-align: center; text-transform: uppercase; letter-spacing: 2px; font-weight: 700;">TRADING METRICS</h2>
</div>
""", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <h3 style="color: #00d4ff; margin: 0; font-size: 1.8rem; font-weight: 700;">{len(filtered_df)}</h3>
        <p style="color: #e0e0e0; margin: 0; font-weight: 500; text-transform: uppercase; letter-spacing: 1px;">Total Trades</p>
    </div>
    """, unsafe_allow_html=True)
    
with col2:
    buy_trades = len(filtered_df[filtered_df['Trade Type'] == 'Buy'])
    st.markdown(f"""
    <div class="metric-card">
        <h3 style="color: #00ff88; margin: 0; font-size: 1.8rem; font-weight: 700;">{buy_trades}</h3>
        <p style="color: #e0e0e0; margin: 0; font-weight: 500; text-transform: uppercase; letter-spacing: 1px;">Buy Trades</p>
    </div>
    """, unsafe_allow_html=True)
    
with col3:
    sell_trades = len(filtered_df[filtered_df['Trade Type'] == 'Sell'])
    st.markdown(f"""
    <div class="metric-card">
        <h3 style="color: #ff6b6b; margin: 0; font-size: 1.8rem; font-weight: 700;">{sell_trades}</h3>
        <p style="color: #e0e0e0; margin: 0; font-weight: 500; text-transform: uppercase; letter-spacing: 1px;">Sell Trades</p>
    </div>
    """, unsafe_allow_html=True)
    
with col4:
    total_value = filtered_df['Value'].sum()
    st.markdown(f"""
    <div class="metric-card">
        <h3 style="color: #00d4ff; margin: 0; font-size: 1.8rem; font-weight: 700;">${total_value:,.0f}</h3>
        <p style="color: #e0e0e0; margin: 0; font-weight: 500; text-transform: uppercase; letter-spacing: 1px;">Total Value</p>
    </div>
    """, unsafe_allow_html=True)

# Charts
st.markdown("""
<div style="background: linear-gradient(135deg, #1a1a1a 0%, #0f0f0f 100%); padding: 1.5rem; border-radius: 0; border: 2px solid #00d4ff; margin: 2rem 0; position: relative; overflow: hidden;">
    <div style="position: absolute; top: 0; left: 0; width: 100%; height: 2px; background: linear-gradient(90deg, #00d4ff, #00ff88, #00d4ff);"></div>
    <h2 style="color: #00d4ff; margin: 0; text-align: center; text-transform: uppercase; letter-spacing: 2px; font-weight: 700;">TRADING ANALYTICS</h2>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    if not filtered_df.empty:
        buy_sell_fig = create_buy_sell_chart(filtered_df)
        st.plotly_chart(buy_sell_fig, use_container_width=True)
    else:
        st.info("No data available for the selected filters")

with col2:
    if not filtered_df.empty:
        volume_fig = create_volume_chart(filtered_df)
        st.plotly_chart(volume_fig, use_container_width=True)
    else:
        st.info("No data available for the selected filters")

# Data table
st.markdown("""
<div style="background: linear-gradient(135deg, #1a1a1a 0%, #0f0f0f 100%); padding: 1.5rem; border-radius: 0; border: 2px solid #00d4ff; margin: 2rem 0; position: relative; overflow: hidden;">
    <div style="position: absolute; top: 0; left: 0; width: 100%; height: 2px; background: linear-gradient(90deg, #00d4ff, #00ff88, #00d4ff);"></div>
    <h2 style="color: #00d4ff; margin: 0; text-align: center; text-transform: uppercase; letter-spacing: 2px; font-weight: 700;">LATEST INSIDER TRADES</h2>
</div>
""", unsafe_allow_html=True)

# Format the dataframe for display
display_df = filtered_df.copy()
display_df['Date'] = display_df['Date'].dt.strftime('%Y-%m-%d')
display_df['Value'] = display_df['Value'].apply(lambda x: f"${x:,.0f}")
display_df['Price'] = display_df['Price'].apply(lambda x: f"${x:.2f}")

# Show additional columns if available
columns_to_show = ['Ticker', 'Insider', 'Title', 'Trade Type', 'Shares', 'Price', 'Value', 'Date']
if 'Security Type' in display_df.columns:
    columns_to_show.append('Security Type')
if 'Transaction Code' in display_df.columns:
    columns_to_show.append('Transaction Code')

st.dataframe(
    display_df[columns_to_show],
    use_container_width=True,
    hide_index=True
)

# Footer
st.markdown("---")
st.markdown(
    "Data sourced from [SEC API by D2V](https://api.sec-api.io/) | Built with Streamlit"
) 