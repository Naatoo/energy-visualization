import json

from bokeh.models import HoverTool
from bokeh.models import ColumnDataSource, LinearAxis, Grid
from bokeh.plotting import figure
from bokeh.models import Legend, LegendItem
from bokeh.core.properties import value

from app.tools.global_paths import TRANSLATIONS_FILE


def generate_stacked_chart(data: dict, text: dict, width=1200, height=800, chart_type: str = 'Column'):
    months = data['months']
    energy_types = [key for key in sorted(data.keys()) if key != "months"]
    if len(energy_types) == 2:
        colors = ["red", "green"]
    elif len(energy_types) == 4:
        colors = ["orange", "red", "blue", "green"]
    else:
        colors = ['red']

    tools = ["pan", "wheel_zoom,save,reset"]

    plot = figure(title=text['title'], x_range=months, plot_height=height, plot_width=width, h_symmetry=False,
                  v_symmetry=False,
                  min_border=0, toolbar_location="above", tools=tools, sizing_mode='scale_width',
                  outline_line_color="#666666", active_scroll='wheel_zoom', active_drag='pan')
    if chart_type == 'Column':
        source = ColumnDataSource(data)
        renderers = plot.vbar_stack(energy_types, x='months', width=0.8, color=colors, source=source,
                                    # legend=[value(x) for x in energy_types] if len(energy_types) != 1 else None)
                                    legend=[item for item in text['legend']] if text.get('legend') else None)

        for r in renderers:
            item = r.name
            hover = HoverTool(tooltips=[
                ("{}: ".format(text["tooltip"]["energy_type"]["label"]), text["tooltip"]["energy_type"]["value"]),
                ("{}: ".format(text["tooltip"]["building"]["label"]), text["tooltip"]["building"]["value"]),
                ("Koszt: ", "@%s{0.00} kWh" % item),
                ("Miesiąc: ", "@months") ], renderers=[r])
            plot.add_tools(hover)

    elif chart_type == 'Line':
        r = plot.multi_line([[month for month in months] for item in energy_types],
                            [data[type_energy] for type_energy in energy_types], color=colors, line_width=4)
        # r = plot.multi_line(xs='months', ys='school', source=source, line_color='color', line_width=4)

        # legend = Legend(
        #     items=[LegendItem(label=item, renderers=[r], index=index) for index, item in enumerate(energy_types)])
        if text.get('legend', None):
            legend = Legend(
                items=[LegendItem(label=item, renderers=[r], index=index) for index, item in enumerate(text['legend'])])

            plot.add_layout(legend)

    xaxis = LinearAxis()
    yaxis = LinearAxis()
    plot.add_layout(Grid(dimension=0, ticker=xaxis.ticker))
    plot.add_layout(Grid(dimension=1, ticker=yaxis.ticker))
    plot.toolbar.logo = None
    plot.min_border_top = 0
    plot.xgrid.grid_line_color = None
    plot.ygrid.grid_line_color = "#999999"
    plot.yaxis.axis_label = text['title']
    plot.ygrid.grid_line_alpha = 0.1
    plot.xaxis.axis_label = "Miesiąc"
    plot.xaxis.major_label_orientation = 1
    return plot


def get_translations():
    with open(TRANSLATIONS_FILE) as f:
        return json.loads(f.read())
