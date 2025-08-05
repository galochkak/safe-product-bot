# bot/handlers.py

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, PhotoSize, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from bot.utils import load_data, save_data, build_response, fetch_e_numbers, update_json_file, get_country_by_language
from bot.database import banned_additives
from utils.ocr import extract_text_from_image

import os
import cv2
from pyzbar.pyzbar import decode
from dotenv import load_dotenv

load_dotenv()

router = Router()

# === Переменная для режима QR-сканирования ===
qr_mode_users = set()

# === ADMIN_ID из .env ===
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

# === Клавиатура внизу экрана ===
def get_bottom_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🔍 Проверить состав")],
            [KeyboardButton(text="📱 Сканировать QR"), KeyboardButton(text="📊 Статистика")],
            [KeyboardButton(text="📋 Список добавок"), KeyboardButton(text="🌱 Веганские")],
            [KeyboardButton(text="⚠️ Аллергены"), KeyboardButton(text="👶 Для детей")],
            [KeyboardButton(text="🔄 Обновить базу")]
        ],
        resize_keyboard=True,
        one_time_keyboard=False
    )

# === Определение страны по языковому коду ===
def get_country_by_language(language_code):
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

# === Главное меню (инлайн-кнопки) ===
def create_main_menu():
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(text="🔍 Проверить состав", callback_data="/start"),
        InlineKeyboardButton(text="📋 Список добавок", callback_data="/list_additives"),
        InlineKeyboardButton(text="🌱 Веганские добавки", callback_data="/vegan"),
        InlineKeyboardButton(text="⚠️ Аллергены", callback_data="/allergen"),
        InlineKeyboardButton(text="👶 Для детей", callback_data="/not_for_kids"),
        InlineKeyboardButton(text="📱 Сканировать QR", callback_data="/scan_qr"),
        InlineKeyboardButton(text="🔄 Обновить базу", callback_data="/update"),
        InlineKeyboardButton(text="📊 Статистика", callback_data="/stats")
    )
    builder.adjust(2)
    return builder.as_markup()

# === Роутеры для инлайн-кнопок ===
@router.callback_query(F.data == "/start")
async def handle_start_callback(callback: CallbackQuery):
    await send_welcome(callback.message)
    await callback.answer()

@router.callback_query(F.data == "/list_additives")
async def handle_list_callback(callback: CallbackQuery):
    await cmd_list_additives(callback.message)
    await callback.answer()

@router.callback_query(F.data == "/vegan")
async def handle_vegan_callback(callback: CallbackQuery):
    await cmd_vegan_additives(callback.message)
    await callback.answer()

@router.callback_query(F.data == "/allergen")
async def handle_allergen_callback(callback: CallbackQuery):
    await cmd_allergen_additives(callback.message)
    await callback.answer()

@router.callback_query(F.data == "/not_for_kids")
async def handle_not_for_kids_callback(callback: CallbackQuery):
    await cmd_not_for_kids_additives(callback.message)
    await callback.answer()

@router.callback_query(F.data == "/scan_qr")
async def handle_scan_qr_callback(callback: CallbackQuery):
    await cmd_scan_qr(callback.message)
    await callback.answer()

@router.callback_query(F.data == "/update")
async def handle_update_callback(callback: CallbackQuery):
    await cmd_update_additives(callback.message)
    await callback.answer()

@router.callback_query(F.data == "/stats")
async def handle_stats_callback(callback: CallbackQuery):
    await stats_command(callback.message)
    await callback.answer()

# === Команда /start ===
@router.message(Command("start", "help"))
async def send_welcome(message: Message):
    user_id = str(message.from_user.id)
    data = load_data()
    if user_id not in data["users"]:
        data["users"][user_id] = 0
        save_data(data)

    user_lang = message.from_user.language_code
    country = get_country_by_language(user_lang)

    keyboard = get_bottom_keyboard()
    await message.answer(
        f"Привет! Я помогу проверить состав продукта для <b>{country}</b>.\n"
        "Выберите, что вы хотите сделать:",
        parse_mode="HTML",
        reply_markup=keyboard
    )

# === Команда /list_additives ===
@router.message(Command("list_additives"))
async def cmd_list_additives(message: Message):
    user_lang = message.from_user.language_code
    country = get_country_by_language(user_lang)
    items = []

    for code, info in sorted(banned_additives.items()):
        if is_valid_food_additive(code):
            items.append({
                "code": code,
                "name": info["name_ru"],
                "description": info["description"],
                "banned_in": ", ".join(info.get("banned_in", ["нигде"])),
                "allowed_in": ", ".join(info.get("allowed_in", ["нигде"]))
            })

    if not items:
        await message.answer("⚠️ База данных пуста или содержит только непищевые добавки.", parse_mode="HTML")
        return

    result = "<b>📌 Список пищевых добавок:</b>\n\n"
    count = 0
    for item in items:
        line = (
            f"<b>{item['code']}</b> — {item['name']}\n"
            f"Описание: {item['description']}\n"
            f"🚫 Запрещён в: {item['banned_in']}\n"
            f"✅ Разрешён в: {item['allowed_in']}\n\n"
        )
        if len(result) + len(line) > 4096:
            await message.answer(result, parse_mode="HTML")
            result = line
        else:
            result += line
        count += 1

    if result.strip():
        await message.answer(result, parse_mode="HTML")

# === Команда /vegan ===
@router.message(Command("vegan"))
async def cmd_vegan_additives(message: Message):
    user_lang = message.from_user.language_code
    country = get_country_by_language(user_lang)
    items = []

    for code, info in banned_additives.items():
        if is_valid_food_additive(code):
            note = info.get("note", "").lower()
            if "не подходит для веганов" not in note:
                status = f"✅ Разрешён в {country}" if country not in info.get("banned_in", []) else f"🚫 Запрещён в {country}"
                items.append({
                    "code": code,
                    "name": info["name_ru"],
                    "description": info["description"],
                    "country_status": status
                })

    response = build_response(items, country=country)
    for msg in response:
        await message.answer(msg, parse_mode="HTML")

# === Команда /allergen ===
@router.message(Command("allergen"))
async def cmd_allergen_additives(message: Message):
    user_lang = message.from_user.language_code
    country = get_country_by_language(user_lang)
    items = []

    for code, info in banned_additives.items():
        if is_valid_food_additive(code):
            desc = info.get("description", "").lower()
            note = info.get("note", "").lower()
            if "аллерг" in desc or "аллерген" in note:
                status = f"✅ Разрешён в {country}" if country not in info.get("banned_in", []) else f"🚫 Запрещён в {country}"
                items.append({
                    "code": code,
                    "name": info["name_ru"],
                    "description": info["description"],
                    "country_status": status
                })

    response = build_response(items, country=country)
    for msg in response:
        await message.answer(msg, parse_mode="HTML")

# === Команда /not_for_kids ===
@router.message(Command("not_for_kids"))
async def cmd_not_for_kids_additives(message: Message):
    user_lang = message.from_user.language_code
    country = get_country_by_language(user_lang)
    items = []

    for code, info in banned_additives.items():
        if is_valid_food_additive(code):
            status_field = info.get("status", "").lower()
            description = info.get("description", "").lower()
            if "ограничен" in status_field or "дети" in description or "запрещён" in description:
                status = f"✅ Разрешён в {country}" if country not in info.get("banned_in", []) else f"🚫 Запрещён в {country}"
                items.append({
                    "code": code,
                    "name": info["name_ru"],
                    "description": info["description"],
                    "country_status": status
                })

    response = build_response(items, country=country)
    for msg in response:
        await message.answer(msg, parse_mode="HTML")

# === Команда /scan_qr ===
@router.message(Command("scan_qr"))
async def cmd_scan_qr(message: Message):
    qr_mode_users.add(message.from_user.id)
    await message.answer("📸 Пришлите фото QR-кода, и я его распознаю.")

# === Распознавание QR-кода ===
def extract_qr_code(image_path):
    try:
        image = cv2.imread(image_path)
        decoded_objects = decode(cv2.cvtColor(image, cv2.COLOR_BGR2GRAY))
        return decoded_objects[0].data.decode('utf-8') if decoded_objects else None
    except Exception as e:
        print(f"[Ошибка] Не удалось распознать QR-код: {e}")
        return None

# === Обработка фото (OCR + QR) ===
@router.message(F.photo)
async def handle_photo(message: Message):
    user_id = str(message.from_user.id)
    data = load_data()
    data["users"][user_id] = data["users"].get(user_id, 0) + 1
    data["total_messages"] += 1
    save_data(data)

    photo = message.photo[-1]
    file = await message.bot.get_file(photo.file_id)
    file_path = file.file_path
    file_name = f"photo_{message.from_user.id}.jpg"

    try:
        await message.bot.download_file(file_path, file_name)

        if user_id in qr_mode_users:
            qr_mode_users.remove(user_id)
            qr_result = extract_qr_code(file_name)
            if qr_result:
                dangerous = check_composition_for_country(qr_result, country=get_country_by_language(message.from_user.language_code))
                response = build_response(dangerous)
                for msg in response:
                    await message.answer(msg, parse_mode="HTML")
            else:
                await message.answer("❌ Не удалось распознать QR-код.")
        else:
            text = extract_text_from_image(file_name)
            if text.strip():
                dangerous = check_composition_for_country(text, country=get_country_by_language(message.from_user.language_code))
                response = build_response(dangerous)
                for msg in response:
                    await message.answer(msg, parse_mode="HTML")
            else:
                await message.answer("❌ Не удалось распознать текст на фото.")
    except Exception as e:
        await message.answer("⚠️ Произошла ошибка при обработке изображения.")
        print(e)
    finally:
        if os.path.exists(file_name):
            os.remove(file_name)

# === Проверка состава по тексту ===
def check_composition_for_country(text, country):
    found_dangerous = []
    text_upper = text.replace('ё', 'е').replace('Ё', 'Е').upper()
    for code, info in banned_additives.items():
        if code in text_upper and is_valid_food_additive(code):
            banned_countries = info.get("banned_in", [])
            allowed_countries = info.get("allowed_in", [])
            if country in banned_countries:
                status = f"🚫 Запрещён в {country}"
            elif country in allowed_countries:
                status = f"✅ Разрешён в {country}"
            else:
                status = f"ℹ️ Неизвестен статус в {country}"
            found_dangerous.append({
                'code': code,
                'name': info['name_ru'],
                'description': info['description'],
                'country_status': status
            })
    return found_dangerous

# === Проверка, является ли код пищевой добавкой ===
def is_valid_food_additive(code):
    if not code.startswith("E") or len(code) > 5:
        return False
    try:
        number = int(code[1:])
    except ValueError:
        return False
    ranges = [(100,199), (200,299), (300,399), (400,499), (500,599), (600,699), (900,999)]
    return any(start <= number <= end for start, end in ranges)

# === Обработчики для кнопок внизу экрана ===
@router.message(F.text == "🔍 Проверить состав")
async def handle_check_composition(message: Message):
    await send_welcome(message)

@router.message(F.text == "📱 Сканировать QR")
async def handle_scan_qr_button(message: Message):
    await cmd_scan_qr(message)

@router.message(F.text == "📊 Статистика")
async def handle_stats_button(message: Message):
    await stats_command(message)

@router.message(F.text == "📋 Список добавок")
async def handle_list_additives_button(message: Message):
    await cmd_list_additives(message)

@router.message(F.text == "🌱 Веганские")
async def handle_vegan_button(message: Message):
    await cmd_vegan_additives(message)

@router.message(F.text == "⚠️ Аллергены")
async def handle_allergen_button(message: Message):
    await cmd_allergen_additives(message)

@router.message(F.text == "👶 Для детей")
async def handle_not_for_kids_button(message: Message):
    await cmd_not_for_kids_additives(message)

@router.message(F.text == "🔄 Обновить базу")
async def handle_update_button(message: Message):
    await cmd_update_additives(message)

# === Команда /update (только для админа) ===
@router.message(Command("update"))
async def cmd_update_additives(message: Message):
    user_id = message.from_user.id
    if user_id != ADMIN_ID:
        await message.answer("🔒 Эта команда доступна только администратору.")
        return

    await message.answer("🔄 Начинаю обновление базы пищевых добавок...")

    try:
        new_additives = fetch_e_numbers()
        added_count = update_json_file(new_additives)

        if added_count > 0:
            await message.answer(f"✅ База успешно обновлена. Добавлено новых записей: **{added_count}**")
        else:
            await message.answer("ℹ️ Новых добавок не найдено или база уже актуальна.")
    except Exception as e:
        await message.answer(f"❌ Ошибка при обновлении: {e}")
        print(f"[Ошибка /update] {e}")

# === Команда /stats (только для админа) ===
@router.message(Command("stats"))
async def stats_command(message: Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("🔒 Эта команда доступна только администратору.")
        return
    data = load_data()
    total_users = len(data["users"])
    total_messages = data["total_messages"]
    avg_per_user = round(total_messages / total_users, 1) if total_users > 0 else 0
    await message.answer(
        f"📊 <b>Статистика бота</b>\n\n"
        f"👥 Пользователей: <b>{total_users}</b>\n"
        f"💬 Сообщений: <b>{total_messages}</b>\n"
        f"📬 В среднем: <b>{avg_per_user}</b>",
        parse_mode="HTML"
    )

# === Обработка любого текста (в конце!) ===
@router.message(F.text)
async def check_additives(message: Message):
    user_id = str(message.from_user.id)
    data = load_data()
    data["users"][user_id] = data["users"].get(user_id, 0) + 1
    data["total_messages"] += 1
    save_data(data)

    user_lang = message.from_user.language_code
    country = get_country_by_language(user_lang)

    dangerous = check_composition_for_country(message.text, country=country)
    response = build_response(dangerous, country=country)
    for msg in response:
        await message.answer(msg, parse_mode="HTML")