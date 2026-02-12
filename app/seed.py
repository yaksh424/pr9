import asyncio
from .db import get_db


SAMPLE_PRODUCTS = [
    {
        "name": "Волшебная палочка — Оливандер (модель №1)",
        "description": "Ручная работа. Идеально подходит для начинающих магов.",
        "price": 49.99,
        "stock": 12,
        "categories": ["палочки", "аксессуары"],
    },
    {
        "name": "Перо феникса — запасной стержень",
        "description": "Высококачественное перо для усиления заклинаний.",
        "price": 19.5,
        "stock": 50,
        "categories": ["компоненты"],
    },
    {
        "name": "Одиночный зелье-чай 'Смелость' (100ml)",
        "description": "Добавляет уверенности перед экзаменами.",
        "price": 9.99,
        "stock": 100,
        "categories": ["зелья"],
    },
]


async def seed():
    db = get_db()
    await db.products.delete_many({})
    await db.orders.delete_many({})
    res = await db.products.insert_many(SAMPLE_PRODUCTS)
    print('Inserted product ids:', res.inserted_ids)


if __name__ == '__main__':
    asyncio.run(seed())
