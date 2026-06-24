import pandas as pd
from app.services.data_service import filter_by_category

def test_filter_all_categories():
    df = pd.DataFrame({'Категория': ['Продукты', 'Транспорт']})
    result = filter_by_category(df, "Все")
    assert len(result) == 2

def test_filter_specific_category():
    df = pd.DataFrame({'Категория': ['Продукты', 'Транспорт']})
    result = filter_by_category(df, "Продукты")
    assert len(result) == 1
    assert result.iloc[0]['Категория'] == 'Продукты'
