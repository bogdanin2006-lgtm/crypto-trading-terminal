import streamlit as st
import pandas as pd
import pandas_ta as ta
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from sklearn.linear_model import LinearRegression
import numpy as np
from datetime import datetime, timedelta

# --- 1. CONFIG ---
st.set_page_config(layout="wide", page_title="QUANTUM: ALGO TERMINAL", page_icon="📈")

st.markdown("""
<style>
    .stApp { background-color: #0b0e11; color: white; }
    div[data-testid="stMetric"] { background-color: #151a21; border-radius: 5px; padding: 10px; border: 1px solid #2a2e39; }
    h1, h2, h3 { color: #00e5ff; }
</style>
""", unsafe_allow_html=True)

# --- 2. DATA ENGINE (FIXED FOR NEW YFINANCE) ---
@st.cache_data(ttl=60)
def get_market_data(ticker, period="1mo", interval="1h"):
    """Fetch real data from Yahoo Finance with robust cleaning"""
    try:
        df = yf.download(ticker, period=period, interval=interval, progress=False)
        
        # --- FIX: Убираем мульти-индекс (причина твоей ошибки) ---
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        
        # Сброс индекса, чтобы дата стала колонкой
        df.reset_index(inplace=True)
        
        # Приводим названия колонок к единому виду (маленькие буквы)
        df.columns = [c.lower() for c in df.columns]
        
        # Переименовываем дату, чтобы она была 'time'
        if 'date' in df.columns:
            df.rename(columns={'date': 'time'}, inplace=True)
        elif 'datetime' in df.columns:
             df.rename(columns={'datetime': 'time'}, inplace=True)

        # Удаляем лишние колонки, если вдруг они задублировались
        df = df.loc[:, ~df.columns.duplicated()]

        # Проверка: если данных нет, вернуть пустоту
        if df.empty:
            return pd.DataFrame()

        # --- PANDAS TA (PROFESSIONAL INDICATORS) ---
        # Теперь данные чистые, pandas_ta не будет падать
        
        # 1. RSI
        df.ta.rsi(length=14, append=True)
        # 2. MACD
        df.ta.macd(append=True)
        # 3. Bollinger Bands
        df.ta.bbands(length=20, std=2, append=True)
        # 4. ADX
        df.ta.adx(length=14, append=True)
        
        # 5. EMA (Ошибка была тут, теперь исправлена)
        # Мы явно берем Series (столбец), даже если ta вернет DF
        ema50 = df.ta.ema(length=50)
        ema200 = df.ta.ema(length=200)
        
        # Если ema вернулся как DataFrame (иногда бывает), берем первую колонку
        if isinstance(ema50, pd.DataFrame): ema50 = ema50.iloc[:, 0]
        if isinstance(ema200, pd.DataFrame): ema200 = ema200.iloc[:, 0]
            
        df['EMA_50'] = ema50
        df['EMA_200'] = ema200

        df.dropna(inplace=True)
        return df
        
    except Exception as e:
        st.error(f"Data Error: {e}")
        return pd.DataFrame()

def run_ml_forecast(df):
    """Real Machine Learning: Linear Regression Trend"""
    if df.empty: return np.zeros(10), 0
    
    df = df.copy()
    # Преобразуем дату в число для регрессии
    df['ordinal_date'] = df['time'].apply(lambda x: x.toordinal())
    
    X = df[['ordinal_date']].values
    y = df['close'].values
    
    # Train Model
    model = LinearRegression()
    model.fit(X, y)
    
    # Predict next 10 candles
    last_date = df['ordinal_date'].iloc[-1]
    future_dates = np.array([last_date + i for i in range(1, 11)]).reshape(-1, 1)
    future_pred = model.predict(future_dates)
    
    return future_pred, model.coef_[0]

# --- 3. SIDEBAR ---
with st.sidebar:
    st.title("⚡ QUANTUM ALGO")
    ticker = st.selectbox("Symbol", ["BTC-USD", "ETH-USD", "SOL-USD", "NVDA", "TSLA", "AAPL"])
    timeframe = st.selectbox("Interval", ["1h", "1d", "1wk"], index=1)
    
    st.markdown("### ⚙️ Strategy Settings")
    rsi_threshold = st.slider("RSI Overbought", 50, 90, 70)
    
    st.info("System uses Pandas-TA + Scikit-Learn (Linear Reg).")

# --- 4. MAIN LOGIC ---
st.title(f"📊 {ticker} QUANTITATIVE ANALYSIS")

# Загружаем данные с обработкой ошибок
df = get_market_data(ticker, period="6mo", interval=timeframe)

if not df.empty and len(df) > 20:
    current_price = df['close'].iloc[-1]
    
    # ML Prediction
    forecast, trend_slope = run_ml_forecast(df)
    trend_msg = "BULLISH 🚀" if trend_slope > 0 else "BEARISH 🔻"
    
    # Signal Logic
    # Проверяем наличие колонок перед обращением
    try:
        last_rsi = df['RSI_14'].iloc[-1]
        last_macd = df['MACD_12_26_9'].iloc[-1]
        last_signal = df['MACDs_12_26_9'].iloc[-1]
        
        signal = "NEUTRAL"
        if last_rsi < 30: signal = "STRONG BUY (Oversold)"
        elif last_rsi > rsi_threshold: signal = "SELL (Overbought)"
        elif last_macd > last_signal: signal = "BUY (MACD Crossover)"
    except KeyError:
        signal = "CALCULATING..."
        last_rsi = 50
        trend_slope = 0

    # --- 5. DASHBOARD METRICS ---
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Current Price", f"${current_price:,.2f}")
    c2.metric("ML Trend", trend_msg, f"Slope: {trend_slope:.4f}")
    c3.metric("RSI (14)", f"{last_rsi:.2f}", "-Overbought" if last_rsi > 70 else "Neutral")
    c4.metric("Algo Signal", signal, delta_color="normal")

    # --- 6. ADVANCED PLOTLY CHART ---
    fig = make_subplots(rows=3, cols=1, shared_xaxes=True, 
                        vertical_spacing=0.05, row_heights=[0.6, 0.2, 0.2],
                        subplot_titles=(f'{ticker} Price & ML Forecast', 'RSI Momentum', 'MACD Oscillator'))

    # ROW 1: CANDLES + BBANDS + ML
    fig.add_trace(go.Candlestick(x=df['time'], open=df['open'], high=df['high'], low=df['low'], close=df['close'], name='Price'), row=1, col=1)
    
    # Проверка на наличие полос Боллинджера
    if 'BBU_20_2.0' in df.columns:
        fig.add_trace(go.Scatter(x=df['time'], y=df['BBU_20_2.0'], line=dict(color='rgba(0, 255, 255, 0.3)', width=1), name='Upper BB'), row=1, col=1)
        fig.add_trace(go.Scatter(x=df['time'], y=df['BBL_20_2.0'], line=dict(color='rgba(0, 255, 255, 0.3)', width=1), fill='tonexty', name='Lower BB'), row=1, col=1)
    
    # ML Forecast Line
    future_times = [df['time'].iloc[-1] + timedelta(hours=i) if timeframe=='1h' else df['time'].iloc[-1] + timedelta(days=i) for i in range(1, 11)]
    fig.add_trace(go.Scatter(x=future_times, y=forecast, line=dict(color='#ff00ff', width=2, dash='dot'), name='AI Prediction'), row=1, col=1)

    # ROW 2: RSI
    if 'RSI_14' in df.columns:
        fig.add_trace(go.Scatter(x=df['time'], y=df['RSI_14'], line=dict(color='#e0fbfc', width=2), name='RSI'), row=2, col=1)
        fig.add_hline(y=70, line_dash="dot", row=2, col=1, line_color="red")
        fig.add_hline(y=30, line_dash="dot", row=2, col=1, line_color="green")

    # ROW 3: MACD
    if 'MACD_12_26_9' in df.columns:
        fig.add_trace(go.Bar(x=df['time'], y=df['MACDh_12_26_9'], marker_color=np.where(df['MACDh_12_26_9'] < 0, 'red', 'green'), name='MACD Hist'), row=3, col=1)
        fig.add_trace(go.Scatter(x=df['time'], y=df['MACD_12_26_9'], line=dict(color='orange'), name='MACD'), row=3, col=1)
        fig.add_trace(go.Scatter(x=df['time'], y=df['MACDs_12_26_9'], line=dict(color='blue'), name='Signal'), row=3, col=1)

    fig.update_layout(height=800, plot_bgcolor='#0b0e11', paper_bgcolor='#0b0e11', font=dict(color='white'), xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)

    # --- 7. STATISTICS TABLE ---
    st.subheader("📋 Statistical Data")
    cols_to_show = ['time', 'close', 'RSI_14', 'ADX_14', 'EMA_50']
    # Показываем только те колонки, которые реально существуют
    available_cols = [c for c in cols_to_show if c in df.columns]
    
    stats_df = df.tail(10)[available_cols].sort_values(by='time', ascending=False)
    st.dataframe(stats_df, use_container_width=True)

else:
    st.warning("No data found. Try selecting a different ticker (e.g. BTC-USD) or wait a moment.")
    st.write("Debug: DataFrame is empty or connection failed.")
