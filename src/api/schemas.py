from pydantic import BaseModel


class Voucher(BaseModel):
    vocher_amount: float
    country_code: str
    segment_name: str
    segment_variants: str

    class Config:
        orm_mode = True
