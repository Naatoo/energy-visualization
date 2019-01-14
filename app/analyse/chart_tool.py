import json
from collections import defaultdict
from bokeh.embed import components
from statistics import mean

from app.analyse.plots_generation.surface_chart import squares
from app.models import Energy, Gas
from app.tools.global_paths import MONTHS_NAMES_FILE, BUILDINGS_CODE_FILE
from app.analyse.plots_generation.column_line_chart import generate_stacked_chart
from collections import OrderedDict


class ChartTool:

    def __init__(self, building: str, interval: str, energy_type: str, chart_type: str):
        self.building = building
        self.interval = interval
        self.energy_type = energy_type
        self.chart_type = chart_type
        self.plot = self.handle_input()

    def get_data_surface(self):
        model = self.models_mapping(self.energy_type)

        prices = OrderedDict((self.months_names_mapping[str(month)], []) for month in reversed(range(1, 13)))
        prices['Year'] = ['2015', '2016', '2017', '2018']

        for row in model.query.filter_by(building=self.building).all():
            prices[self.months_names_mapping[str(row.month)]].append(row.consumption_price if row.consumption_price is not None else 0 +
                                                                                       (
                                                                                           row.transmission_price if row.transmission_price is not None else 0)
                      if energy_type == 'energy' else row.price)
        for k, quan in prices.items():
            if len(quan) != len(prices['Styczeń']):
                quan.append(0)
            prices[k] = [r for r in reversed(prices[k])]
        return prices

    def handle_input(self):
        if self.chart_type == 'Surface':
            if self.building == "All" and self.energy_type == "All":

                data = self.get_data_surface()
            else:
                data = self.get_data_surface()

            plot = squares(data)
        else:
            if self.energy_type != "All":
                if self.building != "All":
                    data = self.get_single_data()

                else:
                    data = self.get_all_building_types_data()
            else:
                if self.building != "All":
                    data = self.get_all_energy_types_data()
                else:
                    data = self.get_all_energy_types_all_building_types_data()
            plot = generate_stacked_chart(data, "Zużycie energii i gazu",
                                                chart_type=self.chart_type)
        return plot



    def get_single_data_surface(self):
        pass
    def get_all_building_types_data_surface(self):
        pass
    def get_all_energy_types_data_surface(self):
        pass
    def get_all_energy_types_all_building_types_data_surface(self):
        pass

    def get_single_data(self):
        filters = {'year': self.interval, 'building': self.building}
        months, data = self.query_data(filters=filters, energy_type=self.energy_type)
        return {
            'months': months,
            'data': data,
        }

    def get_all_building_types_data(self):
        school_data_months, school_data = self.query_data(filters={'year': self.interval, 'building': 'SCH'},
                                                          energy_type=self.energy_type)
        workshop_data_months, workshop_data = self.query_data(filters={'year': self.interval, 'building': 'WOR'},
                                                              energy_type=self.energy_type)
        self.assert_intervals_correct(school_data_months, workshop_data_months)
        return {
            'months': school_data_months,
            'school_data': school_data,
            'workshop_data': workshop_data
        }

    def get_all_energy_types_data(self, building: str=None):
        filters = {'year': self.interval, 'building': self.building if building is None else building}
        energy_data_months, energy_data = self.query_data(filters=filters, energy_type='energy')
        gas_data_months, gas_data = self.query_data(filters=filters, energy_type='gas')
        self.assert_intervals_correct(energy_data_months, gas_data_months)
        return {
            'months': energy_data_months,
            '{}energy_data'.format("" if building is None else building + "_"): energy_data,
            '{}gas_data'.format("" if building is None else building + "_"): gas_data
        }

    def get_all_energy_types_all_building_types_data(self):
        all_school_data = self.get_all_energy_types_data(building='SCH')
        all_workshop_data = self.get_all_energy_types_data(building='WOR')
        all_energy_types_all_building_types_data = {**all_school_data, **all_workshop_data}
        print(all_energy_types_all_building_types_data)
        return all_energy_types_all_building_types_data

    @staticmethod
    def assert_intervals_correct(first_interval: list, second_interval: list) -> None:
        assert first_interval == second_interval, '{} is not equal to {}'.format(first_interval, second_interval)

    def query_data(self, filters: dict, energy_type: str=None):
        model = self.models_mapping(energy_type)
        months, prices = [], []
        if self.interval in ["All", "Avarage"] and 'year' in filters.keys():
            del filters['year']
        if self.interval == 'Avarage':
            price_def = defaultdict(list)
            for row in model.query.filter_by(**filters).all():
                if self.months_names_mapping[str(row.month)] not in months:
                    months.append(self.months_names_mapping[str(row.month)])
                price_def[self.months_names_mapping[str(row.month)]].append((row.consumption_price if row.consumption_price is not None else 0 +
                        (row.transmission_price if row.transmission_price is not None else 0))
                        if energy_type == 'energy' else row.price)

            for month in months:
                prices.append(round(mean(price_def[month]), 1))
        else:
            for row in model.query.filter_by(**filters).all():
                months.append("{} {}".format(self.months_names_mapping[str(row.month)], str(row.year)))
                prices.append((row.consumption_price if row.consumption_price is not None else 0 +
                      ( row.transmission_price if row.transmission_price is not None else 0))
                      if energy_type == 'energy' else row.price)
        return months, prices

    @property
    def months_names_mapping(self):
        with open(MONTHS_NAMES_FILE) as f:
            return json.loads(f.read())

    def models_mapping(self, energy_type=None):
        mapping = {'energy': Energy, 'gas': Gas}
        return mapping[self.energy_type] if energy_type is None else mapping[energy_type]

    @property
    def script(self):
        return components(self.plot)[0]

    @property
    def div(self):
        return components(self.plot)[1]
