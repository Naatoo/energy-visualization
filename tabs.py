from flask import Blueprint
from bokeh.models import HoverTool, FactorRange, LinearAxis, Grid, Range1d
from bokeh.models.glyphs import VBar
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.models.sources import ColumnDataSource
from flask import render_template, request
from tables import SchoolEnergy, WorkshopEnergy
import json

bp = Blueprint('energy', __name__, url_prefix='/energy')


@bp.route('/gas')
def gas():
    pass


@bp.route('/energy', methods=['GET', 'POST'])
def energy():
    building_name = request.form.get('comp_select')
    year = request.form.get('year_select') if request.form.get('year_select') is not None else 2017

    if building_name is not None and year is not None:
        plot = get_data_to_chart(building_name, year)
    else:
        plot = get_data_to_chart('school', 2017)
        building_name = 'school'
    script, div = components(plot)
    return render_template("energy.html", year=year,
                               the_div=div, the_script=script, building='szkoła' if building_name =='school' else 'warsztat')


def get_data_to_chart(building_name: str, year: int):
    names = {'school': SchoolEnergy, 'workshop': WorkshopEnergy}
    building = names[building_name]
    with open('mapping/months_names.json') as f:
        months_names_mapping = json.loads(f.read())

    month, quantity, price = [], [], []
    for row in building.query.filter_by(year=year).all():
        month.append(months_names_mapping[str(row.month)])
        quantity.append(row.quantity)
        price.append((row.consumption_price if row.consumption_price is not None else 0 +
                        (row.transmission_price if row.transmission_price is not None else 0)))
    data = {"month": month, "quantity": quantity, "price": price}
    hover = create_hover_tool()
    plot = create_bar_chart(data, "Zużycie energii", "month",
                            "quantity", hover)
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
