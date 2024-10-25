import os
from unittest.mock import patch
from httpx import AsyncClient, ASGITransport
from main import app
from database import new_session, Document
from router import DOCUMENTS_DIR

async def test_analyze_doc(test_db):
    async with new_session() as session:
        # Создаем тестовый документ
        test_document = Document(name='test_document.txt')
        session.add(test_document)
        await session.commit()
        doc_id = test_document.id

    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as client:
        with patch('tasks.extract_text.delay') as mock_extract_text:
            # Выполняем PUT запрос на анализ документа
            response = await client.put(f'/doc_analyse/{doc_id}')

            # Проверяем ответ
            assert response.status_code == 200
            assert response.json() == {'message': 'Анализ начат'}
            mock_extract_text.assert_called_once_with(doc_id, os.path.join(DOCUMENTS_DIR, test_document.name))

    async with new_session() as session:
        # Проверяем, что документ существует в базе данных
        document = await session.get(Document, doc_id)
        assert document is not None