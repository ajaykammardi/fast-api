from datetime import datetime
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


class Item(BaseModel):
    customer_id: int
    country_code: str
    last_order_ts: datetime
    first_order_ts: datetime
    total_orders: int
    segment_name: str


app = FastAPI()


@app.post("/customer/")
async def read_customer_object(item: Item):

    if str(item.country_code).lower() != 'peru':
        raise HTTPException(status_code=404, detail="Country not found")

    return item