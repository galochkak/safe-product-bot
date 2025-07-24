# update_additives.py

import requests
from bs4 import BeautifulSoup
import json
import os

# Путь к файлу с данными
DATA_FILE = os.path.join(os.path.dirname(__file__), 'data', 'banned_additives.json')

# Пример URL (можно заменить на другие)
URL = "https://en.wikipedia.org/wiki/E_number "

def fetch_e_numbers():
    response = requests.get(URL)
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


def update_json_file(data):
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            existing_data = json.load(f)
    except FileNotFoundError:
        existing_data = {}

    # Объединяем данные
    merged_data = {**existing_data, **data}

    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(merged_data, f, ensure_ascii=False, indent=4)

    print(f"[+] Обновлено {len(data)} новых E-добавок")


if __name__ == "__main__":
    new_additives = fetch_e_numbers()
    update_json_file(new_additives)