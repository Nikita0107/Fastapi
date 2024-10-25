import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from database import Document, DocumentText


async def check_tables_exist(session: AsyncSession, models):
    # Проверяет, что таблицы созданы в базе данных
    for model in models:
        # Выполняем простой запрос к таблице
        try:
            await session.execute(select(model).limit(1))
        except SQLAlchemyError as e:
            pytest.fail(f"Таблица для модели {model.__tablename__} не существует: {e}")


async def test_tables_exist(test_db: AsyncSession):
    # Проверяем, что таблицы созданы
    await check_tables_exist(test_db, [Document, DocumentText])

    await test_db.commit()