from sqlalchemy import Column, Numeric, String

from .database import Base


class User(Base):
    __tablename__ = "customer_voucher_segments"

    country_code = Column(String)
    voucher_amount = Column(Numeric)
    segment_name = Column(String)
    segment_variants = Column(String)