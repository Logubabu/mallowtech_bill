from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
import datetime
from .database import Base

class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(String, unique=True, index=True)
    name = Column(String)
    available_stocks = Column(Integer)
    price = Column(Float)
    tax_percentage = Column(Float)

class Bill(Base):
    __tablename__ = "bills"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_email = Column(String, index=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    total_price_without_tax = Column(Float)
    total_tax_payable = Column(Float)
    net_price = Column(Float)
    rounded_net_price = Column(Float)
    balance_payable = Column(Float)
    
    items = relationship("BillItem", back_populates="bill")

class BillItem(Base):
    __tablename__ = "bill_items"
    
    id = Column(Integer, primary_key=True, index=True)
    bill_id = Column(Integer, ForeignKey("bills.id"))
    product_id = Column(String)
    quantity = Column(Integer)
    unit_price = Column(Float)
    purchase_price = Column(Float)
    tax_for_item = Column(Float)
    tax_payable = Column(Float)
    total_price = Column(Float)
    
    bill = relationship("Bill", back_populates="items")
