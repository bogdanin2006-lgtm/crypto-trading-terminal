import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import ccxt
import requests
import time
from datetime import datetime

# --- 1. КОНФИГУРАЦИЯ ---
st.set_page_config(layout="wide", page_title="Blue Horizon: Command", page_icon="💠")
st.markdown("""<style>.stApp{background-color:#050505;color:#e0fbfc;font-family:sans-serif;}</style>""", unsafe_allow_html=True)

# --- 2. ФУНКЦИИ (ТОЛЬКО ЛОГИКА) ---

def get_token():
    # Читаем токен ТОЛЬКО из секретов
    try:
        return st.secrets["TG_BOT_TOKEN"]
    except:
        return None

def get_real_bot_username():
    """Спрашиваем у Телеграма имя бота по Токену"""
    token = get_token()
    if not token: return None
    
    try:
        # ЗАПРОС К API ТЕЛЕГРАМА (getMe)
        res = requests.get(f"https://api.telegram.org/bot{token}/getMe").json()
        if res.get("ok"):
            # Возвращаем РЕАЛЬНОЕ имя бота (без @)
            return res["result"]["username"]
    except Exception as e:
        st.error(f"Ошибка связи с Telegram API: {e}")
    return None

def check_updates_for_connect():
    """Ищет команду /start от пользователя"""
    token = get_token()
    if not token: return None
    
    try:
        res = requests.get(f"https://api.telegram.org/bot{token}/getUpdates").json()
        if res.get("ok") and res["result"]:
            # Берем последнее сообщение
            last_msg = res["result"][-1]
            chat_id = str(last_msg["message"]["chat"]["id"])
            text = last_msg["message"].get("text", "")
            
            # Если юзер нажал START
            if "/start" in text:
                return chat_id
    except:
        pass
    return None

def send_msg(chat_id, text):
    token = get_token()
    if token and chat_id:
        requests.post(f"https://api.telegram.org/bot{token}/sendMessage", json={"chat_id": chat_id, "text": text, "parse_mode": "HTML"})

# --- 3. ИНТЕРФЕЙС ---

# При загрузке страницы узнаем имя бота
if "bot_username" not in st.session_state:
    st.session_state.bot_username = get_real_bot_username()

if "tg_id" not in st.session_state:
    st.session_state.tg_id = None

# САЙДБАР
with st.sidebar:
    st.title("💠 BLUE HORIZON")
    
    # ПРОВЕРКА ТОКЕНА
    token = get_token()
    if not token:
        st.error("❌ Токен не найден!")
        st.info("Добавь TG_BOT_TOKEN в .streamlit/secrets.toml")
    elif not st.session_state.bot_username:
        st.warning("⚠️ Токен есть, но бот не отвечает. Проверь правильность токена.")
    else:
        st.success(f"🤖 Система: @{st.session_state.bot_username}")

    st.markdown("---")
    
    if st.session_state.tg_id:
        st.success("🟢 ПОДКЛЮЧЕНО")
        if st.button("Отключиться"):
            st.session_state.tg_id = None
            st.rerun()
    else:
        st.warning("🔴 НЕ ПОДКЛЮЧЕНО")

# ГЛАВНЫЙ ЭКРАН
st.title("🎛️ Панель управления")

if not st.session_state.tg_id:
    st.markdown("### 1. Подключение бота")
    
    # Если имя бота удалось получить автоматически
    if st.session_state.bot_username:
        bot_name = st.session_state.bot_username
        
        # ГЕНЕРИРУЕМ ССЫЛКУ ИМЕННО НА ЭТОГО БОТА
        link = f"https://t.me/{bot_name}?start=connect"
        
        st.markdown(f"""
            <a href="{link}" target="_blank">
                <button style="
                    background-color: #0088cc; color: white; border: none;
                    padding: 15px 30px; font-size: 18px; border-radius: 8px; cursor: pointer;
                    width: 100%; font-weight: bold;">
                    👉 ОТКРЫТЬ @{bot_name}
                </button>
            </a>
        """, unsafe_allow_html=True)
        
        st.info("Нажми кнопку выше, затем нажми START в Телеграме, и вернись сюда.")
        st.write("")
        
        if st.button("🔄 Я НАЖАЛ START (ПРОВЕРИТЬ)"):
            with st.spinner("Поиск вашего ID..."):
                time.sleep(1)
                found_id = check_updates_for_connect()
                
                if found_id:
                    st.session_state.tg_id = found_id
                    send_msg(found_id, "✅ <b>ТЕРМИНАЛ УСПЕШНО ПОДКЛЮЧЕН!</b>")
                    st.success("Готово! Ваш ID найден.")
                    st.rerun()
                else:
                    st.error("Сигнал не найден. Убедитесь, что нажали /start в боте.")
    else:
        st.error("Система не может определить имя бота. Проверьте Токен в секретах.")

else:
    # КОГДА ПОДКЛЮЧЕНО
    st.markdown("### ✅ Уведомления активны")
    st.write(f"Ваш ID: `{st.session_state.tg_id}`")
    
    col1, col2 = st.columns(2)
    with col1:
        st.info("Тест связи")
        if st.button("🔔 ОТПРАВИТЬ ТЕСТ"):
            send_msg(st.session_state.tg_id, "👋 Привет! Это тест связи с терминала.")
            st.toast("Отправлено!", icon="✅")
            
    with col2:
        st.error("Опасная зона")
        if st.button("🚨 СИГНАЛ ТРЕВОГИ"):
            send_msg(st.session_state.tg_id, "🚨 <b>ВНИМАНИЕ!</b>\nКритическое изменение цены!")
            st.toast("Тревога отправлена!", icon="🔥")
