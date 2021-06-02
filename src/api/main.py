import os
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
    response = {}
    db_query_result = None
    data = request.get_json()

    app.logger.info('Getting voucher amount for %s' % str(data['country_code']))

    if str(data['country_code']).lower() != 'peru':
        abort(501)

    db_query_result = VoucherAmount.query.with_entities(VoucherAmount.voucher_amount).filter_by(country_code=data['country_code'],segment_name=data['segment_name']).first()
    response['voucher_amount'] = list(db_query_result)
    return voucher_amount_schema.dumps(db_query_result), 200, content_type


@app.errorhandler(501)
def bad_request(error):
    app.logger.error(error)
    return jsonify({'status': 501, 'message': 'Unsupported Country'}), 501


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=os.getenv('PORT'))
