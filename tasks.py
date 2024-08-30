from celery import Celery
from asgiref.sync import sync_to_async
import pytesseract
from PIL import Image
from database import new_session, DocumentText

celery = Celery('tasks', broker='redis://redis:6379/0')

@celery.task
def extract_text_from_image(doc_id, file_path):
    # Загрузка изображения
    image = Image.open(file_path)

    # Извлечение текста из изображения
    text = pytesseract.image_to_string(image, lang='rus')

    # Сохранение извлеченного текста в базе данных
    # Оборачиваем асинхронный код в синхронный
    sync_to_async(save_to_db)(doc_id, text)

def save_to_db(doc_id, text):
    # Используем синхронный контекстный менеджер
    with new_session() as session:
        document_text = DocumentText(document_id=doc_id, text=text)
        session.add(document_text)
        session.commit()