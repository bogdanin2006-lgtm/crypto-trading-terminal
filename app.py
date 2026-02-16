iimport streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import ccxt
import numpy as np
import time
import random
from datetime import datetime, timedelta

# ==========================================
# 1. CORE SYSTEM CONFIGURATION
# ==========================================
st.set_page_config(
    layout="wide",
    page_title="TITANIUM-X TERMINAL",
    page_icon="💠",
    initial_sidebar_state="expanded"
)

# --- Инициализация биржи (Только для чтения данных) ---
@st.cache_resource
def init_exchange():
    return ccxt.kraken({'enableRateLimit': True})

exchange = init_exchange()

# ==========================================
# 2. MEGA-CSS INJECTION (THE VISUAL ENGINE)
# ==========================================
st.markdown("""
<style>
    /* ПОДКЛЮЧЕНИЕ ШРИФТОВ */
    @import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@300;500;700&family=Orbitron:wght@400;700;900&family=Share+Tech+Mono&display=swap');

    /* ГЛОБАЛЬНЫЙ СТИЛЬ */
    .stApp {
        background-color: #030509;
        background-image: 
            linear-gradient(rgba(0, 255, 255, 0.03) 1px, transparent 1px),
            linear-gradient(90deg, rgba(0, 255, 255, 0.03) 1px, transparent 1px);
        background-size: 50px 50px;
        color: #e0fbfc;
        font-family: 'Rajdhani', sans-serif;
    }

    /* СКАН-ЛИНИЯ (CRT EFFECT) */
    .scanline {
        width: 100%;
        height: 100px;
        z-index: 9999;
        background: linear-gradient(0deg, rgba(0,0,0,0) 50%, rgba(0, 255, 255, 0.02) 50%), linear-gradient(90deg, rgba(255,0,0,0.06), rgba(0,255,0,0.02), rgba(0,0,255,0.06));
        background-size: 100% 2px, 3px 100%;
        pointer-events: none;
        position: fixed;
        top: 0; left: 0; right: 0; bottom: 0;
        animation: scanline 10s linear infinite;
    }

    /* ДИЗАЙН САЙДБАРА */
    section[data-testid="stSidebar"] {
        background: rgba(8, 12, 20, 0.95);
        border-right: 2px solid #00BFFF;
        box-shadow: 15px 0 40px rgba(0, 191, 255, 0.1);
    }
    
    /* ЗАГОЛОВКИ */
    h1, h2, h3 {
        font-family: 'Orbitron', sans-serif;
        color: #00BFFF;
        text-transform: uppercase;
        letter-spacing: 3px;
        text-shadow: 0 0 15px rgba(0, 191, 255, 0.7);
    }

    /* КИБЕР-КАРТОЧКИ (Стекло + Неон) */
    .cyber-card {
        background: rgba(14, 20, 30, 0.7);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(0, 191, 255, 0.2);
        border-left: 4px solid #00BFFF;
        padding: 25px;
        border-radius: 0px 15px 0px 15px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
        margin-bottom: 20px;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    .cyber-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 40px rgba(0, 191, 255, 0.2);
        border-color: #00BFFF;
    }
    
    /* ДЕКОРАТИВНЫЕ ЭЛЕМЕНТЫ КАРТОЧЕК */
    .cyber-card::after {
        content: "SYS_RDY";
        position: absolute;
        bottom: 5px; right: 10px;
        font-family: 'Share Tech Mono', monospace;
        font-size: 10px;
        color: rgba(0, 191, 255, 0.4);
    }

    /* КНОПКИ (NEON GLOW) */
    .stButton > button {
        background: transparent !important;
        border: 1px solid #00BFFF !important;
        color: #00BFFF !important;
        font-family: 'Orbitron', sans-serif !important;
        font-weight: 800;
        text-transform: uppercase;
        border-radius: 4px !important;
        transition: all 0.4s ease;
        padding: 15px 0;
        box-shadow: 0 0 5px rgba(0, 191, 255, 0.3);
    }
    .stButton > button:hover {
        background: #00BFFF !important;
        color: #000 !important;
        box-shadow: 0 0 25px #00BFFF, 0 0 50px rgba(0, 191, 255, 0.6);
        transform: scale(1.02);
    }

    /* ИНПУТЫ И СЕЛЕКТОРЫ */
    .stTextInput>div>div>input, .stNumberInput>div>div>input, .stSelectbox>div>div {
        background-color: #0a0e14 !important;
        color: #00BFFF !important;
        border: 1px solid #1f2937 !important;
        font-family: 'Share Tech Mono', monospace !important;
    }
    .stSelectbox > div > div {
        color: white !important;
    }

    /* ТАБЛИЦЫ */
    [data-testid="stDataFrame"] {
        border: 1px solid rgba(0, 191, 255, 0.2);
        border-radius: 5px;
    }

    /* SCROLLBAR */
    ::-webkit-scrollbar { width: 8px; background: #050505; }
    ::-webkit-scrollbar-thumb { background: #00BFFF; border-radius: 2px; }

    /* NEWS TICKER ANIMATION */
    .ticker-container {
        width: 100%;
        overflow: hidden;
        background: rgba(0, 191, 255, 0.05);
        border-top: 1px solid #00BFFF;
        border-bottom: 1px solid #00BFFF;
        padding: 8px 0;
        margin-bottom: 25px;
    }
    .ticker-text {
        display: inline-block;
        white-space: nowrap;
        animation: marquee 30s linear infinite;
        font-family: 'Orbitron';
        color: #00BFFF;
        font-size: 14px;
    }
    @keyframes marquee {
        0% { transform: translate(100%, 0); }
        100% { transform: translate(-100%, 0); }
    }
    
    /* METRIC LABELS */
    [data-testid="stMetricLabel"] { color: #888 !important; font-family: 'Rajdhani'; }
    [data-testid="stMetricValue"] { color: #fff !important; font-family: 'Orbitron'; text-shadow: 0 0 10px rgba(255,255,255,0.3); }
    
</style>
<div class="scanline"></div>
""", unsafe_allow_html=True)

# ==========================================
# 3. HELPER FUNCTIONS (DATA ENGINE)
# ==========================================

def get_market_data(pair):
    """Safe data fetching with simulated fallback"""
    try:
        ticker = exchange.fetch_ticker(pair)
        return {
            'price': ticker['last'],
            'change': ticker['percentage'],
            'high': ticker['high'],
            'low': ticker['low'],
            'vol': ticker['baseVolume']
        }
    except:
        # Fallback for demo
        base = 94000 if 'BTC' in pair else 3000
        return {
            'price': base + random.uniform(-100, 100),
            'change': random.uniform(-2, 2),
            'high': base + 200,
            'low': base - 200,
            'vol': random.uniform(1000, 5000)
        }

def generate_chart_data(pair, limit=100):
    """Generates chart data if API fails or for extended visuals"""
    try:
        ohlcv = exchange.fetch_ohlcv(pair, timeframe='1h', limit=limit)
        df = pd.DataFrame(ohlcv, columns=['time', 'open', 'high', 'low', 'close', 'volume'])
        df['time'] = pd.to_datetime(df['time'], unit='ms')
        return df
    except:
        dates = pd.date_range(end=datetime.now(), periods=limit, freq='h')
        base = 90000
        closes = np.cumsum(np.random.randn(limit)) * 100 + base
        return pd.DataFrame({
            'time': dates,
            'open': closes - 50,
            'high': closes + 100,
            'low': closes - 100,
            'close': closes,
            'volume': np.random.randint(100, 1000, limit)
        })

# ==========================================
# 4. SIDEBAR NAVIGATION
# ==========================================

with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2215/2215538.png", width=70) # Rocket Icon
    st.markdown("## TITANIUM-X")
    st.caption("SYSTEM v.5.0 [PRO]")
    
    st.markdown("---")
    
    menu = st.radio(
        "MODULE SELECTOR", 
        ["DASHBOARD", "TRADING TERMINAL", "AI ANALYTICS", "WALLET"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    st.markdown("### 📡 SYSTEM STATUS")
    c1, c2 = st.columns(2)
    c1.metric("LATENCY", "12ms")
    c2.metric("UPTIME", "99.9%")
    
    st.markdown("### 🔒 SECURITY")
    st.info("ENCRYPTION: AES-256")
    st.info("CONNECTION: SECURE")
    
    st.markdown("---")
    st.caption("ID: USER-8842-ALPHA")

# ==========================================
# 5. MAIN INTERFACE
# ==========================================

# --- NEWS TICKER ---
st.markdown("""
<div class="ticker-container">
    <div class="ticker-text">
        BTC BREAKS $95,000 RESISTANCE  ///  WHALES ACCUMULATING SOLANA  ///  NEW SEC REGULATION APPROVED  ///  TITANIUM-X AI PREDICTS MARKET VOLATILITY  ///  ETH GAS FEES DROP TO RECORD LOWS
    </div>
</div>
""", unsafe_allow_html=True)

if menu == "DASHBOARD":
    st.markdown("### 🌍 GLOBAL MARKET OVERVIEW")
    
    # Top Tickers Row
    coins = ['BTC/USD', 'ETH/USD', 'SOL/USD', 'XRP/USD']
    cols = st.columns(4)
    
    for i, coin in enumerate(coins):
        data = get_market_data(coin)
        color = "#00ff41" if data['change'] >= 0 else "#ff003c"
        arrow = "▲" if data['change'] >= 0 else "▼"
        
        with cols[i]:
            st.markdown(f"""
            <div class="cyber-card">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span style="color:#888; font-family:'Orbitron'">{coin}</span>
                    <span style="color:{color}; font-size:12px;">{data['change']:.2f}% {arrow}</span>
                </div>
                <div style="font-size:26px; font-weight:bold; margin-top:10px;">
                    ${data['price']:,.2f}
                </div>
                <div style="font-size:10px; color:#555; margin-top:5px;">
                    Vol: {data['vol']:,.0f}
                </div>
                <div style="height:2px; width:100%; background:linear-gradient(90deg, {color}, transparent); margin-top:10px;"></div>
            </div>
            """, unsafe_allow_html=True)

    # Big Chart & Heatmap
    c_chart, c_map = st.columns([2, 1])
    
    with c_chart:
        st.markdown('<div class="cyber-card">', unsafe_allow_html=True)
        st.markdown("#### 📈 MARKET CAP DOMINANCE")
        
        # Fake Area Chart
        df_dom = pd.DataFrame({
            'Date': pd.date_range('2024-01-01', periods=50),
            'BTC': np.random.randn(50).cumsum() + 50,
            'ETH': np.random.randn(50).cumsum() + 20,
            'SOL': np.random.randn(50).cumsum() + 10
        })
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df_dom['Date'], y=df_dom['BTC'], stackgroup='one', name='BTC', line_color='#00BFFF'))
        fig.add_trace(go.Scatter(x=df_dom['Date'], y=df_dom['ETH'], stackgroup='one', name='ETH', line_color='#8A2BE2'))
        fig.add_trace(go.Scatter(x=df_dom['Date'], y=df_dom['SOL'], stackgroup='one', name='SOL', line_color='#00ff41'))
        
        fig.update_layout(
            template="plotly_dark", 
            paper_bgcolor='rgba(0,0,0,0)', 
            plot_bgcolor='rgba(0,0,0,0)',
            height=350,
            margin=dict(l=0, r=0, t=0, b=0),
            legend=dict(orientation="h", y=1.1)
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
    with c_map:
        st.markdown('<div class="cyber-card">', unsafe_allow_html=True)
        st.markdown("#### 🔥 FEAR & GREED INDEX")
        
        val = 75
        fig_gauge = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = val,
            title = {'text': "GREED", 'font': {'size': 20, 'color': '#00ff41'}},
            gauge = {
                'axis': {'range': [0, 100], 'tickcolor': "white"},
                'bar': {'color': "#00ff41"},
                'bgcolor': "rgba(0,0,0,0)",
                'borderwidth': 2,
                'bordercolor': "#333",
                'steps': [
                    {'range': [0, 25], 'color': '#ff003c'},
                    {'range': [25, 50], 'color': '#ffcc00'},
                    {'range': [50, 75], 'color': '#00BFFF'},
                    {'range': [75, 100], 'color': '#00ff41'}],
            }
        ))
        fig_gauge.update_layout(height=350, margin=dict(l=20, r=20, t=50, b=20), paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_gauge, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

elif menu == "TRADING TERMINAL":
    
    # Top Bar
    c_sel, c_stat1, c_stat2, c_stat3 = st.columns([2, 1, 1, 1])
    with c_sel:
        active_pair = st.selectbox("SELECT ASSET", ["BTC/USD", "ETH/USD", "SOL/USD"], label_visibility="collapsed")
    
    data = get_market_data(active_pair)
    c_stat1.metric("PRICE", f"${data['price']:,.2f}", f"{data['change']:.2f}%")
    c_stat2.metric("24H HIGH", f"${data['high']:,.2f}")
    c_stat3.metric("VOLUME", f"{data['vol']:,.0f}")
    
    st.markdown("---")
    
    # Main Layout: Chart vs Order Book
    col_chart, col_depth = st.columns([3, 1])
    
    with col_chart:
        st.markdown('<div class="cyber-card">', unsafe_allow_html=True)
        # Advanced Chart
        df = generate_chart_data(active_pair)
        
        # Moving Averages
        df['MA7'] = df['close'].rolling(7).mean()
        df['MA25'] = df['close'].rolling(25).mean()
        
        fig = go.Figure()
        
        # Candlesticks
        fig.add_trace(go.Candlestick(
            x=df['time'], open=df['open'], high=df['high'], low=df['low'], close=df['close'],
            increasing_line_color='#00ff41', decreasing_line_color='#ff003c', name='Price'
        ))
        
        # Lines
        fig.add_trace(go.Scatter(x=df['time'], y=df['MA7'], line=dict(color='#00BFFF', width=1), name='MA 7'))
        fig.add_trace(go.Scatter(x=df['time'], y=df['MA25'], line=dict(color='#FFA500', width=1), name='MA 25'))
        
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            height=600,
            xaxis_rangeslider_visible=False,
            margin=dict(l=0, r=0, t=0, b=0)
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # TRADE EXECUTION
        st.markdown("### ⚡ QUICK EXECUTION")
        ex_c1, ex_c2, ex_c3 = st.columns(3)
        with ex_c1:
            side = st.radio("SIDE", ["BUY", "SELL"], horizontal=True)
        with ex_c2:
            order_type = st.selectbox("TYPE", ["MARKET", "LIMIT", "STOP-LOSS"])
        with ex_c3:
            amt = st.number_input("AMOUNT (USD)", value=1000, step=100)
            
        if st.button("🚀 EXECUTE TRANSACTION", use_container_width=True):
            with st.spinner("BROADCASTING TO BLOCKCHAIN..."):
                time.sleep(1.5)
            st.toast(f"SUCCESS: {side} ORDER FOR ${amt} FILLED", icon="✅")
            st.balloons()

    with col_depth:
        st.markdown('<div class="cyber-card">', unsafe_allow_html=True)
        st.markdown("#### 🌊 DEPTH")
        
        # Fake Order Book Visual
        bids = np.random.randint(10, 100, 10)
        asks = np.random.randint(10, 100, 10)
        prices = np.linspace(data['price'] * 0.99, data['price'] * 1.01, 20)
        
        # Asks (Red)
        for i in range(10):
            st.markdown(f"""
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:2px;">
                <span style="color:#ff003c; font-family:'Share Tech Mono'">${prices[19-i]:,.0f}</span>
                <div style="width:{asks[i]}%; height:10px; background:rgba(255, 0, 60, 0.4); border-radius:2px;"></div>
                <span style="font-size:10px;">{asks[i]/10:.1f}K</span>
            </div>
            """, unsafe_allow_html=True)
            
        st.markdown("<hr style='border-color:#333; margin:10px 0;'>", unsafe_allow_html=True)
        
        # Bids (Green)
        for i in range(10):
            st.markdown(f"""
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:2px;">
                <span style="color:#00ff41; font-family:'Share Tech Mono'">${prices[9-i]:,.0f}</span>
                <div style="width:{bids[i]}%; height:10px; background:rgba(0, 255, 65, 0.4); border-radius:2px;"></div>
                <span style="font-size:10px;">{bids[i]/10:.1f}K</span>
            </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # RECENT TRADES
        st.markdown('<div class="cyber-card">', unsafe_allow_html=True)
        st.markdown("#### TAPE")
        trades = pd.DataFrame({
            "Time": [datetime.now().strftime("%H:%M:%S") for _ in range(5)],
            "Price": [data['price'] + random.randint(-50, 50) for _ in range(5)],
            "Amount": [random.uniform(0.1, 2.0) for _ in range(5)],
            "Type": [random.choice(["BUY", "SELL"]) for _ in range(5)]
        })
        st.dataframe(trades, hide_index=True, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

elif menu == "AI ANALYTICS":
    st.markdown("### 🧠 NEURAL CORE PREDICTIONS")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown('<div class="cyber-card">', unsafe_allow_html=True)
        st.markdown("#### SENTIMENT RADAR")
        
        categories = ['Social Vol', 'Whale Activity', 'Tech Indicators', 'Macro News', 'Volatility']
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=[80, 95, 60, 40, 70],
            theta=categories,
            fill='toself',
            name='BTC',
            line_color='#00BFFF'
        ))
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            showlegend=False,
            template="plotly_dark",
            paper_bgcolor='rgba(0,0,0,0)',
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col2:
        st.markdown('<div class="cyber-card">', unsafe_allow_html=True)
        st.markdown("#### PRICE PROJECTION")
        
        # Fake Prediction Chart
        x = np.arange(20)
        y = np.linspace(94000, 98000, 20) + np.random.randn(20) * 500
        upper = y + 1000
        lower = y - 1000
        
        fig_pred = go.Figure()
        fig_pred.add_trace(go.Scatter(x=x, y=y, line=dict(color='#00BFFF'), name='Forecast'))
        fig_pred.add_trace(go.Scatter(x=x, y=upper, line=dict(width=0), showlegend=False))
        fig_pred.add_trace(go.Scatter(x=x, y=lower, fill='tonexty', fillcolor='rgba(0, 191, 255, 0.1)', line=dict(width=0), showlegend=False))
        
        fig_pred.update_layout(
            template="plotly_dark",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            height=400,
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor='#333')
        )
        st.plotly_chart(fig_pred, use_container_width=True)
        
        st.info("💡 AI VERDICT: STRONG BUY (Confidence 89%)")
        st.markdown('</div>', unsafe_allow_html=True)

elif menu == "WALLET":
    st.markdown("### 💼 ASSET MANAGEMENT")
    
    w1, w2 = st.columns([1, 2])
    
    with w1:
        st.markdown('<div class="cyber-card">', unsafe_allow_html=True)
        st.markdown("#### TOTAL EQUITY")
        st.markdown("<h1 style='color:#00ff41; font-size:40px;'>$124,592.40</h1>", unsafe_allow_html=True)
        st.markdown("<span style='color:#00BFFF'>+12.5% This Month</span>", unsafe_allow_html=True)
        st.markdown("---")
        st.write("BTC: 1.25")
        st.write("ETH: 15.0")
        st.write("USDT: 45,000")
        st.markdown('</div>', unsafe_allow_html=True)
        
    with w2:
        st.markdown('<div class="cyber-card">', unsafe_allow_html=True)
        st.markdown("#### ALLOCATION")
        
        labels = ['Bitcoin', 'Ethereum', 'Solana', 'USDT', 'Other']
        values = [45, 25, 10, 15, 5]
        colors = ['#00BFFF', '#8A2BE2', '#00ff41', '#ffffff', '#ff003c']
        
        fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.6, marker=dict(colors=colors))])
        fig.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', height=400)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

# FOOTER
st.markdown("---")
st.markdown("<center style='color:#444; font-size:10px; font-family:Orbitron'>TITANIUM-X SYSTEMS | QUANTUM ENCRYPTION | NODE: US-EAST-4</center>", unsafe_allow_html=True)
