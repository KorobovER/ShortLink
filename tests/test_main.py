"""Тесты для FastAPI приложения."""

import tempfile
import logging
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from shortlink.database import Database

# Настройка логирования для тестов
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@pytest.fixture
def test_db() -> Database:
    """Создание временной базы данных для тестов."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp_file:
        db_path = tmp_file.name
    
    db = Database(db_path)
    db.initialize()
    
    print(f"Test database path: {db_path}")
    
    yield db
    
    Path(db_path).unlink(missing_ok=True)


@pytest.fixture
def app(test_db: Database):
    """Создание приложения с тестовой базой данных."""
    from shortlink.main import app, db
    
    # Заменяем глобальную базу данных на тестовую
    original_db = db
    import shortlink.main
    shortlink.main.db = test_db
    
    yield app
    
    # Возвращаем оригинальную базу данных
    shortlink.main.db = original_db


@pytest.fixture
def client(app) -> TestClient:
    """Создание тестового клиента."""
    return TestClient(app)


def test_root_endpoint(client: TestClient) -> None:
    """Проверка корневого эндпоинта."""
    logger.info("=== Начало теста: test_root_endpoint ===")
    response = client.get("/")
    logger.info(f"Статус ответа: {response.status_code}")
    assert response.status_code == 200
    assert response.json()["message"] == "ShortLink API is running"
    logger.info("✓ Тест пройден: корневой эндпоинт работает")


def test_shorten_url(client: TestClient) -> None:
    """Проверка создания короткой ссылки."""
    logger.info("=== Начало теста: test_shorten_url ===")
    test_url = "https://aliexpress.ru/item/1005006812133213.html?spm=a2g2w.home.10009201.10.41f35586uMoB4X&mixer_rcmd_bucket_id=controlRu2&ru_algo_pv_id=608c1d-781e02-1d1b0e-9725ba-1770721200&scenario=aerPromoSegments&shpMethod=CAINIAO_PREMIUM&sku_id=12000038386582736&traffic_source=recommendation&type_rcmd=core"
    logger.info(f"Отправляем запрос на сокращение URL: {test_url[:50]}...")
    response = client.post("/shorten", json={"url": test_url})
    
    logger.info(f"Статус ответа: {response.status_code}")
    assert response.status_code == 200
    data = response.json()
    logger.info(f"Полученная короткая ссылка: {data['short_url']}")
    assert data["original_url"] == test_url
    assert "localhost:8000" in data["short_url"]
    logger.info("✓ Тест пройден: короткая ссылка создана успешно")


def test_same_url_same_code(client: TestClient) -> None:
    """Проверка что одинаковый URL дает одинаковый код."""
    logger.info("=== Начало теста: test_same_url_same_code ===")
    test_url = "https://aliexpress.ru/item/1005006812133213.html?spm=a2g2w.home.10009201.10.41f35586uMoB4X&mixer_rcmd_bucket_id=controlRu2&ru_algo_pv_id=608c1d-781e02-1d1b0e-9725ba-1770721200&scenario=aerPromoSegments&shpMethod=CAINIAO_PREMIUM&sku_id=12000038386582736&traffic_source=recommendation&type_rcmd=core"
    
    logger.info("Первый запрос на сокращение...")
    response1 = client.post("/shorten", json={"url": test_url})
    short_url1 = response1.json()["short_url"]
    logger.info(f"Первая короткая ссылка: {short_url1}")
    
    logger.info("Второй запрос на сокращение (тот же URL)...")
    response2 = client.post("/shorten", json={"url": test_url})
    short_url2 = response2.json()["short_url"]
    logger.info(f"Вторая короткая ссылка: {short_url2}")
    
    assert short_url1 == short_url2
    logger.info("✓ Тест пройден: одинаковый URL дает одинаковый код")
