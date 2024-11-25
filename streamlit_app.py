import streamlit as st
import yfinance as yf
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt

# Function to fetch stock data
def fetch_stock_data(tickers, start_date, end_date, include_dividends=False):
    data = yf.download(tickers, start=start_date, end=end_date)
    if include_dividends:
        dividend_data = yf.download(tickers, start=start_date, end=end_date, actions=True)['Dividends']
        for ticker in tickers:
            if ticker in dividend_data.columns:
                data['Adj Close'][ticker] += dividend_data[ticker].cumsum()
    return data['Adj Close']

# Function to calculate compound annual growth rate (CAGR)
def calculate_cagr(start_value, end_value, num_years):
    return (end_value / start_value) ** (1 / num_years) - 1

# Streamlit application
st.title("Multi-Stock Comparison")

# User inputs
stock_symbols = st.text_input("Enter stock symbols (comma-separated):", "AAPL, TSM, MSFT")
start_date = st.date_input("Start Date", pd.to_datetime("2020-01-01"))
end_date = st.date_input("End Date", pd.to_datetime("2023-01-01"))
include_dividends = st.checkbox("Include Dividend Reinvestment", value=False)
initial_investment = st.number_input("Initial Investment Amount (per stock):", min_value=0.0, value=1000.0)

if st.button("Compare Stocks"):
    try:
        tickers = [ticker.strip() for ticker in stock_symbols.split(',')]
        stock_data = fetch_stock_data(tickers, start_date, end_date, include_dividends)
        
        # Check if stock_data is empty
        if stock_data.empty:
            st.error("No data available for the selected stocks and date range. Please try different inputs.")
        else:
            # Plot investment growth over time
            st.write("### Investment Growth Over Time")
            fig, ax = plt.subplots(figsize=(10, 6))
            for ticker in tickers:
                if ticker in stock_data.columns:
                    investment_values = initial_investment * (stock_data[ticker] / stock_data[ticker].iloc[0])
                    ax.plot(stock_data.index, investment_values, label=f"{ticker} Investment Value")
            ax.set_xlabel('Date')
            ax.set_ylabel('Investment Value (USD)')
            ax.set_title('Investment Growth Over Time')
            ax.legend()
            st.pyplot(fig)
            
            # Plot adjusted close prices
            st.write("### Stock Price Over Time")
            fig, ax = plt.subplots(figsize=(10, 6))
            for ticker in tickers:
                if ticker in stock_data.columns:
                    ax.plot(stock_data.index, stock_data[ticker], label=ticker)
            ax.set_xlabel('Date')
            ax.set_ylabel('Adjusted Close Price')
            ax.set_title('Stock Prices Over Time')
            ax.legend()
            st.pyplot(fig)
            
            # Display raw adjusted close data
            st.write("### Adjusted Close Price Data")
            st.dataframe(stock_data)
            
            # Calculate and display CAGR for each stock
            st.write("### CAGR for Each Stock")
            cagr_results = {}
            final_values = {}
            for ticker in tickers:
                if ticker in stock_data.columns:
                    start_value = stock_data[ticker].iloc[0]
                    end_value = stock_data[ticker].iloc[-1]
                    num_years = (end_date - start_date).days / 365.25
                    cagr = calculate_cagr(start_value, end_value, num_years)
                    cagr_results[ticker] = cagr * 100
                    final_values[ticker] = initial_investment * (end_value / start_value)
            
            cagr_df = pd.DataFrame.from_dict(cagr_results, orient='index', columns=['CAGR (%)'])
            st.dataframe(cagr_df)
            
            # Display final investment values
            st.write("### Final Investment Value for Each Stock")
            final_values_df = pd.DataFrame.from_dict(final_values, orient='index', columns=['Final Value (USD)'])
            st.dataframe(final_values_df)
        
    except Exception as e:
        st.error(f"Error occurred: {e}")

# Install dependencies: yfinance, pandas, streamlit, matplotlib
# Run: pip install yfinance pandas streamlit matplotlib
