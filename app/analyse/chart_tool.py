import json
from bokeh.embed import components
from bokeh.models import HoverTool
from bokeh.models import ColumnDataSource, FactorRange, Range1d, VBar, LinearAxis, Grid
from bokeh.plotting import figure

from app.models import Energy, Gas
from app.tools.global_paths import MONTHS_NAMES_FILE, BUILDINGS_CODE_FILE


class ChartTool:

    def __init__(self, building: str, year: str, energy_type: str):
        self.building = building
        self.year = year
        self.energy_type = energy_type
        self.plot = self.generate_chart()

    def prepare_data(self, energy_type: str = None, building: str = None) -> dict:
        if energy_type is None:
            energy_type = self.energy_type
        if building is None:
            building = self.building
        models_mapping = {'energy': Energy, 'gas': Gas}
        model = models_mapping[energy_type]
        month, quantity, price = [], [], []
        filters = {'year': self.year, 'building': building} if self.year != 'All' \
            else {'building': building}
        for row in model.query.filter_by(**filters).all():
            month.append("{} {}".format(self.months_names_mapping[str(row.month)], str(row.year)))
            quantity.append(row.quantity)
            price.append((row.consumption_price if row.consumption_price is not None else 0 +
                        (row.transmission_price if row.transmission_price is not None else 0))
                         if energy_type == 'energy' else row.price)
        return {"month": month, "quantity": quantity, "price": price}

    def generate_chart(self):
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
                                                   create_hover_tool(chart_type='single'))
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
                plot = self.generate_stacked_chart(data, "Zużycie energii", create_hover_tool(chart_type='all'))
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
                                                   create_hover_tool(chart_type='single'))

        return plot

    @staticmethod
    def generate_stacked_chart(data, title, hover_tool=None, width=1200, height=800):
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

        plot.vbar_stack(energy_types, x='months', width=0.8, color=colors, source=data,
                        legend=[value(x) for x in energy_types])

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


def get_data(building_name: str):
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
    hover = create_hover_tool_single()
    # plot = create_bar_chart(data, "Zużycie energii", "month",
    #                         "quantity", hover)
    plot = squares(quantity)
    return plot


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
