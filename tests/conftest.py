import pytest
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from database import Base
import asyncio
DATABASE_URL = 'postgresql+asyncpg://postgres:220689@localhost/test_db'

# Создаем асинхронный движок
engine = create_async_engine(DATABASE_URL, echo=False)
# Создаем асинхронную фабрику сессий
async_session_maker = async_sessionmaker(bind=engine, expire_on_commit=False)

@pytest.fixture(scope='function', autouse=True)
async def setup_database():
    # Создаём таблицы перед тестами
    async with engine.begin() as conn:
        try:
            await conn.run_sync(Base.metadata.create_all)
        except SQLAlchemyError as e:
            print(f"Error creating tables: {e}")
            raise

    yield

    # После всех тестов удаляем таблицы и закрываем движок
    async with engine.begin() as conn:
        try:
            await conn.run_sync(Base.metadata.drop_all)
        except SQLAlchemyError as e:
            print(f"Error deleting tables: {e}")
            raise

    await engine.dispose()

@pytest.fixture
async def test_db():
    # Предоставляем сессию в тест
    async with async_session_maker() as session:
        yield session  # Возвращаем сессию в тест


@pytest.fixture(scope='session')
def event_loop():
    # Создание нового цикла событий для тестов
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

# RuntimeError##
###!!!!!!!! Таким образом, использование @pytest.fixture без указания области видимости
# позволяет создавать фикстуры, которые автоматически настраиваются и очищаются для каждого теста.
# coverage report -m проверка на покрытие тестами 85 %