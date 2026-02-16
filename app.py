import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import ccxt
import requests
import time
from datetime import datetime

# --- 1. CONFIG ---
st.set_page_config(layout="wide", page_title="Blue Horizon: Command", page_icon="💠")
st.markdown("""<style>.stApp{background-color:#050505;color:#e0fbfc;font-family:sans-serif;}</style>""", unsafe_allow_html=True)

# --- 2. ЛОГИКА БОТА ---

def get_token():
    try: return st.secrets["TG_BOT_TOKEN"]
    except: return None

def setup_bot_menu():
    """Создает кнопки (Меню) в самом Телеграме"""
    token = get_token()
    if not token: return
    
    # Настраиваем команды (Кнопки меню)
    commands = [
        {"command": "start", "description": "🚀 Запуск терминала"},
        {"command": "on", "description": "✅ Включить уведомления"},
        {"command": "off", "description": "🔕 Отключить уведомления"},
        {"command": "status", "description": "📡 Проверить связь"}
    ]
    # Отправляем настройку в Телеграм
    requests.post(f"https://api.telegram.org/bot{token}/setMyCommands", json={"commands": commands})

def get_bot_username():
    """Узнает имя бота"""
    try:
        res = requests.get(f"https://api.telegram.org/bot{get_token()}/getMe").json()
        return res["result"]["username"]
    except: return None

def check_updates():
    """Смотрит, что нажал юзер в Телеграме"""
    token = get_token()
    if not token: return None, None
    
    try:
        res = requests.get(f"https://api.telegram.org/bot{token}/getUpdates").json()
        if res.get("ok") and res["result"]:
            last_msg = res["result"][-1]
            chat_id = last_msg["message"]["chat"]["id"]
            text = last_msg["message"].get("text", "")
            return str(chat_id), text
    except:
        pass
    return None, None

def send_msg(chat_id, text):
    requests.post(f"https://api.telegram.org/bot{get_token()}/sendMessage", json={"chat_id": chat_id, "text": text, "parse_mode": "HTML"})

# --- 3. ИНТЕРФЕЙС ---

# При запуске сразу настраиваем кнопки в боте
if "bot_setup" not in st.session_state:
    setup_bot_menu()
    st.session_state.bot_setup = True
    st.session_state.bot_name = get_bot_username()

if "tg_id" not in st.session_state:
    st.session_state.tg_id = None
if "alerts_active" not in st.session_state:
    st.session_state.alerts_active = False

# САЙДБАР
with st.sidebar:
    st.title("💠 BLUE HORIZON")
    st.write("Control Panel")
    
    # Статус бота
    if st.session_state.bot_name:
        st.success(f"🤖 Бот: @{st.session_state.bot_name}")
    else:
        st.error("⚠️ Токен не найден!")

    st.markdown("---")
    
    # БЛОК СИНХРОНИЗАЦИИ
    if st.session_state.tg_id:
        st.success("🟢 СВЯЗЬ ЕСТЬ")
        st.code(f"ID: {st.session_state.tg_id}")
        
        # Индикатор состояния уведомлений
        if st.session_state.alerts_active:
            st.markdown("🔔 **Уведомления: ВКЛ**")
        else:
            st.markdown("🔕 **Уведомления: ВЫКЛ**")
            
        if st.button("Разорвать связь"):
            st.session_state.tg_id = None
            st.rerun()
    else:
        st.warning("🔴 НЕТ СВЯЗИ")

# ГЛАВНЫЙ ЭКРАН (ЛОГИКА ПРОВЕРКИ)
st.title("🎛️ Центр управления уведомлениями")

if not st.session_state.tg_id:
    st.info("Чтобы подключиться, открой бота и нажми кнопку '🚀 Запуск' в меню.")
    if st.session_state.bot_name:
        st.markdown(f"[👉 ОТКРЫТЬ БОТА](https://t.me/{st.session_state.bot_name})")
    
    # Кнопка проверки команд от бота
    if st.button("🔄 ПРОВЕРИТЬ КОМАНДЫ БОТА"):
        chat_id, command = check_updates()
        if chat_id:
            st.session_state.tg_id = chat_id
            if command == "/start":
                send_msg(chat_id, "<b>👋 Терминал подключен!</b>\nИспользуй Меню для управления.")
                st.success("Подключено!")
                st.rerun()
else:
    # Если подключено, слушаем команды Вкл/Выкл
    col1, col2 = st.columns(2)
    with col1:
        st.write("Слушаю команды из Телеграма...")
        if st.button("🔄 ОБНОВИТЬ СТАТУС КОМАНД"):
            chat_id, command = check_updates()
            if chat_id == st.session_state.tg_id:
                if command == "/on":
                    st.session_state.alerts_active = True
                    send_msg(chat_id, "✅ <b>Уведомления ВКЛЮЧЕНЫ</b>")
                    st.success("Получена команда: ВКЛЮЧИТЬ")
                elif command == "/off":
                    st.session_state.alerts_active = False
                    send_msg(chat_id, "🔕 <b>Уведомления ОТКЛЮЧЕНЫ</b>")
                    st.warning("Получена команда: ВЫКЛЮЧИТЬ")
                elif command == "/status":
                    status = "ВКЛ" if st.session_state.alerts_active else "ВЫКЛ"
                    send_msg(chat_id, f"📡 <b>Статус системы:</b> {status}")
    
    with col2:
        st.write("Тест отправки:")
        if st.button("🚀 ОТПРАВИТЬ ТЕСТОВЫЙ СИГНАЛ"):
            if st.session_state.alerts_active:
                send_msg(st.session_state.tg_id, "🚨 <b>ТЕСТОВЫЙ СИГНАЛ</b>\nЦена BTC изменилась!")
                st.toast("Отправлено!")
            else:
                st.error("Уведомления выключены пользователем (в боте).")
