from flask_wtf import FlaskForm
from wtforms import SubmitField, SelectField
from wtforms.validators import DataRequired


class ChartForm(FlaskForm):
    """
    Form for users to add new energy bill
    """
    year = SelectField('Okres', validators=[DataRequired()], choices=[("2015", "2015"), ("2016", "2016"),
                                                                      ("2017", "2017"), ("2018", "2018"),
                                                                      ("2019", "2019"), ("All", "Wszystkie"),
                                                                      ('Avarage', 'Średnia')])
    building = SelectField('Budynek', validators=[DataRequired()], choices=[("SCH", "Szkoła"), ("WOR", "Warsztat"),
                                                                            ("All", "Wszystkie")])
    energy_type = SelectField('Rodzaj energii', validators=[DataRequired()],
                              choices=[("energy", "Energia elektryczna"), ("gas", "Gaz"),
                                       ("All", "Wszystkie")])
    chart_type = SelectField('Typ wykresu', validators=[DataRequired()],
                             choices=[("Column", "Kolumnowy"), ("Line", "Liniowy"),
                                      ("Surface", "Powierzchniowy")])
    submit = SubmitField('Wygeneruj wykres')

    # TODO: validators
