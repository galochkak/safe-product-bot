# bot/utils.py

import os
import json
import requests
from bs4 import BeautifulSoup

DATA_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'banned_additives.json')


def fetch_e_numbers():
    """Парсит E-добавки с Wikipedia"""
    url = "https://en.wikipedia.org/wiki/E_number "
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        e_numbers = {}
        tables = soup.find_all('table', {'class': 'wikitable'})

        for table in tables:
            rows = table.find_all('tr')[1:]  # Пропускаем заголовок
            for row in rows:
                cols = row.find_all('td')
                if len(cols) >= 3:
                    code = cols[0].get_text(strip=True)
                    name = cols[1].get_text(strip=True)
                    description = cols[2].get_text(strip=True)

                    if code.startswith("E") and len(code) <= 5:
                        e_numbers[code] = {
                            "name_ru": name,
                            "description": description,
                            "status": "Неизвестно",
                            "banned_in": [],
                            "allowed_in": []
                        }

        return e_numbers
    except Exception as e:
        print(f"[Ошибка при парсинге]: {e}")
        return {}


def update_json_file(data):
    """Обновляет JSON-файл с новыми добавками"""
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            existing_data = json.load(f)
    except FileNotFoundError:
        existing_data = {}

    merged_data = {**existing_data, **data}

    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(merged_data, f, ensure_ascii=False, indent=4)

    return len(data)

def load_data():
    if not os.path.exists(DATA_FILE):
        print("[Предупреждение] Файл базы данных не найден. Создаю новый...")
        data = {"users": {}, "total_messages": 0, "additives": {}}
        save_data(data)
        return data
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[Критическая ошибка] Не удалось загрузить базу добавок: {e}")
        return {"users": {}, "total_messages": 0, "additives": {}}

def save_data(data):
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)