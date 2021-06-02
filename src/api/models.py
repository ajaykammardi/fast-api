from sqlalchemy import Column, Numeric, String

from .database import Base


class CustomerVoucher(Base):
    __tablename__ = "customer_voucher_segments"

    country_code = Column(String, primary_key=True)
    voucher_amount = Column(Numeric)
    segment_name = Column(String, primary_key=True)
    segment_variants = Column(String, primary_key=True)
