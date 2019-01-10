from flask import Blueprint
from bokeh.models import HoverTool, FactorRange, LinearAxis, Grid, Range1d
from bokeh.models.glyphs import VBar
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.models.sources import ColumnDataSource
from flask import render_template, request, redirect, url_for
from app.models import Energy
from app.tools.global_paths import MONTHS_NAMES_FILE, BUILDINGS_CODE_FILE
import json

bp = Blueprint('analyse', __name__, url_prefix='')


@bp.route('/gas')
def gas():
    return redirect(url_for('analyse.energy'))


@bp.route('/show', methods=['GET', 'POST'])
def energy():
    building_name = request.form.get('comp_select')
    year = request.form.get('year_select') if request.form.get('year_select') is not None else 2017

    if building_name is not None and year is not None:
        plot = get_data(building_name)
    else:
        plot = get_data('school')
        building_name = 'school'
    script, div = components(plot)
    return render_template("energy.html", year=year,
                           the_div=div, the_script=script,
                           building='szkoła' if building_name == 'school' else 'warsztat')


def get_data_to_chart(building_name: str, year: int):
    names = {'school': Energy, 'workshop': Energy}
    building = names[building_name]
    with open(MONTHS_NAMES_FILE) as f:
        months_names_mapping = json.loads(f.read())

    month, quantity, price = [], [], []
    with open(BUILDINGS_CODE_FILE) as f:
        buildings_codes = json.loads(f.read())
    for row in building.query.filter_by(year=year, building=buildings_codes[building_name]).all():
        month.append(months_names_mapping[str(row.month)])
        quantity.append(row.quantity)
        price.append((row.consumption_price if row.consumption_price is not None else 0 +
            (row.transmission_price if row.transmission_price is not None else 0)))
    data = {"month": month, "quantity": quantity, "price": price}
    hover = create_hover_tool()
    # plot = create_bar_chart(data, "Zużycie energii", "month",
    #                         "quantity", hover)
    plot = squares()
    return plot


def create_hover_tool():
    """Generates the HTML for the Bokeh's hover data tool on our graph."""
    hover_html = """
      <div>
        <span class="hover-tooltip">$x</span>
      </div>
      <div>
        <span class="hover-tooltip">Zużycie: @quantity kWh</span>
      </div>
      <div>
        <span class="hover-tooltip">Koszt: @price{0.00} zł</span>
      </div>
    """
    return HoverTool(tooltips=hover_html)


def create_bar_chart(data, title, x_name, y_name, hover_tool=None,
                     width=1200, height=600):
    """Creates a bar chart plot with the exact styling for the centcom
       dashboard. Pass in data as a dictionary, desired plot title,
       name of x axis, y axis and the hover tool HTML.
    """
    source = ColumnDataSource(data)
    xdr = FactorRange(factors=data[x_name])
    ydr = Range1d(start=0, end=max(data[y_name]) * 1.5)

    tools = []
    if hover_tool:
        tools = [hover_tool, ]

    plot = figure(title=title, x_range=xdr, y_range=ydr, plot_width=width,
                  plot_height=height, h_symmetry=False, v_symmetry=False,
                  min_border=0, toolbar_location="above", tools=tools,
                  responsive=True, outline_line_color="#666666")

    glyph = VBar(x=x_name, top=y_name, bottom=0, width=.8,
                 fill_color="#e12127")
    plot.add_glyph(source, glyph)

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


def get_data(building_name: str):
    names = {'school': Energy, 'workshop': Energy}
    building = names[building_name]
    with open(MONTHS_NAMES_FILE) as f:
        months_names_mapping = json.loads(f.read())

    year, month, quantity, price = [], [], [], []
    with open(BUILDINGS_CODE_FILE) as f:
        buildings_codes = json.loads(f.read())

    quantity = {str(month): [] for month in range(1, 13)}
    quantity['Year'] = ['2015', '2016', '2017']
    quantity['Annual'] = [1,1,1]

    for row in building.query.filter_by(building=buildings_codes[building_name]).order_by("month").all():
        quantity[str(row.month)].append(row.quantity)
    print(quantity)
    hover = create_hover_tool()
    # plot = create_bar_chart(data, "Zużycie energii", "month",
    #                         "quantity", hover)
    plot = squares(quantity)
    return plot


def squares(quantity):

    from math import pi
    import pandas as pd

    from bokeh.io import show
    from bokeh.models import LinearColorMapper, BasicTicker, PrintfTickFormatter, ColorBar
    from bokeh.plotting import figure


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

