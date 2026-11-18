import json
import re
import os
import pandas as pd
from src.reading_files import reading_excel_files


def search_translations(data: list[dict]) -> str:
    """Функция принимает список словарей с данными о банковских операциях,
    а возвращать список словарей с переводами физическим лицам"""
    data_with_search = []
    pattern = re.compile(r'\b[А-ЯЁ][а-яё]+\s+[А-ЯЁ]\.', re.IGNORECASE)
    for operation in data:
        category = operation.get('Категория', '')
        description = operation.get('Описание')
        if category == 'Переводы' and pattern.search(description):
            data_with_search.append(operation)

    return json.dumps(data_with_search, ensure_ascii=False, indent=4)

if __name__ == '__main__':
    result = search_translations(reading_excel_files())
    print(result)
