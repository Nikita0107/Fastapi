# Начинаем с базового образа Python
FROM python:3.10-slim

# Обновляем пакеты и устанавливаем tesseract-ocr и языковые данные
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-rus \
    libtesseract-dev \
    libleptonica-dev \
    pkg-config \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы зависимостей
COPY requirements.txt .

# Устанавливаем зависимости Python
RUN pip install --no-cache-dir -r requirements.txt

# Копируем остальной код приложения
COPY . /app

# Открываем порт для FastAPI
EXPOSE 8000

# Устанавливаем команду по умолчанию (для FastAPI)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]