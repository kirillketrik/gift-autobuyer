FROM python:3.12-slim

WORKDIR /app

# Копируем только необходимые файлы для установки зависимостей
COPY pyproject.toml poetry.lock ./

# Установка poetry и зависимостей
RUN pip install --upgrade pip \
    && pip install poetry \
    && poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-root

# Копируем только нужные части проекта
COPY main.py ./main.py
COPY app/ ./app/

# Переменные окружения
ENV PYTHONUNBUFFERED=1
ENV LOGURU_LEVEL=INFO

# Запуск бота
CMD ["python", "main.py"]
