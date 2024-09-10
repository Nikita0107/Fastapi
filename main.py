from fastapi import FastAPI
from contextlib import asynccontextmanager
from database import create_tables, delete_tables
from router import router as router_doc

# Декоратор для управления жизненным циклом приложения
@asynccontextmanager
async def lifespan(_: FastAPI):  # Используем _ для неиспользуемого параметра
    await create_tables()
    print('Таблицы созданы')
    yield  # Здесь происходит выход из контекста
    await delete_tables()
    print('Таблицы удалены')

app = FastAPI(
    title="Nika",
    description="API сохраняет изображение в базу данных и на локальный сервер. Извлекает текст с изображения в базе данных. Удаляет запись по ID из базы данных и изображение с сервера!",
    version="1.0.0",
    lifespan=lifespan  # Используем lifespan с параметром
)

# Добавляем роутер
app.include_router(router_doc)