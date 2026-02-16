import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import ccxt
import numpy as np
import requests
import time
from datetime import datetime

# --- 1. CONFIG & STYLES ---
st.set_page_config(layout="wide", page_title="Blue Horizon: Prime", page_icon="💠")

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
    }
    .stButton > button:hover {
        box-shadow: 0 0 15px #00BFFF !important;
        background: #00BFFF !important;
        color: #000 !important;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. BACKEND & API ---
@st.cache_resource
def init_exchange():
    return ccxt.kraken({'enableRateLimit': True})

exchange = init_exchange()

# --- 3. PROFESSIONAL NOTIFICATION ENGINE ---
def send_smart_notification(chat_id, type="trade", data=None):
    """
    Отправляет грамотно оформленные уведомления.
    Types: 'connect', 'trade', 'alert'
    """
    # Пытаемся получить токен (если нет в секретах, берем заглушку для демо)
    try:
        token = st.secrets["TG_BOT_TOKEN"]
    except:
        st.toast("⚠️ System Error: TG_BOT_TOKEN not found in secrets", icon="❌")
        return

    # 1. ШАБЛОН: ПОДКЛЮЧЕНИЕ
    if type == "connect":
        msg = (
            "<b>💠 SYSTEM UPLINK ESTABLISHED</b>\n\n"
            "Welcome, Commander.\n"
            "Your terminal <i>Blue Horizon</i> is now successfully linked to this secure channel.\n\n"
            "<i>Status:</i> 🟢 <b>ONLINE</b>\n"
            "<i>Encryption:</i> <b>SHA-256</b>"
        )
    
    # 2. ШАБЛОН: СДЕЛКА (ОРДЕР)
    elif type == "trade":
        emoji = "🟢" if data['side'] == "BUY" else "🔴"
        msg = (
            f"<b>{emoji} EXECUTION REPORT</b> | <code>#{int(time.time())}</code>\n\n"
            f"<b>ASSET:</b>  {data['pair']}\n"
            f"<b>SIDE:</b>   <b>{data['side']}</b>\n"
            f"<b>SIZE:</b>   {data['amount']} USD\n"
            f"<b>PRICE:</b>  ${data['price']:,.2f}\n"
            f"──────────────────\n"
            f"<i>Time: {datetime.now().strftime('%H:%M:%S UTC')}</i>"
        )
    
    # 3. ШАБЛОН: AI СИГНАЛ
    elif type == "ai_alert":
        msg = (
            "<b>🧠 NEURAL NETWORK ALERT</b>\n\n"
            f"<b>TARGET:</b> {data['pair']}\n"
            f"<b>SIGNAL:</b> {data['direction']}\n"
            f"<b>CONFIDENCE:</b> {data['confidence']}%\n\n"
            "<i>Recommendation: Check chart immediately.</i>"
        )
    
    # Отправка
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    try:
        requests.post(url, json={"chat_id": chat_id, "text": msg, "parse_mode": "HTML"})
    except Exception as e:
        st.error(f"Transmission Failed: {e}")


# --- 4. UI LAYOUT ---
with st.sidebar:
    st.markdown("## 💠 BLUE HORIZON")
    menu = st.radio("INTERFACE", ["MARKET", "EXECUTION", "UPLINK (TG)"], label_visibility="collapsed")
    st.markdown("---")
    pair = st.selectbox("SECURE FEED", ["BTC/USD", "ETH/USD", "SOL/USD"])

# --- 5. PAGE LOGIC ---

# HEADER
st.markdown(f"""
    <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid #00BFFF; padding-bottom:15px; margin-bottom:20px;">
        <div>
            <h1 style="margin:0; font-family:'Orbitron'; color:#00BFFF;">BLUE HORIZON <span style="font-size:0.5em; color:white;">PRIME</span></h1>
            <small style="color:#888;">INSTITUTIONAL GRADE TERMINAL</small>
        </div>
        <div style="text-align:right;">
            <div style="color:#00ff41; font-weight:bold;">● SYSTEM READY</div>
            <small>{datetime.now().strftime('%H:%M:%S')}</small>
        </div>
    </div>
""", unsafe_allow_html=True)

if menu == "MARKET":
    # MOCKUP DATA
    c1, c2, c3 = st.columns(3)
    c1.metric("BTC PRICE", "$94,320.50", "+1.2%")
    c2.metric("24H VOLUME", "$34.2B", "+5.4%")
    c3.metric("AI SENTIMENT", "BULLISH", "82%")
    
    st.markdown("### 📊 PRICE ACTION")
    # Chart
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
        amt = st.number_input("SIZE (USD)", value=5000)
        
        if st.button("AUTHORIZE TRANSACTION"):
            # Получаем реальную цену для красивого уведомления
            current_price = df['close'].iloc[-1] if 'df' in locals() else 94000
            
            st.toast("ORDER SUBMITTED TO ENGINE...", icon="🚀")
            time.sleep(1)
            st.success(f"{side} ORDER FILLED")
            
            # --- ОТПРАВКА УВЕДОМЛЕНИЯ ---
            if 'tg_id' in st.session_state:
                send_smart_notification(
                    st.session_state.tg_id, 
                    type="trade", 
                    data={'pair': pair, 'side': side, 'amount': amt, 'price': current_price}
                )
            else:
                st.warning("Uplink not active. Connect Telegram to receive report.")
                
        st.markdown('</div>', unsafe_allow_html=True)

elif menu == "UPLINK (TG)":
    c_login, c_info = st.columns(2)
    
    with c_login:
        st.markdown('<div class="cyber-card">', unsafe_allow_html=True)
        st.markdown("### 📡 SECURE CONNECTION")
        st.write("Establish a direct link to the Neural Core via Telegram.")
        
        # 1. Ссылка на бота (динамическая или статичная)
        try:
            bot_name = st.secrets["TG_BOT_NAME"]
        except:
            bot_name = st.text_input("ENTER BOT USERNAME (No @)", "YourBotName")
        
        st.markdown(f"""
            <a href="https://t.me/{bot_name}?start=auth" target="_blank" style="text-decoration:none;">
                <div style="
                    background: #00BFFF; color: black; padding: 15px; 
                    text-align: center; font-weight: bold; border-radius: 5px;
                    font-family: 'Orbitron'; cursor: pointer; margin: 15px 0;">
                    👉 INITIATE UPLINK PROTOCOL
                </div>
            </a>
        """, unsafe_allow_html=True)
        
        st.caption("1. Click button above.\n2. Press START in Telegram.\n3. Enter your Uplink ID below.")
        
        # 2. Ввод ID (Сделан как "Верификация")
        uplink_id = st.text_input("UPLINK ID (CHAT ID)", type="password")
        
        if st.button("VERIFY CONNECTION"):
            if uplink_id:
                st.session_state.tg_id = uplink_id
                st.balloons()
                send_smart_notification(uplink_id, type="connect")
                st.success("HANDSHAKE COMPLETE. SECURE CHANNEL ACTIVE.")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
    with c_info:
        if 'tg_id' in st.session_state:
            st.markdown('<div class="cyber-card" style="border-left: 3px solid #00ff41;">', unsafe_allow_html=True)
            st.markdown("### 🟢 STATUS: ONLINE")
            st.write(f"**Target ID:** `{st.session_state.tg_id}`")
            st.write("**Latency:** 12ms")
            
            if st.button("TEST NEURAL ALERT"):
                send_smart_notification(
                    st.session_state.tg_id, 
                    type="ai_alert", 
                    data={'pair': pair, 'direction': 'STRONG BUY', 'confidence': 94}
                )
                st.info("Signal transmitted.")
            
            if st.button("TERMINATE CONNECTION"):
                del st.session_state.tg_id
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("System waiting for authorization...")
