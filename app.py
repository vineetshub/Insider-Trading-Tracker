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

# Custom CSS for futuristic design
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #0f0f23 0%, #1a1a2e 50%, #16213e 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        border: 1px solid #00d4ff;
        box-shadow: 0 0 20px rgba(0, 212, 255, 0.3);
    }
    
    .metric-card {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid #00d4ff;
        box-shadow: 0 4px 15px rgba(0, 212, 255, 0.2);
        margin: 0.5rem 0;
    }
    
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #0f0f23 0%, #1a1a2e 100%);
    }
    
    .stSelectbox, .stTextInput, .stSlider {
        background: #1a1a2e !important;
        border: 1px solid #00d4ff !important;
        border-radius: 5px !important;
    }
    
    .stButton > button {
        background: linear-gradient(90deg, #00d4ff 0%, #0099cc 100%) !important;
        border: none !important;
        border-radius: 5px !important;
        color: #0f0f23 !important;
        font-weight: bold !important;
    }
    
    .stDataFrame {
        background: #1a1a2e !important;
        border: 1px solid #00d4ff !important;
        border-radius: 10px !important;
    }
    
    h1, h2, h3 {
        color: #00d4ff !important;
        font-weight: 300 !important;
    }
    
    .stMarkdown {
        color: #e0e0e0 !important;
    }
</style>
""", unsafe_allow_html=True)

# Main header
st.markdown("""
<div class="main-header">
    <h1 style="text-align: center; margin: 0; font-size: 3rem; font-weight: 300; color: #00d4ff;">
        INSIDER TRADING TRACKER
    </h1>
    <p style="text-align: center; margin: 0.5rem 0 0 0; color: #e0e0e0; font-size: 1.1rem;">
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

# Data source selection
data_source = st.sidebar.selectbox(
    "Data Source",
    ["SEC API (Real Data)", "Sample Data"],
    help="Choose between real SEC API data or sample data for demonstration"
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
if data_source == "SEC API (Real Data)":
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

# Filters section
st.sidebar.markdown("""
<div style="background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); padding: 1rem; border-radius: 10px; border: 1px solid #00d4ff; margin: 1rem 0;">
    <h3 style="color: #00d4ff; margin: 0;">FILTERS</h3>
</div>
""", unsafe_allow_html=True)

# Load data
@st.cache_data(ttl=300)
def load_data(data_source="SEC API (Real Data)", api_key=None, symbols=None, data_type="Recent Trades", days_back=30):
    try:
        if data_source == "SEC API (Real Data)":
            if data_type == "Recent Trades":
                data = get_recent_insider_trades(api_key=api_key, days=days_back)
            elif data_type == "Multiple Companies" and len(symbols) > 1:
                data = get_multiple_symbols_insider_trades(symbols=symbols, api_key=api_key)
            else:
                data = get_latest_insider_trades(api_key=api_key, symbol=symbols[0])
        else:
            from scraper import generate_sample_data
            data = generate_sample_data()
        
        return data
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

# Load the data
with st.spinner("Loading insider trading data..."):
    if data_source == "SEC API (Real Data)":
        df = load_data(
            data_source=data_source, 
            api_key=api_key, 
            symbols=symbols_to_fetch,
            data_type=data_type,
            days_back=days_back if data_type == "Recent Trades" else 30
        )
    else:
        df = load_data(data_source=data_source)

if df.empty:
    st.error("No data available. Please check your configuration.")
    st.stop()

# Convert date column to datetime
df['Date'] = pd.to_datetime(df['Date'])

# Display data source info
if data_source == "SEC API (Real Data)":
    if api_key:
        if data_type == "Recent Trades":
            st.success(f"Using real SEC insider trading data from the last {days_back} days")
        elif data_type == "Company Specific":
            st.success(f"Using real SEC insider trading data for: {symbols_to_fetch[0]}")
        else:
            st.success(f"Using real SEC insider trading data for: {', '.join(symbols_to_fetch)}")
    else:
        st.warning("No API key provided. Using limited API access")
else:
    st.info("Using sample data for demonstration purposes")

# Filters
col1, col2 = st.sidebar.columns(2)

with col1:
    # Ticker filter
    tickers = ['All'] + sorted(df['Ticker'].unique().tolist())
    selected_tickers = st.multiselect(
        "Ticker",
        options=tickers,
        default=['All']
    )
    
    # Trade type filter
    trade_types = ['All'] + sorted(df['Trade Type'].unique().tolist())
    selected_trade_types = st.multiselect(
        "Trade Type",
        options=trade_types,
        default=['All']
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

# Filter by trade type
if 'All' not in selected_trade_types:
    filtered_df = filtered_df[filtered_df['Trade Type'].isin(selected_trade_types)]

# Filter by date range
filtered_df = filtered_df[
    (filtered_df['Date'].dt.date >= start_date) &
    (filtered_df['Date'].dt.date <= end_date)
]

# Display summary metrics
st.markdown("""
<div style="background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); padding: 1rem; border-radius: 10px; border: 1px solid #00d4ff; margin: 2rem 0;">
    <h2 style="color: #00d4ff; margin: 0; text-align: center;">TRADING METRICS</h2>
</div>
""", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <h3 style="color: #00d4ff; margin: 0; font-size: 1.5rem;">{len(filtered_df)}</h3>
        <p style="color: #e0e0e0; margin: 0;">Total Trades</p>
    </div>
    """, unsafe_allow_html=True)
    
with col2:
    buy_trades = len(filtered_df[filtered_df['Trade Type'] == 'Buy'])
    st.markdown(f"""
    <div class="metric-card">
        <h3 style="color: #00ff88; margin: 0; font-size: 1.5rem;">{buy_trades}</h3>
        <p style="color: #e0e0e0; margin: 0;">Buy Trades</p>
    </div>
    """, unsafe_allow_html=True)
    
with col3:
    sell_trades = len(filtered_df[filtered_df['Trade Type'] == 'Sell'])
    st.markdown(f"""
    <div class="metric-card">
        <h3 style="color: #ff6b6b; margin: 0; font-size: 1.5rem;">{sell_trades}</h3>
        <p style="color: #e0e0e0; margin: 0;">Sell Trades</p>
    </div>
    """, unsafe_allow_html=True)
    
with col4:
    total_value = filtered_df['Value'].sum()
    st.markdown(f"""
    <div class="metric-card">
        <h3 style="color: #00d4ff; margin: 0; font-size: 1.5rem;">${total_value:,.0f}</h3>
        <p style="color: #e0e0e0; margin: 0;">Total Value</p>
    </div>
    """, unsafe_allow_html=True)

# Charts
st.markdown("""
<div style="background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); padding: 1rem; border-radius: 10px; border: 1px solid #00d4ff; margin: 2rem 0;">
    <h2 style="color: #00d4ff; margin: 0; text-align: center;">TRADING ANALYTICS</h2>
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
<div style="background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); padding: 1rem; border-radius: 10px; border: 1px solid #00d4ff; margin: 2rem 0;">
    <h2 style="color: #00d4ff; margin: 0; text-align: center;">LATEST INSIDER TRADES</h2>
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

# Export functionality
st.markdown("""
<div style="background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); padding: 1rem; border-radius: 10px; border: 1px solid #00d4ff; margin: 2rem 0;">
    <h2 style="color: #00d4ff; margin: 0; text-align: center;">EXPORT DATA</h2>
</div>
""", unsafe_allow_html=True)

# Prepare data for export
export_df = filtered_df.copy()
export_df['Date'] = export_df['Date'].dt.strftime('%Y-%m-%d')

# Convert to CSV
csv = export_df.to_csv(index=False)

# Download button
st.download_button(
    label="Download CSV",
    data=csv,
    file_name=f"insider_trading_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
    mime="text/csv"
)

# Footer
st.markdown("---")
st.markdown(
    "Data sourced from [SEC API by D2V](https://api.sec-api.io/) | Built with Streamlit"
) 