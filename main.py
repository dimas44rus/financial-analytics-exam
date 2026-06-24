import streamlit as st
import pandas as pd
import plotly.express as px
from config.settings import APP_TITLE
from app.services.data_service import generate_mock_data, filter_by_category
from app.utils.analytics import calculate_summary

st.set_page_config(page_title=APP_TITLE, layout="wide")

# Инициализация сессии для авторизации
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# --- ОКНО АВТОРИЗАЦИИ ---
if not st.session_state.logged_in:
    st.container()
    st.title("🔐 Вход в систему")
    with st.form("login_form"):
        username = st.text_input("Логин (Имя пользователя)")
        password = st.text_input("Пароль", type="password")
        submit = st.form_submit_button("Войти в аккаунт")
        
        if submit:
            if username and password: # Упрощенная проверка для экзамена
                st.session_state.logged_in = True
                st.session_state.username = username
                st.rerun()
            else:
                st.error("Пожалуйста, заполните все поля")
    st.stop()

# --- ГЛАВНЫЙ ИНТЕРФЕЙС (ПОСЛЕ ВХОДА) ---
st.sidebar.markdown(f"👤 Пользователь: **{st.session_state.username}**")
if st.sidebar.button("Выйти из аккаунта"):
    st.session_state.logged_in = False
    st.rerun()

st.title(APP_TITLE)

# --- ИСТОЧНИК ДАННЫХ ---
st.sidebar.header("📁 Источник данных")
# Добавили третий универсальный вариант в ваше меню
data_source = st.sidebar.radio(
    "Выберите данные:", 
    ["Тестовые данные", "Загрузить свои данные (CSV)", "Универсальный анализатор (любые файлы)"]
)

# === ЛОГИКА ДЛЯ ВАШИХ СТАРЫХ ВАРИАНТОВ ===
if data_source in ["Тестовые данные", "Загрузить свои данные (CSV)"]:
    if data_source == "Тестовые данные":
        df = generate_mock_data()
    else:
        uploaded_file = st.sidebar.file_uploader("Загрузите ваш CSV-файл", type=["csv"])
        if uploaded_file is not None:
            try:
                df = pd.read_csv(uploaded_file)
                required_cols = ['Категория', 'Сумма', 'Дата']
                if not all(col in df.columns for col in required_cols):
                    st.sidebar.warning("Убедитесь, что в файле есть колонки: Категория, Сумма, Дата. Показываем тестовые.")
                    df = generate_mock_data()
            except Exception as e:
                st.sidebar.error(f"Ошибка чтения файла: {e}")
                df = generate_mock_data()
        else:
            st.info("💡 Загрузите CSV-файл в боковом меню. Пока показываются демонстрационные данные.")
            df = generate_mock_data()

    # --- ВАША СТАРЯ ФИЛЬТРАЦИЯ И АНАЛИТИКА ---
    st.sidebar.header("⏳ Фильтры")
    categories = ["Все"] + list(df['Категория'].unique()) if 'Категория' in df.columns else ["Все"]
    selected_category = st.sidebar.selectbox("Выберите категорию:", categories)

    filtered_df = filter_by_category(df, selected_category)

    # Аналитическая сводка
    stats = calculate_summary(filtered_df)
    col1, col2, col3 = st.columns(3)
    col1.metric("Общий оборот", f"{stats['total']} ₽")
    col2.metric("Средний чек", f"{stats['avg']} ₽")
    col3.metric("Макс. транзакция", f"{stats['max']} ₽")

    # Графики
    st.subheader("📊 Аналитика и Визуализация")
    g1, g2 = st.columns(2)

    with g1:
        if 'Категория' in filtered_df.columns and 'Сумма' in filtered_df.columns:
            fig_pie = px.pie(filtered_df, values='Сумма', names='Категория', title="Распределение по категориям / товарам")
            st.plotly_chart(fig_pie, use_container_width=True)

    with g2:
        if 'Дата' in filtered_df.columns and 'Сумма' in filtered_df.columns:
            fig_line = px.line(filtered_df, x='Дата', y='Сумма', title="Динамика по дням")
            st.plotly_chart(fig_line, use_container_width=True)

    # Таблица данных
    st.subheader("📋 Таблица операций")
    st.dataframe(filtered_df, use_container_width=True)

# === НОВАЯ ЛОГИКА ДЛЯ ЛЮБЫХ ФАЙЛОВ ===
else:
    st.subheader("📊 Универсальный анализ любых таблиц (CSV или Excel)")
    
    # Позволяем загружать и CSV, и Excel в этом режиме
    univ_file = st.file_uploader("Выберите любой файл для анализа", type=["csv", "xlsx", "xls"])
    
    if univ_file is not None:
        try:
            # Читаем файл в зависимости от расширения
            if univ_file.name.endswith('.csv'):
                df_any = pd.read_csv(univ_file)
            else:
                df_any = pd.read_excel(univ_file)
                
            st.success("✅ Файл успешно загружен!")
            
            # Показываем структуру файла
            st.subheader("📋 Предварительный просмотр данных")
            st.dataframe(df_any.head(10), use_container_width=True)
            
            # Динамически вытаскиваем названия колонок из загруженного файла
            all_cols = df_any.columns.tolist()
            numeric_cols = df_any.select_dtypes(include=['number']).columns.tolist()
            
            # Настройки графиков прямо на странице
            st.subheader("⚙️ Настройка графиков под ваш файл")
            c1, c2 = st.columns(2)
            
            with c1:
                group_col = st.selectbox("Выберите колонку для группировки (текст/категории):", options=all_cols)
            with c2:
                if numeric_cols:
                    value_col = st.selectbox("Выберите колонку с числами (для подсчета сумм):", options=numeric_cols)
                else:
                    value_col = None
                    st.warning("В файле нет числовых колонок для математических расчетов.")
            
            # Строим графики на основе выбора пользователя
            if value_col:
                # Группируем данные динамически
                summary_df = df_any.groupby(group_col)[value_col].sum().reset_index()
                
                g1, g2 = st.columns(2)
                with g1:
                    fig_any_pie = px.pie(summary_df, values=value_col, names=group_col, title=f"Доли: {group_col}")
                    st.plotly_chart(fig_any_pie, use_container_width=True)
                with g2:
                    fig_any_bar = px.bar(summary_df, x=group_col, y=value_col, title=f"Объемы по {group_col}")
                    st.plotly_chart(fig_any_bar, use_container_width=True)
            
            # Статистика по файлу
            st.subheader("🔢 Информация о таблице")
            st.write(f"Всего строк в файле: **{df_any.shape[0]}**, Всего колонок: **{df_any.shape[1]}**")
            
        except Exception as e:
            st.error(f"❌ Ошибка при чтении или обработке файла: {e}")
    else:
        st.info("💡 Пожалуйста, загрузите любой файл таблицы выше, чтобы протестировать этот режим.")
