# bot/utils.py

import json
import requests

def load_data():
    """Загружает статистику пользователей"""
    try:
        with open("bot/users.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"users": {}, "total_messages": 0}


def save_data(data):
    """Сохраняет статистику пользователей"""
    with open("bot/users.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    # ❌ Никогда не возвращайте 'messages'!
    return True  # ✅


def build_response(items, country=None):
    """Разбивает список на сообщения по 4096 символов"""
    if not items:
        return ["✅ Запрещённых или опасных добавок не найдено."]

    max_length = 4096
    messages = []
    current_message = ""

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


def fetch_e_numbers():
    """
    Загружает актуальную базу E-добавок с GitHub.
    Пример URL: замените на свой репозиторий
    """
    url = "https://raw.githubusercontent.com/ ваш_пользователь/ваш_репозиторий/main/data/banned_additives.json"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Если есть вложенность {"additives": {...}}, извлекаем
        if isinstance(data, dict) and "additives" in data:
            data = data["additives"]
            
        return data
    except Exception as e:
        print(f"[Ошибка] Не удалось загрузить данные: {e}")
        return {}


def update_json_file(new_additives):
    """
    Обновляет локальный JSON-файл новыми данными.
    """
    if not new_additives:
        return 0

    try:
        with open("data/banned_additives.json", "r", encoding="utf-8") as f:
            current_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        current_data = {}

    added_count = 0
    for code, info in new_additives.items():
        if code.startswith("E") and code not in current_data:
            current_data[code] = info
            added_count += 1

    with open("data/banned_additives.json", "w", encoding="utf-8") as f:
        json.dump(current_data, f, indent=2, ensure_ascii=False)

    return added_count