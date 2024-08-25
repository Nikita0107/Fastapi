# Используем официальный образ Python как основу
FROM python:3.9-slim-buster

# Устанавливаем необходимые зависимости
RUN pip install --upgrade pip

# Создаем рабочую директорию в контейнере
WORKDIR /app

# Копируем файлы проекта в контейнер
COPY . /app

# Устанавливаем зависимости проекта
RUN pip install -r requirements.txt

# Открываем порт 80 для внешнего доступа
EXPOSE 80

# Запускаем FastAPI на порте 80
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]