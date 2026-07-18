from sqlalchemy.orm import Session
from . import models, schemas
import math

def get_product_by_product_id(db: Session, product_id: str):
    return db.query(models.Product).filter(models.Product.product_id == product_id).first()

def get_products(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Product).offset(skip).limit(limit).all()

def create_bill(db: Session, bill_in: schemas.BillCreate, balance_denoms: dict):
    # Calculate totals
    total_price_without_tax = 0.0
    total_tax_payable = 0.0
    
    db_items = []
    
    for item in bill_in.items:
        product = get_product_by_product_id(db, item.product_id)
        if not product:
            continue
            
        purchase_price = product.price * item.quantity
        tax_payable = (purchase_price * product.tax_percentage) / 100
        total_price = purchase_price + tax_payable
        
        total_price_without_tax += purchase_price
        total_tax_payable += tax_payable
        
        db_item = models.BillItem(
            product_id=product.product_id,
            quantity=item.quantity,
            unit_price=product.price,
            purchase_price=purchase_price,
            tax_for_item=product.tax_percentage,
            tax_payable=tax_payable,
            total_price=total_price
        )
        db_items.append(db_item)
        
        # update stock
        product.available_stocks -= item.quantity
        db.add(product)

    net_price = total_price_without_tax + total_tax_payable
    rounded_net_price = math.floor(net_price)
    balance_payable = bill_in.cash_paid - rounded_net_price

    db_bill = models.Bill(
        customer_email=bill_in.customer_email,
        total_price_without_tax=total_price_without_tax,
        total_tax_payable=total_tax_payable,
        net_price=net_price,
        rounded_net_price=rounded_net_price,
        balance_payable=balance_payable
    )
    
    db.add(db_bill)
    db.commit()
    db.refresh(db_bill)
    
    for item in db_items:
        item.bill_id = db_bill.id
        db.add(item)
        
    db.commit()
    db.refresh(db_bill)
    
    return db_bill

def get_bills_by_email(db: Session, email: str):
    return db.query(models.Bill).filter(models.Bill.customer_email == email).order_by(models.Bill.created_at.desc()).all()

def get_bill_by_id(db: Session, bill_id: int):
    return db.query(models.Bill).filter(models.Bill.id == bill_id).first()
