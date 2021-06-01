from fastapi.testclient import TestClient


from .main import app

client = TestClient(app)


def test_for_unsupported_countries():
    response = client.post(
        "/customer/",
        json={"customer_id": 123
            , "country_code": "Germany"
            , "last_order_ts":  "2018-05-03 00:00:00"
            , "first_order_ts": "2017-05-03 00:00:00"
            , "total_orders": 15
            , "segment_name": "recency_segment"},
    )
    assert response.status_code == 404
    assert response.json() == {'detail': 'Country not found'}


def test_for_bad_request():
    response = client.post(
        "/customer/",
        json={"customer_id": 123
            , "country_code": "Germany"},
    )
    assert response.status_code == 422
