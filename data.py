from flask import Blueprint
from flask import render_template, request, redirect, url_for
from tables import Energy, Gas
from tools.global_paths import MONTHS_NAMES_FILE, BUILDINGS_NAMES_POLISH_FILE
import json
from database import db


bp = Blueprint('data', __name__, url_prefix='')


@bp.route('/add/energy', methods=['GET', 'POST'])
def add_energy():
    type_choice = get_energy_type(current_page="energy")
    if request.method == 'POST':
        if "data_input" in request.form:
            date = request.form.get('date')
            year, month = date.split('-')[:2]
            quantity = request.form.get('quantity')
            consumption_price = request.form.get('consumption_price')
            transmission_price = request.form.get('transmission_price')

            db.session.add(Energy(year=year, month=month, quantity=quantity,
                                  consumption_price=consumption_price, transmission_price=transmission_price,
                                  building='SCH'))

            db.session.commit()
    if type_choice == 'energy':
        return render_template("add_energy.html", rows=get_data(type_choice="energy"))
    else:
        return redirect(url_for("data.add_gas"))


@bp.route('/add/gas', methods=['GET', 'POST'])
def add_gas():
    type_choice = get_energy_type(current_page="gas")
    if request.method == 'POST':

        if "data_input" in request.form:
            date = request.form.get('date')
            year, month = date.split('-')[:2]
            quantity = request.form.get('quantity')
            price = request.form.get('price')

            db.session.add(Gas(year=year, month=month, quantity=quantity,
                               price=price, building='WOR'))
            db.session.commit()

    if type_choice == 'gas':
        return render_template("add_gas.html", rows=get_data(type_choice="gas"))
    else:
        return redirect(url_for("data.add_energy"))


def get_energy_type(current_page):
    type_choice = current_page
    if request.method == "POST" and "energy_type" in request.form:
        type_choice = request.form["options"]
    return type_choice


def get_data(type_choice):
    with open(MONTHS_NAMES_FILE) as f:
        months_names_mapping = json.loads(f.read())

    with open(BUILDINGS_NAMES_POLISH_FILE) as f:
        buildings_names = json.loads(f.read())

    if type_choice == 'energy':
        rows = Energy.query.order_by(Energy.year.desc(), Energy.month.desc()).limit(10).all()
        data = [[row.year, months_names_mapping[str(row.month)], buildings_names[row.building],
                 row.quantity, row.consumption_price, row.transmission_price] for row in rows]
    elif type_choice == 'gas':
        rows = Gas.query.order_by(Gas.year.desc(), Gas.month.desc()).limit(10).all()
        data = [[row.year, months_names_mapping[str(row.month)], buildings_names[row.building],
                 row.quantity, row.price] for row in rows]
    return data