import os
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from bson import ObjectId
from typing import List

from .db import get_db
from .models import ProductCreate, ProductOut, OrderCreate

app = FastAPI(title="Интернет-магазин 'Лавка у Оливандера'")

# Allow local testing from tools / browser
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="templates")


def doc_to_product(doc: dict) -> dict:
    if doc is None:
        return None
    out = dict(doc)
    _id = out.pop("_id", None)
    if _id is not None:
        out["id"] = str(_id)
    return out


@app.on_event("startup")
async def startup():
    db = get_db()
    # Create text index for search if not exists
    await db.products.create_index([("name", "text"), ("description", "text")], name="text_idx")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    db = get_db()
    products = []
    async for p in db.products.find().limit(12):
        products.append(doc_to_product(p))
    return templates.TemplateResponse("index.html", {"request": request, "products": products})


@app.get("/api/products", response_model=List[ProductOut])
async def list_products(q: str | None = None, limit: int = 50, skip: int = 0):
    db = get_db()
    filter_ = {}
    if q:
        filter_ = {"$text": {"$search": q}}
    cursor = db.products.find(filter_).skip(skip).limit(limit)
    items = []
    async for p in cursor:
        items.append(doc_to_product(p))
    return items


@app.get("/api/products/{product_id}", response_model=ProductOut)
async def get_product(product_id: str):
    db = get_db()
    try:
        oid = ObjectId(product_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid product id")
    p = await db.products.find_one({"_id": oid})
    if not p:
        raise HTTPException(status_code=404, detail="Product not found")
    return doc_to_product(p)


@app.post("/api/products", response_model=ProductOut, status_code=201)
async def create_product(payload: ProductCreate):
    db = get_db()
    doc = payload.model_dump()
    res = await db.products.insert_one(doc)
    created = await db.products.find_one({"_id": res.inserted_id})
    return doc_to_product(created)


@app.put("/api/products/{product_id}", response_model=ProductOut)
async def update_product(product_id: str, payload: ProductCreate):
    db = get_db()
    try:
        oid = ObjectId(product_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid product id")
    res = await db.products.update_one({"_id": oid}, {"$set": payload.model_dump()})
    if res.matched_count == 0:
        raise HTTPException(status_code=404, detail="Product not found")
    p = await db.products.find_one({"_id": oid})
    return doc_to_product(p)


@app.delete("/api/products/{product_id}")
async def delete_product(product_id: str):
    db = get_db()
    try:
        oid = ObjectId(product_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid product id")
    res = await db.products.delete_one({"_id": oid})
    if res.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"deleted": product_id}


@app.post("/api/orders", status_code=201)
async def create_order(payload: OrderCreate):
    db = get_db()
    total = 0.0
    items = []
    for it in payload.items:
        try:
            oid = ObjectId(it.product_id)
        except Exception:
            raise HTTPException(status_code=400, detail=f"Invalid product id {it.product_id}")
        prod = await db.products.find_one({"_id": oid})
        if not prod:
            raise HTTPException(status_code=400, detail=f"Product {it.product_id} not found")
        price = float(prod.get("price", 0.0))
        items.append({"product_id": it.product_id, "quantity": it.quantity, "price": price})
        total += price * it.quantity
    order = {
        "customer_name": payload.customer_name,
        "customer_email": payload.customer_email,
        "items": items,
        "total": total,
    }
    res = await db.orders.insert_one(order)
    order_db = await db.orders.find_one({"_id": res.inserted_id})
    order_db = doc_to_product(order_db) if order_db else order
    return order_db
