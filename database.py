from datetime import datetime
from sqlalchemy import Integer, String, TIMESTAMP, ForeignKey, create_engine
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import (
    sessionmaker,
    Mapped,
    mapped_column,
    declarative_base,
    relationship,
)
from sqlalchemy.sql import func


# Асинхронный движок и сессия для FastAPI
ASYNC_DATABASE_URL = 'postgresql+asyncpg://postgres:220689@db:5432/mydb'
# ASYNC_DATABASE_URL = 'postgresql+asyncpg://postgres:220689@localhost/test_db'
async_engine = create_async_engine(ASYNC_DATABASE_URL)
AsyncSessionLocal = async_sessionmaker(async_engine, expire_on_commit=False)

# Синхронный движок и сессия для Celery
SYNC_DATABASE_URL = 'postgresql://postgres:220689@db:5432/mydb'
sync_engine = create_engine(SYNC_DATABASE_URL)
SyncSessionLocal = sessionmaker(bind=sync_engine)

Base = declarative_base()

class Document(Base):
    __tablename__ = 'documents'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(64), unique=True)
    date: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), index=True, server_default=func.now()
    )

    document_texts: Mapped['DocumentText'] = relationship(
        'DocumentText', back_populates='document', cascade='all, delete-orphan'
    )

class DocumentText(Base):
    __tablename__ = 'documents_text'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    document_id: Mapped[int] = mapped_column(Integer, ForeignKey('documents.id'))
    text: Mapped[str] = mapped_column(String(1000))

    document: Mapped[Document] = relationship('Document', back_populates='document_texts')


async def create_tables():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def delete_tables():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)