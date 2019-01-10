from database import db


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
