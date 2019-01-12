from flask_wtf import FlaskForm
from wtforms import SubmitField, SelectField
from wtforms.validators import DataRequired


class ChartForm(FlaskForm):
    """
    Form for users to add new energy bill
    """
    year = SelectField('Year', validators=[DataRequired()], choices=[("2015", "2015"), ("2016", "2016"),
                                                                     ("2017", "2017"), ("2018", "2018"),
                                                                     ("2019", "2019"), ("All", "All")])
    building = SelectField('Building', validators=[DataRequired()], choices=[("SCH", "School"), ("WOR", "Workshop"),
                                                                             ("All", "All")])
    energy_type = SelectField('Energy type', validators=[DataRequired()], choices=[("energy", "energy"), ("gas", "gas"),
                                                                                   ("All", "All")])
    submit = SubmitField('Show')

    # TODO: validators
