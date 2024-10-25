from datetime import timezone
from dateutil import parser
from httpx import AsyncClient, ASGITransport
from sqlalchemy import select
from database import Document
from main import app


async def test_upload_doc(test_db):
    async with (AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as client):
        image_path = '/home/nikita/PycharmProjects/Fastapi/tests/qwe.jpeg'
        with open(image_path, 'rb') as image_file:
            response = await client.post(
                '/upload_doc',
                files={'file': ('qwe.jpeg', image_file, 'image/jpeg')})

        assert response.status_code == 200
        response_data = response.json()
        assert response_data['id'] == 1
        assert response_data["name"] is not None, "Имя файла не должно быть None"
        assert response_data["date"] == response.json()["date"]
        assert response_data["name"].endswith('.jpeg'), "Имя файла должно заканчиваться на .jpeg"

 # Проверка, что запись сохранена
    async with test_db.begin():
        result = await test_db.execute(select(Document).where(Document.id == response_data["id"]))
        document = result.scalar_one_or_none()
        assert document is not None, f"Документ с ID {response_data['id']} не найден в базе данных"
        assert document.name == response_data["name"], "Имена файлов не совпадают"
        # преобразуем в datetime
        response_date = parser.isoparse(response_data["date"])
        assert document.date.replace(tzinfo=timezone.utc) == response_date, "Даты не совпадают"
