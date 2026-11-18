import heapq
import json
import requests
from datetime import datetime
from src.reading_files import reading_excel_files
import yfinance as yf


def greeting(date_string: str) -> str:
    """Функция возвращает приветствие в зависимости от времени суток"""
    now_time = datetime.now().hour
    if 6 <= now_time < 12:
        return 'Доброе утро'
    elif 12 <= now_time < 18:
        return 'Добрый день'
    elif 18 <= now_time < 23:
        return 'Добрый вечер'
    else:
        return 'Доброй ночи'


def get_card_info(transactions: list[dict]):
    """Функция собирает данные по последним 4 цифрам номера карты,
    сумме операций по этой карте"""
    cards_data = []
    for trans in transactions:
        card_number = trans.get("Номер карты")
        amount = trans.get("Сумма операции")

        if isinstance(card_number, str) and card_number and amount is not None:
            try:
                amount_float = float(str(amount). replace(',', '.'))
            except ValueError:
                continue

            if amount_float < 0:
                last_digits = f'**{card_number[-4:]}'
                card_exists = False
                for card in cards_data:
                    if card['last_digits'] == last_digits:
                        card_exists = True
                        card['total_spent'] += abs(amount_float)
                        break
                if not card_exists:
                    cards_data.append({
                        'last_digits': last_digits,
                        'total_spent': abs(amount_float),
                        'cashback': 0.0
                    })
    for card in cards_data:
        card['total_spent'] = round(card['total_spent'], 2)
        card['cashback'] = round(card['total_spent'] / 100, 2)
    return cards_data


def get_top_transactions(transactions: list[dict]) -> list[dict]:
    """Функция возвращает топ-5 транзакций по сумме платежа"""
    valid_transactions = []
    for trans in transactions:
        amount = trans.get('Сумма операции')
        if amount is None or amount == '':
            continue
        try:
            amount_float = float(str(amount).replace(',', '.'))
        except ValueError:
            continue

        if amount_float < 0:
            valid_transactions.append({
                'date': trans.get('Дата операции', ''),
                'amount': abs(amount_float),
                'category': trans.get('Категория', ''),
                'description': trans.get('Описание', '')
            })
    top_5 = heapq.nlargest(5, valid_transactions, key=lambda x: x['amount'])
    return top_5


def get_currency_rates(currencies: list = None) -> list[dict]:
    """Функция получает актуальные курсы валют через API"""
    if currencies is None:
        currencies = ['USD', 'EUR']
    url = 'https://api.exchangerate-api.com/v4/latest/RUB'
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()

        rates = []

        for curr in currencies:
            if curr in data['rates']:
                rate = round(1 / data['rates'][curr], 2)
                rates.append({'currency': curr, 'rate': rate})
        return rates

    except requests.RequestException as e:
        print(f'Ошибка API валют: {e}')
        return [{'currency': 'USD', 'rate': 90.0}, {'currency': 'EUR', 'rate': 98.0}]


def get_stock_prices():
    """Получаем цены акций S&P500 (топ-5 компаний)"""
    tickers = ["AAPL", "MSFT", "GOOGL"]
    result = []
    for t in tickers:
        try:
            # Пытаемся скачать
            stock = yf.Ticker(t)
            price = stock.history(period="1d")['Close'].iloc[-1]
            result.append({"stock": t, "price": round(price, 2)})
        except:
            result.append({"stock": t, "price": 0.0})
    return result


def main_page(date_string: str) -> str:
    """Главная функция для запуска всех функций"""
    try:
        # Получение данных их Excel
        transactions = reading_excel_files()
        # Приветствие
        greeting_text = greeting(date_string)
        # Получение данных по карте
        cards = get_card_info(transactions)
        # Получение топ-5 транзакций
        top_transactions = get_top_transactions(transactions)
        # Работа с API для получения данных о курсах валют и акциях
        currency_rates = get_currency_rates()
        stock_prices = get_stock_prices()

        response_dict = {
            'greeting': greeting_text,
            'cards': cards,
            'top_transactions': top_transactions,
            'currency_rates': currency_rates,
            'stock_prices': stock_prices
        }
        return json.dumps(response_dict, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({'error': str(e)}, ensure_ascii=False)


result = main_page('2021-12-31 14:30:00')
print(result)