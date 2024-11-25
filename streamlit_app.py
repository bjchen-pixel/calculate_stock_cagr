import streamlit as st
import yfinance as yf
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt

def calculate_cagr_with_dividends(ticker, start_date, initial_investment):
    """
    Calculate the annualized return (CAGR) considering reinvested dividends
    and generate a DataFrame tracking investment growth over time.
    """
    # Fetch stock data
    stock = yf.Ticker(ticker)
    hist_data = stock.history(start=start_date, actions=True)
    
    if hist_data.empty:
        st.error("Invalid stock ticker or no data available for the given date range.")
        return None, None, None
    
    # Filter price and dividends
    prices = hist_data['Close']
    dividends = hist_data['Dividends']
    
    if prices.empty:
        st.error("No price data available for the given stock.")
        return None, None, None
    
    # Initialize investment values
    shares = initial_investment / prices.iloc[0]
    total_investment = initial_investment
    investment_growth = []  # To track investment value over time
    
    for date, price in prices.items():
        # Track current value of investment
        investment_growth.append({"Date": date, "Investment Value": shares * price})
        if date in dividends.index and dividends[date] > 0:
            # Reinvest dividends to buy more shares
            total_dividends = shares * dividends[date]
            new_shares = total_dividends / price
            shares += new_shares
    
    # Final value of investment
    final_value = shares * prices.iloc[-1]

    # Convert start_date to a datetime object without timezone
    start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
    # Convert end_date_obj to a naive datetime (remove timezone if exists)
    end_date_obj = prices.index[-1].to_pydatetime().replace(tzinfo=None)

    # Calculate CAGR
    years = (end_date_obj - start_date_obj).days / 365.25
    cagr = (final_value / initial_investment) ** (1 / years) - 1

    # Create DataFrame for investment growth
    growth_df = pd.DataFrame(investment_growth)
    growth_df['Date'] = pd.to_datetime(growth_df['Date'])
    growth_df.set_index('Date', inplace=True)

    return cagr, final_value, growth_df

# Streamlit App
st.title("Stock CAGR Calculator with Dividends")

# User Inputs
ticker = st.text_input("Enter the stock ticker (e.g., AAPL):").upper()
start_date = st.date_input("Enter the start date of investment:", value=datetime(2019, 1, 1))
initial_investment = st.number_input("Enter the initial investment amount (USD):", min_value=1.0, step=100.0)

# Calculate CAGR
if st.button("Calculate"):
    if ticker and initial_investment > 0:
        cagr, final_value, growth_df = calculate_cagr_with_dividends(ticker, str(start_date), initial_investment)
        if cagr is not None:
            st.success(f"Final Investment Value: ${final_value:,.2f}")
            st.success(f"Annualized Return (CAGR) with Reinvested Dividends: {cagr:.2%}")
            
            # Plot investment growth curve
            st.subheader("Investment Growth Over Time")
            st.line_chart(growth_df, use_container_width=True)
    else:
        st.error("Please provide valid inputs.")
