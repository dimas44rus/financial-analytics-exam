import pandas as pd
import numpy as np

def generate_mock_data():
    """Генерация тестовых данных о расходах (минимум 20 элементов)"""
    np.random.seed(42)
    categories = ['Продукты', 'Транспорт', 'Кафе', 'Развлечения', 'Инвестиции']
    data = {
        'ID': range(1, 26),
        'Категория': np.random.choice(categories, 25),
        'Сумма': np.random.randint(500, 15000, 25),
        'Дата': pd.date_range(start='2026-01-01', periods=25, freq='D')
    }
    return pd.DataFrame(data)

def filter_by_category(df, category):
    """Фильтрация данных по выбранной категории"""
    if category == "Все":
        return df
    return df[df['Категория'] == category]
