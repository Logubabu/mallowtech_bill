from pydantic import BaseModel
from typing import List
from datetime import datetime

class ProductBase(BaseModel):
    product_id: str
    name: str
    available_stocks: int
    price: float
    tax_percentage: float

class ProductCreate(ProductBase):
    pass

class Product(ProductBase):
    id: int
    class Config:
        orm_mode = True

class BillItemCreate(BaseModel):
    product_id: str
    quantity: int

class BillCreate(BaseModel):
    customer_email: str
    items: List[BillItemCreate]
    cash_paid: float
    denominations: dict

class BillItem(BaseModel):
    product_id: str
    quantity: int
    unit_price: float
    purchase_price: float
    tax_for_item: float
    tax_payable: float
    total_price: float

    class Config:
        orm_mode = True

class BillResponse(BaseModel):
    id: int
    customer_email: str
    created_at: datetime
    items: List[BillItem]
    total_price_without_tax: float
    total_tax_payable: float
    net_price: float
    rounded_net_price: float
    balance_payable: float
    balance_denominations: dict

    class Config:
        orm_mode = True

class BillHistoryList(BaseModel):
    id: int
    customer_email: str
    created_at: datetime
    net_price: float
    
    class Config:
        orm_mode = True
