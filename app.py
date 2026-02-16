import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import ccxt
import numpy as np
import time
import random
from datetime import datetime

# --- 1. CONFIGURATION ---
st.set_page_config(
    page_title="BLUE HORIZON: CYBER TERMINAL",
    layout="wide",
    page_icon="💠",
    initial_sidebar_state="expanded"
)

# --- 2. THE MEGA-CSS INJECTION (100% CUSTOM UI) ---
st.markdown("""
<style>
    /* ИМПОРТ ШРИФТОВ */
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@300;500;700&display=swap');

    /* ОСНОВНОЙ ФОН И СЕТКА */
    .stApp {
        background-color: #030508;
        background-image: 
            linear-gradient(rgba(0, 191, 255, 0.03) 1px, transparent 1px),
            linear-gradient(90deg, rgba(0, 191, 255, 0.03) 1px, transparent 1px);
        background-size: 30px 30px;
        color: #e0fbfc;
        font-family: 'Rajdhani', sans-serif;
    }

    /* СКРОЛЛБАР (HACKER STYLE) */
    ::-webkit-scrollbar { width: 8px; height: 8px; }
    ::-webkit-scrollbar-track { background: #0b0e11; }
    ::-webkit-scrollbar-thumb { background: #00BFFF; border-radius: 2px; }
    ::-webkit-scrollbar-thumb:hover { background: #00e5ff; box-shadow: 0 0 10px #00e5ff; }

    /* ЗАГОЛОВКИ */
    h1, h2, h3 {
        font-family: 'Orbitron', sans-serif;
        text-transform: uppercase;
        letter-spacing: 3px;
        color: #00BFFF;
        text-shadow: 0 0 15px rgba(0, 191, 255, 0.6);
    }

    /* САЙДБАР (СТЕКЛО) */
    section[data-testid="stSidebar"] {
        background: rgba(11, 14, 23, 0.95);
        border-right: 1px solid rgba(0, 191, 255, 0.3);
        box-shadow: 10px 0 30px rgba(0, 0, 0, 0.5);
    }

    /* КАРТОЧКИ (HUD STYLE) */
    .cyber-card {
        background: rgba(20, 26, 35, 0.6);
        border: 1px solid rgba(0, 191, 255, 0.2);
        border-left: 4px solid #00BFFF;
        padding: 20px;
        border-radius: 0px 15px 0px 15px; /* Скошенные углы */
        position: relative;
        overflow: hidden;
        transition: all 0.3s ease;
        margin-bottom: 20px;
    }
    .cyber-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 30px rgba(0, 191, 255, 0.15);
        border-color: #00BFFF;
    }
    .cyber-card::before {
        content: '';
        position: absolute;
        top: 0; left: -100%;
        width: 100%; height: 100%;
        background: linear-gradient(90deg, transparent, rgba(0, 191, 255, 0.1), transparent);
        transition: 0.5s;
    }
    .cyber-card:hover::before {
        left: 100%;
    }

    /* КНОПКИ (NEON GLOW) */
    .stButton > button {
        background: transparent !important;
        border: 1px solid #00BFFF !important;
        color: #00BFFF !important;
        font-family: 'Orbitron', sans-serif !important;
        font-weight: bold;
        text-transform: uppercase;
        border-radius: 0px !important;
        position: relative;
        overflow: hidden;
        transition: 0.3s;
        box-shadow: 0 0 5px rgba(0, 191, 255, 0.2);
    }
    .stButton > button:hover {
        background: #00BFFF !important;
        color: #000 !important;
        box-shadow: 0 0 20px #00BFFF, 0 0 40px #00BFFF;
    }

    /* INPUT FIELDS */
    .stTextInput > div > div > input {
        background-color: #0b0e11;
        color: #00BFFF;
        border: 1px solid #1f2937;
        font-family: 'Rajdhani', sans-serif;
    }
    .stTextInput > div > div > input:focus {
        border-color: #00BFFF;
        box-shadow: 0 0 10px rgba(0, 191, 255, 0.3);
    }

    /* АНИМАЦИИ */
    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(0, 191, 255, 0.4); }
        70% { box-shadow: 0 0 0 10px rgba(0, 191, 255, 0); }
        100% { box-shadow: 0 0 0 0 rgba(0, 191, 255, 0); }
    }
    .live-indicator {
        width: 10px; height: 10px;
        background-color: #00ff41;
        border-radius: 50%;
        display: inline-block;
        animation: pulse 2s infinite;
        margin-right: 5px;
    }

    /* HEADER SCANLINE */
    .scanline {
        width: 100%;
        height: 100px;
        z-index: 9999;
        background: linear-gradient(0deg, rgba(0,0,0,0) 50%, rgba(0, 191, 255, 0.02) 50%), linear-gradient(90deg, rgba(255,0,0,0.06), rgba(0,255,0,0.02), rgba(0,0,255,0.06));
        background-size: 100% 2px, 3px 100%;
        pointer-events: none;
        position: fixed;
        top: 0; left: 0; right: 0; bottom: 0;
    }
</style>
<div class="scanline"></div>
""", unsafe_allow_html=True)

# --- 3. SYSTEM FUNCTIONS ---

@st.cache_resource
def init_system():
    # Фейковая задержка для эффекта "Загрузки ядра"
    return ccxt.kraken({'enableRateLimit': True})

exchange = init_system()

def simulate_boot():
    if 'booted' not in st.session_state:
        placeholder = st.empty()
        logs = [
            "INITIALIZING KRAKEN UPLINK...",
            "BYPASSING GEO-BLOCK PROTOCOLS...",
            "LOADING NEURAL NETWORKS...",
            "DECRYPTING WALLET KEYS...",
            "SYSTEM ONLINE."
        ]
        for log in logs:
            placeholder.code(f">_ {log}")
            time.sleep(0.3)
        placeholder.empty()
        st.session_state.booted = True

# --- 4. SIDEBAR NAVIGATION ---

with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/9103/9103608.png", width=80)
    st.markdown("## 💠 SYSTEM CONTROL")
    
    selected_menu = st.radio("MODULE SELECTOR", 
        ["DASHBOARD", "EXECUTION TERMINAL", "AI SENTINEL", "SETTINGS"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    st.markdown("### 📡 ACTIVE FEED")
    active_pair = st.selectbox("ASSET CLASS", ["BTC/USD", "ETH/USD", "SOL/USD", "XRP/USD"])
    
    st.markdown("---")
    st.caption("v.4.0.2 | UNREGISTERED USER")
    st.caption("SERVER TIME: " + datetime.now().strftime("%H:%M:%S UTC"))

# --- 5. MAIN LOGIC ---

simulate_boot()

# HEADER WITH NEWS TICKER
st.markdown(f"""
    <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #00BFFF; padding-bottom: 10px;">
        <h1>BLUE HORIZON <span style="font-size:16px; color:#00BFFF; vertical-align:middle;">[PRO]</span></h1>
        <div style="text-align: right;">
            <div class="live-indicator"></div><span style="color:#00ff41; font-weight:bold; font-family:'Orbitron'">SYSTEM ONLINE</span>
        </div>
    </div>
    <div style="background: rgba(0, 191, 255, 0.1); padding: 5px; margin-top: 10px; border-radius: 4px;">
        <marquee style="color: #00BFFF; font-family: 'Rajdhani'; font-weight: bold;">
            BTC BREAKS RESISTANCE AT $94k  ///  SEC APPROVES NEW ETF OPTIONS  ///  WHALE ALERT: 5000 ETH MOVED TO COINBASE  ///  AI MODEL PREDICTS BULL RUN
        </marquee>
    </div>
    <br>
""", unsafe_allow_html=True)

if selected_menu == "DASHBOARD":
    # 3D Metric Cards
    col1, col2, col3, col4 = st.columns(4)
    
    # Генерация данных (чтобы не дергать API каждую секунду)
    metrics = {
        "BTC Price": "$94,230.50", "24h Vol": "$42B",
        "Network Hash": "450 EH/s", "Dominance": "52.4%"
    }
    
    for i, (label, value) in enumerate(metrics.items()):
        cols = [col1, col2, col3, col4]
        with cols[i]:
            st.markdown(f"""
            <div class="cyber-card">
                <div style="font-size: 12px; color: #888; text-transform: uppercase;">{label}</div>
                <div style="font-size: 24px; font-weight: 700; color: #fff; text-shadow: 0 0 10px #00BFFF;">{value}</div>
                <div style="height: 2px; width: 100%; background: #00BFFF; margin-top: 10px; box-shadow: 0 0 10px #00BFFF;"></div>
            </div>
            """, unsafe_allow_html=True)

    # Big Chart
    st.markdown("### 📊 MARKET DEPTH VISUALIZER")
    
    # Fake Data for demo visuals
    df = pd.DataFrame({
        "Date": pd.date_range(start="2024-01-01", periods=100),
        "Price": np.cumsum(np.random.randn(100)) + 100,
        "Volume": np.random.randint(10, 100, 100)
    })
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['Date'], y=df['Price'], mode='lines', 
                             line=dict(color='#00BFFF', width=2), fill='tozeroy', 
                             fillcolor='rgba(0, 191, 255, 0.1)'))
    
    fig.update_layout(
        template="plotly_dark",
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showgrid=False),
        yaxis=dict(gridcolor='#1f2937'),
        height=500,
        margin=dict(l=0, r=0, t=0, b=0)
    )
    st.plotly_chart(fig, use_container_width=True)

elif selected_menu == "EXECUTION TERMINAL":
    c1, c2 = st.columns([2, 1])
    
    with c1:
        st.markdown('<div class="cyber-card">', unsafe_allow_html=True)
        st.subheader("⚡ ORDER ENTRY")
        
        col_in1, col_in2 = st.columns(2)
        with col_in1:
            ord_type = st.selectbox("ORDER TYPE", ["LIMIT", "MARKET", "STOP-LOSS"])
        with col_in2:
            leverage = st.slider("LEVERAGE", 1, 100, 10)
            
        amount = st.text_input("AMOUNT (USD)", "1000")
        
        c_buy, c_sell = st.columns(2)
        if c_buy.button("🚀 LONG / BUY"):
            st.toast("ORDER SENT TO KRAKEN NODE [ID: 84930]", icon="✅")
        if c_sell.button("🔻 SHORT / SELL"):
             st.toast("ORDER SENT TO KRAKEN NODE [ID: 84931]", icon="🔴")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Recent Trades Table with custom styling
        st.subheader("RECENT FILLS")
        trades = pd.DataFrame({
            "TIME": ["12:01:44", "12:01:42", "12:00:15"],
            "TYPE": ["BUY", "SELL", "BUY"],
            "PRICE": ["94,230", "94,210", "94,150"],
            "SIZE": ["0.45", "1.20", "0.05"]
        })
        st.table(trades)

    with c2:
        st.markdown('<div class="cyber-card">', unsafe_allow_html=True)
        st.markdown("### 🌊 ORDER BOOK")
        # Visualizing Order Book as bars
        bids = [random.randint(50, 100) for _ in range(10)]
        asks = [random.randint(50, 100) for _ in range(10)]
        
        for b in bids:
            st.markdown(f"""
            <div style="display:flex; justify-content:space-between; margin-bottom:2px;">
                <div style="color:#00ff41;">{94000 - random.randint(1,100)}</div>
                <div style="background:rgba(0,255,65,0.3); width:{b}px; height:18px;"></div>
            </div>""", unsafe_allow_html=True)
        
        st.markdown("<hr style='border-color:#333'>", unsafe_allow_html=True)
        
        for a in asks:
             st.markdown(f"""
            <div style="display:flex; justify-content:space-between; margin-bottom:2px;">
                <div style="color:#ff003c;">{94200 + random.randint(1,100)}</div>
                <div style="background:rgba(255,0,60,0.3); width:{a}px; height:18px;"></div>
            </div>""", unsafe_allow_html=True)
            
        st.markdown('</div>', unsafe_allow_html=True)

elif selected_menu == "AI SENTINEL":
    c_ai1, c_ai2 = st.columns([1, 2])
    
    with c_ai1:
        st.markdown('<div class="cyber-card">', unsafe_allow_html=True)
        st.markdown("### 🤖 NEURAL STATUS")
        st.write("MODEL: LSTM-Transformer-v4")
        st.write("ACCURACY: 87.4%")
        st.write("LAST EPOCH: 4ms ago")
        st.progress(87)
        
        if st.button("RUN DEEP SCAN"):
            with st.status("ANALYZING BLOCKCHAIN...", expanded=True):
                time.sleep(1)
                st.write("Parsing Whales...")
                time.sleep(1)
                st.write("Calculating RSI...")
                st.write("Done.")
            st.balloons()
        st.markdown('</div>', unsafe_allow_html=True)

    with c_ai2:
        # Radar Chart
        categories = ['Volatility', 'Trend', 'Volume', 'Social', 'Macro']
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=[80, 90, 60, 40, 70],
            theta=categories,
            fill='toself',
            name='BTC Analysis',
            line_color='#00BFFF'
        ))
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            template="plotly_dark",
            paper_bgcolor='rgba(0,0,0,0)',
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)

elif selected_menu == "SETTINGS":
    st.header("🔧 CONFIGURATION")
    
    with st.expander("API KEYS (ENCRYPTED)"):
        st.text_input("KRAKEN KEY", type="password")
        st.text_input("KRAKEN SECRET", type="password")
        
    with st.expander("INTERFACE SETTINGS"):
        st.checkbox("ENABLE HAPTIC FEEDBACK", value=True)
        st.checkbox("SHOW LIQUIDATION HEATMAP", value=True)
        st.slider("REFRESH RATE (ms)", 100, 5000, 1000)

# FOOTER
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #555; font-size: 12px; font-family: 'Orbitron'">
    BLUE HORIZON SYSTEMS © 2026 | SECURE CONNECTION SHA-256
</div>
""", unsafe_allow_html=True)
