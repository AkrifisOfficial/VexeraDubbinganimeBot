FROM python:3.10-slim

# Создаем необходимые директории
RUN mkdir -p admin_panel/static

# Установка зависимостей
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Проверка структуры (для отладки)
RUN ls -laR /app

CMD ["sh", "-c", "python -m bot.main & uvicorn admin_panel.main:app --host 0.0.0.0 --port 8000"]
