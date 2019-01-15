from flask_wtf import FlaskForm
from wtforms import SubmitField, FloatField, SelectField
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired


class EnergyAdditionForm(FlaskForm):
    """
    Form for users to add new energy bill
    """
    date = DateField('Data', validators=[DataRequired()])
    quantity = FloatField('Ilość zużytej energii elektrycznej [kWh]', validators=[DataRequired()])
    consumption_price = FloatField('Cena za zużycie energii elektrycznej [zł]', validators=[DataRequired()])
    transmission_price = FloatField('Cena za przesył energii elektrycznej [zł]', validators=[DataRequired()], )
    building = SelectField('Budynek', validators=[DataRequired()], choices=[("SCH", "Szkoła"), ("WOR", "Warsztat")])
    submit = SubmitField('Dodaj')

    # TODO: validators


class GasAdditionForm(FlaskForm):
    """
    Form for users to add new gas bill
    """
    date = DateField('Data', validators=[DataRequired()])
    quantity = FloatField('Ilość zużytego gazu [m3]', validators=[DataRequired()])
    price = FloatField('Cena za zużyty gaz [zł]', validators=[DataRequired()])
    building = SelectField('Budynek', validators=[DataRequired()], choices=[("SCH", "Szkoła"), ("WOR", "Warsztat")])
    submit = SubmitField('Dodaj')

    # TODO: validators
