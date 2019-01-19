from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired

from ..models import User


class LoginForm(FlaskForm):

    username = StringField('Nazwa użytkownika', validators=[DataRequired()])
    password = PasswordField('Hasło', validators=[DataRequired()])
    submit = SubmitField('Login')


# class RegistrationForm(FlaskForm):
#     username = StringField('Username', validators=[DataRequired()])
#     password = PasswordField('Password', validators=[
#                                         DataRequired(),
#                                         EqualTo('confirm_password')
#                                         ])
#     confirm_password = PasswordField('Confirm Password')
#     submit = SubmitField('Register')
#     def validate_username(self, field):
#         if User.query.filter_by(username=field.data).first():
#             raise ValidationError('Username is already in use.')