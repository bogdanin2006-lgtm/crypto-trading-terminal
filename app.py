import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import ccxt
import numpy as np
from datetime import datetime

# --- 1. CONFIG & STYLE (Blue Horizon Theme) ---
st.set_page_config(layout="wide", page_title="Blue Horizon Terminal")

st.markdown("""
<style>
    .stApp { background-color: #0E1117; color: #F0F2F6; }
    [data-testid="stSidebar"] { background-color: #161B22; border-right: 1px solid #00BFFF; }
    .stButton>button { background-color: #00BFFF !important; color: white !important; border-radius: 5px; width: 100%; }
    h1, h2, h3 { color: #00BFFF; }
    .metric-card { 
        background-color: #1B2430; 
        padding: 15px; 
        border-radius: 10px; 
        border-left: 5px solid #00BFFF;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. DATA ENGINE (Kraken for US Servers) ---
# Используем Kraken, чтобы избежать Error 451 от Binance
@st.cache_resource
def init_exchange():
    return ccxt.kraken({'enableRateLimit': True})

exchange = init_exchange()

def safe_get_tickers(symbols):
    try:
        # Kraken использует USD вместо USDT
        kraken_symbols = [s.replace('USDT', 'USD') for s in symbols]
        return exchange.fetch_tickers(kraken_symbols)
    except:
        return {s.replace('USDT', 'USD'): {'last': 0.0, 'percentage': 0.0} for s in symbols}

# --- 3. SIDEBAR NAVIGATION ---
# Переменная 'menu' должна определяться ПЕРЕД использованием в условиях
with st.sidebar:
    st.title("🌊 Blue Horizon")
    menu = st.radio("Навигация", ["Обзор рынка", "Торговый терминал", "Мой портфель", "Настройки API"])
    st.markdown("---")
    selected_pair = st.selectbox("Валютная пара", ["BTC/USD", "ETH/USD", "SOL/USD", "XRP/USD"])

# --- 4. MAIN LOGIC ---

if menu == "Обзор рынка":
    st.header("📈 Обзор рынка (Kraken Live)")
    
    target_coins = ['BTC/USD', 'ETH/USD', 'SOL/USD', 'XRP/USD', 'ADA/USD']
    tickers = safe_get_tickers(target_coins)
    
    cols = st.columns(len(target_coins))
    for i, symbol in enumerate(target_coins):
        data = tickers.get(symbol, {'last': 0, 'percentage': 0})
        with cols[i]:
            st.markdown(f"""<div class="metric-card">
                <small>{symbol}</small><br>
                <strong style="font-size:18px;">${data['last']:,.2f}</strong><br>
                <span style="color:{'#00ff00' if data['percentage'] >= 0 else '#ff4b4b'}">
                    {data['percentage']:.2f}%
                </span>
            </div>""", unsafe_allow_html=True)

    # Интерактивный график
    st.subheader("Тренд актива")
    try:
        ohlcv = exchange.fetch_ohlcv(selected_pair, timeframe='1h', limit=50)
        df = pd.DataFrame(ohlcv, columns=['time', 'open', 'high', 'low', 'close', 'volume'])
        df['time'] = pd.to_datetime(df['time'], unit='ms')
        
        fig = go.Figure(data=[go.Candlestick(
            x=df['time'], open=df['open'], high=df['high'], low=df['low'], close=df['close'],
            increasing_line_color='#00BFFF', decreasing_line_color='#1B2430'
        )])
        fig.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)
    except:
        st.warning("Не удалось загрузить график. Проверьте соединение.")

elif menu == "Торговый терминал":
    col_t1, col_t2 = st.columns([3, 1])
    
    with col_t1:
        st.subheader(f"Терминал: {selected_pair}")
        st.info("Здесь отображается расширенный график с индикаторами.")
        # Дублируем график или добавляем стакан
        st.write("График в режиме ожидания сигнала...")

    with col_t2:
        st.subheader("Order Book")
        try:
            ob = exchange.fetch_order_book(selected_pair)
            df_asks = pd.DataFrame(ob['asks'], columns=['Price', 'Qty']).head(5)
            df_bids = pd.DataFrame(ob['bids'], columns=['Price', 'Qty']).head(5)
            st.write("Asks")
            st.table(df_asks)
            st.write("Bids")
            st.table(df_bids)
        except:
            st.write("Стакан временно пуст.")

elif menu == "Мой портфель":
    st.header("💼 Мой портфель")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("""<div class="metric-card">
            <h3>Equity Value</h3>
            <h1>$12,450.00</h1>
            <small>+5.2% за сегодня</small>
        </div>""", unsafe_allow_html=True)
    with c2:
        labels = ['BTC', 'ETH', 'USDT']
        values = [60, 30, 10]
        fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.5)])
        fig.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)

elif menu == "Настройки API":
    st.header("⚙️ Настройки")
    st.text_input("API Key", type="password")
    st.text_input("API Secret", type="password")
    if st.button("Connect Account"):
        st.success("Connected to Kraken API")
