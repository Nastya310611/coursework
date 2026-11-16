import os.path
from datetime import datetime
import pandas as pd
from functools import wraps
from typing import Callable, ParamSpec, TypeVar
from dateutil.relativedelta import relativedelta
from src.reading_files import reading_excel_files

P = ParamSpec("P")
T = TypeVar("T")


def save_report(filename: str | None = None):
    """Декоратор дл сохранения результата функции в файл"""
    if callable(filename):
        func = filename
        return save_report()(func)
    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        """Внутренний декоратор, который принимает функцию для логирования"""
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            """Выполнение функции"""
            result = func(*args, **kwargs)
            if filename:
                target_file = filename
            else:
                current_time = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
                target_file = f'report_{current_time}.txt'
            try:
                if isinstance(result, pd.DataFrame):
                    result.to_csv(target_file, sep='\t', index=True)
                else:
                    with open(target_file, "w", encoding="utf-8") as f:
                        f.write(str(result))
                print(f'Отчет сохранен: {target_file}')
            except Exception as e:
                print(f"Ошибка при сохранении файла: {e}")
            return result

        return wrapper
    return decorator

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
data_dir = os.path.join(base_dir, 'data')

@save_report(os.path.join(data_dir, 'Средние_траты_по_дням_недели.txt'))
def spending_by_weekday(transactions: pd.DataFrame,
                        date: Optional[str] = None) -> pd.DataFrame:
    """Функция выводит средние траты в каждый из дней недели за последние три месяца"""
    if date is None:
        end_date = datetime.now()
    else:
        end_date = datetime.strptime(date, '%Y-%m-%d')
    start_date = end_date - relativedelta(months=3)
    df = transactions.copy()
    df['Дата платежа'] = pd.to_datetime(df['Дата платежа'], dayfirst=True)
    mask = (df['Дата платежа'] >= start_date) & (df['Дата платежа'] <= end_date)
    filtered_df = df.loc[mask].copy()
    filtered_df['Снмма платежа'] = pd.to_numeric(filtered_df['Сумма платежа'], errors='coerce').abs()

    filtered_df['weekday'] = filtered_df['Дата платежа'].dt.day_name()
    result = filtered_df.groupby('weekday')['Сумма платежа'].mean().reset_index()
    result.columns = ['День недели', 'Средние траты']
    return result


if __name__ == '__main__':
    dfs_list = reading_excel_files()
    if dfs_list:
        df = pd.DataFrame(dfs_list)
        result = spending_by_weekday(df, date='2021-12-31')
        print(result)