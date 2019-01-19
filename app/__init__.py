import os
import pandas
from flask import Flask
from flask_bootstrap import Bootstrap

from .analyse import analyse as analyse_blueprint
from .data_crud import data as data_blueprint
from .home import home as home_blueprint
from .auth import auth as auth_blueprint
from app.models import Gas, Energy
from database import db
from login_manager import login_manager


def create_app():
    app = Flask(__name__)
    app.config['DEBUG'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///../main_data.db"
    SECRET_KEY = os.urandom(32)
    app.config['SECRET_KEY'] = SECRET_KEY
    Bootstrap(app)
    db.init_app(app)
    login_manager.init_app(app)
    app.register_blueprint(analyse_blueprint)
    app.register_blueprint(data_blueprint)
    app.register_blueprint(home_blueprint)
    app.register_blueprint(auth_blueprint)

    return app


def setup_database(app):
    with app.app_context():
        db.create_all()
        insert_initial_energy_data()
        insert_initial_gas_data()


def insert_initial_energy_data():
    for name in 'school', 'workshop':
        data = pandas.read_excel('app/initial_data/{}_energy.xlsx'.format(name)).to_dict('list')
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
        data = pandas.read_excel('app/initial_data/{}_gas.xlsx'.format(name)).to_dict('list')
        for year, month, quantity, price in zip(data['year'], data['month'], data['quantity'], data['price']):
            db.session.add(Gas(year=year, month=month, quantity=quantity, price=price,
                               building='SCH' if name == 'school' else 'WOR'))
            db.session.commit()
