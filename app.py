import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import ccxt
import numpy as np
import requests
import time
from datetime import datetime

# --- 1. CONFIGURATION (НАСТРОЙКИ) ---
st.set_page_config(layout="wide", page_title="Blue Horizon: Prime", page_icon="💠")

# 🔥 ВПИШИ ИМЯ СВОЕГО БОТА СЮДА (без @) 🔥
# Например: "MySuperTradeBot"
YOUR_BOT_NAME = "CryptoTerminal_Bot" 

# --- 2. STYLES (CYBERPUNK) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;600;700&family=Orbitron:wght@500;900&display=swap');
    
    .stApp {
        background-color: #050505;
        background-image: radial-gradient(circle at 50% 50%, #0a101f 0%, #000000 100%);
        color: #e0fbfc;
        font-family: 'Rajdhani', sans-serif;
    }
    
    /* NEON ACCENTS */
    .highlight { color: #00BFFF; font-weight: bold; }
    .success { color: #00ff41; }
    .danger { color: #ff003c; }

    /* CARDS */
    .cyber-card {
        background: rgba(16, 20, 28, 0.8);
        border: 1px solid rgba(0, 191, 255, 0.1);
        border-left: 3px solid #00BFFF;
        padding: 20px;
        border-radius: 4px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
    }
    
    /* BUTTONS */
    .stButton > button {
        background: linear-gradient(90deg, rgba(0,191,255,0.1) 0%, rgba(0,0,0,0) 100%);
        border: 1px solid #00BFFF !important;
        color: #00BFFF !important;
        font-family: 'Orbitron', sans-serif !important;
        text-transform: uppercase;
        letter-spacing: 1px;
        width: 100%;
    }
    .stButton > button:hover {
        box-shadow: 0 0 15px #00BFFF !important;
        background: #00BFFF !important;
        color: #000 !important;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. BACKEND ---
@st.cache_resource
def init_exchange():
    return ccxt.kraken({'enableRateLimit': True})

exchange = init_exchange()

def send_smart_notification(chat_id, type="trade", data=None):
    # Пытаемся найти токен в секретах, если нет - ничего не делаем (безопасно)
    try:
        token = st.secrets["TG_BOT_TOKEN"]
    except:
        st.toast("⚠️ Error: TG_BOT_TOKEN not found in secrets", icon="❌")
        return

    if type == "connect":
        msg = (
            "<b>💠 UPLINK ESTABLISHED</b>\n\n"
            "Terminal <i>Blue Horizon</i> connected successfully.\n"
            f"<i>Secure ID:</i> <code>{chat_id}</code>\n"
            "<i>Status:</i> 🟢 <b>ONLINE</b>"
        )
    elif type == "trade":
        emoji = "🟢" if data['side'] == "BUY" else "🔴"
        msg = (
            f"<b>{emoji} EXECUTION REPORT</b>\n\n"
            f"<b>PAIR:</b>   {data['pair']}\n"
            f"<b>SIDE:</b>   <b>{data['side']}</b>\n"
            f"<b>SIZE:</b>   {data['amount']} USD\n"
            f"<b>PRICE:</b>  ${data['price']:,.2f}\n"
            f"──────────────────\n"
            f"<i>Time: {datetime.now().strftime('%H:%M UTC')}</i>"
        )
    
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    try:
        requests.post(url, json={"chat_id": chat_id, "text": msg, "parse_mode": "HTML"})
    except:
        pass

# --- 4. UI LAYOUT ---
with st.sidebar:
    st.markdown("## 💠 BLUE HORIZON")
    menu = st.radio("INTERFACE", ["MARKET", "EXECUTION", "UPLINK (TG)"], label_visibility="collapsed")
    st.markdown("---")
    pair = st.selectbox("SECURE FEED", ["BTC/USD", "ETH/USD", "SOL/USD"])

# --- 5. MAIN LOGIC ---

# HEADER
st.markdown(f"""
    <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid #00BFFF; padding-bottom:15px; margin-bottom:20px;">
        <div>
            <h1 style="margin:0; font-family:'Orbitron'; color:#00BFFF;">BLUE HORIZON <span style="font-size:0.5em; color:white;">PRIME</span></h1>
            <small style="color:#888;">INSTITUTIONAL GRADE TERMINAL</small>
        </div>
        <div style="text-align:right;">
            <div style="color:#00ff41; font-weight:bold;">● SYSTEM READY</div>
        </div>
    </div>
""", unsafe_allow_html=True)

if menu == "MARKET":
    c1, c2, c3 = st.columns(3)
    # Получаем реальные данные для шапки
    try:
        ticker = exchange.fetch_ticker(pair)
        price = ticker['last']
        change = ticker['percentage']
        vol = ticker['baseVolume']
    except:
        price, change, vol = 0, 0, 0

    c1.metric("PRICE", f"${price:,.2f}", f"{change:.2f}%")
    c2.metric("24H VOL", f"{vol:,.0f}", "High")
    c3.metric("AI SENTIMENT", "NEUTRAL", "Wait")
    
    st.markdown("### 📊 PRICE ACTION")
    ohlcv = exchange.fetch_ohlcv(pair, timeframe='1h', limit=50)
    df = pd.DataFrame(ohlcv, columns=['time', 'open', 'high', 'low', 'close', 'volume'])
    df['time'] = pd.to_datetime(df['time'], unit='ms')
    
    fig = go.Figure(data=[go.Candlestick(x=df['time'], open=df['open'], high=df['high'], low=df['low'], close=df['close'], increasing_line_color='#00BFFF', decreasing_line_color='#1B2430')])
    fig.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=500)
    st.plotly_chart(fig, use_container_width=True)

elif menu == "EXECUTION":
    c1, c2 = st.columns([2, 1])
    with c1:
        st.markdown('<div class="cyber-card">', unsafe_allow_html=True)
        st.subheader("⚡ INSTANT ORDER")
        
        side = st.radio("SIDE", ["BUY", "SELL"], horizontal=True)
        amt = st.number_input("SIZE (USD)", value=1000)
        
        if st.button("AUTHORIZE TRANSACTION"):
            st.toast("ORDER SENT TO ENGINE...", icon="🚀")
            time.sleep(1)
            st.success(f"{side} ORDER FILLED")
            
            # --- UPLINK CHECK ---
            if 'tg_id' in st.session_state:
                # Берем цену для уведомления
                try: 
                    price = exchange.fetch_ticker(pair)['last']
                except: 
                    price = 0
                
                send_smart_notification(
                    st.session_state.tg_id, 
                    type="trade", 
                    data={'pair': pair, 'side': side, 'amount': amt, 'price': price}
                )
            else:
                st.warning("Uplink not active. Connect Telegram to receive report.")
        st.markdown('</div>', unsafe_allow_html=True)

elif menu == "UPLINK (TG)":
    c_login, c_info = st.columns(2)
    
    with c_login:
        st.markdown('<div class="cyber-card">', unsafe_allow_html=True)
        st.markdown("### 📡 SECURE CONNECTION")
        st.write("Link your personal device to receive real-time execution reports.")
        
        # --- КНОПКА ССЫЛКИ НА БОТА ---
        # Ссылка формируется автоматически из переменной в начале кода
        bot_link = f"https://t.me/{YOUR_BOT_NAME}?start=auth"
        
        st.markdown(f"""
            <a href="{bot_link}" target="_blank" style="text-decoration:none;">
                <div style="
                    background: linear-gradient(45deg, #00BFFF, #0088cc); 
                    color: white; padding: 15px; 
                    text-align: center; font-weight: bold; border-radius: 5px;
                    font-family: 'Orbitron'; cursor: pointer; margin: 20px 0;
                    box-shadow: 0 0 15px rgba(0,191,255,0.4);">
                    👉 OPEN TELEGRAM UPLINK
                </div>
            </a>
        """, unsafe_allow_html=True)
        
        st.info("1. Click button above.\n2. Press START in Telegram.\n3. Enter the ID you receive below.")
        
        # Ввод ID
        uplink_id = st.text_input("ENTER UPLINK ID", placeholder="Example: 123456789")
        
        if st.button("VERIFY CONNECTION"):
            if uplink_id:
                st.session_state.tg_id = uplink_id
                st.balloons()
                send_smart_notification(uplink_id, type="connect")
                st.success("HANDSHAKE COMPLETE. CHANNEL SECURE.")
            else:
                st.error("Please enter a valid ID.")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
    with c_info:
        if 'tg_id' in st.session_state:
            st.markdown('<div class="cyber-card" style="border-left: 3px solid #00ff41;">', unsafe_allow_html=True)
            st.markdown("### 🟢 STATUS: ONLINE")
            st.write(f"**Linked ID:** `{st.session_state.tg_id}`")
            
            if st.button("TEST SIGNAL"):
                send_smart_notification(st.session_state.tg_id, type="connect")
                st.info("Signal transmitted.")
            
            if st.button("TERMINATE CONNECTION"):
                del st.session_state.tg_id
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("System waiting for authorization...")
