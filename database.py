from datetime import datetime
from sqlalchemy import Integer, String, TIMESTAMP, ForeignKey
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import Mapped, mapped_column, declarative_base, relationship
from sqlalchemy.sql import func

# 'postgresql+asyncpg://postgres:220689@db:5432/mydb'
# postgresql+asyncpg://postgres:220689@localhost/test_db)
engine = create_async_engine('postgresql+asyncpg://postgres:220689@localhost/test_db')
new_session = async_sessionmaker(engine, expire_on_commit=False)
Base = declarative_base()

class Document(Base):
    __tablename__ = 'documents'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(64), unique=True)
    date: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), index=True, server_default=func.now())

    document_texts: Mapped['DocumentText'] = relationship('DocumentText', back_populates='document')

class DocumentText(Base):
    __tablename__ = 'documents_text'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    document_id: Mapped[int] = mapped_column(Integer, ForeignKey('documents.id'))
    text: Mapped[str] = mapped_column(String(1000))

    document: Mapped[Document] = relationship('Document', back_populates='document_texts')


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def delete_tables():
   async with engine.begin() as conn:
       await conn.run_sync(Base.metadata.drop_all)