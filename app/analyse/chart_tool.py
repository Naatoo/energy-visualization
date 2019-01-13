import json
from collections import defaultdict
from bokeh.embed import components
from bokeh.models import HoverTool
from bokeh.models import ColumnDataSource, FactorRange, Range1d, VBar, LinearAxis, Grid
from bokeh.plotting import figure
from statistics import mean

from app.models import Energy, Gas
from app.tools.global_paths import MONTHS_NAMES_FILE, BUILDINGS_CODE_FILE


class ChartTool:

    def __init__(self, building: str, year: str, energy_type: str, chart_type: str):
        self.building = building
        self.year = year
        self.energy_type = energy_type
        self.chart_type = chart_type
        self.plot = self.generate_chart()

    def prepare_data(self, energy_type: str = None, building: str = None) -> dict:
        if energy_type is None:
            energy_type = self.energy_type
        if building is None:
            building = self.building
        models_mapping = {'energy': Energy, 'gas': Gas}
        model = models_mapping[energy_type]
        months, quantity, price = [], [], []
        filters = {'year': self.year, 'building': building} if self.year not in ['All', 'Avarage'] \
            else {'building': building}
        if self.year != "Avarage":
            for row in model.query.filter_by(**filters).all():
                months.append("{} {}".format(self.months_names_mapping[str(row.month)], str(row.year)))
                quantity.append(row.quantity)
                price.append((row.consumption_price if row.consumption_price is not None else 0 +
                            (row.transmission_price if row.transmission_price is not None else 0))
                             if energy_type == 'energy' else row.price)
        else:
            quantity_def = defaultdict(list)
            price_def = defaultdict(list)
            for row in model.query.filter_by(**filters).all():
                if self.months_names_mapping[str(row.month)] not in months:
                    months.append(self.months_names_mapping[str(row.month)])
                quantity_def[self.months_names_mapping[str(row.month)]].append(row.quantity)
                price_def[self.months_names_mapping[str(row.month)]].append((row.consumption_price if row.consumption_price is not None else 0 +
                        (row.transmission_price if row.transmission_price is not None else 0))
                        if energy_type == 'energy' else row.price)

            for month in months:
                quantity.append(mean(quantity_def[month]))
                price.append(mean(price_def[month]))
        return {"month": months, "quantity": quantity, "price": price}

    def generate_chart(self):
        if self.chart_type == 'Surface':
            plot = self.get_data()
        else:
            if self.energy_type != "All":
                if self.building != "All":
                    data = self.prepare_data()
                    plot = self.create_bar_chart(data, "Zużycie energii", "month",
                                                 "price", create_hover_tool(chart_type='single'))
                else:
                    school_data = self.prepare_data(building='SCH')
                    workshop_data = self.prepare_data(building='WOR')
                    data = {
                        'months': school_data['month'],
                        'school': school_data['price'],
                        'workshop': workshop_data['price']
                    }
                    # TODO Add months validation: if gas and energy is the same

                    plot = self.generate_stacked_chart(data, "Zużycie energii i gazu",
                                                       create_hover_tool(chart_type='single'), chart_type=self.chart_type)
            else:
                if self.building != "All":
                    energy_data = self.prepare_data(energy_type='energy')
                    gas_data = self.prepare_data(energy_type='gas')
                    data = {
                        'months': energy_data['month'],
                        'energy': energy_data['price'],
                        'gas': gas_data['price']
                    }
                    # TODO Add months validation: if gas and energy is the same
                    plot = self.generate_stacked_chart(data, "Zużycie energii", create_hover_tool(chart_type='all'), chart_type=self.chart_type)
                else:
                    school_energy_data = self.prepare_data(building='SCH', energy_type='energy')
                    workshop_energy_data = self.prepare_data(building='WOR', energy_type='energy')
                    school_gas_data = self.prepare_data(building='SCH', energy_type='gas')
                    workshop_gas_data = self.prepare_data(building='WOR', energy_type='gas')

                    data = {
                        'months': school_energy_data['month'],
                        'School Energy': school_energy_data['price'],
                        'Workshop Energy': workshop_energy_data['price'],
                        'School Gas': school_gas_data['price'],
                        'Workshop Gas': workshop_gas_data['price'],
                    }
                    # TODO Add months validation: if gas and energy is the same
                    plot = self.generate_stacked_chart(data, "Zużycie energii i gazu",
                                                       create_hover_tool(chart_type='single'), chart_type=self.chart_type)

        return plot

    @staticmethod
    def generate_stacked_chart(data: dict, title: str, hover_tool=None, width=1200, height=800, chart_type: str='Column'):
        months = data['months']
        energy_types = [key for key in data.keys() if key != "months"]
        colors = ["red", "green"] if len(energy_types) == 2 else ["orange", "red", "blue", "green"]
        from bokeh.core.properties import value

        tools = []
        if hover_tool:
            tools = [hover_tool, "pan", "wheel_zoom,save,reset"]

        plot = figure(title=title, x_range=months, plot_height=height, plot_width=width, h_symmetry=False,
                      v_symmetry=False,
                      min_border=0, toolbar_location="above", tools=tools, sizing_mode='scale_width',
                      outline_line_color="#666666", active_scroll='wheel_zoom', active_drag='pan')

        if chart_type == 'Column':
            plot.vbar_stack(energy_types, x='months', width=0.8, color=colors, source=data,
                            legend=[value(x) for x in energy_types])

        elif chart_type == 'Line':
            r = plot.multi_line([[month for month in months] for item in energy_types],
                            [data[type_energy] for type_energy in energy_types],color=colors, line_width=4)

            from bokeh.models import Legend, LegendItem


            legend = Legend(items=[LegendItem(label=item, renderers=[r], index=index) for index, item in enumerate(energy_types)])
            plot.add_layout(legend)



        xaxis = LinearAxis()
        yaxis = LinearAxis()
        plot.add_layout(Grid(dimension=0, ticker=xaxis.ticker))
        plot.add_layout(Grid(dimension=1, ticker=yaxis.ticker))
        plot.toolbar.logo = None
        plot.min_border_top = 0
        plot.xgrid.grid_line_color = None
        plot.ygrid.grid_line_color = "#999999"
        plot.yaxis.axis_label = "Zużycie energii elektrycznej [kWh]"
        plot.ygrid.grid_line_alpha = 0.1
        plot.xaxis.axis_label = "Miesiąc"
        plot.xaxis.major_label_orientation = 1

        return plot

    @staticmethod
    def create_bar_chart(data, title, x_name, y_name, hover_tool=None,
                         width=1200, height=800):
        """Creates a bar chart plot with the exact styling for the centcom
           dashboard. Pass in data as a dictionary, desired plot title,
           name of x axis, y axis and the hover tool HTML.
        """
        source = ColumnDataSource(data)
        xdr = FactorRange(factors=data[x_name])
        ydr = Range1d(start=0, end=max(data[y_name]) * 1.5)

        tools = []
        if hover_tool:
            tools = [hover_tool, "pan", "wheel_zoom,save,reset"]

        plot = figure(title=title, x_range=xdr, y_range=ydr, plot_width=width,
                      plot_height=height, h_symmetry=False, v_symmetry=False,
                      min_border=0, toolbar_location="above", tools=tools, sizing_mode='scale_width',
                      outline_line_color="#666666", active_scroll='wheel_zoom', active_drag='pan')

        glyph = VBar(x=x_name, top=y_name, bottom=0, width=.8,
                     fill_color="red")
        plot.add_glyph(source, glyph)

        xaxis = LinearAxis()
        yaxis = LinearAxis()

        plot.add_layout(Grid(dimension=0, ticker=xaxis.ticker))
        plot.add_layout(Grid(dimension=1, ticker=yaxis.ticker))
        plot.toolbar.logo = None
        plot.min_border_top = 0
        plot.xgrid.grid_line_color = None
        plot.ygrid.grid_line_color = "#999999"
        plot.yaxis.axis_label = "Koszt energii elektrycznej [zł]"
        plot.ygrid.grid_line_alpha = 0.1
        plot.xaxis.axis_label = "Miesiąc"
        plot.xaxis.major_label_orientation = 1
        return plot

    # TODO TAB PANES!!!!!!!!!!!!!!!!!!!!!!!!

    @property
    def months_names_mapping(self):
        with open(MONTHS_NAMES_FILE) as f:
            return json.loads(f.read())

    @property
    def buildings_codes(self):
        with open(BUILDINGS_CODE_FILE) as f:
            return json.loads(f.read())

    def generate_components(self):
        # print(components(self.plot))
        return components(self.plot)


    def get_data(self, building_name: str='school'):
        names = {'school': Energy, 'workshop': Gas}
        building = names[building_name]
        with open(MONTHS_NAMES_FILE) as f:
            months_names_mapping = json.loads(f.read())

        year, month, quantity, price = [], [], [], []
        with open(BUILDINGS_CODE_FILE) as f:
            buildings_codes = json.loads(f.read())

        quantity = {str(month): [] for month in range(1, 13)}
        quantity['Year'] = ['2015', '2016', '2017']
        quantity['Annual'] = [1, 1, 1]

        for row in building.query.filter_by(building=buildings_codes[building_name]).order_by("month").all():
            quantity[str(row.month)].append(row.quantity)
        print(quantity)
        # hover = create_hover_tool(chart_type='single')
        # plot = create_bar_chart(data, "Zużycie energii", "month",
        #                         "quantity", hover)
        for quan in quantity.values():
            if len(quan) != len(quantity['1']):
                quan.append(0)
        plot = squares(quantity)
        return plot


from math import pi
import pandas as pd

from bokeh.models import LinearColorMapper, BasicTicker, PrintfTickFormatter, ColorBar
from bokeh.plotting import figure


def squares(quantity):
    # print(data)
    data = pd.DataFrame(quantity)
    # print(data)
    data['Year'] = data['Year'].astype(str)
    data = data.set_index('Year')
    data.drop('Annual', axis=1, inplace=True)
    data.columns.name = 'Month'

    years = list(data.index)
    months = list(data.columns)

    # reshape to 1D array or rates with a month and year for each row.
    df = pd.DataFrame(data.stack(), columns=['rate']).reset_index()

    # this is the colormap from the original NYTimes plot
    colors = ["#75968f", "#a5bab7", "#c9d9d3", "#e2e2e2", "#dfccce", "#ddb7b1", "#cc7878", "#933b41", "#550b1d"]
    mapper = LinearColorMapper(palette=colors, low=df.rate.min(), high=df.rate.max())

    TOOLS = "hover,save,pan,box_zoom,reset,wheel_zoom"

    p = figure(title="US Unemployment ({0} - {1})".format(years[0], years[-1]),
               y_range=years, x_range=list(reversed(months)),
               x_axis_location="above", plot_width=900, plot_height=400,
               tools=TOOLS, toolbar_location='below')
               # ('rate', '@rate%')])
    # tooltips = [('date', '@Month @Year'),
    p.grid.grid_line_color = None
    p.axis.axis_line_color = None
    p.axis.major_tick_line_color = None
    p.axis.major_label_text_font_size = "5pt"
    p.axis.major_label_standoff = 0
    p.xaxis.major_label_orientation = pi / 3

    p.rect(y="Year", x="Month", width=1, height=1,
           source=df,
           fill_color={'field': 'rate', 'transform': mapper},
           line_color=None)

    color_bar = ColorBar(color_mapper=mapper, major_label_text_font_size="5pt",
                         ticker=BasicTicker(desired_num_ticks=len(colors)),
                         formatter=PrintfTickFormatter(format="%d%%"),
                         label_standoff=6, border_line_color=None, location=(0, 0))
    p.add_layout(color_bar, 'right')

    return p


def create_hover_tool(chart_type: str):
    """Generates the HTML for the Bokeh's hover data tool on our graph."""
    hover_html_single = """
      <div>
        <span class="hover-tooltip">Miesiąc: @month </span>
      </div>
      <div>
        <span class="hover-tooltip">Zużycie: @quantity kWh</span>
      </div>
      <div>
        <span class="hover-tooltip">Koszt: @price{0.00} zł</span>
      </div>
    """
    hover_html_all = """
      <div>
        <span class="hover-tooltip">Koszt: @price{0.00} zł</span>
      </div>
    """
    return HoverTool(tooltips=hover_html_single if chart_type == "single" else hover_html_all)
