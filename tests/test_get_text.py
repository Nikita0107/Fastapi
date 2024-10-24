import pytest
from httpx import AsyncClient, ASGITransport
import sqlalchemy as sa
from main import app
from database import new_session, Document, DocumentText

# Путь к изображению
image_path = '/home/nikita/PycharmProjects/Fastapi/tests/qwe.jpeg'


@pytest.mark.asyncio
async def test_get_text(test_db):
    async with new_session() as session:
        # Создаем тестовый документ
        test_document = Document(name='test_document.txt')
        session.add(test_document)
        await session.commit()
        doc_id = test_document.id

        # Создаем тестовый текст для документа
        test_text = DocumentText(document_id=doc_id, text='Пример текста извлеченного из изображения.')
        session.add(test_text)
        await session.commit()

    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as client:
        # Выполняем GET запрос для получения текста документа
        response = await client.get(f'/get_text/{doc_id}')

        # Проверяем ответ
        assert response.status_code == 200
        data = response.json()
        assert data['document_id'] == doc_id
        assert len(data['texts']) == 1
        assert data['texts'][0]['text'] == 'Пример текста извлеченного из изображения.'

    # Удаление тестового документа и текста после теста (опционально)
    async with new_session() as session:
        await session.execute(sa.delete(DocumentText).where(DocumentText.document_id == doc_id))
        await session.commit()
        await session.delete(test_document)
        await session.commit()