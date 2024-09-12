# Используем официальный образ Python в качестве базового образа
FROM python:3.10-slim

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Копируем файл зависимостей в контейнер
COPY requirements.txt .

# Устанавливаем зависимости

RUN pip install --no-cache-dir -r requirements.txt

RUN apt-get update && apt-get install -y tesseract-ocr-rus

# Копируем все файлы проекта в контейнер
COPY . .

RUN mkdir -p /app/documents

# Открываем порт, по которому будет доступно приложение
EXPOSE 8000

# Команда для запуска приложения
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
