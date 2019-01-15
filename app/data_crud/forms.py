from flask_wtf import FlaskForm
from wtforms import SubmitField, FloatField, SelectField
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired


class EnergyAdditionForm(FlaskForm):
    """
    Form for users to add new energy bill
    """
    date = DateField('Data', validators=[DataRequired()])
    quantity = FloatField('Ilość [kWh]', validators=[DataRequired()])
    consumption_price = FloatField('Cena za zużycie', validators=[DataRequired()])
    transmission_price = FloatField('Cena za przesył', validators=[DataRequired()], )
    building = SelectField('Budynek', validators=[DataRequired()], choices=[("SCH", "Szkoła"), ("WOR", "Warsztat")])
    submit = SubmitField('Dodaj')

    # TODO: validators


class GasAdditionForm(FlaskForm):
    """
    Form for users to add new gas bill
    """
    date = DateField('Data', validators=[DataRequired()])
    quantity = FloatField('Ilość [m3]', validators=[DataRequired()])
    price = FloatField('Cena', validators=[DataRequired()])
    building = SelectField('Budynek', validators=[DataRequired()], choices=[("SCH", "Szkoła"), ("WOR", "Warsztat")])
    submit = SubmitField('Dodaj')

    # TODO: validators
