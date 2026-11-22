
[![Foodgram workflow](https://github.com/lisa-evt/foodgram/actions/workflows/main.yml/badge.svg)](https://github.com/lisa-evt/foodgram/actions/workflows/main.yml)

# Foodgram — хранилище вкусных рецептов

Foodgram — это онлайн-платформа, где пользователи могут создавать, хранить и делиться своими любимыми рецептами. Кроме того, можно скачать список продуктов, необходимых для приготовления блюда, просмотреть рецепты друзей и добавить любимые рецепты в список избранных.

Чтобы использовать все возможности сайта — нужна регистрация. Проверка адреса электронной почты не осуществляется, вы можете ввести любой email.

**Сайт:** https://foodgram.servecounterstrike.com/
**Документация API:** https://foodgram.servecounterstrike.com/api/docs/

---

## Стек

**Бэкенд**

![Python](https://img.shields.io/badge/-Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Django](https://img.shields.io/badge/-Django-092E20?style=for-the-badge&logo=django&logoColor=white)
![DRF](https://img.shields.io/badge/-DRF-ff1709?style=for-the-badge&logo=django&logoColor=white)
![djoser](https://img.shields.io/badge/-djoser_Token_Auth-5A5A5A?style=for-the-badge)
![PostgreSQL](https://img.shields.io/badge/-PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)

**Инфраструктура**

![Gunicorn](https://img.shields.io/badge/-Gunicorn-499848?style=for-the-badge&logo=gunicorn&logoColor=white)
![Nginx](https://img.shields.io/badge/-Nginx-009639?style=for-the-badge&logo=nginx&logoColor=white)
![Docker](https://img.shields.io/badge/-Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/-GitHub_Actions-2088FF?style=for-the-badge&logo=githubactions&logoColor=white)

**Фронтенд и проверка API**

![React](https://img.shields.io/badge/-React-61DAFB?style=for-the-badge&logo=react&logoColor=black)
![Postman](https://img.shields.io/badge/-Postman-FF6C37?style=for-the-badge&logo=postman&logoColor=white)

Фронтенд (React) предоставлен проектом курса, я занималась бэкендом, контейнеризацией и деплоем.

---

## Возможности

- Регистрация и вход по email, авторизация по токену (djoser + `TokenAuthentication`).
- Профиль пользователя, загрузка и удаление аватара (изображение в формате base64).
- Рецепты: создание, просмотр, редактирование и удаление. Редактировать и удалять рецепт может только его автор.
- Теги и ингредиенты с количеством для каждого рецепта.
- Фильтрация рецептов по автору, тегам, избранному и списку покупок.
- Избранное и список покупок.
- Скачивание списка покупок в формате TXT: ингредиенты суммируются по названию и единице измерения.
- Подписки на авторов и просмотр рецептов тех, на кого подписан.
- Короткие ссылки на рецепты.
- Постраничный вывод списков.
- Административная зона Django: поиск и фильтры, количество добавлений рецепта в избранное.

---

## Архитектура

Проект запускается как четыре контейнера в одной сети Docker Compose:

| Сервис     | Назначение                                                            |
|------------|-----------------------------------------------------------------------|
| `db`       | PostgreSQL, данные хранятся в volume                                  |
| `backend`  | Django + DRF под Gunicorn, статика и медиа в общих volume             |
| `frontend` | собирает React-приложение и отдаёт сборку                             |
| `gateway`  | Nginx: раздаёт статику и медиа, проксирует `/api/` и `/admin/` в бэкенд, отдаёт документацию по `/api/docs/` |

---

## Структура репозитория

```
foodgram/
├── .github/workflows/      # CI/CD (GitHub Actions)
├── backend/
│   ├── foodgram/           # manage.py и проект Django
│   │   ├── config/         # настройки, urls, wsgi
│   │   └── apps/
│   │       ├── api/        # DRF: сериализаторы, вьюсеты, фильтры, права
│   │       ├── recipes/    # модели рецептов, избранное, корзина, короткие ссылки
│   │       └── users/      # пользователь с входом по email, подписки
│   ├── requirements/       # base / development / production
│   └── Dockerfile
├── frontend/               # React-приложение и его Dockerfile
├── gateway/                # Dockerfile и nginx.conf шлюза
├── docs/                   # спецификация API (redoc.html)
├── docker-compose.yml              # локальная сборка
└── docker-compose.production.yml   # запуск на сервере из готовых образов
```

---

## Запуск локально

Понадобятся Git и Docker с плагином Docker Compose.

1. Клонируйте репозиторий и перейдите в папку проекта:

   ```bash
   git clone https://github.com/lisa-evt/foodgram.git
   cd foodgram
   ```

2. Создайте файл `.env` рядом с `docker-compose.yml`. Пример (значения замените на свои):

   ```env
   SECRET_KEY=<секретный ключ Django>
   DEBUG=False
   ALLOWED_HOSTS=localhost,127.0.0.1
   POSTGRES_DB=foodgram
   POSTGRES_USER=foodgram_user
   POSTGRES_PASSWORD=<пароль>
   DB_HOST=db
   DB_PORT=5432
   ```

3. Соберите и запустите контейнеры:

   ```bash
   docker compose up --build
   ```

4. В отдельном терминале выполните миграции, соберите статику и создайте суперпользователя:

   ```bash
   docker compose exec backend python manage.py migrate
   docker compose exec backend python manage.py collectstatic --no-input
   docker compose exec backend python manage.py createsuperuser
   ```

5. Загрузите ингредиенты в базу:

   ```bash
   docker compose exec backend <команда загрузки ингредиентов>
   ```

6. Откройте проект:
   - сайт: http://localhost:<порт>
   - документация API: http://localhost:<порт>/api/docs/
   - админка: http://localhost:<порт>/admin/

> Если локально уже запущена другая база данных на порту 5432, остановите её или не публикуйте порт PostgreSQL наружу, иначе контейнер `db` не стартует.

---

## Основные эндпоинты API

Полная спецификация находится в `docs/` и доступна по адресу `/api/docs/`. Кратко:

| Метод | Адрес | Что делает |
|-------|-------|-----------|
| POST | `/api/users/` | регистрация |
| POST | `/api/auth/token/login/` | получить токен |
| POST | `/api/auth/token/logout/` | удалить токен |
| PUT / DELETE | `/api/users/me/avatar/` | загрузить / удалить аватар |
| GET | `/api/users/subscriptions/` | мои подписки |
| POST / DELETE | `/api/users/{id}/subscribe/` | подписаться / отписаться |
| GET, POST | `/api/recipes/` | список и создание рецептов |
| GET, PATCH, DELETE | `/api/recipes/{id}/` | рецепт: просмотр, правка, удаление |
| GET | `/api/recipes/{id}/get-link/` | короткая ссылка |
| POST / DELETE | `/api/recipes/{id}/favorite/` | в избранное / из избранного |
| POST / DELETE | `/api/recipes/{id}/shopping_cart/` | в список покупок / из него |
| GET | `/api/recipes/download_shopping_cart/` | скачать список покупок |
| GET | `/api/tags/`, `/api/ingredients/` | теги и ингредиенты |

---

## CI/CD

Пайплайн описан в GitHub Actions и запускается при пуше в ветку `main`. Если один из этапов падает, следующие не выполняются.

1. **Проверка кода:** линтер flake8 для бэкенда и тесты фронтенда.
2. **Сборка и публикация образов:** `backend`, `frontend` и `gateway` собираются и отправляются в Docker Hub.
3. **Деплой:** по SSH на сервер доставляется `docker-compose.production.yml`, подтягиваются новые образы и контейнеры перезапускаются.
4. **После запуска:** выполняются миграции и `collectstatic`.

Секреты хранятся в настройках репозитория (Settings → Secrets and variables → Actions):

- `DOCKER_USERNAME`, `DOCKER_PASSWORD` — доступ к Docker Hub;
- `HOST`, `USER`, `SSH_KEY`, `SSH_PASSPHRASE` — доступ к серверу;
- <другие секреты из твоего workflow>

Файл `.env` на сервере создаётся вручную и лежит рядом с `docker-compose.production.yml`.

---

## Тестирование

Автоматических тестов у бэкенда нет, API проверялась коллекцией Postman из задания: все запросы коллекции проходят.

---

## Автор

Лиза — [GitHub](https://github.com/lisa-evt)