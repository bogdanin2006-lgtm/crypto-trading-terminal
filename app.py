import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import ccxt
import time

# --- ИНИЦИАЛИЗАЦИЯ БИРЖИ ---
# Используем Kraken, так как он дружелюбен к серверам в США
exchange = ccxt.kraken({
    'enableRateLimit': True,
})

# --- ФУНКЦИИ ПОЛУЧЕНИЯ ДАННЫХ С ОБРАБОТКОЙ ОШИБОК ---

def safe_fetch_tickers(symbols):
    try:
        # Kraken использует другой формат тикеров (напр. BTC/USD вместо BTC/USDT)
        # Автоматически меняем USDT на USD для совместимости с Kraken
        kraken_symbols = [s.replace('USDT', 'USD') for s in symbols]
        tickers = exchange.fetch_tickers(kraken_symbols)
        return tickers
    except Exception as e:
        st.error(f"Ошибка API: Биржа временно недоступна. Используются демо-данные.")
        # Возвращаем фейковые данные, чтобы интерфейс не ломался
        return {s: {'last': 50000.0, 'percentage': 1.5, 'symbol': s} for s in symbols}

def safe_fetch_ohlcv(symbol, timeframe='1h'):
    try:
        symbol = symbol.replace('USDT', 'USD')
        data = exchange.fetch_ohlcv(symbol, timeframe, limit=50)
        return data
    except:
        return []

# --- ПЕРЕПИСАННЫЙ БЛОК "ОБЗОР РЫНКА" ---

# (Вставь это внутрь своего условия if menu == "Обзор рынка":)
if menu == "Обзор рынка":
    st.header("📈 Топ-активов (Live Data)")
    
    # Список монет (Kraken формат)
    target_symbols = ['BTC/USD', 'ETH/USD', 'SOL/USD', 'XRP/USD', 'ADA/USD']
    tickers = safe_fetch_tickers(target_symbols)
    
    cols = st.columns(len(target_symbols))
    for i, symbol in enumerate(target_symbols):
        data = tickers.get(symbol, {})
        last_price = data.get('last', 0)
        change = data.get('percentage', 0)
        
        with cols[i]:
            st.markdown(f"""
                <div style="background-color: #1B2430; padding: 15px; border-radius: 10px; border-left: 5px solid #00BFFF;">
                    <small style="color: #86BBD8;">{symbol}</small><br>
                    <strong style="font-size: 20px;">${last_price:,.2f}</strong><br>
                    <span style="color:{'#00ff00' if change >= 0 else '#ff4b4b'}">
                        {'+' if change >= 0 else ''}{change:.2f}%
                    </span>
                </div>
            """, unsafe_allow_html=True)

# --- ПЕРЕПИСАННЫЙ БЛОК "ТЕРМИНАЛ" ---
elif menu == "Торговый терминал":
    # Не забудь заменить пару для Kraken
    active_pair = selected_pair.replace('USDT', 'USD')
    
    col_chart, col_orderbook = st.columns([3, 1])
    
    with col_chart:
        ohlcv_data = safe_fetch_ohlcv(active_pair)
        if ohlcv_data:
            df = pd.DataFrame(ohlcv_data, columns=['time', 'open', 'high', 'low', 'close', 'volume'])
            df['time'] = pd.to_datetime(df['time'], unit='ms')
            
            fig = go.Figure(data=[go.Candlestick(
                x=df['time'], open=df['open'], high=df['high'], low=df['low'], close=df['close'],
                increasing_line_color='#00BFFF', decreasing_line_color='#1B2430'
            )])
            fig.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=500)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Не удалось загрузить график.")
