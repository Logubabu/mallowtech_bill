from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from typing import List

try:
    from . import models, schemas, crud, utils
    from .database import engine, get_db
except ImportError:  # pragma: no cover - allows running main.py directly from backend/
    import models
    import schemas
    import crud
    import utils
    from database import engine, get_db

models.Base.metadata.create_all(bind=engine)


def _seed_products_if_missing(db: Session) -> None:
    products = [
        models.Product(product_id="P001", name="Product A", available_stocks=100, price=100.0, tax_percentage=5.0),
        models.Product(product_id="P002", name="Product B", available_stocks=50, price=50.0, tax_percentage=12.0),
        models.Product(product_id="P003", name="Product C", available_stocks=200, price=10.0, tax_percentage=18.0),
    ]
    for product in products:
        existing = db.query(models.Product).filter(models.Product.product_id == product.product_id).first()
        if not existing:
            db.add(product)
    db.commit()


with Session(engine) as session:
    _seed_products_if_missing(session)

app = FastAPI(title="Billing System API")


def _build_bill_payload(db: Session, db_bill, balance_denoms: dict):
    bill_items = db.query(models.BillItem).filter(models.BillItem.bill_id == db_bill.id).all()
    return {
        "id": db_bill.id,
        "customer_email": db_bill.customer_email,
        "created_at": db_bill.created_at,
        "items": [
            {
                "product_id": item.product_id,
                "quantity": item.quantity,
                "unit_price": item.unit_price,
                "purchase_price": item.purchase_price,
                "tax_for_item": item.tax_for_item,
                "tax_payable": item.tax_payable,
                "total_price": item.total_price,
            }
            for item in bill_items
        ],
        "total_price_without_tax": db_bill.total_price_without_tax,
        "total_tax_payable": db_bill.total_tax_payable,
        "net_price": db_bill.net_price,
        "rounded_net_price": db_bill.rounded_net_price,
        "balance_payable": db_bill.balance_payable,
        "balance_denominations": balance_denoms,
    }

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

@app.post("/api/products", response_model=schemas.Product)
def create_product(product_in: schemas.ProductCreate, db: Session = Depends(get_db)):
    existing = crud.get_product_by_product_id(db, product_in.product_id)
    if existing:
        raise HTTPException(status_code=400, detail="Product ID already exists")

    product = models.Product(
        product_id=product_in.product_id,
        name=product_in.name,
        available_stocks=product_in.available_stocks,
        price=product_in.price,
        tax_percentage=product_in.tax_percentage,
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return product

@app.post("/api/bills", response_model=schemas.BillResponse)
def create_bill(bill_in: schemas.BillCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    if not bill_in.items:
        raise HTTPException(status_code=400, detail="At least one bill item is required.")

    total_price = 0.0
    for item in bill_in.items:
        product = crud.get_product_by_product_id(db, item.product_id)
        if not product:
            raise HTTPException(status_code=404, detail=f"Product {item.product_id} not found")

        purchase_price = product.price * item.quantity
        tax_payable = (purchase_price * product.tax_percentage) / 100
        total_price += purchase_price + tax_payable

    rounded_net_price = int(total_price)

    if bill_in.cash_paid < rounded_net_price:
        raise HTTPException(status_code=400, detail="Cash paid is less than the net price.")

    balance_payable = bill_in.cash_paid - rounded_net_price
    balance_denoms = utils.calculate_balance_denominations(balance_payable, bill_in.denominations)

    db_bill = crud.create_bill(db, bill_in, balance_denoms)

    background_tasks.add_task(utils.send_invoice_email, db_bill.customer_email, db_bill.id, db_bill.net_price)

    return _build_bill_payload(db, db_bill, balance_denoms)

@app.get("/api/bills", response_model=List[schemas.BillHistoryList])
def read_bills(email: str, db: Session = Depends(get_db)):
    bills = crud.get_bills_by_email(db, email)
    return bills

@app.get("/api/bills/{bill_id}", response_model=schemas.BillResponse)
def read_bill(bill_id: int, db: Session = Depends(get_db)):
    db_bill = crud.get_bill_by_id(db, bill_id)
    if db_bill is None:
        raise HTTPException(status_code=404, detail="Bill not found")
        
    balance_denoms = utils.calculate_balance_denominations(db_bill.balance_payable, {})
    return _build_bill_payload(db, db_bill, balance_denoms)

# Seed data endpoint for testing
@app.post("/api/seed")
def seed_data(db: Session = Depends(get_db)):
    _seed_products_if_missing(db)
    return {"message": "Data seeded"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
