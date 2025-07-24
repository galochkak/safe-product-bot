import json
import os

# Пример базы (можно расширить потом)
banned_additives = {
    "E102": {
        "name_ru": "Тартразин",
        "description": "Жёлтый краситель. Может вызывать гиперактивность.",
        "status": "Запрещён в некоторых странах",
        "banned_in": ["Норвегия", "Австрия"],
        "allowed_in": ["Россия", "США"]
    },
    "E123": {
        "name_ru": "Амарант",
        "description": "Красный краситель. Подозревается в канцерогенности.",
        "status": "Запрещён во многих странах",
        "banned_in": ["США", "Япония", "Россия"]
    }
}

# Создаём папку data, если её нет
os.makedirs("data", exist_ok=True)

# Сохраняем в JSON с кодировкой UTF-8
with open("data/banned_additives.json", "w", encoding="utf-8") as f:
    json.dump(banned_additives, f, ensure_ascii=False, indent=2)

print("✅ Файл banned_additives.json создан!")