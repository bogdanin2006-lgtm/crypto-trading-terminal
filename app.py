import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import ccxt
import numpy as np
from sklearn.linear_model import LinearRegression
from datetime import datetime, timedelta
import requests

# --- 1. SETTINGS & MAX CUSTOM UI ---
st.set_page_config(layout="wide", page_title="Blue Horizon Pro", page_icon="🌊")

# Внедряем "стеклянный" дизайн и кастомные шрифты
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'JetBrains Mono', monospace;
        background-color: #0E1117;
    }

    .stApp { background-color: #0E1117; color: #F0F2F6; }
    
    /* Glassmorphism Card */
    .metric-card {
        background: rgba(27, 36, 48, 0.7);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(0, 191, 255, 0.2);
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
        margin-bottom: 20px;
    }

    /* Neon Buttons */
    .stButton>button {
        background: transparent !important;
        color: #00BFFF !important;
        border: 2px solid #00BFFF !important;
        border-radius: 8px !important;
        transition: 0.3s !important;
        font-weight: bold !important;
        text-transform: uppercase;
    }
    .stButton>button:hover {
        background: #00BFFF !important;
        color: white !important;
        box-shadow: 0 0 20px #00BFFF;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. DATA & AI ENGINE ---
@st.cache_resource
def init_exchange():
    return ccxt.kraken({'enableRateLimit': True})

exchange = init_exchange()

def get_ai_prediction(df):
    try:
        df['n'] = np.arange(len(df))
        X = df[['n']].values
        y = df['close'].values
        model = LinearRegression().fit(X, y)
        future_n = np.array([len(df) + i for i in range(10)]).reshape(-1, 1)
        return model.predict(future_n), model.score(X, y)
    except:
        return np.array([0]*10), 0

# --- 3. SIDEBAR NAVIGATION ---
with st.sidebar:
    st.title("🌊 BLUE HORIZON")
    menu = st.radio("NAVIGATION", ["Market Overview", "Trading Terminal", "Portfolio", "Settings"])
    st.markdown("---")
    pair = st.selectbox("ACTIVE PAIR", ["BTC/USD", "ETH/USD", "SOL/USD"])
    
    st.markdown("### 🤖 TELEGRAM ALERTS")
    tg_token = st.text_input("Bot Token", type="password")
    tg_chat = st.text_input("Chat ID")

# --- 4. MAIN LOGIC ---

if menu == "Market Overview":
    st.header("🌍 Global Market Pulse")
    
    # Live Tickers
    coins = ['BTC/USD', 'ETH/USD', 'SOL/USD', 'XRP/USD']
    try:
        tickers = exchange.fetch_tickers(coins)
        cols = st.columns(len(coins))
        for i, symbol in enumerate(coins):
            val = tickers.get(symbol, {'last': 0, 'percentage': 0})
            with cols[i]:
                st.markdown(f"""<div class="metric-card">
                    <small style='color:#00BFFF'>{symbol}</small><br>
                    <span style='font-size:22px; font-weight:bold;'>${val['last']:,.2f}</span><br>
                    <span style='color:{'#00ff00' if val['percentage'] >= 0 else '#ff4b4b'}'>
                        {val['percentage']:.2f}%
                    </span>
                </div>""", unsafe_allow_html=True)
    except:
        st.error("Connection issue...")

    # Chart
    ohlcv = exchange.fetch_ohlcv(pair, timeframe='1h', limit=60)
    df = pd.DataFrame(ohlcv, columns=['time', 'open', 'high', 'low', 'close', 'volume'])
    df['time'] = pd.to_datetime(df['time'], unit='ms')
    
    fig = go.Figure(data=[go.Candlestick(
        x=df['time'], open=df['open'], high=df['high'], low=df['low'], close=df['close'],
        increasing_line_color='#00BFFF', decreasing_line_color='#1B2430'
    )])
    fig.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=500)
    st.plotly_chart(fig, use_container_width=True)

elif menu == "Trading Terminal":
    st.header("⚡ Live Execution Terminal")
    
    # Load data for AI
    ohlcv = exchange.fetch_ohlcv(pair, timeframe='1h', limit=100)
    df_ai = pd.DataFrame(ohlcv, columns=['time', 'open', 'high', 'low', 'close', 'volume'])
    
    col_trade, col_ai = st.columns([1, 1])
    
    with col_trade:
        st.subheader("Manual Execution")
        side = st.radio("Side", ["BUY", "SELL"], horizontal=True)
        amount = st.number_input("Amount", min_value=0.0)
        if st.button("Confirm Trade"):
            st.success(f"{side} order for {amount} {pair} placed!")

    with col_ai:
        st.subheader("AI Forecast")
        preds, confidence = get_ai_prediction(df_ai)
        trend = "UP 📈" if preds[-1] > preds[0] else "DOWN 📉"
        st.metric("Neural Verdict", trend, f"{confidence*100:.1f}% Confidence")
        
        fig_pred = go.Figure()
        fig_pred.add_trace(go.Scatter(y=df_ai['close'][-20:], name="Actual", line_color="#00BFFF"))
        fig_pred.add_trace(go.Scatter(x=np.arange(20, 30), y=preds, name="AI Prediction", line=dict(color="#FF00FF", dash='dot')))
        fig_pred.update_layout(template="plotly_dark", height=300, margin=dict(t=0, b=0, l=0, r=0))
        st.plotly_chart(fig_pred, use_container_width=True)

elif menu == "Portfolio":
    st.header("💼 My Assets")
    st.markdown("""<div class="metric-card">
        <h3>Estimated Balance</h3>
        <h1 style='color:#00BFFF;'>$24,105.80</h1>
    </div>""", unsafe_allow_html=True)
    
elif menu == "Settings":
    st.header("⚙️ Terminal Settings")
    st.text_input("Kraken API Key", type="password")
    st.text_input("Kraken Secret Key", type="password")
