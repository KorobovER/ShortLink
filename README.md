# ShortLink - Сервис коротких ссылок

## Установка

### 1. Клонирование репозитория

```bash
git clone <repository-url>
cd ShortLink
```

### 2. Создание виртуального окружения

```bash
# Windows
py -m venv venv
venv\Scripts\activate

### 3. Установка зависимостей

```bash
# Установить основные зависимости
pip install -e .

# Установить с dev зависимостями (для разработки и тестирования)
pip install -e ".[dev]"
```

### Запуск приложения

```bash
uvicorn shortlink.main:app --reload
```

Приложение будет доступно по адресу: **http://localhost:8000**

### Документация API

После запуска приложения документация доступна по адресам:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Эндпоинты

### Создание короткой ссылки

**Запрос:**
```bash
POST /shorten
Content-Type: application/json

{
  "url": "https://example.com/very/long/url/with/parameters?param1=value1&param2=value2"
}
```

**Ответ (200 OK):**
```json
{
  "short_url": "http://localhost:8000/abc123",
  "original_url": "https://example.com/very/long/url/with/parameters?param1=value1&param2=value2"
}
```

### Перенаправление по короткой ссылке

**Запрос:**
```bash
GET /abc123
```

**Ответ (302 Found):**
Браузер автоматически перенаправляется на оригинальный URL

## Тестирование

### Запуск всех тестов

```bash
pytest -v
```

### Запуск тестов конкретного модуля

```bash
# Тесты API
pytest tests/test_main.py -v

# Тесты базы данных
pytest tests/test_database.py -v
```


## Структура проекта

```
ShortLink/
├── src/shortlink/              # Исходный код приложения
│   ├── __init__.py            # Инициализация пакета
│   ├── main.py                # Основное FastAPI приложение
│   └── database.py            # Модуль работы с SQLite3
├── tests/                      # Тесты
│   ├── __init__.py
│   ├── test_main.py           # Тесты API
│   └── test_database.py       # Тесты базы данных
├── pyproject.toml             # Конфигурация проекта и зависимости
├── pytest.ini                 # Конфигурация pytest
├── .gitignore                 # Файлы для игнорирования в git
└── README.md                  # Этот файл
```

## Как работает кодирование

Приложение использует **SHA-256 хеширование** для создания коротких кодов:

1. **Хеширование**: URL преобразуется в SHA-256 хеш
2. **Извлечение**: Берутся первые 6 байт хеша
3. **Кодирование**: Байты кодируются в base62 (0-9, a-z, A-Z)
4. **Результат**: Получается 6-символьный код

**Преимущества:**
- Детерминированность - одинаковый URL → одинаковый код
- Уникальность - разные URL → разные коды (в 99.99% случаев)
- Компактность - всего 6 символов
- Безопасность - невозможно угадать существующие коды

## База данных

Приложение использует **SQLite3** - встроенную базу данных Python.

### Структура таблицы `links`

```sql
CREATE TABLE links (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    short_code TEXT UNIQUE NOT NULL,        -- Короткий код (например: abc123)
    original_url TEXT NOT NULL,             -- Оригинальный длинный URL
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP  -- Время создания
)
```

### Файл базы данных

База данных хранится в файле `shortlink.db` в корневой директории проекта.

**Примечание:** Файл `shortlink.db` добавлен в `.gitignore` и не отслеживается git.

## Примеры использования

### Пример 1: Создание короткой ссылки в Python

```python
import requests

url = "https://example.com/very/long/url"
response = requests.post(
    "http://localhost:8000/shorten",
    json={"url": url}
)

data = response.json()
print(f"Короткая ссылка: {data['short_url']}")
# Вывод: Короткая ссылка: http://localhost:8000/abc123
```

### Пример 2: Использование в curl

```bash
# Создать короткую ссылку
curl -X POST "http://localhost:8000/shorten" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/long/url"}'

# Проверить статус
curl "http://localhost:8000/health"
```

## Жизненный цикл запроса

```
1. Пользователь отправляет длинный URL
   ↓
2. Приложение хеширует URL (SHA-256)
   ↓
3. Проверяет есть ли уже такой URL в БД
   ↓
4. Если нет - сохраняет новую ссылку
   ↓
5. Возвращает короткую ссылку пользователю
   ↓
6. Пользователь переходит по короткой ссылке
   ↓
7. Приложение находит оригинальный URL в БД
   ↓
8. Перенаправляет на оригинальный URL (HTTP 302)
```

