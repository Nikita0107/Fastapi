# Используем официальный образ Python в качестве базового образа
FROM python:3.10-slim

# Устанавливаем переменные окружения
ENV PYTHONUNBUFFERED=1 \
    APP_USER=appuser \
    APP_HOME=/app \
    DOCUMENTS_DIR=/app/documents

# Создаем пользователя
RUN useradd --create-home $APP_USER

# Устанавливаем рабочую директорию
WORKDIR $APP_HOME

# Обновляем пакеты и устанавливаем зависимости
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-rus \
    libtesseract-dev && \
    rm -rf /var/lib/apt/lists/*

# Копируем файл зависимостей в контейнер
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем все файлы проекта в контейнер
COPY . .

# Создаем директорию для документов и устанавливаем права доступа
RUN mkdir -p $DOCUMENTS_DIR && \
    chown -R $APP_USER:$APP_USER $APP_HOME

# Переключаемся на созданного пользователя
USER $APP_USER

# Открываем порт, по которому будет доступно приложение
EXPOSE 8000

# Команда для запуска приложения
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]