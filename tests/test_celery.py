from sqlalchemy import text
from tasks import extract_text
from database import Document, new_session

async def test_extract_text(test_db):
    file_path = '/home/nikita/PycharmProjects/Fastapi/tests/qwe.jpeg'

    async with new_session() as session:
        # Создаем тестовый документ
        test_document = Document(name='test_document.txt')
        session.add(test_document)
        await session.commit()  # Сохраняем документ и фиксируем изменения
        doc_id = test_document.id  # Получаем ID созданного документа

    # Запускаем функцию извлечения текста
    await extract_text(doc_id, file_path)

    # Проверяем, что текст был сохранен в базе данных
    async with new_session() as session:  # Используем новую сессию для чтения данных
        result = await session.execute(
            text("SELECT text FROM documents_text WHERE document_id = :doc_id"), {"doc_id": doc_id}
        )
        document_text = result.fetchone()

    # Проверяем, что текст извлечен правильно
    assert document_text is not None, 'Текст для документа не найден».'
