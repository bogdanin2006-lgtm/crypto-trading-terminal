import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import ccxt
from plotly.subplots import make_subplots

# --- КОНФИГУРАЦИЯ И СТИЛЬ (BLUE HORIZON THEME) ---
st.set_page_config(layout="wide", page_title="Blue Horizon Terminal")

st.markdown("""
<style>
    .stApp { background-color: #0E1117; color: #F0F2F6; }
    [data-testid="stSidebar"] { background-color: #161B22; border-right: 1px solid #00BFFF; }
    .stButton>button { background-color: #00BFFF; color: white; border-radius: 5px; width: 100%; }
    h1, h2, h3 { color: #00BFFF; font-family: 'Segoe UI', sans-serif; }
    .metric-card { background-color: #1B2430; padding: 15px; border-radius: 10px; border-left: 5px solid #00BFFF; }
</style>
""", unsafe_allow_html=True)

# Инициализация биржи (Public API Binance для тестов)
exchange = ccxt.binance()

# --- SIDEBAR НАВИГАЦИЯ ---
with st.sidebar:
    st.title("🌊 Blue Horizon")
    menu = st.radio("Навигация", ["Обзор рынка", "Торговый терминал", "Мой портфель", "Настройки API"])
    st.markdown("---")
    selected_pair = st.selectbox("Валютная пара", ["BTC/USDT", "ETH/USDT", "SOL/USDT", "BNB/USDT"])

# --- ЛОГИКА СТРАНИЦ ---

if menu == "Обзор рынка":
    st.header("📈 Топ-10 активов по капитализации")
    
    # Загрузка тикеров через CCXT
    tickers = exchange.fetch_tickers(['BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'SOL/USDT', 'XRP/USDT', 'ADA/USDT', 'DOGE/USDT', 'TRX/USDT', 'DOT/USDT', 'MATIC/USDT'])
    
    cols = st.columns(5)
    for i, (symbol, data) in enumerate(list(tickers.items())[:10]):
        with cols[i % 5]:
            st.markdown(f"""<div class="metric-card">
                <small>{symbol}</small><br>
                <strong>${data['last']:,.2f}</strong><br>
                <span style="color:{'#00ff00' if data['change'] >= 0 else '#ff4b4b'}">{data['percentage']:.2f}%</span>
            </div>""", unsafe_allow_html=True)
    
    st.markdown("### График тренда (Sky Blue Style)")
    # Здесь можно вставить большой график из предыдущего этапа, но в синих тонах

elif menu == "Торговый терминал":
    col_chart, col_orderbook = st.columns([3, 1])
    
    with col_chart:
        st.subheader(f"График {selected_pair}")
        # Загрузка свечей
        ohlcv = exchange.fetch_ohlcv(selected_pair, timeframe='1h', limit=50)
        df = pd.DataFrame(ohlcv, columns=['time', 'open', 'high', 'low', 'close', 'volume'])
        df['time'] = pd.to_datetime(df['time'], unit='ms')
        
        fig = go.Figure(data=[go.Candlestick(
            x=df['time'], open=df['open'], high=df['high'], low=df['low'], close=df['close'],
            increasing_line_color='#00BFFF', decreasing_line_color='#1B2430'
        )])
        fig.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=500)
        st.plotly_chart(fig, use_container_width=True)
        
        # Панель покупки/продажи
        st.markdown("### ⚡ Быстрая сделка")
        c1, c2, c3 = st.columns(3)
        amount = c1.number_input("Количество", min_value=0.0)
        price = c2.number_input("Цена", value=df['close'].iloc[-1])
        c3.write("") # Отступ
        if c3.button("Разместить ордер"):
            st.success("Ордер отправлен в очередь (симуляция)")

    with col_orderbook:
        st.subheader("Order Book")
        ob = exchange.fetch_order_book(selected_pair)
        
        # Таблицы Ask/Bid
        df_asks = pd.DataFrame(ob['asks'], columns=['Price', 'Qty']).head(10)
        df_bids = pd.DataFrame(ob['bids'], columns=['Price', 'Qty']).head(10)
        
        st.write("Asks (Продажа)")
        st.dataframe(df_asks.style.background_gradient(cmap='Reds'), hide_index=True)
        st.write("Bids (Покупка)")
        st.dataframe(df_bids.style.background_gradient(cmap='Greens'), hide_index=True)

elif menu == "Мой портфель":
    st.header("💰 Личный кабинет")
    c1, c2 = st.columns([1, 1])
    
    with c1:
        st.markdown("""<div class="metric-card">
            <h3>Общий баланс</h3>
            <h1>$42,500.12</h1>
            <small>≈ 0.64 BTC</small>
        </div>""", unsafe_allow_html=True)
        
    with c2:
        # Распределение активов
        labels = ['BTC', 'ETH', 'SOL', 'USDT']
        values = [45, 25, 15, 15]
        fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.6, marker_colors=['#00BFFF', '#1B2430', '#3E5C76', '#86BBD8'])])
        fig.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', showlegend=True)
        st.plotly_chart(fig, use_container_width=True)

elif menu == "Настройки API":
    st.header("🔑 Конфигурация API")
    st.info("Введите ключи вашей биржи для включения реальной торговли. Данные сохраняются только в текущей сессии.")
    api_key = st.text_input("API Key", type="password")
    api_secret = st.text_input("API Secret", type="password")
    if st.button("Сохранить"):
        st.success("Ключи приняты!")
