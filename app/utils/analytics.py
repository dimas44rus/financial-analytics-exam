def calculate_summary(df):
    """Расчет базовых метрик"""
    if df.empty:
        return {"total": 0, "avg": 0, "max": 0}
    return {
        "total": int(df['Сумма'].sum()),
        "avg": int(df['Сумма'].mean()),
        "max": int(df['Сумма'].max())
    }
