from flask import Flask, request, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base
from sqlalchemy_utils import create_view
import os

app = Flask(__name__)

if __name__ == '__main__':
    app.run(debug=False)

engine = create_engine(os.environ.get('DATABASE_URL'))
session = Session(engine)

Base = automap_base()
Base.prepare(autoload_with=engine, reflect=True)

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

tableMap = {'Actor':Actor, 
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

@app.route('/query/table/<tablename>', methods=['GET'])
def get_table(tablename):
    if tablename not in tableMap.keys():
        return f'{tablename} table does not exist'
    table_content = []
    for item in session.query(tableMap[tablename]).all():
        del item.__dict__['_sa_instance_state']
        table_content.append(item.__dict__)
    return jsonify(table_content)

@app.route('/query/item', methods=['POST'])
def generic_query():
    body = request.get_json()
    item = session.query(tableMap[body["table"]]).get(body["id"])
    if item is None:
        return f'No object found in {tableMap[body["table"]]} with id {body["id"]}'
    del item.__dict__['_sa_instance_state']
    return jsonify(item.__dict__)


