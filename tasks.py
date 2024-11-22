from celery import Celery
import pytesseract
from PIL import Image
from database import SyncSessionLocal, DocumentText

# Настройка брокера на RabbitMQ
celery = Celery('tasks', broker='amqp://guest:guest@rabbitmq:5672//')

@celery.task
def extract_text(doc_id, file_path):
    # Загрузка изображения и извлечение текста
    with Image.open(file_path) as image:
        text = pytesseract.image_to_string(image, lang='rus')

    # Сохранение текста в базе данных
    save_text_to_db(doc_id, text)

def save_text_to_db(doc_id, text):
    # Создаем синхронную сессию
    session = SyncSessionLocal()
    try:
        # Создаем новый объект DocumentText
        document_text = DocumentText(document_id=doc_id, text=text)
        session.add(document_text)
        session.commit()
    except Exception as e:
        session.rollback()
        print(f"Ошибка при сохранении данных в базу: {e}")
        raise
    finally:
        session.close()