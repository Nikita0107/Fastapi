from httpx import AsyncClient, ASGITransport
from main import app
from database import Document, DocumentText, new_session

async def test_doc_delete(test_db):
    async with new_session() as session:
        # Создаем тестовый документ
        test_document = Document(name='test_document.txt')
        session.add(test_document)
        await session.flush()
        doc_id = test_document.id

        # Создаем связанный текст
        test_document_text = DocumentText(text='Тестовый текст', document_id=doc_id)
        session.add(test_document_text)
        await session.commit()

    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as client:
        # Выполняем запрос на удаление
        response = await client.delete(f'/doc_delete/{doc_id}')

    assert response.status_code == 200
    assert response.json() == {"Сообщение": "документ удален"}

    # Проверяем что документ удалён
    async with new_session() as session:
        deleted_document = await session.get(Document, doc_id)
        assert deleted_document is None  #
