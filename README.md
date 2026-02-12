# Интернет-магазин "Лавка у Оливандера" (минимальный)

Короткая реализация задания: FastAPI + MongoDB (motor). Приложение предоставляет минимальный REST API для товаров и заказов и небольшую страницу-список.

Запуск локально:

1. Установите зависимости:

```bash
python -m pip install -r requirements.txt
```

2. Настройте `MONGO_URI` при необходимости (файл `.env.example`).

3. Заполните базу тестовыми данными:

```bash
python -m app.seed
```

4. Запустите сервер:

```bash
uvicorn app.main:app --reload --port 8000
```

Примеры запросов:

- Список товаров: `GET /api/products`
- Детали товара: `GET /api/products/{id}`
- Создать продукт: `POST /api/products` (json body)
- Создать заказ: `POST /api/orders` (см. `app.models.OrderCreate`)
