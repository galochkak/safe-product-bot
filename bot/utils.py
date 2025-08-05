# bot/utils.py

import os
import json
import requests
from bs4 import BeautifulSoup

# Определяем пути
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE = os.path.join(BASE_DIR, 'data', 'banned_additives.json')
STATS_FILE = os.path.join(BASE_DIR, 'data', 'stats.json')


def build_response(items, country=None):
    """
    Формирует список сообщений, разбитых по частям (макс. 4096 символов).
    """
    if not items:
        return ["✅ Запрещённых или опасных добавок не найдено."]

    max_length = 4096
    messages = []
    current_message = ""

    if country:
        current_message += f"<b>⚠️ Для <i>{country}</i>:</b>\n\n"

    for item in items:
        status = item.get("country_status", "ℹ️ Статус неизвестен")
        name = item.get("name", "Неизвестная добавка")
        code = item.get("code", "неизвестный код")
        description = item.get("description", "нет описания")

        line = (
            f"<b>{code}</b> — {name}\n"
            f"{status}\n"
            f"Описание: {description}\n\n"
        )

        if len(current_message) + len(line) > max_length:
            messages.append(current_message)
            current_message = line
        else:
            current_message += line

    if current_message.strip():
        messages.append(current_message)

    return messages


def get_country_by_language(language_code):
    """
    Возвращает страну по языковому коду пользователя.
    """
    country_map = {
        "ru": "Россия",
        "uk": "Украина",
        "be": "Беларусь",
        "en": "США",
        "es": "Испания",
        "de": "Германия",
        "fr": "Франция",
        "it": "Италия",
        "pl": "Польша",
        "tr": "Турция"
    }
    return country_map.get(language_code, "Россия")


def fetch_e_numbers():
    """
    Заглушка. Парсинг Wikipedia не работает стабильно.
    Используется локальная база данных.
    """
    print("[INFO] fetch_e_numbers() — временно отключён. Используется локальная база.")
    return {}


def update_json_file(data):
    """
    Обновляет JSON-файл с новыми добавками.
    """
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
        else:
            existing_data = {}

        # Объединяем данные
        merged_data = {**existing_data, **data}

        # Сохраняем
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(merged_data, f, ensure_ascii=False, indent=4)

        print(f"[INFO] Обновлено {len(data)} добавок в базе данных.")
        return len(data)
    except Exception as e:
        print(f"[Ошибка] Не удалось обновить базу данных: {e}")
        return 0


def load_data():
    """
    Загружает данные из JSON-файла.
    """
    if not os.path.exists(DATA_FILE):
        print("[Предупреждение] Файл базы данных не найден. Создаю новый...")
        data = {"users": {}, "total_messages": 0}
        save_data(data)
        return data

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            raw_data = json.load(f)
            if "users" not in raw_data:
                raw_data["users"] = {}
            if "total_messages" not in raw_data:
                raw_data["total_messages"] = 0
            return raw_data
    except Exception as e:
        print(f"[Критическая ошибка] Не удалось загрузить базу: {e}")
        return {"users": {}, "total_messages": 0}


def save_data(data):
    """
    Сохраняет данные в JSON-файл.
    """
    os.makedirs(os.path.dirname(STATS_FILE), exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    # Не возвращаем ничего — убираем 'return messages'