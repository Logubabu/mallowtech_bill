from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from typing import List

from . import models, schemas, crud, utils
from .database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Billing System API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/products", response_model=List[schemas.Product])
def read_products(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    products = crud.get_products(db, skip=skip, limit=limit)
    return products

@app.post("/api/bills", response_model=schemas.BillResponse)
def create_bill(bill_in: schemas.BillCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    # Calculate net price first to check balance
    total_price = 0
    for item in bill_in.items:
        product = crud.get_product_by_product_id(db, item.product_id)
        if product:
            purchase_price = product.price * item.quantity
            tax_payable = (purchase_price * product.tax_percentage) / 100
            total_price += purchase_price + tax_payable
            
    import math
    rounded_net_price = math.floor(total_price)
    
    if bill_in.cash_paid < rounded_net_price:
        raise HTTPException(status_code=400, detail="Cash paid is less than the net price.")
        
    balance_payable = bill_in.cash_paid - rounded_net_price
    balance_denoms = utils.calculate_balance_denominations(balance_payable, bill_in.denominations)
    
    db_bill = crud.create_bill(db, bill_in, balance_denoms)
    
    background_tasks.add_task(utils.send_invoice_email, db_bill.customer_email, db_bill.id, db_bill.net_price)
    
    # We add balance_denominations to the response dynamically
    response_data = db_bill.__dict__
    response_data["balance_denominations"] = balance_denoms
    return response_data

@app.get("/api/bills", response_model=List[schemas.BillHistoryList])
def read_bills(email: str, db: Session = Depends(get_db)):
    bills = crud.get_bills_by_email(db, email)
    return bills

@app.get("/api/bills/{bill_id}", response_model=schemas.BillResponse)
def read_bill(bill_id: int, db: Session = Depends(get_db)):
    db_bill = crud.get_bill_by_id(db, bill_id)
    if db_bill is None:
        raise HTTPException(status_code=404, detail="Bill not found")
        
    # Recalculate or mock denoms since we don't store the exact returned denoms in DB
    # For a real system we might store it.
    balance_denoms = utils.calculate_balance_denominations(db_bill.balance_payable, {})
    
    response_data = db_bill.__dict__
    response_data["balance_denominations"] = balance_denoms
    return response_data

# Seed data endpoint for testing
@app.post("/api/seed")
def seed_data(db: Session = Depends(get_db)):
    products = [
        models.Product(product_id="P001", name="Product A", available_stocks=100, price=100.0, tax_percentage=5.0),
        models.Product(product_id="P002", name="Product B", available_stocks=50, price=50.0, tax_percentage=12.0),
        models.Product(product_id="P003", name="Product C", available_stocks=200, price=10.0, tax_percentage=18.0),
    ]
    for p in products:
        existing = db.query(models.Product).filter(models.Product.product_id == p.product_id).first()
        if not existing:
            db.add(p)
    db.commit()
    return {"message": "Data seeded"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
