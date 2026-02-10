"""Тесты для работы с базой данных."""

import tempfile
import logging
from pathlib import Path

import pytest

from shortlink.database import Database

# Настройка логирования для тестов
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@pytest.fixture
def temp_db() -> Database:
    """Создание временной базы данных для тестов."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp_file:
        db_path = tmp_file.name
    
    logger.info(f"Создаем временную БД: {db_path}")
    db = Database(db_path)
    db.initialize()
    logger.info("Временная БД инициализирована")
    yield db
    # База данных закрывается автоматически через context manager
    Path(db_path).unlink(missing_ok=True)
    logger.info(f"Временная БД удалена: {db_path}")


def test_add_and_get_link(temp_db: Database) -> None:
    """Проверка добавления и получения ссылки."""
    logger.info("=== Начало теста: test_add_and_get_link ===")
    test_url = "https://aliexpress.ru/item/1005009397184440.html?spm=a2g2w.home.10009201.8.41f35586uMoB4X&mixer_rcmd_bucket_id=controlRu2&ru_algo_pv_id=608c1d-781e02-1d1b0e-9725ba-1770721200&scenario=aerPromoSegments&shpMethod=CAINIAO_FULFILLMENT_STD&sku_id=12000048977206524&traffic_source=recommendation&type_rcmd=core"
    short_code = "test123"
    
    logger.info(f"Добавляем ссылку в БД: {short_code} -> {test_url[:50]}...")
    temp_db.add_link(short_code, test_url)
    logger.info("Ссылка добавлена успешно")
    
    logger.info(f"Получаем ссылку из БД по коду: {short_code}")
    result = temp_db.get_link_by_short_code(short_code)
    assert result is not None
    logger.info(f"Ссылка найдена: {result['original_url'][:50]}...")
    assert result["original_url"] == test_url
    logger.info("✓ Тест пройден: ссылка успешно добавлена и получена")


def test_get_by_original_url(temp_db: Database) -> None:
    """Проверка поиска по оригинальному URL."""
    logger.info("=== Начало теста: test_get_by_original_url ===")
    test_url = "https://aliexpress.ru/item/1005009397184440.html?spm=a2g2w.home.10009201.8.41f35586uMoB4X&mixer_rcmd_bucket_id=controlRu2&ru_algo_pv_id=608c1d-781e02-1d1b0e-9725ba-1770721200&scenario=aerPromoSegments&shpMethod=CAINIAO_FULFILLMENT_STD&sku_id=12000048977206524&traffic_source=recommendation&type_rcmd=core"
    short_code = "ali123"
    
    logger.info(f"Добавляем ссылку в БД: {short_code} -> {test_url[:50]}...")
    temp_db.add_link(short_code, test_url)
    logger.info("Ссылка добавлена успешно")
    
    logger.info(f"Ищем ссылку по оригинальному URL: {test_url[:50]}...")
    result = temp_db.get_link_by_original_url(test_url)
    assert result is not None
    logger.info(f"Ссылка найдена с кодом: {result['short_code']}")
    assert result["short_code"] == short_code
    logger.info("✓ Тест пройден: поиск по оригинальному URL работает")
