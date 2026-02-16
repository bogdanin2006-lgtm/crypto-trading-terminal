import streamlit as st
import ccxt
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from datetime import datetime, timedelta

# --- 1. КОНФИГУРАЦИЯ И CSS-СТИЛИ (КИБЕРПАНК) ---
st.set_page_config(page_title="NANO BANANA TRADE", layout="wide", page_icon="🍌")

# Этот CSS превращает стандартный Streamlit в неоновый терминал
st.markdown("""
    <style>
        /* Основной фон и текст */
        .stApp {
            background-color: #050816; /* Глубокий темный фон */
            color: #e0fbfc; /* Светло-голубой текст */
            font-family: 'Roboto Mono', monospace; /* Моноширинный шрифт */
        }
        
        /* Сайдбар */
        section[data-testid="stSidebar"] {
            background-color: #0a0e24; /* Чуть светлее фон сайдбара */
            border-right: 1px solid #1b2b4b;
        }

        /* Заголовки */
        h1, h2, h3 {
            color: #00f2ff !important; /* Неоновый голубой */
            text-shadow: 0 0 10px rgba(0, 242, 255, 0.5);
            font-weight: bold;
            letter-spacing: 1px;
        }

        /* Метрики (Виджеты с ценами) */
        div[data-testid="stMetric"] {
            background-color: rgba(13, 19, 43, 0.8);
            border: 1px solid #00f2ff; /* Голубая рамка */
            padding: 10px;
            border-radius: 8px;
            box-shadow: 0 0 10px rgba(0, 242, 255, 0.2) inset; /* Внутреннее свечение */
            transition: all 0.3s ease;
        }
        div[data-testid="stMetric"]:hover {
             box-shadow: 0 0 20px rgba(0, 242, 255, 0.4) inset, 0 0 10px rgba(0, 242, 255, 0.4); /* Эффект при наведении */
        }
        div[data-testid="stMetricLabel"] { color: #8a9dbf; font-size: 12px; }
        div[data-testid="stMetricValue"] { color: #ffffff; font-size: 18px; }
        div[data-testid="stMetricDelta"] { font-size: 12px; }

        /* Кнопки BUY / SELL */
        .stButton button {
            width: 100%;
            border: none;
            color: white;
            padding: 15px 32px;
            text-align: center;
            text-decoration: none;
            display: inline-block;
            font-size: 16px;
            margin: 4px 2px;
            cursor: pointer;
            border-radius: 8px;
            font-weight: bold;
            text-transform: uppercase;
            letter-spacing: 1px;
            transition: transform 0.1s;
        }
        .stButton button:active { transform: scale(0.98); }

        /* Зеленая кнопка BUY */
        div.row-widget.stButton > button[kind="primary"] {
            background: linear-gradient(90deg, #00c853 0%, #69f0ae 100%);
            box-shadow: 0 0 20px rgba(0, 200, 83, 0.6);
        }

        /* Красная кнопка SELL */
        div.row-widget.stButton > button[kind="secondary"] {
             background: linear-gradient(90deg, #d50000 0%, #ff5252 100%);
             box-shadow: 0 0 20px rgba(213, 0, 0, 0.6);
             color: white !important; /* Принудительно белый текст */
        }

        /* Вкладки (Tabs) */
        .stTabs [data-baseweb="tab-list"] {
            gap: 10px;
            background-color: transparent;
            border-bottom: 1px solid #1b2b4b;
        }
        .stTabs [data-baseweb="tab"] {
            height: 40px;
            border-radius: 4px 4px 0 0;
            color: #8a9dbf;
            border: 1px solid transparent;
            background-color: transparent;
            transition: all 0.3s;
        }
        .stTabs [aria-selected="true"] {
            background-color: rgba(0, 242, 255, 0.1);
            color: #00f2ff;
            border-color: #00f2ff;
            border-bottom: none;
        }

        /* Таблицы (Dataframes) */
        .stDataFrame {
            border: 1px solid #1b2b4b;
            border-radius: 8px;
            overflow: hidden;
        }
    </style>
""", unsafe_allow_html=True)


# --- 2. ФУНКЦИИ ДАННЫХ (С ФОЛЛБЭКОМ) ---
@st.cache_data(ttl=30)
def fetch_top_coins_data():
    """Получает данные для списка монет в сайдбаре."""
    coins = ['BTC/USD', 'ETH/USD', 'SOL/USD', 'XRP/USD', 'DOGE/USD']
    data = {}
    kraken = ccxt.kraken()
    try:
        tickers = kraken.fetch_tickers(coins)
        for symbol, ticker in tickers.items():
            data[symbol] = {
                'price': ticker['last'],
                'change': ticker['percentage']
            }
    except:
        # Фейковые данные, если API не отвечает
        for symbol in coins:
            base = 50000 if 'BTC' in symbol else (3000 if 'ETH' in symbol else 100)
            price = base + np.random.uniform(-base*0.05, base*0.05)
            change = np.random.uniform(-5, 5)
            data[symbol] = {'price': price, 'change': change}
    return data

@st.cache_data(ttl=60)
def fetch_ohlcv_data(symbol, timeframe):
    """Получает исторические данные для графика."""
    try:
        exchange = ccxt.kraken()
        kraken_symbol = symbol.replace("USDT", "USD")
        bars = exchange.fetch_ohlcv(kraken_symbol, timeframe, limit=100)
        df = pd.DataFrame(bars, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        return df
    except Exception:
        # Фейковые данные для графика
        dates = pd.date_range(end=datetime.now(), periods=100, freq=timeframe.replace('m', 'T'))
        base_price = 50000 if 'BTC' in symbol else 3000
        prices = base_price + np.cumsum(np.random.randn(100) * (base_price * 0.002))
        df = pd.DataFrame({
            'timestamp': dates,
            'open': prices, 'high': prices*1.005, 'low': prices*0.995,
            'close': prices + np.random.randn(100)*(base_price*0.001),
            'volume': np.random.randint(100, 1000, 100)
        })
        return df

# --- 3. САЙДБАР (ЛЕВАЯ ПАНЕЛЬ) ---
with st.sidebar:
    # Заголовок как на картинке
    st.markdown("# 🍌 NANO BANANA")
    st.markdown("### MARKET WATCH")
    
    # Список монет с ценами
    top_coins = fetch_top_coins_data()
    for symbol, data in top_coins.items():
        short_name = symbol.split('/')[0]
        st.metric(
            label=short_name,
            value=f"${data['price']:,.2f}",
            delta=f"{data['change']:.2f}%",
            delta_color="normal" # Автоматически зеленый/красный
        )
    
    st.markdown("---")
    # Имитация нижней навигации через радио-кнопки
    nav_selection = st.radio(
        "NAVIGATION",
        ["📊 Market", "💼 Portfolio", "📈 Charts", "⚙️ Settings", "📰 News"],
        label_visibility="collapsed" # Скрываем заголовок радио
    )


# --- 4. ОСНОВНОЙ ЭКРАН ---
# Логика переключения вкладок
if nav_selection == "📊 Market":
    
    # Верхняя часть: Заголовок и Карта
    col_title, col_map = st.columns([1, 2])
    with col_title:
        st.title("GLOBAL TRADE VIEW")
        # Выбор актива и таймфрейма для главного графика
        selected_pair = st.selectbox("SELECT ASSET", ["BTC/USD", "ETH/USD", "SOL/USD"], index=0)
        selected_tf = st.selectbox("TIMEFRAME", ["1m", "15m", "1h", "4h", "1d"], index=2)
        
    with col_map:
        # Заглушка для карты мира (Plotly Express)
        df_map = pd.DataFrame({
            'lat': np.random.uniform(-50, 70, 20),
            'lon': np.random.uniform(-120, 140, 20),
            'size': np.random.randint(10, 50, 20)
        })
        fig_map = px.scatter_geo(df_map, lat='lat', lon='lon', size='size', 
                                 projection="natural earth", template="plotly_dark")
        fig_map.update_geos(bgcolor='rgba(0,0,0,0)', showcountries=True, countrycolor="#1b2b4b",
                            showcoastlines=False, showland=True, landcolor="#0a0e24")
        fig_map.update_layout(height=250, margin={"r":0,"t":0,"l":0,"b":0}, paper_bgcolor='rgba(0,0,0,0)')
        fig_map.update_traces(marker=dict(color="#00f2ff", opacity=0.7, line=dict(width=0)))
        st.plotly_chart(fig_map, use_container_width=True)

    # Центральная часть: График
    df = fetch_ohlcv_data(selected_pair, selected_tf)
    if not df.empty:
        # График свечей + Объем
        fig = go.Figure()
        fig.add_trace(go.Candlestick(x=df['timestamp'], open=df['open'], high=df['high'],
                                     low=df['low'], close=df['close'], name="Price",
                                     increasing_line_color='#00c853', decreasing_line_color='#d50000'))
        # Добавляем объем вторым слоем (прозрачным)
        fig.add_trace(go.Bar(x=df['timestamp'], y=df['volume'], name="Volume", 
                             marker_color='rgba(0, 242, 255, 0.3)', yaxis='y2'))

        fig.update_layout(
            height=500,
            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
            font={'color': '#e0fbfc'},
            xaxis_rangeslider_visible=False,
            yaxis=dict(title="Price", gridcolor='#1b2b4b'),
            yaxis2=dict(title="Volume", overlaying='y', side='right', showgrid=False),
            margin=dict(l=10, r=10, t=10, b=10),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig, use_container_width=True)

    # Нижняя часть: Торговля и Ордера
    col_trade, col_orders = st.columns([1, 2])
    
    with col_trade:
        st.subheader("QUICK TRADE")
        # Поля ввода (заглушки)
        amount = st.number_input("Amount", min_value=0.0, value=0.1, step=0.01)
        price_input = st.number_input("Price (Limit)", min_value=0.0, value=df['close'].iloc[-1], format="%.2f")
        
        # Кнопки BUY / SELL с кастомными стилями
        c1, c2 = st.columns(2)
        with c1:
            # type="primary" используется для зеленой кнопки в CSS
            if st.button("BUY NOW", type="primary", use_container_width=True):
                st.toast(f"BUY Order Placed: {amount} {selected_pair.split('/')[0]} @ ${price_input}", icon="🟢")
        with c2:
            # type="secondary" используется для красной кнопки в CSS
            if st.button("SELL NOW", type="secondary", use_container_width=True):
                st.toast(f"SELL Order Placed: {amount} {selected_pair.split('/')[0]} @ ${price_input}", icon="🔴")

    with col_orders:
        # Вкладки для таблиц
        tab_open, tab_history = st.tabs(["OPEN ORDERS", "TRADE HISTORY"])
        
        with tab_open:
            # Фейковые данные для таблицы открытых ордеров
            orders_data = {
                'Time': [datetime.now().strftime("%H:%M:%S"), (datetime.now()-timedelta(minutes=5)).strftime("%H:%M:%S")],
                'Symbol': [selected_pair, 'ETH/USD'],
                'Type': ['BUY', 'SELL'],
                'Price': [f"${price_input:,.2f}", "$3,450.00"],
                'Amount': [amount, 1.5],
                'Status': ['Open', 'Open']
            }
            st.dataframe(pd.DataFrame(orders_data), use_container_width=True, hide_index=True)
            
        with tab_history:
             # Фейковые данные для истории
            history_data = {
                'Time': [(datetime.now()-timedelta(hours=1)).strftime("%H:%M:%S"), (datetime.now()-timedelta(days=1)).strftime("%H:%M:%S")],
                'Symbol': [selected_pair, 'SOL/USD'],
                'Side': ['BUY', 'BUY'],
                'Price': [f"${df['open'].iloc[0]:,.2f}", "$120.50"],
                'Filled': ['100%', '100%'],
                'Total ($)': [f"${df['open'].iloc[0]*0.5:,.2f}", "$602.50"]
            }
            st.dataframe(pd.DataFrame(history_data), use_container_width=True, hide_index=True)

# --- ЗАГЛУШКИ ДЛЯ ОСТАЛЬНЫХ ВКЛАДОК НАВИГАЦИИ ---
elif nav_selection == "💼 Portfolio":
    st.title("PORTFOLIO OVERVIEW")
    st.info("Portfolio features are under construction. Stay tuned! 🚧")
elif nav_selection == "📈 Charts":
    st.title("ADVANCED CHARTS")
    st.info("Advanced charting tools coming soon! 🚀")
elif nav_selection == "⚙️ Settings":
    st.title("TERMINAL SETTINGS")
    st.write("API Keys, Notifications, Theme selection...")
elif nav_selection == "📰 News":
    st.title("CRYPTO NEWS FEED")
    st.write("Latest headlines from the crypto world...")
