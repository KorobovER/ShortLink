"""Main FastAPI application."""

import hashlib
from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel, HttpUrl

from shortlink.database import db


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


@app.on_event("startup")
async def startup_event() -> None:
    """Initialize database on startup."""
    db.initialize()


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
    
    # Генерируем детерминированный короткий код из URL
    short_code = generate_short_code(original_url)
    
    # Проверяем, существует ли URL уже
    existing = db.get_link_by_original_url(original_url)
    if not existing:
        # Обрабатываем потенциальную коллизию хеша
        collision = db.get_link_by_short_code(short_code)
        if collision:
            # Добавляем суффикс для разрешения коллизии
            suffix = 1
            while True:
                new_code = f"{short_code}{suffix}"
                if not db.get_link_by_short_code(new_code):
                    short_code = new_code
                    break
                suffix += 1
        db.add_link(short_code, original_url)
    else:
        short_code = existing["short_code"]
    
    short_url = f"http://localhost:8000/{short_code}"
    
    return URLResponse(
        short_url=short_url,
        original_url=original_url
    )


@app.get("/{short_code}")
async def redirect_url(short_code: str) -> Response:
    """Перенаправить на оригинальный URL."""
    link = db.get_link_by_short_code(short_code)
    if not link:
        raise HTTPException(status_code=404, detail="Short URL not found")
    
    return Response(
        status_code=302,
        headers={"Location": link["original_url"]}
    )


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint."""
    return {"message": "ShortLink API is running"}


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"}
