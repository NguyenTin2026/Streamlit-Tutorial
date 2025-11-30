import streamlit as st
import yfinance as yf
from prophet import Prophet
import pandas as pd
import plotly.graph_objects as go
import numpy as np

st.set_page_config(page_title="Trading Dashboard Overlay", layout="wide")
st.title("📊 Trading Dashboard: Overlay Price + Forecast + Buy/Sell Signals")

# ----- Inputs -----
tickers = st.text_input("Enter ticker symbols (comma separated)", "AAPL,MSFT")
start = st.date_input("Start date")
end = st.date_input("End date")
forecast_days = st.slider("Days to forecast", min_value=7, max_value=180, value=30)

ticker_list = [t.strip().upper() for t in tickers.split(",")]

for ticker in ticker_list:
    st.header(f"🔹 {ticker}")

    # ----- Load Data -----
    data = yf.download(ticker, start=start, end=end)
    if data.empty:
        st.error(f"No data found for {ticker} in the selected date range.")
        continue

    # ----- Prepare Technical Indicators -----
    df = data[['Close']].copy()
    df['MA20'] = df['Close'].rolling(20).mean()
    df['MA50'] = df['Close'].rolling(50).mean()

    # RSI
    delta = df['Close'].diff()
    up = delta.clip(lower=0)
    down = -1 * delta.clip(upper=0)
    ema_up = up.ewm(com=13, adjust=False).mean()
    ema_down = down.ewm(com=13, adjust=False).mean()
    rs = ema_up / ema_down
    df['RSI'] = 100 - (100 / (1 + rs))

    # Buy/Sell signal
    df['Signal_MA'] = np.where(df['MA20'] > df['MA50'], 'Buy', 'Sell')
    df['Signal_RSI'] = np.where(df['RSI'] < 30, 'Buy', np.where(df['RSI'] > 70, 'Sell', 'Hold'))

    # ----- Prophet Forecast -----
    df_prophet = df.reset_index()[['Date','Close']].rename(columns={'Date':'ds','Close':'y'})
    df_prophet = df_prophet.dropna()
    
    if df_prophet.shape[0] < 2:
        st.warning(f"❌ Not enough data to forecast {ticker}. Please select a longer date range.")
        continue

    m = Prophet(daily_seasonality=True)
    m.fit(df_prophet)
    future = m.make_future_dataframe(periods=forecast_days)
    forecast = m.predict(future)

    # ----- Interactive Overlay Chart -----
    fig = go.Figure()

    # Price line
    fig.add_trace(go.Scatter(
        x=df.index, y=df['Close'], name='Close Price', line=dict(color='black')
    ))

    # Forecast line
    fig.add_trace(go.Scatter(
        x=forecast['ds'], y=forecast['yhat'], name='Forecast', line=dict(color='blue', dash='dash')
    ))

    # Forecast interval
    fig.add_trace(go.Scatter(
        x=list(forecast['ds']) + list(forecast['ds'][::-1]),
        y=list(forecast['yhat_upper']) + list(forecast['yhat_lower'][::-1]),
        fill='toself', fillcolor='rgba(173,216,230,0.2)',
        line=dict(color='rgba(255,255,255,0)'), hoverinfo="skip", showlegend=True,
        name='Forecast interval'
    ))

    # Buy/Sell markers (last 30 days)
    last = df.iloc[-30:]
    buys = last[(last['Signal_MA']=='Buy') & (last['Signal_RSI']=='Buy')]
    sells = last[(last['Signal_MA']=='Sell') & (last['Signal_RSI']=='Sell')]

    fig.add_trace(go.Scatter(
        x=buys.index, y=buys['Close'],
        mode='markers', marker_symbol='triangle-up', marker_color='green', marker_size=10, name='Buy Signal'
    ))
    fig.add_trace(go.Scatter(
        x=sells.index, y=sells['Close'],
        mode='markers', marker_symbol='triangle-down', marker_color='red', marker_size=10, name='Sell Signal'
    ))

    fig.update_layout(
        title=f"{ticker} — Price + Forecast + Buy/Sell Signals",
        xaxis_title='Date', yaxis_title='Price',
        hovermode='x unified'
    )

    st.plotly_chart(fig, use_container_width=True)

    # ----- Download Forecast CSV -----
    csv = forecast[['ds','yhat','yhat_lower','yhat_upper']].to_csv(index=False)
    st.download_button(
        label=f"📥 Download {ticker} Forecast CSV",
        data=csv,
        file_name=f"{ticker}_forecast.csv",
        mime='text/csv',
    )
