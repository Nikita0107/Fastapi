from tasks import extract_text
from fastapi import HTTPException, File, UploadFile, APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from database import AsyncSessionLocal, DocumentText, Document
from datetime import datetime, timezone
import shutil
import os
import uuid
from schemas import DocumentResponse, DocumentTextsResponse, DocumentTextResponse
from conf import DOCUMENTS_DIR

router = APIRouter()


# import tempfile
# DOCUMENTS_DIR = tempfile.mkdtemp()
# os.makedirs(DOCUMENTS_DIR, exist_ok=True)

# Зависимость для получения асинхронной сессии
async def get_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session

from fastapi import Request

@router.post('/upload_doc', tags=['Задачи'], response_model=DocumentResponse,
             summary='Загрузка документа',
             description='Загружает документ и сохраняет его в системе.')
async def document_upload(
    request: Request,  # Переместили этот параметр вперёд
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_session)
):
    # Генерируем уникальное имя файла
    unique_filename = f'{uuid.uuid4()}.{file.filename.split(".")[-1]}'

    # Путь к файлу
    file_path = os.path.join(DOCUMENTS_DIR, unique_filename)

    # Сохраняем файл на диск
    try:
        # Открываем файл для записи и сохраняем загруженный файл
        with open(file_path, 'wb') as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Ошибка при сохранении файла: {str(e)}')

    # Создаем запись в базе данных
    document = Document(name=unique_filename, date=datetime.now(timezone.utc))
    session.add(document)
    try:
        await session.commit()
        await session.refresh(document)
    except Exception as e:
        await session.rollback()
        # Удаляем файл в случае ошибки записи в базу данных
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f'Ошибка при сохранении документа в базе данных: {str(e)}')

    # Формируем URL для доступа к файлу
    file_url = f"{request.base_url}documents/{unique_filename}"

    return DocumentResponse(
        id=document.id,
        name=document.name,
        date=document.date,
        url=file_url  # Возвращаем URL файла
    )

@router.delete('/doc_delete/{doc_id}',
               tags=['Задачи'],
               summary='Удаление документа',
               description='Удаляет документ и все связанные данные по ID документа.')
async def delete_doc(doc_id: int, session: AsyncSession = Depends(get_session)):
    try:
        # Находим документ по ID
        result = await session.execute(
            select(Document).where(Document.id == doc_id)
        )
        document = result.scalar_one_or_none()
        if not document:
            raise HTTPException(status_code=404, detail='Документ не найден')

        # Удаляем файл с диска
        file_path = os.path.join(DOCUMENTS_DIR, document.name)
        if os.path.exists(file_path):
            os.remove(file_path)

        # Удаляем связанные записи из таблицы DocumentText
        await session.execute(delete(DocumentText).where(DocumentText.document_id == doc_id))

        # Удаляем запись из таблицы Document
        await session.delete(document)
        await session.commit()
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=str(e))

    return {"Сообщение": "Документ удален"}

@router.put('/doc_analyse/{doc_id}', tags=['Задачи'], summary='Анализ документа',
            description='Запустить анализ извлечения текста в указанном документе.')
async def analyze_doc(doc_id: int, session: AsyncSession = Depends(get_session)):
    # Проверяем наличие документа
    result = await session.execute(
        select(Document).where(Document.id == doc_id)
    )
    document = result.scalar_one_or_none()
    if not document:
        raise HTTPException(status_code=404, detail='Документ не найден')

    file_path = os.path.join(DOCUMENTS_DIR, document.name)

    # Запускаем задачу Celery по извлечению текста
    extract_text.delay(doc_id, file_path)

    return {'message': 'Анализ начат'}

@router.get('/get_text/{doc_id}',
            tags=['Задачи'],
            response_model=DocumentTextsResponse,
            summary='Получение текста документа',
            description='Получает извлеченный текст для указанного документа по ID.')
async def get_text(doc_id: int, session: AsyncSession = Depends(get_session)):
    result = await session.execute(
        select(DocumentText).where(DocumentText.document_id == doc_id)
    )
    texts = result.scalars().all()

    if not texts:
        raise HTTPException(status_code=404, detail='Текст для этого документа не найден')

    return DocumentTextsResponse(
        document_id=doc_id,
        texts=[
            DocumentTextResponse(
                id=text.id,
                document_id=text.document_id,
                text=text.text
            ) for text in texts
        ]
    )