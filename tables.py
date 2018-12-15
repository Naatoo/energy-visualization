from database import db


class SchoolEnergy(db.Model):

    year = db.Column(db.Integer, primary_key=True)
    month = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, nullable=True, unique=False)
    consumption_price = db.Column(db.Float, nullable=True, unique=False)
    transmission_price = db.Column(db.Float, nullable=True, unique=False)

    def __repr__(self):
        return 'SchoolEnergy {}.{} quantity={}'.format(self.year, self.month,  self.quantity)


class WorkshopEnergy(db.Model):

    year = db.Column(db.Integer, primary_key=True)
    month = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, nullable=True, unique=False)
    consumption_price = db.Column(db.Float, nullable=True, unique=False)
    transmission_price = db.Column(db.Float, nullable=True, unique=False)

    def __repr__(self):
        return 'WorkshopEnergy {}.{} quantity={}'.format(self.year, self.month,  self.quantity)
