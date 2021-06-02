from sqlalchemy.orm import Session

from . import models


def get_voucher_amount(db: Session, country_code: str, segment_name: str, segment_variants: str):
    return db.query(models.CustomerVoucher.voucher_amount).filter(models.CustomerVoucher.country_code == country_code,
                                                                  models.CustomerVoucher.segment_name == segment_name)
