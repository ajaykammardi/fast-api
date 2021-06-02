import json
import unittest

from src.api.main import app


class UnitTests(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()

    def test_for_unsupported_countries(self):
        r = self.app.post('/voucher-amount', data=json.dumps({"customer_id": 123
            , "country_code": "Germany"
            , "last_order_ts":  "2018-05-03 00:00:00"
            , "first_order_ts": "2017-05-03 00:00:00"
            , "total_orders": 15
            , "segment_name": "recency_segment"}), headers={'Accept': 'application/json', 'Content-Type': 'application/json'})
        self.assertEqual(501, r.status_code)

    def test_for_voucher_amount(self):
        r = self.app.post('/voucher-amount', data=json.dumps({"customer_id": 123
            , "country_code": "peru"
            , "last_order_ts":  "2018-05-03 00:00:00"
            , "first_order_ts": "2017-05-03 00:00:00"
            , "total_orders": 15
            , "segment_name": "recency_segment"}), headers={'Accept': 'application/json', 'Content-Type': 'application/json'})
        self.assertEqual(200, r.status_code)