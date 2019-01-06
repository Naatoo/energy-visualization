from database import db

import pandas

from flask import Flask, redirect, url_for
from tables import Energy, Gas

import tabs


def setup_database(app):
    with app.app_context():
        db.create_all()
        insert_initial_energy_data()
        insert_initial_gas_data()


def insert_initial_energy_data():
    for name in 'school', 'workshop':
        data = pandas.read_excel('data/{}_energy.xlsx'.format(name)).to_dict('list')

        for year, month, quantity, consumption_price, transmission_price in zip(data['year'], data['month'],
                                                                                data['quantity'],
                                                                                data['consumption_price'],
                                                                                data['transmission_price']):
            db.session.add(Energy(year=year, month=month, quantity=quantity,
                                  consumption_price=consumption_price, transmission_price=transmission_price,
                                  building='SCH' if name == 'school' else 'WOR'))
            db.session.commit()


def insert_initial_gas_data():
    for name in 'school', 'workshop':
        data = pandas.read_excel('data/{}_gas.xlsx'.format(name)).to_dict('list')

        for year, month, quantity, price in zip(data['year'], data['month'], data['quantity'], data['price']):
            db.session.add(Gas(year=year, month=month, quantity=quantity, price=price,
                               building='SCH' if name == 'school' else 'WOR'))
            db.session.commit()


app = Flask(__name__)

app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///main_data.db"
db_name = 'main_data.db'

db.init_app(app)

app.register_blueprint(tabs.bp)


@app.route('/')
def index():
    return redirect(url_for('energy.energy'))


if __name__ == "__main__":
    import os
    if not os.path.isfile('main_data.db'):
        setup_database(app)
    app.run(debug=True)
