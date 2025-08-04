# bot/handlers.py
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, PhotoSize, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.formatting import as_list, Bold
from bot.utils import load_data, save_data, build_response, fetch_e_numbers, update_json_file
from bot.database import banned_additives
from utils.ocr import extract_text_from_image
import os
from dotenv import load_dotenv

load_dotenv()

router = Router()

# === Функция определения страны ===
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

# === Команда /start ===
@router.message(Command("start"))
async def send_welcome(message: Message):
    user_id = str(message.from_user.id)
    data = load_data()
    if user_id not in data["users"]:
        data["users"][user_id] = 0
        save_data(data)

    await message.answer(
        "Привет! Я помогу проверить состав продукта.\n"
        "Напиши, например: <code>E102</code>\n\n"
        "💬 Бот поддерживается <a href='https://example.com'>Натуральными продуктами 24</a> — "
        "доставка экопродуктов по России.",
        parse_mode="HTML",
        disable_web_page_preview=False
    )

# === Проверка E-добавки ===
@router.message(F.text)
async def check_additives(message: Message):
    text = message.text.strip().upper()
    data = load_data()
    data["total_messages"] += 1
    save_data(data)

    if not text.startswith("E") or not text[1:].isdigit():
        return

    code = text
    if code in banned_additives:
        info = banned_additives[code]
        user_lang = message.from_user.language_code
        country = get_country_by_language(user_lang)

        status = f"✅ Разрешён в {country}" if country not in info.get("banned_in", []) else f"🚫 Запрещён в {country}"

        response = as_list(
            Bold(f"{code} — {info['name_ru']}"),
            f"Статус: {status}",
            f"Описание: {info['description']}"
        )
        await message.answer(**response.as_kwargs())
    else:
        await message.answer("❌ Добавка не найдена в базе.")