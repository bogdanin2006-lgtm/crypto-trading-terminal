import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import ccxt
import numpy as np
import time
import requests
from datetime import datetime

# --- 1. CONFIGURATION ---
st.set_page_config(
    page_title="BLUE HORIZON: CYBER TERMINAL",
    layout="wide",
    page_icon="💠",
    initial_sidebar_state="expanded"
)

# --- 2. CSS STYLES (CYBERPUNK) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@300;500;700&display=swap');
    
    .stApp {
        background-color: #030508;
        background-image: linear-gradient(rgba(0, 191, 255, 0.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0, 191, 255, 0.03) 1px, transparent 1px);
        background-size: 30px 30px;
        color: #e0fbfc;
        font-family: 'Rajdhani', sans-serif;
    }
    
    /* Neon Text Inputs */
    .stTextInput > div > div > input {
        background-color: #0b0e11; color: #00BFFF; border: 1px solid #1f2937;
    }
    
    /* Cyber Cards */
    .cyber-card {
        background: rgba(20, 26, 35, 0.8);
        border-left: 4px solid #00BFFF;
        padding: 15px;
        margin-bottom: 15px;
        box-shadow: 0 0 15px rgba(0, 191, 255, 0.1);
    }
    
    /* Buttons */
    .stButton > button {
        border: 1px solid #00BFFF !important;
        color: #00BFFF !important;
        background: transparent !important;
        font-family: 'Orbitron', sans-serif !important;
    }
    .stButton > button:hover {
        box-shadow: 0 0 20px #00BFFF !important;
        color: white !important;
        background: #00BFFF !important;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. SYSTEM FUNCTIONS ---

@st.cache_resource
def init_system():
    return ccxt.kraken({'enableRateLimit': True})

exchange = init_system()

# Функция отправки (использует встроенный токен)
def send_telegram_alert(chat_id, message):
    # Пытаемся взять токен из секретов, если нет - заглушка
    try:
        token = st.secrets["TG_BOT_TOKEN"]
    except:
        st.error("SYSTEM ERROR: Bot Token not found in secrets.")
        return

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message, "parse_mode": "HTML"}
    try:
        requests.post(url, json=payload)
    except:
        pass

# --- 4. SIDEBAR ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/9103/9103608.png", width=80)
    st.markdown("## 💠 SYSTEM CONTROL")
    
    selected_menu = st.radio("MODULE", ["DASHBOARD", "TRADING", "NOTIFICATIONS", "SETTINGS"], label_visibility="collapsed")
    
    st.markdown("---")
    active_pair = st.selectbox("ASSET", ["BTC/USD", "ETH/USD", "SOL/USD"])

# --- 5. MAIN LOGIC ---

# HEADER
st.markdown(f"""
    <div style="border-bottom: 1px solid #00BFFF; padding-bottom: 10px; margin-bottom: 20px;">
        <h1 style="color:#00BFFF; font-family:'Orbitron'">BLUE HORIZON <span style="font-size:15px">[PRO]</span></h1>
    </div>
""", unsafe_allow_html=True)

if selected_menu == "DASHBOARD":
    st.markdown("### 🌍 GLOBAL MARKET OVERVIEW")
    
    # Live Tickers
    coins = ['BTC/USD', 'ETH/USD', 'SOL/USD', 'XRP/USD']
    try:
        tickers = exchange.fetch_tickers(coins)
        cols = st.columns(len(coins))
        for i, symbol in enumerate(coins):
            val = tickers.get(symbol, {'last': 0, 'percentage': 0})
            color = "#00ff41" if val['percentage'] >= 0 else "#ff003c"
            with cols[i]:
                st.markdown(f"""
                <div class="cyber-card">
                    <div style="color:#888; font-size:12px;">{symbol}</div>
                    <div style="font-size:20px; font-weight:bold;">${val['last']:,.2f}</div>
                    <div style="color:{color};">{val['percentage']:.2f}%</div>
                </div>
                """, unsafe_allow_html=True)
    except:
        st.error("Uplink unstable...")

    # Chart
    ohlcv = exchange.fetch_ohlcv(active_pair, timeframe='1h', limit=50)
    df = pd.DataFrame(ohlcv, columns=['time', 'open', 'high', 'low', 'close', 'volume'])
    df['time'] = pd.to_datetime(df['time'], unit='ms')
    
    fig = go.Figure(data=[go.Candlestick(x=df['time'], open=df['open'], high=df['high'], low=df['low'], close=df['close'], increasing_line_color='#00BFFF', decreasing_line_color='#1B2430')])
    fig.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=500)
    st.plotly_chart(fig, use_container_width=True)

elif selected_menu == "TRADING":
    st.markdown("### ⚡ EXECUTION TERMINAL")
    c1, c2 = st.columns([2, 1])
    
    with c1:
        st.markdown('<div class="cyber-card">', unsafe_allow_html=True)
        action = st.radio("SIDE", ["BUY", "SELL"], horizontal=True)
        amt = st.number_input("AMOUNT (USD)", value=1000)
        
        if st.button("EXECUTE ORDER"):
            st.toast("ORDER SENT TO ENGINE", icon="🚀")
            # ПРОВЕРКА: Если уведомления включены - шлем в телегу
            if 'tg_chat_id' in st.session_state and st.session_state.tg_chat_id:
                send_telegram_alert(st.session_state.tg_chat_id, f"🚨 <b>TRADE EXECUTED</b>\nSide: {action}\nPair: {active_pair}\nAmount: ${amt}")
            else:
                st.warning("Connect Telegram in 'Notifications' tab to receive alerts.")
        st.markdown('</div>', unsafe_allow_html=True)

elif selected_menu == "NOTIFICATIONS":
    st.markdown("### 📡 UPLINK CONFIGURATION")
    
    c_setup, c_test = st.columns(2)
    
    with c_setup:
        st.markdown('<div class="cyber-card">', unsafe_allow_html=True)
        st.subheader("1. Connect to Bot")
        
        try:
            bot_name = st.secrets["TG_BOT_NAME"]
        except:
            bot_name = "BotFather" # Заглушка, если секреты не настроены
            
        st.write(f"Click the button below to open our secure bot **@{bot_name}**.")
        st.markdown(f"""
            <a href="https://t.me/{bot_name}?start=connect" target="_blank">
                <button style="
                    background:#00BFFF; color:black; border:none; padding:10px 20px; 
                    font-weight:bold; cursor:pointer; width:100%; border-radius:5px;">
                    👉 OPEN TELEGRAM BOT
                </button>
            </a>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.subheader("2. Link Your ID")
        st.caption("After starting the bot, type /start. Paste your numeric Chat ID below.")
        
        # Сохраняем ID в сессию браузера
        user_chat_id = st.text_input("YOUR CHAT ID", placeholder="Example: 123456789")
        if st.button("🔗 LINK DEVICE"):
            if user_chat_id:
                st.session_state.tg_chat_id = user_chat_id
                st.success("DEVICE PAIRED SUCCESSFULLY")
                send_telegram_alert(user_chat_id, "✅ <b>SYSTEM CONNECTED</b>\nBlue Horizon Terminal is now linked to this device.")
            else:
                st.error("INPUT INVALID")
        
        st.markdown('</div>', unsafe_allow_html=True)

    with c_test:
        if 'tg_chat_id' in st.session_state:
            st.markdown('<div class="cyber-card">', unsafe_allow_html=True)
            st.subheader("System Status: ONLINE 🟢")
            st.write(f"Connected ID: `{st.session_state.tg_chat_id}`")
            
            if st.button("🔔 SEND TEST SIGNAL"):
                send_telegram_alert(st.session_state.tg_chat_id, "⚠️ <b>TEST ALERT</b>\nThis is a test message from Blue Horizon.")
                st.success("Signal Sent.")
            
            if st.button("❌ DISCONNECT"):
                del st.session_state.tg_chat_id
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("System Disconnected. Please link your device.")

elif selected_menu == "SETTINGS":
    st.write("System settings unvailable in demo mode.")
