import json
from collections import defaultdict, OrderedDict
from statistics import mean

from app.analyse.plots_generation.surface_chart import squares
from app.models import Energy, Gas
from app.tools.global_paths import MONTHS_NAMES_FILE
from app.analyse.plots_generation.column_line_chart import generate_stacked_chart
from app.tools.global_paths import TRANSLATIONS_FILE


class ChartTool:

    def __init__(self, building: str, interval: str, energy_type: str, chart_type: str):
        self.building = building
        self.interval = interval
        self.energy_type = energy_type
        self.chart_type = chart_type
        self.tra = self.get_translations()

        self.plot = self.handle_input()

        #TODO text in surface
        #TODO tooltips for columns

    def handle_input(self):
        if self.chart_type == 'Surface':
            data = self.get_data_surface()
            plot = squares(data)
        else:
            if self.energy_type != "All":
                if self.building != "All":
                    text, data = self.get_single_data()
                else:
                    text, data = self.get_all_building_types_data()
            else:
                if self.building != "All":
                    text, data = self.get_all_energy_types_data()
                else:
                    text, data = self.get_all_energy_types_all_building_types_data()
            plot = generate_stacked_chart(data, text,
                                          chart_type=self.chart_type)
        return plot

    def get_data_surface(self):
        data = OrderedDict((self.months_names_mapping[str(month)], []) for month in reversed(range(1, 13)))
        data['Year'] = ['2015', '2016', '2017', '2018']
        energy_types = [self.models_mapping(self.energy_type)] if self.energy_type != "All" else [Energy, Gas]
        buildings = [self.building] if self.building != "All" else ['SCH', 'WOR']

        for model in energy_types:
            for building in buildings:
                for row in model.query.filter_by(building=building).all():
                    if model == Energy:
                        price = row.consumption_price if row.consumption_price is not None else 0\
                            + row.transmission_price if row.transmission_price is not None else 0
                    else:
                        price = row.price
                    if len(data[self.months_names_mapping[str(row.month)]]) != 4:
                        data[self.months_names_mapping[str(row.month)]].append(price)
                    else:
                        data[self.months_names_mapping[str(row.month)]][data['Year'].index(str(row.year))] \
                            += price
        for k, quan in data.items():
            if len(quan) != len(data['Styczeń']):
                quan.append(0)
            data[k] = [r for r in reversed(data[k])]
        return data

    def get_data_column_line(self, filters: dict, energy_type: str = None):
        model = self.models_mapping(energy_type)
        months, prices = [], []
        if self.interval in ["All", "Avarage"] and 'year' in filters.keys():
            del filters['year']
        if self.interval == 'Avarage':
            price_def = defaultdict(list)
            for row in model.query.filter_by(**filters).all():
                if model == Energy:
                    price = row.consumption_price if row.consumption_price is not None else 0 + row.transmission_price \
                        if row.transmission_price is not None else 0
                else:
                    price = row.price
                if self.months_names_mapping[str(row.month)] not in months:
                    months.append(self.months_names_mapping[str(row.month)])
                price_def[self.months_names_mapping[str(row.month)]].append(price)
            for month in months:
                prices.append(round(mean(price_def[month]), 1))
        else:
            for row in model.query.filter_by(**filters).all():
                if model == Energy:
                    price = row.consumption_price if row.consumption_price is not None else 0 + row.transmission_price \
                        if row.transmission_price is not None else 0
                else:
                    price = row.price
                months.append("{} {}".format(self.months_names_mapping[str(row.month)], str(row.year)))
                prices.append(price)
        return months, prices

    def get_single_data(self):
        filters = {'year': self.interval, 'building': self.building}
        months, data = self.get_data_column_line(filters=filters, energy_type=self.energy_type)
        text = {
            "title": self.tra["title"]["single"].format(energy_type=self.tra["names_title"][self.energy_type],
                                                        building=self.tra["names_title"][self.building],
                                                        interval=self.interval),
            "tooltip": {

                "energy_type": {

                    "label": self.tra["tooltip_labels"][self.energy_type],
                    "value": self.tra["tooltip_values"][self.energy_type]
                },
                "building":
                    {
                        "label": self.tra["tooltip_labels"][self.building],
                        "value": self.tra["tooltip_values"][self.building]
                    }
            }

        }
        return text, {
            'months': months,
            'data': data,
        }

    def get_all_building_types_data(self):
        school_data_months, school_data = self.get_data_column_line(filters={'year': self.interval, 'building': 'SCH'},
                                                                    energy_type=self.energy_type)
        workshop_data_months, workshop_data = self.get_data_column_line(
            filters={'year': self.interval, 'building': 'WOR'},
            energy_type=self.energy_type)
        self.assert_intervals_correct(school_data_months, workshop_data_months)
        text = {
            "title": self.tra["title"]["both_buildings"].format(energy_type=self.tra["names_title"][self.energy_type],
                                                        building_1=self.tra["names_title"]["SCH"],
                                                        building_2=self.tra["names_title"]["WOR"],
                                                        interval=self.interval),
            "tooltip": {

                "energy_type": {

                    "label": '123',
                    "value": '123'
                },
                "building":
                    {
                        "label": '123',
                        "value": '123'
                    }
            },
            "legend": self.tra["legend"]["both_buildings"]


        }
        return text, {
            'months': school_data_months,
            'school_data': school_data,
            'workshop_data': workshop_data
        }

    def get_all_energy_types_data(self, building: str = None):
        if not building:
            building = self.building
        filters = {'year': self.interval, 'building': self.building if building is None else building}
        energy_data_months, energy_data = self.get_data_column_line(filters=filters, energy_type='energy')
        gas_data_months, gas_data = self.get_data_column_line(filters=filters, energy_type='gas')
        self.assert_intervals_correct(energy_data_months, gas_data_months)
        text = {
            "title": self.tra["title"]["both_mediums"].format(energy_type_1=self.tra["names_title"]["energy"],
                                                              energy_type_2=self.tra["names_title"]["gas"],
                                                        building=self.tra["names_title"][building],
                                                        interval=self.interval),
            "tooltip": {

                "energy_type": {

                    "label": '123',
                    "value": '123'
                },
                "building":
                    {
                        "label": '123',
                        "value": '123'
                    }

            },
            "legend": self.tra["legend"]["both_mediums"]
        }
        return text, {
            'months': energy_data_months,
            '{}energy_data'.format("" if building is None else building + "_"): energy_data,
            '{}gas_data'.format("" if building is None else building + "_"): gas_data
        }

    def get_all_energy_types_all_building_types_data(self):
        all_school_data = self.get_all_energy_types_data(building='SCH')[1]
        all_workshop_data = self.get_all_energy_types_data(building='WOR')[1]
        all_energy_types_all_building_types_data = {**all_school_data, **all_workshop_data}

        text = {
            "title": self.tra["title"]["both_mediums_and_buildings"].format(energy_type_1=self.tra["names_title"]["energy"],
                                                              energy_type_2=self.tra["names_title"]["gas"],
                                                                            building_1=self.tra["names_title"]["SCH"],
                                                                            building_2=self.tra["names_title"]["WOR"],
                                                        interval=self.interval),
            "tooltip": {

                "energy_type": {

                    "label": '123',
                    "value": '123'
                },
                "building":
                    {
                        "label": '123',
                        "value": '123'
                    }
            },
            "legend": self.tra["legend"]["both_mediums_and_buildings"]
        }
        return text, all_energy_types_all_building_types_data

    @staticmethod
    def assert_intervals_correct(first_interval: list, second_interval: list) -> None:
        assert first_interval == second_interval, '{} is not equal to {}'.format(first_interval, second_interval)

    @property
    def months_names_mapping(self):
        with open(MONTHS_NAMES_FILE) as f:
            return json.loads(f.read())

    def models_mapping(self, energy_type=None):
        mapping = {'energy': Energy, 'gas': Gas}
        return mapping[self.energy_type] if energy_type is None else mapping[energy_type]

    def get_translations(self):
        with open(TRANSLATIONS_FILE) as f:
            return json.loads(f.read())
