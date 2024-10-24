from celery import Celery
import pytesseract
from PIL import Image
from database import new_session, DocumentText
import asyncio

# Изменяем адрес брокера на RabbitMQ
# celery = Celery('tasks', broker='amqp://rabbitmq:5672//')
celery = Celery('tasks', broker='amqp://guest:guest@localhost:5672//')

@celery.task
# def extract_text(doc_id, file_path):
async def extract_text(doc_id, file_path):
    # Загрузка изображения
    image = Image.open(file_path)
    # Извлечение текста из изображения
    text = pytesseract.image_to_string(image, lang='rus')

    # Сохранение извлеченного текста в базе данных
    # asyncio.run(save_text_to_db(doc_id, text))
    await save_text_to_db(doc_id, text)  # Изменение здесь

async def save_text_to_db(doc_id, text):
    async with new_session() as session:
        document_text = DocumentText(document_id=doc_id, text=text)
        session.add(document_text)
        await session.commit()
