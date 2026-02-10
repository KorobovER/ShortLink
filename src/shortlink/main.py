"""Main FastAPI application."""

import hashlib
import logging
from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel, HttpUrl

from shortlink.database import db

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def base62_encode(num: int) -> str:
    """Encode integer to base62 string."""
    chars = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    if num == 0:
        return chars[0]
    
    result = []
    base = len(chars)
    while num > 0:
        result.append(chars[num % base])
        num //= base
    
    return "".join(reversed(result))


class URLRequest(BaseModel):
    """Request model for URL shortening."""
    url: HttpUrl


class URLResponse(BaseModel):
    """Response model for shortened URL."""
    short_url: str
    original_url: str


app = FastAPI(
    title="ShortLink API",
    description="A simple URL shortening service",
    version="0.1.0",
)


def generate_short_code(url: str, length: int = 6) -> str:
    """Генерирует короткий код с помощью хеширования URL."""
    hash_obj = hashlib.sha256(url.encode())
    # Берем первые 6 байт хеша, преобразуем в число и кодируем в base62
    hash_bytes = hash_obj.digest()[:length]
    num = int.from_bytes(hash_bytes, byteorder='big')
    return base62_encode(num)[:length]


@app.post("/shorten", response_model=URLResponse)
async def shorten_url(request: URLRequest) -> URLResponse:
    """Создать короткую URL из длинного."""
    original_url = str(request.url)
    logger.info(f"Получен запрос на сокращение URL: {original_url}")
    
    # Генерируем детерминированный короткий код из URL
    short_code = generate_short_code(original_url)
    logger.debug(f"Сгенерирован короткий код: {short_code}")
    
    # Проверяем, существует ли URL уже
    existing = db.get_link_by_original_url(original_url)
    if not existing:
        logger.info(f"URL не найден в БД, добавляем новую ссылку")
        # Обрабатываем потенциальную коллизию хеша
        collision = db.get_link_by_short_code(short_code)
        if collision:
            logger.warning(f"Обнаружена коллизия для кода {short_code}, добавляем суффикс")
            # Добавляем суффикс для разрешения коллизии
            suffix = 1
            while True:
                new_code = f"{short_code}{suffix}"
                if not db.get_link_by_short_code(new_code):
                    short_code = new_code
                    logger.info(f"Коллизия разрешена, новый код: {short_code}")
                    break
                suffix += 1
        
        db.add_link(short_code, original_url)
        logger.info(f"Ссылка успешно добавлена в БД: {short_code} -> {original_url}")
    else:
        short_code = existing["short_code"]
        logger.info(f"URL уже существует в БД с кодом: {short_code}")
    
    short_url = f"http://localhost:8000/{short_code}"
    logger.info(f"Возвращаем короткую ссылку: {short_url}")
    
    return URLResponse(
        short_url=short_url,
        original_url=original_url
    )


@app.get("/{short_code}")
async def redirect_url(short_code: str) -> Response:
    """Перенаправить на оригинальный URL."""
    logger.info(f"Получен запрос на редирект для кода: {short_code}")
    
    link = db.get_link_by_short_code(short_code)
    if not link:
        logger.warning(f"Короткая ссылка не найдена: {short_code}")
        raise HTTPException(status_code=404, detail="Short URL not found")
    
    original_url = link["original_url"]
    logger.info(f"Найдена ссылка для кода {short_code}, перенаправляем на: {original_url}")
    
    return Response(
        status_code=302,
        headers={"Location": original_url}
    )


@app.get("/")
async def root() -> dict[str, str]:
    """Корневой эндпоинт."""
    logger.debug("Получен запрос к корневому эндпоинту")
    return {"message": "ShortLink API is running"}


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Проверка здоровья приложения."""
    logger.debug("Получен запрос на проверку здоровья")
    return {"status": "healthy"}
