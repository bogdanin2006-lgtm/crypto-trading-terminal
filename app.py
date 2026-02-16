import streamlit as st
import ccxt
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import requests
from datetime import datetime, timedelta

# --- 1. CONFIG & SESSION STATE (СИМУЛЯТОР) ---
st.set_page_config(page_title="NANO TRADER PRO", layout="wide", page_icon="💎")

# Инициализация виртуального кошелька
if 'balance_usd' not in st.session_state:
    st.session_state.balance_usd = 10000.0  # $10,000 старт
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = {'BTC': 0.0, 'ETH': 0.0, 'SOL': 0.0, 'XRP': 0.0}
if 'trade_history' not in st.session_state:
    st.session_state.trade_history = []

# --- 2. CSS STYLING (CYBERPUNK) ---
st.markdown("""
    <style>
        .stApp { background-color: #050816; color: #e0fbfc; font-family: 'Roboto Mono', monospace; }
        section[data-testid="stSidebar"] { background-color: #0a0e24; border-right: 1px solid #1b2b4b; }
        
        /* Metrics */
        div[data-testid="stMetric"] {
            background-color: rgba(13, 19, 43, 0.8);
            border: 1px solid #00f2ff;
            padding: 10px; border-radius: 8px;
            box-shadow: 0 0 10px rgba(0, 242, 255, 0.1) inset;
        }
        div[data-testid="stMetricLabel"] { color: #8a9dbf; }
        div[data-testid="stMetricValue"] { color: #fff; text-shadow: 0 0 5px #00f2ff; }
        
        /* Buttons */
        div.stButton > button { width: 100%; border-radius: 5px; font-weight: bold; border: none; }
        div.stButton > button:hover { transform: scale(1.02); }
        
        /* Tabs */
        .stTabs [data-baseweb="tab-list"] { gap: 20px; }
        .stTabs [data-baseweb="tab"] { color: #8a9dbf; }
        .stTabs [aria-selected="true"] { color: #00f2ff; border-bottom-color: #00f2ff; }
    </style>
""", unsafe_allow_html=True)

# --- 3. DATA ENGINE ---
@st.cache_data(ttl=300)
def fetch_fear_greed():
    """Получает реальный индекс страха и жадности"""
    try:
        r = requests.get("https://api.alternative.me/fng/")
        data = r.json()
        return int(data['data'][0]['value']), data['data'][0]['value_classification']
    except:
        return 50, "Neutral"

@st.cache_data(ttl=60)
def fetch_ohlcv(symbol, timeframe):
    """Данные с Kraken или генерация"""
    try:
        exchange = ccxt.kraken()
        kraken_symbol = symbol.replace("USDT", "USD")
        bars = exchange.fetch_ohlcv(kraken_symbol, timeframe, limit=100)
        df = pd.DataFrame(bars, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        return df
    except:
        # Fallback generator
        dates = pd.date_range(end=datetime.now(), periods=100, freq=timeframe.replace('m', 'T'))
        base = 50000 if 'BTC' in symbol else 3000
        prices = base + np.cumsum(np.random.randn(100) * (base*0.002))
        return pd.DataFrame({'timestamp': dates, 'open': prices, 'high': prices*1.01, 'low': prices*0.99, 'close': prices, 'volume': np.random.randint(100,1000,100)})

# --- 4. SIDEBAR (WALLET & SETTINGS) ---
with st.sidebar:
    st.title("💎 NANO TRADER")
    
    # 1. Виртуальный кошелек
    st.markdown("### 💳 YOUR WALLET")
    total_balance = st.session_state.balance_usd
    # Считаем стоимость крипты в портфеле (примерно)
    crypto_val = 0
    for coin, qty in st.session_state.portfolio.items():
        if qty > 0:
            # Для простоты берем фикс цены, в реале надо брать текущую
            price = 90000 if coin == 'BTC' else (3000 if coin == 'ETH' else 100) 
            crypto_val += qty * price
            
    st.metric("Total Equity", f"${total_balance + crypto_val:,.2f}", delta=f"{((total_balance + crypto_val - 10000)/10000)*100:.2f}% PnL")
    st.metric("Cash (USD)", f"${st.session_state.balance_usd:,.2f}")
    
    st.markdown("### 🎒 POSITIONS")
    for coin, qty in st.session_state.portfolio.items():
        if qty > 0:
            st.write(f"**{coin}:** {qty:.4f}")
            
    st.markdown("---")
    st.caption("Mode: Paper Trading (Simulation)")

# --- 5. MAIN AREA ---

# Top Bar: Ticker & Sentiment
col1, col2 = st.columns([3, 1])

with col1:
    selected_pair = st.selectbox("Select Asset", ["BTC/USD", "ETH/USD", "SOL/USD"], index=0)
    timeframe = st.selectbox("Timeframe", ["1m", "15m", "1h", "4h"], index=2)
    df = fetch_ohlcv(selected_pair, timeframe)
    current_price = df['close'].iloc[-1]
    
with col2:
    fng_val, fng_text = fetch_fear_greed()
    st.metric("Fear & Greed Index", f"{fng_val}/100", fng_text)

# --- CHARTING AREA ---
tab_chart, tab_depth, tab_ai = st.tabs(["📈 PRO CHART", "🌊 DEPTH", "🤖 AI PREDICTION"])

with tab_chart:
    # Controls
    c1, c2, c3 = st.columns(3)
    show_sma = c1.checkbox("Show SMA (20)", value=True)
    show_bb = c2.checkbox("Bollinger Bands", value=False)
    show_vol = c3.checkbox("Show Volume", value=True)

    fig = go.Figure()
    
    # Candlestick
    fig.add_trace(go.Candlestick(x=df['timestamp'], open=df['open'], high=df['high'],
                                 low=df['low'], close=df['close'], name="Price",
                                 increasing_line_color='#00ff00', decreasing_line_color='#ff0000'))
    
    # Indicators
    if show_sma:
        sma = df['close'].rolling(20).mean()
        fig.add_trace(go.Scatter(x=df['timestamp'], y=sma, line=dict(color='orange', width=1.5), name="SMA 20"))
        
    if show_bb:
        sma = df['close'].rolling(20).mean()
        std = df['close'].rolling(20).std()
        upper = sma + (std * 2)
        lower = sma - (std * 2)
        fig.add_trace(go.Scatter(x=df['timestamp'], y=upper, line=dict(color='rgba(0, 242, 255, 0.3)'), name="BB Upper"))
        fig.add_trace(go.Scatter(x=df['timestamp'], y=lower, line=dict(color='rgba(0, 242, 255, 0.3)'), fill='tonexty', name="BB Lower"))

    fig.update_layout(height=500, plot_bgcolor='#050816', paper_bgcolor='#050816', 
                      font={'color': '#e0fbfc'}, xaxis_rangeslider_visible=False,
                      margin=dict(l=0, r=0, t=0, b=0))
    st.plotly_chart(fig, use_container_width=True)

with tab_depth:
    # Simulated Order Book
    st.markdown("### Market Depth (Order Book)")
    depth_x = np.linspace(current_price * 0.98, current_price * 1.02, 100)
    bid_vol = np.exp(-((depth_x - current_price*0.98)**2) / 1000) * 50 # Fake math for shape
    ask_vol = np.exp(-((depth_x - current_price*1.02)**2) / 1000) * 50
    
    fig_depth = go.Figure()
    fig_depth.add_trace(go.Scatter(x=depth_x[depth_x < current_price], y=bid_vol[depth_x < current_price], fill='tozeroy', name='Bids (Buy)', line_color='#00ff00'))
    fig_depth.add_trace(go.Scatter(x=depth_x[depth_x >= current_price], y=ask_vol[depth_x >= current_price], fill='tozeroy', name='Asks (Sell)', line_color='#ff0000'))
    fig_depth.update_layout(height=400, plot_bgcolor='#050816', paper_bgcolor='#050816', font={'color': '#fff'})
    st.plotly_chart(fig_depth, use_container_width=True)

with tab_ai:
    st.markdown("### 🤖 Neural Network Trend Prediction")
    st.info("Based on LSTM model simulation (Beta)")
    
    # Fake AI projection
    future_dates = [df['timestamp'].iloc[-1] + timedelta(minutes=i*15) for i in range(1, 11)]
    trend = 1 if fng_val > 50 else -1
    future_prices = [current_price * (1 + (i * 0.001 * trend)) for i in range(1, 11)]
    
    fig_ai = go.Figure()
    fig_ai.add_trace(go.Scatter(x=df['timestamp'][-20:], y=df['close'][-20:], name="Historical", line_color='gray'))
    fig_ai.add_trace(go.Scatter(x=future_dates, y=future_prices, name="AI Forecast", line=dict(color='#00f2ff', dash='dot')))
    fig_ai.update_layout(height=400, plot_bgcolor='#050816', paper_bgcolor='#050816', font={'color': '#fff'})
    st.plotly_chart(fig_ai, use_container_width=True)

# --- 6. TRADING TERMINAL ---
st.markdown("---")
st.subheader("⚡ EXECUTION TERMINAL")

c_trade1, c_trade2 = st.columns([1, 2])

with c_trade1:
    trade_amount = st.number_input("Amount (USD)", min_value=10.0, max_value=st.session_state.balance_usd, value=1000.0)
    coin_symbol = selected_pair.split('/')[0]
    
    col_buy, col_sell = st.columns(2)
    
    if col_buy.button("BUY MARKET 🟢", type="primary"):
        cost = trade_amount
        if cost <= st.session_state.balance_usd:
            # Execute Buy
            coin_qty = cost / current_price
            st.session_state.balance_usd -= cost
            st.session_state.portfolio[coin_symbol] += coin_qty
            
            # Log
            st.session_state.trade_history.append({
                "Time": datetime.now().strftime("%H:%M:%S"),
                "Type": "BUY",
                "Asset": coin_symbol,
                "Price": current_price,
                "Amount": coin_qty,
                "Total": cost
            })
            st.toast(f"Bought {coin_qty:.4f} {coin_symbol}!", icon="✅")
            st.rerun() # Refresh UI
        else:
            st.error("Insufficient Funds!")

    if col_sell.button("SELL MARKET 🔴", type="secondary"):
        # Продаем всё что есть (упрощенно для примера)
        qty_owned = st.session_state.portfolio[coin_symbol]
        if qty_owned > 0:
            sale_value = qty_owned * current_price
            st.session_state.balance_usd += sale_value
            st.session_state.portfolio[coin_symbol] = 0.0
            
            # Log
            st.session_state.trade_history.append({
                "Time": datetime.now().strftime("%H:%M:%S"),
                "Type": "SELL",
                "Asset": coin_symbol,
                "Price": current_price,
                "Amount": qty_owned,
                "Total": sale_value
            })
            st.toast(f"Sold {qty_owned:.4f} {coin_symbol}!", icon="💰")
            st.rerun()
        else:
            st.error(f"You don't own any {coin_symbol}")

with c_trade2:
    st.write("📜 Recent Transactions")
    if st.session_state.trade_history:
        df_hist = pd.DataFrame(st.session_state.trade_history)
        st.dataframe(df_hist.sort_index(ascending=False), use_container_width=True, height=150)
    else:
        st.info("No trades executed yet. Start trading!")
