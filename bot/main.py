import os
import sys

# Проверка существования критических файлов
required_files = [
    'bot/keyboards.py',
    'admin_panel/static'
]

for file in required_files:
    if not os.path.exists(file):
        print(f"CRITICAL ERROR: Missing file/directory - {file}")
        sys.exit(1)
import os
import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from bot.handlers import register_handlers
from bot.database import Database

# Настройка логгирования
logging.basicConfig(level=logging.INFO)

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
