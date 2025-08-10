import os
import logging
from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from bot.database import Database
from bot.handlers import register_handlers

# Настройка логгирования
logging.basicConfig(level=logging.INFO)

# Проверка обязательных файлов
if not os.path.exists("bot/keyboards.py"):
    logging.critical("Файл bot/keyboards.py не найден!")
    exit(1)

# Инициализация бота
bot = Bot(token=os.getenv("BOT_TOKEN"))
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Инициализация базы данных
db = Database()

async def on_startup(dp):
    logging.info("Бот запущен")
    register_handlers(dp, db)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
