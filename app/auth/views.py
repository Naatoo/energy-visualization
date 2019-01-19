from flask import flash, redirect, render_template, url_for
from flask_login import login_required, login_user, logout_user

from app.auth import auth
from app.auth.forms import LoginForm
# from app.auth.forms import RegistrationForm
from database import db
from ..models import User


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is not None and user.verify_password(
                form.password.data):
            login_user(user)
            return redirect(url_for('analyse.show'))
        else:
            flash('Invalid user or password.')
    return render_template('login.html', form=form, title='Login')


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Wylogowanie przebiegło poprawnie.')
    return redirect(url_for('auth.login'))


# @auth.route('/register', methods=['GET', 'POST'])
# def register():
#     form = RegistrationForm()
#     if form.validate_on_submit():
#         user = User(username=form.username.data,
#                         password=form.password.data)
#         db.session.add(user)
#         db.session.commit()
#         flash('You have successfully registered! You may now login.')
#         return redirect(url_for('auth.login'))
#
#     # load registration template
#     return render_template('register.html', form=form, title='Register')
