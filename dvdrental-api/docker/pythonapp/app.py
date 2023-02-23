from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy_utils import create_view
import os

app = Flask(__name__)

if __name__ == '__main__':
    app.run(debug=False)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
db = SQLAlchemy(app)

with app.app_context():
    Base = automap_base()
    Base.prepare(db.engine, reflect=True)
    Actor = Base.classes.actor
    Address = Base.classes.address
    Category = Base.classes.category
    City = Base.classes.city
    Country = Base.classes.country
    Customer = Base.classes.customer
    Film = Base.classes.film
    Film_Actor = Base.classes.film_actor
    Film_Category = Base.classes.film_category
    Inventory = Base.classes.inventory
    Language = Base.classes.language
    Payment = Base.classes.payment
    Rental = Base.classes.rental 
    Staff = Base.classes.staff
    Store = Base.classes.store

classMap = {'Actor':Actor, 
            'Address':Address, 
            'Category':Category, 
            'City':City, 
            'Country':Country, 
            'Customer':Customer, 
            'Film':Film,
            'Film_Actor':Film_Actor,
            'Film_Category':Film_Category,
            'Inventory':Inventory,
            'Language':Language,
            'Payment':Payment,
            'Rental': Rental,
            'Staff':Staff,
            'Store':Store}


@app.route('/return', methods=['POST'])
def return_content():
    body = request.get_json()
    return body['print']


@app.route('/table/<tablename>', methods=['GET'])
def get_table(tablename):
    table_content = []
    for item in db.session.query(classMap[tablename]).all():
        del item.__dict__['_sa_instance_state']
        table_content.append(item.__dict__)
    return jsonify(table_content)


@app.route('/payments/customer/<id>', methods=['GET'])
def get_payments_by_customer(id):
    payments = []
    for payment in db.session.query(Payment).filter_by(customer_id=id).all():
        del payment.__dict__['_sa_instance_state']
        payments.append(payment.__dict__)
    return jsonify(payments)

@app.route('/customer', methods=['GET'])
def get_customer_all():
    customers = []
    for customer in db.session.query(Customer).all():
        del customer.__dict__['_sa_instance_state']
        customers.append(customer.__dict__)
    return jsonify(customers)


@app.route('/customer/<id>', methods=['GET'])
def get_customer_by_id(id):
    customer = db.session.query(Customer).filter_by(customer_id=id).first()
    del customer.__dict__['_sa_instance_state']
    return jsonify(customer.__dict__)
