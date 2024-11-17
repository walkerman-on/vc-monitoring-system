import json
from pathlib import Path

SHARED_DATA_PATH = Path("/app/shared_data/latest_values.json")

def save_latest_values(data: dict):
    """Сохраняет последние значения в общий файл"""
    with SHARED_DATA_PATH.open('w') as file:
        json.dump(data, file)

def load_latest_values() -> dict:
    """Загружает последние значения из общего файла"""
    if not SHARED_DATA_PATH.exists():
        return {}
    with SHARED_DATA_PATH.open('r') as file:
        return json.load(file)
