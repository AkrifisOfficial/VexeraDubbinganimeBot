FROM python:3.10-slim

# Установка зависимостей
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Рабочая директория
WORKDIR /app

# Копирование зависимостей
COPY requirements.txt .

# Установка Python зависимостей
RUN pip install --no-cache-dir -r requirements.txt

# Копирование исходного кода
COPY . .

# Команда запуска
CMD ["sh", "-c", "python -m bot.main & uvicorn admin_panel.main:app --host 0.0.0.0 --port 8000"]
