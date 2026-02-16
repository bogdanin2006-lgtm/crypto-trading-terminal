import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import ccxt
import requests
from datetime import datetime

# --- 1. SETTINGS & THEMES ---
st.set_page_config(layout="wide", page_title="Blue Horizon Pro", page_icon="🌊")

# Функция для смены темы (можно расширять)
def apply_style():
    st.markdown("""
    <style>
        .stApp { background-color: #0E1117; color: #F0F2F6; }
        [data-testid="stSidebar"] { background-color: #161B22; border-right: 1px solid #00BFFF; }
        .stButton>button { 
            background-color: #00BFFF !important; 
            color: white !important; 
            border: none;
            box-shadow: 0px 4px 10px rgba(0, 191, 255, 0.3);
        }
        .stButton>button:hover { box-shadow: 0px 4px 20px rgba(0, 191, 255, 0.6); }
        .card { 
            background-color: #1B2430; 
            padding: 20px; 
            border-radius: 12px; 
            border-bottom: 3px solid #00BFFF;
            margin-bottom: 15px;
        }
    </style>
    """, unsafe_allow_html=True)

apply_style()

# --- 2. DATA ENGINE ---
@st.cache_resource
def init_exchange():
    return ccxt.kraken({'enableRateLimit': True})

exchange = init_exchange()

# --- 3. TELEGRAM ALERT SYSTEM ---
def send_telegram_msg(token, chat_id, message):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message}
    try:
        requests.post(url, json=payload)
    except:
        pass

# --- 4. SIDEBAR (English) ---
with st.sidebar:
    st.title("🌊 BLUE HORIZON")
    st.subheader("Navigation")
    menu = st.radio("Go to:", ["Market Overview", "Trading Terminal", "Portfolio", "System Settings"])
    st.markdown("---")
    pair = st.selectbox("Trading Pair", ["BTC/USD", "ETH/USD", "SOL/USD"])
    
    st.markdown("### 🤖 Telegram Alerts")
    tg_token = st.text_input("Bot Token", type="password", placeholder="123456:ABC...")
    tg_chat = st.text_input("Chat ID", placeholder="987654321")

# --- 5. MAIN INTERFACE ---

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
                st.markdown(f"""<div class="card">
                    <small style='color:#00BFFF'>{symbol}</small><br>
                    <span style='font-size:22px; font-weight:bold;'>${val['last']:,.2f}</span><br>
                    <span style='color:{'#00ff00' if val['percentage'] >= 0 else '#ff4b4b'}'>
                        {val['percentage']:.2f}%
                    </span>
                </div>""", unsafe_allow_html=True)
    except:
        st.error("API Connection unstable. Please wait.")

    # Main Chart
    st.subheader(f"Price Action: {pair}")
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
    
    col_order, col_tools = st.columns([2, 1])
    
    with col_order:
        st.subheader("Order Placement")
        side = st.segmented_control("Action", ["BUY", "SELL"], default="BUY")
        amount = st.number_input("Amount to trade", min_value=0.0, step=0.01)
        price_limit = st.number_input("Limit Price", value=0.0)
        
        if st.button(f"Execute {side} Order"):
            st.warning("Simulation: Order sent to Kraken matching engine.")
            if tg_token and tg_chat:
                send_telegram_msg(tg_token, tg_chat, f"🚀 Alert: {side} order for {amount} {pair} executed!")

    with col_tools:
        st.subheader("Market Depth")
        ob = exchange.fetch_order_book(pair)
        bids = pd.DataFrame(ob['bids'], columns=['Price', 'Qty']).head(5)
        st.write("Current Bids")
        st.dataframe(bids, hide_index=True)

elif menu == "Portfolio":
    st.header("💼 Asset Allocation")
    c1, c2 = st.columns([1, 1])
    with c1:
        st.markdown("""<div class="card">
            <h3 style='margin-top:0;'>Estimated Balance</h3>
            <h1 style='color:#00BFFF;'>$24,105.80</h1>
            <p style='color:#00ff00;'>+12.4% Monthly Growth</p>
        </div>""", unsafe_allow_html=True)
    with c2:
        fig = go.Figure(data=[go.Pie(labels=['BTC', 'ETH', 'USD'], values=[55, 35, 10], hole=.4)])
        fig.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', margin=dict(t=0, b=0, l=0, r=0))
        st.plotly_chart(fig, use_container_width=True)

elif menu == "System Settings":
    st.header("⚙️ Terminal Configuration")
    st.text_input("Kraken API Key", type="password")
    st.text_input("Kraken Secret Key", type="password")
    st.selectbox("Default Currency", ["USD", "EUR", "GBP"])
    if st.button("Save Settings"):
        st.success("Configuration updated successfully!")
