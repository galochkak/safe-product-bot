# bot/main.py

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from bot.handlers import router  # ✅ Абсолютный импорт
import os
from dotenv import load_dotenv
import asyncio

# Загружаем переменные окружения
load_dotenv()

# Получаем токен
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("❌ Ошибка: BOT_TOKEN не найден в .env файле. Проверьте файл .env")

# Создаём бота и диспетчер
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
dp.include_router(router)

async def main():
    print("🚀 БезопасныйПродукт — бот запущен и готов к работе!")
    try:
        await dp.start_polling(bot)
    except Exception as e:
        print(f"❌ Ошибка при запуске бота: {e}")

if __name__ == "__main__":
    asyncio.run(main())