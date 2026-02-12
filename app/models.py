from pydantic import BaseModel, Field
from typing import List, Optional


class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    stock: int = 0
    categories: List[str] = Field(default_factory=list)


class ProductCreate(ProductBase):
    pass


class ProductOut(ProductBase):
    id: str = Field(..., alias="id")

    model_config = {"json_schema_extra": {"example": {"id": "698d...", "name": "Волшебная палочка", "price": 49.99}}}


class OrderItem(BaseModel):
    product_id: str
    quantity: int


class OrderCreate(BaseModel):
    customer_name: str
    customer_email: str
    items: List[OrderItem]
