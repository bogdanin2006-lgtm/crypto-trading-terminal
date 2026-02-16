import streamlit as st
import ccxt
import pandas as pd
import plotly.graph_objects as go
import time
from datetime import datetime

# --- 1. CONFIG & SETUP ---
st.set_page_config(page_title="QUANTUM TRADER", layout="wide", page_icon="⚡")

# --- 2. PROFESSIONAL TRADING CSS ---
st.markdown("""
    <style>
    /* Dark Trading Theme */
    .stApp { background-color: #0e1117; }
    
    /* Metrics */
    div[data-testid="stMetric"] {
        background-color: #1e2329;
        border: 1px solid #2b3139;
        padding: 15px;
        border-radius: 5px;
    }
    div[data-testid="stMetricLabel"] { color: #848e9c; font-size: 14px; }
    div[data-testid="stMetricValue"] { color: #ffffff; font-family: 'Roboto Mono', monospace; }
    
    /* Green/Red Colors for Finance */
    .positive { color: #0ecb81 !important; }
    .negative { color: #f6465d !important; }
    
    /* Sidebar */
    section[data-testid="stSidebar"] { background-color: #161a1e; }
    
    /* Buttons */
    .stButton button {
        width: 100%;
        border-radius: 4px;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. DATA ENGINE (CCXT) ---
@st.cache_data(ttl=5) # Кэшируем на 5 секунд, чтобы не банили API
def fetch_crypto_data(symbol, timeframe, limit=100):
    exchange = ccxt.binance() # Используем Binance (публичный API)
    try:
        # Получаем свечи (OHLCV)
        bars = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
        df = pd.DataFrame(bars, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        return df
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return pd.DataFrame()

# --- 4. SIDEBAR CONTROLS ---
with st.sidebar:
    st.title("⚡ QUANTUM TRADER")
    st.caption("Real-Time Market Data")
    
    # Выбор пары
    selected_pair = st.selectbox("Select Asset", ["BTC/USDT", "ETH/USDT", "SOL/USDT", "XRP/USDT", "DOGE/USDT"])
    
    # Таймфрейм
    timeframe = st.selectbox("Timeframe", ["1m", "5m", "15m", "1h", "4h", "1d"], index=3)
    
    st.markdown("---")
    st.markdown("### 🤖 AI Signals")
    st.info("Signal: **STRONG BUY** 🟢")
    st.caption("Confidence: 87%")
    
    # Фейковые кнопки торговли для UI
    c1, c2 = st.columns(2)
    c1.button("BUY", type="primary")
    c2.button("SELL")

# --- 5. MAIN SCREEN ---
# Заголовок и цена
df = fetch_crypto_data(selected_pair, timeframe)

if not df.empty:
    last_price = df['close'].iloc[-1]
    prev_price = df['close'].iloc[-2]
    price_change = last_price - prev_price
    percent_change = (price_change / prev_price) * 100
    
    # Цвет изменения
    color_delta = "normal" 
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Current Price", f"${last_price:,.2f}", f"{percent_change:.2f}%")
    c2.metric("24h High", f"${df['high'].max():,.2f}")
    c3.metric("24h Low", f"${df['low'].min():,.2f}")
    c4.metric("Volume", f"{df['volume'].iloc[-1]:,.2f}")

    # --- 6. CANDLESTICK CHART (ГРАФИК СВЕЧЕЙ) ---
    st.markdown(f"### {selected_pair} • {timeframe} Chart")
    
    fig = go.Figure(data=[go.Candlestick(
        x=df['timestamp'],
        open=df['open'],
        high=df['high'],
        low=df['low'],
        close=df['close'],
        increasing_line_color='#0ecb81', # Binance Green
        decreasing_line_color='#f6465d'  # Binance Red
    )])

    fig.update_layout(
        plot_bgcolor='#161a1e',
        paper_bgcolor='#0e1117',
        font=dict(color='white'),
        xaxis_rangeslider_visible=False,
        height=500,
        margin=dict(t=20, b=20, l=0, r=0),
        xaxis=dict(showgrid=False),
        yaxis=dict(gridcolor='#2b3139')
    )
    
    st.plotly_chart(fig, use_container_width=True)

    # --- 7. TECHNICAL ANALYSIS (RSI & TABLES) ---
    t1, t2 = st.tabs(["📊 Technicals", "📜 Order Book"])
    
    with t1:
        # Простой расчет SMA (Скользящая средняя)
        df['SMA_20'] = df['close'].rolling(window=20).mean()
        
        # Линейный график SMA
        fig_line = go.Figure()
        fig_line.add_trace(go.Scatter(x=df['timestamp'], y=df['close'], name='Price', line=dict(color='#0ecb81')))
        fig_line.add_trace(go.Scatter(x=df['timestamp'], y=df['SMA_20'], name='SMA 20', line=dict(color='#ffa726')))
        fig_line.update_layout(height=300, plot_bgcolor='#161a1e', paper_bgcolor='#0e1117', font=dict(color='white'))
        st.plotly_chart(fig_line, use_container_width=True)
        
    with t2:
        # Имитация стакана ордеров
        st.dataframe(df.tail(10)[['timestamp', 'close', 'volume']].sort_values(by='timestamp', ascending=False), use_container_width=True)

    st.caption(f"Last update: {datetime.now().strftime('%H:%M:%S')}")
    
    # Кнопка обновления (чтобы не делать бесконечный цикл, который грузит сервер)
    if st.button("🔄 Refresh Data"):
        st.rerun()

else:
    st.error("Failed to load data. API connection issue.")
