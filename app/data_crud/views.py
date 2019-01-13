from flask import render_template, redirect, url_for

from app.data_crud import data
from app.data_crud.forms import EnergyAdditionForm, GasAdditionForm
from app.data_crud.prepare_data import get_data
from app.models import Energy, Gas
from database import db


@data.route('/add/energy', methods=['GET', 'POST'])
def add_energy():
    """
     Handle requests to the /add/energy route
     Add an electricity bill to the database through the form
    """
    form = EnergyAdditionForm()
    if form.validate_on_submit():
        bill = Energy(year=form.date.data.year,
                      month=form.date.data.month,
                      quantity=form.quantity.data,
                      consumption_price=form.consumption_price.data,
                      transmission_price=form.transmission_price.data,
                      building=form.building.data)
        db.session.add(bill)
        db.session.commit()
        return redirect(url_for("data_crud.add_energy"))

    return render_template("add_energy.html", rows=get_data(type_choice="energy"), form=form)


@data.route('/add/gas', methods=['GET', 'POST'])
def add_gas():
    """
     Handle requests to the /add/gas route
     Add an gas bill to the database through the form
    """
    form = GasAdditionForm()
    if form.validate_on_submit():
        bill = Gas(year=form.date.data.year,
                   month=form.date.data.month,
                   quantity=form.quantity.data,
                   price=form.price.data,
                   building=form.building.data)
        db.session.add(bill)
        db.session.commit()
        return redirect(url_for("data_crud.add_gas"))

    return render_template("add_gas.html", rows=get_data(type_choice="gas"), form=form)
