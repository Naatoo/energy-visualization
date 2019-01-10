import json

from app.models import Energy, Gas
from app.tools.global_paths import MONTHS_NAMES_FILE, BUILDINGS_NAMES_POLISH_FILE


def get_data(type_choice):
    with open(MONTHS_NAMES_FILE) as f:
        months_names_mapping = json.loads(f.read())

    with open(BUILDINGS_NAMES_POLISH_FILE) as f:
        buildings_names = json.loads(f.read())

    if type_choice == 'energy':
        rows = Energy.query.order_by(Energy.year.desc(), Energy.month.desc()).limit(10).all()
        data = [[row.year, months_names_mapping[str(row.month)], buildings_names[row.building],
                 row.quantity, row.consumption_price, row.transmission_price] for row in rows]
    elif type_choice == 'gas':
        rows = Gas.query.order_by(Gas.year.desc(), Gas.month.desc()).limit(10).all()
        data = [[row.year, months_names_mapping[str(row.month)], buildings_names[row.building],
                 row.quantity, row.price] for row in rows]
    return data
