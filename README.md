# URL Shortener API

Сервис для сокращения ссылок с возможностью создания кастомных алиасов, отслеживания статистики и управления ссылками.

**Автор:** Сморчкова Юлиана

**Репозиторий:** [https://github.com/smorchkova001-git/url-shortener-fastapi](https://github.com/smorchkova001-git/url-shortener-fastapi)

**Деплой:** [https://url-shortener-fastapi-1-4r0q.onrender.com/](https://url-shortener-fastapi-1-4r0q.onrender.com/)  
**Документация Swagger:** [https://url-shortener-fastapi-1-4r0q.onrender.com/docs](https://url-shortener-fastapi-1-4r0q.onrender.com/docs)

---

## 📋 Содержание
- [Инструкция по запуску](#инструкция-по-запуску)
- [Описание API](#описание-api)
- [Примеры запросов](#примеры-запросов)
- [Структура БД](#структура-бд)
- [Дополнительный функционал](#дополнительный-функционал)

---

## Инструкция по запуску

### Предварительные требования
Docker и Docker Compose


### Запуск через Docker

```bash
# 1. Клонировать репозиторий
git clone https://github.com/smorchkova001-git/url-shortener-fastapi.git
cd url-shortener-fastapi

# 2. Создать файл .env (скопировать из примера)
cp .env.example .env
# Отредактировать при необходимости

# 3. Запустить контейнеры
docker-compose up -d

# 4. Проверить работу сервиса
curl http://localhost:9999/health

# Ожидаемый ответ: {"status":"healthy"}
```

---
### Аутентификация

| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| POST | `/auth/register` | Регистрация нового пользователя |
| POST | `/auth/jwt/login` | Вход (получение JWT токена) |

### Основные операции со ссылками

| Метод | Эндпоинт | Описание | Доступ |
|-------|----------|----------|--------|
| POST | `/links/shorten` | Создать короткую ссылку (можно указать `custom_alias` и `expires_at`) | Все |
| GET | `/{short_code}` | Перенаправление на оригинальный URL | Все |
| GET | `/links/{short_code}/stats` | Получить статистику (дата создания, кол-во переходов, последнее использование) | Все |
| PUT | `/links/{short_code}` | Обновить оригинальный URL | Только владелец |
| DELETE | `/links/{short_code}` | Удалить ссылку | Только владелец |
| GET | `/links/search` | Поиск ссылок по оригинальному URL | Все |

### Дополнительные функции

#### 1. Управление неиспользуемыми ссылками

| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| GET | `/links/unused?days=N` | Просмотр ссылок без переходов за последние N дней |
| POST | `/links/cleanup-unused?days=N` | Удаление ссылок без переходов за последние N дней |

#### 2. Отображение истории истекших ссылок

| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| GET | `/links/expired` | Просмотр всех истекших ссылок (`expires_at` < текущей даты) |

### Функциональность на дополнительные баллы

| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| GET | `/links/{short_code}/qr` | Генерация QR-кода для короткой ссылки (PNG) |
| GET | `/links/{short_code}/analytics` | Детальная аналитика (IP, referer, user-agent) |

---

## Примеры запросов

Все запросы используют базовый URL https://url-shortener-fastapi-1-4r0q.onrender.com.

Для локального запуска замените на http://localhost:8000 или http://localhost:9999.

#### 1. Регистрация пользователя
```bash
curl -X POST https://url-shortener-fastapi-1-4r0q.onrender.com/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "StrongPass123!",
    "username": "testuser"
  }'
```
#### 2. Вход (получение токена)
```bash
curl -X POST https://url-shortener-fastapi-1-4r0q.onrender.com/auth/jwt/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user@example.com&password=StrongPass123!"
```
#### 3. Создание короткой ссылки (анонимно)
```bash
curl -X POST https://url-shortener-fastapi-1-4r0q.onrender.com/links/shorten \
  -H "Content-Type: application/json" \
  -d '{"original_url": "https://google.com"}'
```
#### 4. Создание ссылки с кастомным алиасом
```bash
curl -X POST https://url-shortener-fastapi-1-4r0q.onrender.com/links/shorten \
  -H "Content-Type: application/json" \
  -d '{
    "original_url": "https://www.youtube.com",
    "custom_alias": "yt"
  }'
```
#### 5. Создание ссылки с временем жизни
```bash
curl -X POST https://url-shortener-fastapi-1-4r0q.onrender.com/links/shorten \
  -H "Content-Type: application/json" \
  -d '{
    "original_url": "https://stackoverflow.com",
    "expires_at": "2026-12-31T23:59:59"
  }'
```
#### 6. Редирект по короткой ссылке
```bash
curl -v https://url-shortener-fastapi-1-4r0q.onrender.com/{short_code}
```
#### 7. Получение статистики
```bash
curl https://url-shortener-fastapi-1-4r0q.onrender.com/links/{short_code}/stats
```

#### 8. Поиск по оригинальному URL (в данном примере где содержит слово "google")
```bash
curl "https://url-shortener-fastapi-1-4r0q.onrender.com/links/search?original_url=google"
```
#### 9. Обновление ссылки (только владелец)
```bash
curl -X PUT https://url-shortener-fastapi-1-4r0q.onrender.com/links/zZfBJu \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"original_url": "https://docker.com"}'
```
#### 10. Удаление ссылки (только владелец)
```bash
curl -X DELETE https://url-shortener-fastapi-1-4r0q.onrender.com/links/zZfBJu \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```
#### 11. Получение QR-кода
```bash
curl -X GET https://url-shortener-fastapi-1-4r0q.onrender.com/links/KKWFMT/qr --output qrcode.png
```
#### 12. Детальная аналитика (только владелец)
```bash
curl -X GET https://url-shortener-fastapi-1-4r0q.onrender.com/links/zZfBJu/analytics \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```
#### 13. Просмотр неиспользуемых ссылок
```bash
curl "https://url-shortener-fastapi-1-4r0q.onrender.com/links/unused?days=30"
```
#### 14. Очистка неиспользуемых ссылок
```bash
curl -X POST "https://url-shortener-fastapi-1-4r0q.onrender.com/links/cleanup-unused?days=30"
```
#### 15. Просмотр истекших ссылок
```bash
curl "https://url-shortener-fastapi-1-4r0q.onrender.com/links/expired"
```
## Структура БД

### Таблица user

| Колонка | Тип | Описание |
|---------|-----|----------|
| id | UUID | Первичный ключ |
| email | String | Email (уникальный) |
| username | String | Имя пользователя |
| hashed_password | String | Хеш пароля |
| is_active | Boolean | Активен ли пользователь |
| is_superuser | Boolean | Администратор |
| is_verified | Boolean | Подтверждён ли email |

### Таблица links

| Колонка | Тип | Описание |
|---------|-----|----------|
| id | Integer | Первичный ключ |
| short_code | String | Короткий код (уникальный) |
| original_url | String | Оригинальный URL |
| custom_alias | String | Кастомный алиас (уникальный) |
| user_id | UUID | Владелец (FK к user.id) |
| created_at | DateTime | Дата создания |
| last_accessed | DateTime | Последнее использование |
| click_count | Integer | Количество переходов |
| is_active | Boolean | Активна ли ссылка |
| expires_at | DateTime | Дата истечения срока |

### Таблица clicks

| Колонка | Тип | Описание |
|---------|-----|----------|
| id | Integer | Первичный ключ |
| link_id | Integer | Ссылка (FK к links.id) |
| accessed_at | DateTime | Время перехода |
| referer | String | Откуда пришёл пользователь |
| user_agent | String | Информация о браузере |
| ip_address | String | IP-адрес |

---

## Дополнительный функционал

- **Генерация QR-кодов** для любой короткой ссылки.
- **Детальная аналитика** переходов с сохранением IP, referer и user-agent.
- **Автоматическая очистка** неиспользуемых ссылок по заданному количеству дней.
- **Просмотр истории истекших ссылок** (с истекшим сроком жизни).

---

## Кэширование

Для оптимизации работы используется Redis:

- Кэшируются результаты поиска (`/links/search`) на 60 секунд.
- Кэшируется статистика по ссылке (`/links/{code}/stats`) на 60 секунд.
- Кэш автоматически сбрасывается при создании, обновлении или удалении ссылки.

---

## Технологии

- **FastAPI** — веб-фреймворк
- **PostgreSQL** + **asyncpg** — основная база данных
- **Redis** + **fastapi-cache2** — кэширование
- **SQLAlchemy 2.0** + **Alembic** — ORM и миграции
- **FastAPI Users** — аутентификация (JWT)
- **Docker** + **docker-compose** — контейнеризация и оркестрация
- **Pytest** — тестирование