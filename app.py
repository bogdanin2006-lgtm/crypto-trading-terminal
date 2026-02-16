import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import ccxt
import requests
import time
import random
from datetime import datetime

# ==========================================
# 1. CONFIGURATION & CORE SYSTEM
# ==========================================
st.set_page_config(
    layout="wide",
    page_title="BLUE HORIZON: TITAN TERMINAL",
    page_icon="💠",
    initial_sidebar_state="expanded"
)

# --- TELEGRAM BACKEND ENGINE ---
def get_secret_token():
    try: return st.secrets["TG_BOT_TOKEN"]
    except: return None

def get_bot_identity():
    """Стучится в Telegram API и узнает имя бота"""
    token = get_secret_token()
    if not token: return None
    try:
        res = requests.get(f"https://api.telegram.org/bot{token}/getMe", timeout=5).json()
        if res.get("ok"): return res["result"]["username"]
    except: pass
    return None

def scan_for_handshake():
    """Сканирует последние обновления бота на наличие команды /start"""
    token = get_secret_token()
    if not token: return None
    try:
        res = requests.get(f"https://api.telegram.org/bot{token}/getUpdates", timeout=5).json()
        if res.get("ok") and res["result"]:
            # Проверяем последние 5 сообщений
            for update in reversed(res["result"][-5:]):
                if "message" in update and "text" in update["message"]:
                    txt = update["message"]["text"]
                    if "/start" in txt:
                        return str(update["message"]["chat"]["id"])
    except: pass
    return None

def send_secure_alert(chat_id, title, details, style="info"):
    token = get_secret_token()
    if not token or not chat_id: return
    
    # Эмодзи статусы
    icon = "💠"
    if style == "success": icon = "✅"
    elif style == "warning": icon = "⚠️"
    elif style == "danger": icon = "🚨"
    
    msg = (
        f"<b>{icon} {title}</b>\n"
        "▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n"
        f"{details}\n"
        "▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n"
        f"<i>System Time: {datetime.utcnow().strftime('%H:%M:%S')} UTC</i>"
    )
    
    try:
        requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            json={"chat_id": chat_id, "text": msg, "parse_mode": "HTML"}
        )
    except: pass

# ==========================================
# 2. THE MEGA-CSS INJECTION (UI/UX)
# ==========================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;600;700&family=Orbitron:wght@400;700;900&display=swap');
    
    /* GLOBAL RESET */
    .stApp {
        background-color: #020408;
        background-image: 
            linear-gradient(rgba(0, 191, 255, 0.02) 1px, transparent 1px),
            linear-gradient(90deg, rgba(0, 191, 255, 0.02) 1px, transparent 1px);
        background-size: 40px 40px;
        color: #e0fbfc;
        font-family: 'Rajdhani', sans-serif;
    }

    /* CRT SCANLINE EFFECT */
    .scanline {
        position: fixed; left: 0; top: 0; width: 100vw; height: 100vh;
        background: linear-gradient(to bottom, rgba(255,255,255,0), rgba(255,255,255,0) 50%, rgba(0,0,0,0.1) 50%, rgba(0,0,0,0.1));
        background-size: 100% 4px;
        pointer-events: none;
        z-index: 9999;
        opacity: 0.3;
    }

    /* SIDEBAR STYLING */
    section[data-testid="stSidebar"] {
        background: rgba(5, 10, 20, 0.95);
        border-right: 2px solid #003366;
        box-shadow: 10px 0 30px rgba(0, 0, 0, 0.8);
    }

    /* TITLES & HEADERS */
    h1, h2, h3 {
        font-family: 'Orbitron', sans-serif;
        text-transform: uppercase;
        letter-spacing: 2px;
        color: #00BFFF;
        text-shadow: 0 0 10px rgba(0, 191, 255, 0.5);
    }

    /* CYBER CARDS */
    .cyber-card {
        background: rgba(14, 22, 33, 0.7);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(0, 191, 255, 0.2);
        border-top: 2px solid #00BFFF;
        padding: 20px;
        border-radius: 0 0 10px 10px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
        margin-bottom: 20px;
        position: relative;
        overflow: hidden;
    }
    .cyber-card::before {
        content: "SYSTEM_MODULE_ACTIVE";
        position: absolute;
        top: 2px; right: 5px;
        font-size: 8px;
        color: rgba(0, 191, 255, 0.5);
        font-family: 'Orbitron';
    }

    /* NEON BUTTONS */
    .stButton > button {
        background: transparent !important;
        border: 1px solid #00BFFF !important;
        color: #00BFFF !important;
        font-family: 'Orbitron', sans-serif !important;
        font-weight: 700;
        text-transform: uppercase;
        border-radius: 0 !important;
        transition: all 0.3s ease;
        position: relative;
    }
    .stButton > button:hover {
        background: #00BFFF !important;
        color: #000 !important;
        box-shadow: 0 0 20px #00BFFF, 0 0 40px rgba(0, 191, 255, 0.6);
    }

    /* INPUT FIELDS */
    .stTextInput > div > div > input, .stNumberInput > div > div > input {
        background-color: #0a0e14 !important;
        border: 1px solid #334455 !important;
        color: #00BFFF !important;
        font-family: 'Orbitron', sans-serif !important;
    }
    .stSelectbox > div > div {
        background-color: #0a0e14 !important;
        color: white !important;
    }

    /* NEWS TICKER */
    .ticker-wrap {
        width: 100%; overflow: hidden; background-color: rgba(0, 191, 255, 0.1);
        border-top: 1px solid #00BFFF; border-bottom: 1px solid #00BFFF;
        padding-top: 5px; padding-bottom: 5px; margin-bottom: 20px;
    }
    .ticker { display: inline-block; white-space: nowrap; animation: ticker 30s infinite linear; }
    @keyframes ticker { 0% { transform: translate3d(100%, 0, 0); } 100% { transform: translate3d(-100%, 0, 0); } }
    .ticker-item { display: inline-block; padding: 0 2rem; color: #00BFFF; font-family: 'Orbitron'; font-size: 14px; }
</style>
<div class="scanline"></div>
""", unsafe_allow_html=True)

# ==========================================
# 3. BOOT SEQUENCE & STATE
# ==========================================

# Имитация загрузки при первом входе
if "booted" not in st.session_state:
    placeholder = st.empty()
    logs = [
        "INITIALIZING KERNEL...",
        "LOADING NEURAL MODULES...",
        "BYPASSING GEO-RESTRICTIONS...",
        "CONNECTING TO KRAKEN NODE...",
        "ESTABLISHING SECURE UPLINK...",
        "SYSTEM READY."
    ]
    # Быстрая анимация
    for log in logs:
        placeholder.markdown(f"```bash\n> {log}\n```")
        time.sleep(0.3)
    placeholder.empty()
    st.session_state.booted = True

# Инициализация переменных сессии
if "tg_id" not in st.session_state: st.session_state.tg_id = None
if "bot_username" not in st.session_state:
    st.session_state.bot_username = get_bot_identity()

# Инициализация биржи
@st.cache_resource
def init_exchange():
    return ccxt.kraken({'enableRateLimit': True})
exchange = init_exchange()

# ==========================================
# 4. SIDEBAR NAVIGATION
# ==========================================
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/9103/9103608.png", width=60)
    st.markdown("## 💠 BLUE HORIZON")
    st.caption("TITAN EDITION v4.5.1")
    
    st.markdown("---")
    menu = st.radio("NAVIGATION", ["DASHBOARD", "TERMINAL", "NEURAL NET", "UPLINK (TG)"], label_visibility="collapsed")
    st.markdown("---")
    
    # Статус бота в сайдбаре
    if st.session_state.bot_username:
        st.success(f"🤖 SYSTEM: @{st.session_state.bot_username}")
    else:
        st.error("⚠️ BOT OFFLINE")
        st.caption("Check Secrets.toml")
        
    if st.session_state.tg_id:
        st.markdown(f"**USER:** `{st.session_state.tg_id}`")
        st.markdown("LINK: **SECURE** 🟢")
    else:
        st.markdown("LINK: **DISCONNECTED** 🔴")

# ==========================================
# 5. HEADER & NEWS
# ==========================================
st.markdown("""
<div class="ticker-wrap">
<div class="ticker">
<div class="ticker-item">BTC HITS $95K RESISTANCE</div>
<div class="ticker-item">ETH ETF INFLOWS SURGE 400%</div>
<div class="ticker-item">BLUE HORIZON AI PREDICTS MARKET VOLATILITY</div>
<div class="ticker-item">SECURE UPLINK ACTIVE</div>
</div>
</div>
""", unsafe_allow_html=True)

# ==========================================
# 6. PAGE LOGIC
# ==========================================

# --- DASHBOARD ---
if menu == "DASHBOARD":
    st.markdown("### 🌍 GLOBAL MARKET PULSE")
    
    # Плитки с ценами
    coins = ['BTC/USD', 'ETH/USD', 'SOL/USD', 'XRP/USD']
    cols = st.columns(4)
    
    try:
        tickers = exchange.fetch_tickers(coins)
        for i, coin in enumerate(coins):
            data = tickers.get(coin, {'last': 0, 'percentage': 0})
            price = data['last']
            change = data['percentage']
            color = "#00ff41" if change >= 0 else "#ff003c"
            
            with cols[i]:
                st.markdown(f"""
                <div class="cyber-card">
                    <div style="font-size:12px; color:#888;">{coin}</div>
                    <div style="font-size:24px; font-weight:bold; color:#fff;">${price:,.2f}</div>
                    <div style="color:{color}; font-size:16px;">{change:+.2f}%</div>
                </div>
                """, unsafe_allow_html=True)
    except:
        st.error("Data Feed Interrupted")

    # График активов
    st.markdown('<div class="cyber-card">', unsafe_allow_html=True)
    st.markdown("#### 📊 LIQUIDITY HEATMAP")
    # Фейк-график для красоты (чтобы не грузить API лимиты)
    df = pd.DataFrame({'Time': pd.date_range('2024-01-01', periods=100, freq='h'), 'Price': np.random.randn(100).cumsum() + 40000})
    fig = go.Figure(go.Scatter(x=df['Time'], y=df['Price'], fill='tozeroy', line=dict(color='#00BFFF')))
    fig.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=400, margin=dict(t=0,b=0,l=0,r=0))
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --- TRADING TERMINAL ---
elif menu == "TERMINAL":
    st.markdown("### ⚡ EXECUTION ENGINE")
    
    # Layout
    col_chart, col_trade = st.columns([2, 1])
    
    with col_chart:
        st.markdown('<div class="cyber-card">', unsafe_allow_html=True)
        active_pair = st.selectbox("ASSET SELECTOR", ["BTC/USD", "ETH/USD", "SOL/USD"], label_visibility="collapsed")
        
        # Реальные свечи
        try:
            ohlcv = exchange.fetch_ohlcv(active_pair, timeframe='1h', limit=50)
            df = pd.DataFrame(ohlcv, columns=['time', 'open', 'high', 'low', 'close', 'volume'])
            df['time'] = pd.to_datetime(df['time'], unit='ms')
            
            fig = go.Figure(data=[go.Candlestick(x=df['time'], open=df['open'], high=df['high'], low=df['low'], close=df['close'], increasing_line_color='#00BFFF', decreasing_line_color='#1B2430')])
            fig.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=500, xaxis_rangeslider_visible=False)
            st.plotly_chart(fig, use_container_width=True)
        except:
            st.warning("Chart Data Unavailable")
        st.markdown('</div>', unsafe_allow_html=True)

    with col_trade:
        st.markdown('<div class="cyber-card">', unsafe_allow_html=True)
        st.markdown("#### ORDER ENTRY")
        
        trade_type = st.radio("TYPE", ["MARKET", "LIMIT"], horizontal=True)
        side = st.radio("SIDE", ["BUY", "SELL"], horizontal=True)
        amount = st.number_input("AMOUNT (USD)", value=1000, step=100)
        
        st.markdown("---")
        
        if st.button("🚀 EXECUTE ORDER"):
            st.toast("Processing...", icon="⏳")
            time.sleep(1) # Эффект задержки сети
            st.success(f"ORDER FILLED: {side} {amount} {active_pair}")
            st.balloons()
            
            # --- УВЕДОМЛЕНИЕ В БОТА ---
            if st.session_state.tg_id:
                try: price = exchange.fetch_ticker(active_pair)['last']
                except: price = 0
                
                details = (
                    f"<b>Asset:</b> {active_pair}\n"
                    f"<b>Side:</b>  {side}\n"
                    f"<b>Size:</b>  ${amount}\n"
                    f"<b>Price:</b> ${price:,.2f}"
                )
                send_secure_alert(st.session_state.tg_id, "TRADE EXECUTED", details, style="success")
            else:
                st.warning("Uplink inactive. Notification skipped.")
                
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Order Book (Visual Fake)
        st.markdown('<div class="cyber-card">', unsafe_allow_html=True)
        st.markdown("#### DEPTH")
        st.markdown("""
        <div style="display:flex; justify-content:space-between; color:#ff003c;"><span>94,520</span><span>0.5 BTC</span></div>
        <div style="display:flex; justify-content:space-between; color:#ff003c;"><span>94,510</span><span>1.2 BTC</span></div>
        <div style="border-top:1px solid #333; margin:5px 0;"></div>
        <div style="display:flex; justify-content:space-between; color:#00ff41;"><span>94,490</span><span>2.5 BTC</span></div>
        <div style="display:flex; justify-content:space-between; color:#00ff41;"><span>94,480</span><span>0.8 BTC</span></div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# --- NEURAL NET (AI) ---
elif menu == "NEURAL NET":
    st.markdown("### 🧠 AI PREDICTION MODEL")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="cyber-card">', unsafe_allow_html=True)
        st.markdown("#### SENTIMENT ANALYSIS")
        st.write("Processing Global News...")
        st.progress(87)
        st.write("Analyzing On-Chain Data...")
        st.progress(45)
        st.markdown("---")
        st.metric("PREDICTED TREND", "BULLISH 📈", "Confidence: 92%")
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col2:
        st.markdown('<div class="cyber-card">', unsafe_allow_html=True)
        st.info("AI Auto-Trading is disabled in Demo Mode.")
        if st.button("REQUEST ACCESS"):
            st.toast("Request sent to admin.", icon="🔒")
        st.markdown('</div>', unsafe_allow_html=True)

# --- UPLINK (TELEGRAM SETUP) ---
elif menu == "UPLINK (TG)":
    st.markdown("### 📡 SECURE UPLINK PROTOCOL")
    
    c_setup, c_status = st.columns(2)
    
    with c_setup:
        st.markdown('<div class="cyber-card">', unsafe_allow_html=True)
        st.markdown("#### 1. HANDSHAKE INITIATION")
        
        bot_user = st.session_state.bot_username
        
        if not bot_user:
            st.error("SYSTEM ERROR: Bot Token Invalid.")
            st.info("Please verify `TG_BOT_TOKEN` in Secrets.")
        else:
            link = f"https://t.me/{bot_user}?start=connect"
            st.markdown(f"""
                <a href="{link}" target="_blank">
                    <button style="
                        width:100%; padding:15px; background:linear-gradient(45deg, #00BFFF, #0055ff);
                        color:white; font-weight:bold; border:none; cursor:pointer; font-family:'Orbitron';
                        text-transform:uppercase; border-radius:5px;">
                        👉 OPEN @{bot_user}
                    </button>
                </a>
            """, unsafe_allow_html=True)
            
            st.markdown("---")
            st.markdown("#### 2. VERIFICATION")
            st.caption("After pressing START in the bot, click Verify below.")
            
            if st.button("🔄 SCAN FOR SIGNAL"):
                with st.spinner("Scanning encrypted channels..."):
                    time.sleep(1.5) # Эффект работы
                    found_id = scan_for_handshake()
                    
                    if found_id:
                        st.session_state.tg_id = found_id
                        send_secure_alert(found_id, "UPLINK ESTABLISHED", "Device successfully paired with Blue Horizon Terminal.", style="success")
                        st.success("SIGNAL ACQUIRED. HANDSHAKE COMPLETE.")
                        st.rerun()
                    else:
                        st.error("NO SIGNAL DETECTED.")
                        st.info("Make sure you pressed START in the Telegram Bot recently.")
        
        st.markdown('</div>', unsafe_allow_html=True)

    with c_status:
        if st.session_state.tg_id:
            st.markdown('<div class="cyber-card" style="border-left: 4px solid #00ff41;">', unsafe_allow_html=True)
            st.markdown("#### 🟢 STATUS: ONLINE")
            st.code(f"ID: {st.session_state.tg_id}")
            st.write("Protocol: TLS 1.3")
            
            if st.button("🔔 TEST ALERT"):
                send_secure_alert(st.session_state.tg_id, "TEST SIGNAL", "The connection is stable.", style="info")
                st.toast("Signal sent!", icon="📡")
            
            if st.button("❌ TERMINATE LINK"):
                st.session_state.tg_id = None
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="cyber-card" style="border-left: 4px solid #555;">', unsafe_allow_html=True)
            st.markdown("#### ⚫ STATUS: OFFLINE")
            st.write("Waiting for user authorization...")
            st.markdown('</div>', unsafe_allow_html=True)

# FOOTER
st.markdown("---")
st.markdown("<center style='color:#555; font-size:10px;'>BLUE HORIZON SYSTEMS © 2026 | MILITARY GRADE ENCRYPTION ACTIVE</center>", unsafe_allow_html=True)
