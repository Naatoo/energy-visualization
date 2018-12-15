from database import db

import pandas
import os

from flask import Flask
from tables import SchoolEnergy, WorkshopEnergy

import tabs


def create_app():
    app = Flask(__name__)
    app.config['DEBUG'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///historical_data.db"
    db_name = 'historical_data.db'
    if os.path.isfile(db_name):
        os.remove(db_name)
    db.init_app(app)
    app.register_blueprint(tabs.bp)
    return app


def setup_database(app):
    with app.app_context():
        db.create_all()
        names = {'school': SchoolEnergy, 'workshop': WorkshopEnergy}
        for name in names:
            data = pandas.read_excel('data/{}_energy.xlsx'.format(name)).to_dict('list')

            for year, month, quantity, consumption_price, transmission_price in zip(data['year'], data['month'],
                                                                                    data['quantity'],
                                                                                    data['consumption_price'],
                                                                                    data['transmission_price']):
                db.session.add(names[name](year=year, month=month, quantity=quantity,
                                           consumption_price=consumption_price, transmission_price=transmission_price))
                db.session.commit()


if __name__ == "__main__":
    app = create_app()
    if not os.path.isfile('historical_data.db'):
        setup_database(app)
    app.run(debug=True)
