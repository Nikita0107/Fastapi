import os

# Каталог для хранения загруженных документов
DOCUMENTS_DIR = '/app/documents'

# Создаём директорию, если её нет
os.makedirs(DOCUMENTS_DIR, exist_ok=True)