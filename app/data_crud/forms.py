from flask_wtf import FlaskForm
from wtforms import SubmitField, FloatField, SelectField
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired


class EnergyAdditionForm(FlaskForm):
    """
    Form for users to add new energy bill
    """
    date = DateField('Date', validators=[DataRequired()])
    quantity = FloatField('Quantity', validators=[DataRequired()])
    consumption_price = FloatField('Consumption Price', validators=[DataRequired()])
    transmission_price = FloatField('Transmission Price', validators=[DataRequired()])
    building = SelectField('Building', validators=[DataRequired()], choices=[("SCH", "School"), ("WOR", "Workshop")])
    submit = SubmitField('Add')

    # TODO: validators


class GasAdditionForm(FlaskForm):
    """
    Form for users to add new gas bill
    """
    date = DateField('Date', validators=[DataRequired()])
    quantity = FloatField('Quantity', validators=[DataRequired()])
    price = FloatField('Price', validators=[DataRequired()])
    building = SelectField('Building', validators=[DataRequired()], choices=[("SCH", "School"), ("WOR", "Workshop")])
    submit = SubmitField('Add')

    # TODO: validators
