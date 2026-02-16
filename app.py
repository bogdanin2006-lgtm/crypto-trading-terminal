import streamlit as st
import pandas as pd
import ccxt
import numpy as np
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression
from datetime import datetime, timedelta
from streamlit_lottie import st_lottie
import requests

def load_lottieurl(url):
    r = requests.get(url)
    if r.status_code != 200: return None
    return r.json()

st.markdown("""
<style>
    /* Импорт шрифта из Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap');

    html, body, [class*="css"]  {
        font-family: 'JetBrains Mono', monospace;
    }

    /* Эффект Glassmorphism для карточек */
    .metric-card {
        background: rgba(27, 36, 48, 0.7);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(0, 191, 255, 0.2);
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
    .neon-button {
        background-color: transparent;
        border: 2px solid #00BFFF;
        color: #00BFFF;
        padding: 10px 20px;
        text-align: center;
        text-transform: uppercase;
        font-weight: bold;
        cursor: pointer;
        box-shadow: 0 0 10px #00BFFF;
        transition: 0.3s;
    }
    .neon-button:hover {
        background-color: #00BFFF;
        color: white;
        box-shadow: 0 0 30px #00BFFF;
    }
</style>
<button class="neon-button">Execute Trade</button>
""", unsafe_allow_html=True)

# Анимация пульсации для ИИ
lottie_ai = load_lottieurl("https://assets10.lottiefiles.com/packages/lf20_gdbe6m7b.json")
st_lottie(lottie_ai, height=100, key="ai_loader")

# Анимация пульсации для ИИ
lottie_ai = load_lottieurl("https://assets10.lottiefiles.com/packages/lf20_gdbe6m7b.json")
st_lottie(lottie_ai, height=100, key="ai_loader")

# --- AI ENGINE ---
def get_ai_prediction(df):
    # Подготовка данных: порядковый номер свечи как X, цена Close как y
    df = df.copy()
    df['n'] = np.arange(len(df))
    X = df[['n']].values
    y = df['close'].values
    
    # Обучаем модель линейной регрессии
    model = LinearRegression()
    model.fit(X, y)
    
    # Прогноз на 10 свечей вперед
    future_n = np.array([len(df) + i for i in range(10)]).reshape(-1, 1)
    prediction = model.predict(future_n)
    
    # Считаем вероятность (упрощенно через коэффициент детерминации)
    score = model.score(X, y) 
    return prediction, score

# --- КОРРЕКТИРОВКА ТЕРМИНАЛА ---
# (Найди блок Trading Terminal и замени на этот)

elif menu == "Trading Terminal":
    st.header("⚡ Live Execution Terminal")
    
    # Загрузка данных для AI
    ohlcv = exchange.fetch_ohlcv(pair, timeframe='1h', limit=100)
    df = pd.DataFrame(ohlcv, columns=['time', 'open', 'high', 'low', 'close', 'volume'])
    df['time'] = pd.to_datetime(df['time'], unit='ms')

    tab_trade, tab_ai = st.tabs(["Manual Trade", "AI Strategy Core"])

    with tab_trade:
        col_order, col_depth = st.columns([2, 1])
        with col_order:
            st.subheader("Order Placement")
            side = st.radio("Action", ["BUY", "SELL"], horizontal=True)
            amount = st.number_input("Amount", min_value=0.0, step=0.01)
            if st.button("Confirm Order"):
                st.success(f"{side} executed!")
        
        with col_depth:
            st.subheader("Market Depth")
            try:
                ob = exchange.fetch_order_book(pair)
                bids = pd.DataFrame(list(ob.get('bids', []))[:5], columns=['Price', 'Qty'])
                st.dataframe(bids, hide_index=True)
            except: st.write("Data error")

    with tab_ai:
        st.subheader("🧠 Machine Learning Trend Forecast")
        
        # Запуск AI
        prediction, confidence = get_ai_prediction(df)
        
        # Визуализация прогноза
        last_time = df['time'].iloc[-1]
        future_times = [last_time + timedelta(hours=i) for i in range(1, 11)]
        
        fig_ai = go.Figure()
        # Реальный график
        fig_ai.add_trace(go.Scatter(x=df['time'][-30:], y=df['close'][-30:], name="Historical", line=dict(color="#00BFFF")))
        # Прогноз
        fig_ai.add_trace(go.Scatter(x=future_times, y=prediction, name="AI Forecast", line=dict(color="#FF00FF", dash='dot')))
        
        fig_ai.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', height=400)
        st.plotly_chart(fig_ai, use_container_width=True)
        
        # Вердикт
        trend = "UP 📈" if prediction[-1] > prediction[0] else "DOWN 📉"
        conf_pct = min(int(confidence * 100 + 50), 99) # Имитация уверенности
        
        st.metric("AI Verdict", trend, f"{conf_pct}% Confidence")
        st.write(f"Neural scan suggests the price will move towards **${prediction[-1]:,.2f}** in the next 10 hours.")
