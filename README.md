# Insider Trading Tracker

Real-time dashboard for tracking insider trading activity using SEC API data. Built with Python, Streamlit, and Plotly.

## Features

- Real SEC data from official Form 3, 4, and 5 filings
- Multiple data sources: SEC API, sample data
- Interactive dashboard with filters and visualizations
- Advanced filtering by ticker, trade type, and date range
- Data visualization with buy/sell patterns and volume trends
- Export functionality for CSV downloads
- Responsive design for desktop and mobile

## Installation

1. Clone the repository
   ```bash
   git clone https://github.com/vineetshub/Insider-Trading-Tracker.git
   cd Insider-Trading-Tracker
   ```

2. Create virtual environment
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Run the application
   ```bash
   streamlit run app.py
   ```

2. Open browser at `http://localhost:8501`

3. Configure data source and filters in the sidebar

4. Explore trading analytics and export data as needed

## Data Sources

- **SEC API by D2V**: Real insider trading data from official SEC filings
- **Sample Data**: Generated data for demonstration purposes

## Technology Stack

- Python 3.8+
- Streamlit
- SEC API by D2V
- Pandas
- Plotly
- Requests

## Project Structure

```
insider-trading-tracker/
├── app.py                 # Main Streamlit application
├── scraper.py             # SEC API data fetching
├── utils.py               # Utility functions and charts
├── requirements.txt       # Python dependencies
├── README.md             # Project documentation
├── run_app.sh            # Unix/Mac startup script
└── run_app.bat           # Windows startup script
```

## Data Schema

| Column | Type | Description |
|--------|------|-------------|
| Ticker | String | Stock ticker symbol |
| Insider | String | Insider name |
| Title | String | Position/title |
| Trade Type | String | Buy, Sell, or Other |
| Shares | Float | Number of shares traded |
| Price | Float | Price per share |
| Value | Float | Total transaction value |
| Date | DateTime | Date of the trade |

## Disclaimer

This tool is for educational and informational purposes only. Insider trading data should not be used as the sole basis for investment decisions. Always conduct thorough research and consider consulting with financial advisors.


<img width="1245" height="418" alt="image" src="https://github.com/user-attachments/assets/16968739-74d2-41a9-8869-994573a11490" />
