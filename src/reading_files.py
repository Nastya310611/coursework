import os
import pandas as pd


def reading_excel_files():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, '..', 'data', 'operations.xlsx')
    df = pd.read_excel(file_path, engine='openpyxl')
    data_list = df.to_dict(orient='records')
    return data_list
