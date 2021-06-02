from datetime import datetime
from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel

from sqlalchemy.orm import Session

from . import crud, models, schemas
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)


class Item(BaseModel):
    customer_id: int
    country_code: str
    last_order_ts: datetime
    first_order_ts: datetime
    total_orders: int
    segment_name: str


app = FastAPI()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/customer/")
def read_customer_object(item: Item, db: Session = Depends(get_db)):

    if str(item.country_code).lower() != 'peru':
        raise HTTPException(status_code=404, detail="Country not found")

    voucher_amount = crud.get_voucher_amount(db, country_code=item.country_code, segment_name=item.segment_name)

    return {'voucher_amount': voucher_amount}
