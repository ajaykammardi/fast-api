import os
import datetime

from flask import Flask, jsonify, abort, request
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from marshmallow import fields


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres_user:postgres@postgresdb/postgres_db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['DEBUG'] = True

db = SQLAlchemy(app)
ma = Marshmallow(app)
migrate = Migrate(app, db)

content_type = {'Content-Type': 'application/json'}


class VoucherAmount(db.Model):
    __tablename__ = 'customer_voucher_segments'

    country_code = db.Column(db.Integer, primary_key=True)
    voucher_amount = db.Column(db.Numeric)
    segment_name = db.Column(db.String(100), primary_key=True)
    segment_variants = db.Column(db.String(100), primary_key=True)


class VoucherAmountSchema(ma.SQLAlchemyAutoSchema):
    voucher_amount = fields.Float(dump_only=True)

    class Meta:
        model = VoucherAmount


voucher_amount_schema = VoucherAmountSchema()


@app.route('/voucher-amount', methods=['POST'])
def get_voucher_amount():
    db_query_result = None
    segment_variants = None
    data = request.get_json()

    app.logger.info('Getting voucher amount for %s' % str(data['country_code']))

    if str(data['country_code']).lower() != 'peru':
        abort(501)

    if str(data['segment_name']).lower() != 'recency_segment' and str(
            data['segment_name']).lower() != 'frequent_segment':
        abort(501)

    if str(data['segment_name']).lower() == 'frequent_segment':
        if 0 <= int(data['total_orders']) < 5:
            segment_variants = '0-4'
        if 5 <= int(data['total_orders']) < 14:
            segment_variants = '5-13'
        if 14 <= int(data['total_orders']) < 38:
            segment_variants = '14-37'
        if 14 <= int(data['total_orders']) < 38:
            segment_variants = '14-37'
        if int(data['total_orders']) >= 38:
            segment_variants = '38>'
    elif str(data['segment_name']).lower() == 'recency_segment':
        today = datetime.date.today()
        last_order_date = datetime.datetime.strptime(data['last_order_ts'], '%Y-%m-%d %H:%M:%S').date()
        diff = today - last_order_date

        if 30 <= int(diff.days) < 61:
            segment_variants = '30-60'
        if 61 <= int(diff.days) < 91:
            segment_variants = '61-90'
        if 91 <= int(diff.days) < 121:
            segment_variants = '91-120'
        if 121 <= int(diff.days) < 181:
            segment_variants = '121-180'
        if int(diff.days) > 180:
            segment_variants = '180+'

    db_query_result = VoucherAmount.query.with_entities(VoucherAmount.voucher_amount).filter_by(
        country_code=data['country_code'], segment_name=data['segment_name'], segment_variants=segment_variants).first()
    return voucher_amount_schema.dumps(db_query_result), 200, content_type


@app.errorhandler(501)
def bad_request(error):
    app.logger.error(error)
    return jsonify({'status': 501, 'message': 'Unsupported Country/Segment Variant'}), 501


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=os.getenv('PORT'))
