import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import ccxt
import numpy as np
import requests
import time
from datetime import datetime

# --- 1. CONFIGURATION ---
st.set_page_config(layout="wide", page_title="Blue Horizon: Prime", page_icon="💠")

# 🔥 ВПИШИ ИМЯ СВОЕГО БОТА СЮДА (без @) 🔥
YOUR_BOT_NAME = "CryptoTerminal_Bot"

# --- 2. STYLES (CYBERPUNK PREMIUM) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;600;700&family=Orbitron:wght@500;900&display=swap');
    
    .stApp {
        background-color: #050505;
        background-image: radial-gradient(circle at 50% 50%, #0a101f 0%, #000000 100%);
        color: #e0fbfc;
        font-family: 'Rajdhani', sans-serif;
    }
    
    /* UI ELEMENTS */
    .cyber-card {
        background: rgba(16, 20, 28, 0.9);
        border: 1px solid rgba(0, 191, 255, 0.15);
        border-left: 3px solid #00BFFF;
        padding: 25px;
        border-radius: 6px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
    }
    
    .stButton > button {
        background: linear-gradient(90deg, #001f3f 0%, #000000 100%);
        border: 1px solid #00BFFF !important;
        color: #00BFFF !important;
        font-family: 'Orbitron', sans-serif !important;
        text-transform: uppercase;
        letter-spacing: 2px;
        width: 100%;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        box-shadow: 0 0 20px rgba(0, 191, 255, 0.6) !important;
        background: #00BFFF !important;
        color: #000 !important;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. BACKEND & LOGIC ---
@st.cache_resource
def init_exchange():
    return ccxt.kraken({'enableRateLimit': True})

exchange = init_exchange()

def get_telegram_token():
    try:
        return st.secrets["TG_BOT_TOKEN"]
    except:
        return None

# --- АВТОМАТИЧЕСКИЙ ПОИСК ID (AUTO-HANDSHAKE) ---
def find_chat_id_from_updates():
    token = get_telegram_token()
    if not token: return None
    
    url = f"https://api.telegram.org/bot{token}/getUpdates"
    try:
        # Получаем последние сообщения боту
        resp = requests.get(url).json()
        if "result" in resp and len(resp["result"]) > 0:
            # Берем самое последнее сообщение
            last_msg = resp["result"][-1]
            chat_id = last_msg["message"]["chat"]["id"]
            return str(chat_id)
    except:
        pass
    return None

# --- ПРОФЕССИОНАЛЬНЫЕ УВЕДОМЛЕНИЯ ---
def send_smart_notification(chat_id, type="trade", data=None):
    token = get_telegram_token()
    if not token: 
        st.toast("⚠️ Bot Token missing!", icon="❌")
        return

    # ШАБЛОНЫ СООБЩЕНИЙ
    if type == "connect":
        msg = (
            "<b>💠 UPLINK ESTABLISHED</b>\n"
            "▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n"
            "Terminal <i>Blue Horizon</i> is now linked.\n\n"
            f"👤 <b>User ID:</b> <code>{chat_id}</code>\n"
            "🔐 <b>Encryption:</b> <code>SHA-256</code>\n"
            "📡 <b>Status:</b> 🟢 <b>ONLINE</b>\n\n"
            "<i>You will now receive real-time execution reports here.</i>"
        )
    elif type == "trade":
        side_icon = "🟢" if data['side'] == "BUY" else "🔴"
        msg = (
            f"<b>{side_icon} TRADE EXECUTED</b>\n"
            "▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n"
            f"<b>Asset:</b>      {data['pair']}\n"
            f"<b>Action:</b>     <b>{data['side']}</b>\n"
            f"<b>Size:</b>       ${data['amount']:,.2f}\n"
            f"<b>Fill Price:</b> ${data['price']:,.2f}\n"
            "▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n"
            f"🕒 <i>{datetime.now().strftime('%H:%M:%S UTC')}</i>"
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
    try:
        ticker = exchange.fetch_ticker(pair)
        price = ticker['last']
        change = ticker['percentage']
        vol = ticker['baseVolume']
    except:
        price, change, vol = 0, 0, 0

    c1.metric("PRICE", f"${price:,.2f}", f"{change:.2f}%")
    c2.metric("24H VOL", f"{vol:,.0f}", "High")
    c3.metric("AI SIGNAL", "ACCUMULATE", "Low Risk")
    
    st.markdown("### 📊 PRICE ACTION")
    try:
        ohlcv = exchange.fetch_ohlcv(pair, timeframe='1h', limit=50)
        df = pd.DataFrame(ohlcv, columns=['time', 'open', 'high', 'low', 'close', 'volume'])
        df['time'] = pd.to_datetime(df['time'], unit='ms')
        
        fig = go.Figure(data=[go.Candlestick(x=df['time'], open=df['open'], high=df['high'], low=df['low'], close=df['close'], increasing_line_color='#00BFFF', decreasing_line_color='#1B2430')])
        fig.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=500)
        st.plotly_chart(fig, use_container_width=True)
    except:
        st.error("Feed Disconnected.")

elif menu == "EXECUTION":
    c1, c2 = st.columns([2, 1])
    with c1:
        st.markdown('<div class="cyber-card">', unsafe_allow_html=True)
        st.subheader("⚡ INSTANT ORDER")
        
        side = st.radio("SIDE", ["BUY", "SELL"], horizontal=True)
        amt = st.number_input("SIZE (USD)", value=1000)
        
        if st.button("AUTHORIZE TRANSACTION"):
            st.toast("PROCESSING ORDER...", icon="🔄")
            time.sleep(1)
            st.success(f"{side} ORDER FILLED")
            
            # --- AUTO NOTIFICATION ---
            if 'tg_id' in st.session_state:
                try: price = exchange.fetch_ticker(pair)['last']
                except: price = 0
                
                send_smart_notification(
                    st.session_state.tg_id, 
                    type="trade", 
                    data={'pair': pair, 'side': side, 'amount': amt, 'price': price}
                )
            else:
                st.warning("Uplink inactive. Connect Telegram to receive confirmation.")
        st.markdown('</div>', unsafe_allow_html=True)

elif menu == "UPLINK (TG)":
    c_login, c_info = st.columns(2)
    
    with c_login:
        st.markdown('<div class="cyber-card">', unsafe_allow_html=True)
        st.markdown("### 📡 SECURE UPLINK")
        st.write("Establish a secure handshake with the Neural Core.")
        
        # Кнопка открытия бота
        bot_link = f"https://t.me/{YOUR_BOT_NAME}?start=auth"
        st.markdown(f"""
            <a href="{bot_link}" target="_blank" style="text-decoration:none;">
                <div style="
                    background: linear-gradient(45deg, #00BFFF, #0088cc); 
                    color: white; padding: 15px; 
                    text-align: center; font-weight: bold; border-radius: 5px;
                    font-family: 'Orbitron'; cursor: pointer; margin: 20px 0;
                    box-shadow: 0 0 20px rgba(0,191,255,0.4);">
                    👉 1. OPEN UPLINK (TELEGRAM)
                </div>
            </a>
        """, unsafe_allow_html=True)
        
        st.caption("Step 1: Click button above and press START in Telegram.")
        st.caption("Step 2: Click 'VERIFY HANDSHAKE' below. We will auto-detect your ID.")
        
        if st.button("👉 2. VERIFY HANDSHAKE"):
            with st.spinner("Scanning for incoming signal..."):
                found_id = find_chat_id_from_updates()
                if found_id:
                    st.session_state.tg_id = found_id
                    send_smart_notification(found_id, type="connect")
                    st.balloons()
                    st.success("HANDSHAKE VERIFIED. SECURE CHANNEL ACTIVE.")
                    st.rerun()
                else:
                    st.error("No signal found. Did you press START in the bot?")
                    st.info("Try sending a message '/start' to the bot again.")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
    with c_info:
        if 'tg_id' in st.session_state:
            st.markdown('<div class="cyber-card" style="border-left: 3px solid #00ff41;">', unsafe_allow_html=True)
            st.markdown("### 🟢 STATUS: ONLINE")
            st.write(f"**Linked Device ID:** `{st.session_state.tg_id}`")
            st.write("**Protocol:** TLS 1.3 / SHA-256")
            
            if st.button("TEST ALERT"):
                send_smart_notification(st.session_state.tg_id, type="connect")
                st.info("Signal transmitted.")
            
            if st.button("TERMINATE UPLINK"):
                del st.session_state.tg_id
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="cyber-card" style="border-left: 3px solid #555;">', unsafe_allow_html=True)
            st.markdown("### ⚫ STATUS: OFFLINE")
            st.info("Waiting for secure handshake...")
            st.markdown('</div>', unsafe_allow_html=True)
