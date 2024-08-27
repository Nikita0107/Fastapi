from celery import Celery
import pytesseract
from PIL import Image
from database import new_session, DocumentText
import asyncio

# Замените localhost на имя сервиса Redis в Docker
celery = Celery('tasks', broker='redis://redis:6379/0')

@celery.task
def extract_text_from_image(doc_id, file_path):
    # Запускаем асинхронную функцию в цикле событий
    asyncio.run(extract_text(doc_id, file_path))

async def extract_text(doc_id, file_path):
    # Загрузка изображения
    image = Image.open(file_path)

    # Извлечение текста из изображения
    text = pytesseract.image_to_string(image, lang='rus')

    # Сохранение извлеченного текста в базе данных
    async with new_session() as session:
        document_text = DocumentText(document_id=doc_id, text=text)
        session.add(document_text)
        await session.commit()