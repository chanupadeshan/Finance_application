import streamlit as st
import yfinance as yf
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import datetime as dt
import pandas as pd

# Function to calculate RSI
def calculate_rsi(data, window=14):
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

# Function to calculate MACD
def calculate_macd(data, short_window=12, long_window=26, signal_window=9):
    short_ema = data['Close'].ewm(span=short_window, adjust=False).mean()
    long_ema = data['Close'].ewm(span=long_window, adjust=False).mean()
    macd = short_ema - long_ema
    signal = macd.ewm(span=signal_window, adjust=False).mean()
    return macd, signal

# Function to calculate Bollinger Bands
def calculate_bollinger_bands(data, window=20):
    sma = data['Close'].rolling(window=window).mean()
    std = data['Close'].rolling(window=window).std()
    upper_band = sma + (std * 2)
    lower_band = sma - (std * 2)
    return sma, upper_band, lower_band

# Initialize Streamlit app
date = dt.datetime.now().date()
st.title("Finance App")
ticker = st.sidebar.text_input("Ticker", "AAPL")
ticker = ticker.upper()
startDate = st.sidebar.date_input("Start Date", value=dt.date(2024, 1, 1))
endDate = st.sidebar.date_input("End Date", value=date)

# Fetch stock data
data = yf.download(ticker, start=startDate, end=endDate)

# Sidebar options for indicators
RSI = st.sidebar.checkbox("RSI", value=False)
MACD = st.sidebar.checkbox("MACD", value=False)
Bollinger = st.sidebar.checkbox("Bollinger Bands", value=False)

# Display stock information
st.write(f"## Stock Analysis for {ticker}")

# Company Information
st.subheader("Company Information")
info = yf.Ticker(ticker).info
st.write(f"**Name:** {info['longName']}")
st.write(f"**Sector:** {info['sector']}")
st.write(f"**Industry:** {info['industry']}")
st.write(f"**Description:** {info['longBusinessSummary']}")

# Current Price
st.subheader("Current Price")
current_price = round(data['Close'].iloc[-1],2)
st.write(f"**Current Price:** {current_price} USD")

# Stock Data Visualization
st.write(f"### {ticker} from {startDate} to {endDate}")

# Determine the number of rows for subplots
num_rows = 1  
if RSI:
    num_rows += 1
if MACD:
    num_rows += 1

# Create subplots
fig = make_subplots(rows=num_rows + 1, cols=1, shared_xaxes=True, 
                    row_heights=[0.6] + [0.2] * num_rows, vertical_spacing=0.02)

# Candlestick chart
fig.add_trace(go.Candlestick(
    x=data.index,
    open=data['Open'],
    high=data['High'],
    low=data['Low'],
    close=data['Close'],
    name='Candlestick'
), row=1, col=1)

# Volume bar chart
fig.add_trace(go.Bar(
    x=data.index,
    y=data['Volume'],
    name='Volume'
), row=num_rows + 1, col=1)

# Add RSI
current_row = 2
if RSI:
    rsi = calculate_rsi(data)
    fig.add_trace(go.Scatter(
        x=data.index,
        y=rsi,
        mode='lines',
        name='RSI'
    ), row=current_row, col=1)
    fig.update_yaxes(title_text="RSI", row=current_row, col=1)
    current_row += 1

# Add MACD
if MACD:
    macd, signal = calculate_macd(data)
    fig.add_trace(go.Scatter(
        x=data.index,
        y=macd,
        mode='lines',
        name='MACD'
    ), row=current_row, col=1)
    fig.add_trace(go.Scatter(
        x=data.index,
        y=signal,
        mode='lines',
        name='Signal Line'
    ), row=current_row, col=1)
    fig.update_yaxes(title_text="MACD", row=current_row, col=1)
    current_row += 1

# Add Bollinger Bands
if Bollinger:
    sma, upper_band, lower_band = calculate_bollinger_bands(data)
    fig.add_trace(go.Scatter(
        x=data.index,
        y=upper_band,
        mode='lines',
        name='Upper Band',
        line=dict(width=1, color="blue")  
    ), row=1, col=1)
    fig.add_trace(go.Scatter(
        x=data.index,
        y=lower_band,
        mode='lines',
        name='Lower Band',
        line=dict(width=1)  
    ), row=1, col=1)
    fig.add_trace(go.Scatter(
        x=data.index,
        y=sma,
        mode='lines',
        name='SMA',
        line=dict(width=1)  
    ), row=1, col=1)

# Update layout
fig.update_layout(
    yaxis_title='Price',
    xaxis_rangeslider_visible=False,
    width=900,  
    height=500  
)

# Update y-axis labels for the volume chart
fig.update_yaxes(title_text="Volume", row=num_rows + 1, col=1)

# Display the plot
st.plotly_chart(fig)
