from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.automap import automap_base
import os

app = Flask(__name__)

if __name__ == '__main__':
    app.run(debug=True)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
db = SQLAlchemy(app)

with app.app_context():
    Base = automap_base()
    Base.prepare(db.engine, reflect=True)
    Customer = Base.classes.customer

@app.route('/customer', methods=['GET'])
def get_customer():
    customers = []
    for customer in db.session.query(Customer).all():
        del customer.__dict__['_sa_instance_state']
        customers.append(customer.__dict__)
    return jsonify(customers)