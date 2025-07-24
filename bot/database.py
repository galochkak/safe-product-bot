# bot/database.py

import json
from pathlib import Path

DATA_PATH = Path(__file__).parent.parent / "data" / "banned_additives.json"

banned_additives = {}

try:
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    # Если JSON имеет вложенность через "additives", используем её
    if isinstance(raw_data, dict) and "additives" in raw_data:
        raw_data = raw_data["additives"]

    if not isinstance(raw_data, dict):
        raise ValueError("Данные должны быть объектом (dict)")

    for code, info in raw_data.items():
        if code.startswith("E") and isinstance(info, dict) and "name_ru" in info:
            banned_additives[code] = info

    print(f"? Успешно загружено {len(banned_additives)} пищевых добавок")

except Exception as e:
    print(f"[Ошибка] Не удалось загрузить базу: {e}")
    banned_additives = {}