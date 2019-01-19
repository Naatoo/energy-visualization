from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from database import db
from login_manager import login_manager


class Energy(db.Model):
    building = db.Column(db.String, primary_key=True)
    year = db.Column(db.Integer, primary_key=True)
    month = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, unique=False)
    consumption_price = db.Column(db.Float, unique=False)
    transmission_price = db.Column(db.Float, unique=False)

    def __repr__(self):
        return '{} Energy {}.{} quantity={}'.format('School' if self.building == 'SCH' else 'Workshop',
                                                    self.year, self.month, self.quantity)


class Gas(db.Model):
    building = db.Column(db.String, primary_key=True)
    year = db.Column(db.Integer, primary_key=True)
    month = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, unique=False)
    price = db.Column(db.Float, unique=False)

    def __repr__(self):
        return '{} Gas {}.{} quantity={}'.format('School' if self.building == 'SCH' else 'Workshop',
                                                 self.year, self.month, self.quantity)


class User(UserMixin, db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(60), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute.')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User: {}>'.format(self.username)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
