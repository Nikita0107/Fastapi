from fastapi import FastAPI
from contextlib import asynccontextmanager
from database import create_tables, delete_tables
from router import router as router_doc
from conf import DOCUMENTS_DIR
from fastapi.staticfiles import StaticFiles

# Декоратор для управления жизненным циклом приложения
@asynccontextmanager
async def lifespan(_: FastAPI):
    # Создание таблиц при запуске приложения
    await create_tables()
    print('Таблицы созданы')
    yield
    # Удаление таблиц при остановке приложения
    await delete_tables()
    print('Таблицы удалены')


app = FastAPI(
    title="Nika",
    description=(
        "API сохраняет изображение в базу данных и на локальный сервер. "
        "Извлекает текст с изображения в базе данных. Удаляет запись по ID из базы данных и изображение с сервера!"
    ),
    version="1.0.0",
    lifespan=lifespan
)

# Монтируем директорию с документами на URL /documents
app.mount("/documents", StaticFiles(directory=DOCUMENTS_DIR), name="documents")

# Добавляем роутеры из модуля router
app.include_router(router_doc)