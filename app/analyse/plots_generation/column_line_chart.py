from bokeh.models import HoverTool
from bokeh.models import ColumnDataSource, FactorRange, Range1d, VBar, LinearAxis, Grid
from bokeh.plotting import figure
from bokeh.models import Legend, LegendItem


def generate_stacked_chart(data: dict, title: str, width=1200, height=800, chart_type: str = 'Column'):
    months = data['months']
    energy_types = [key for key in data.keys() if key != "months"]
    if len(energy_types) == 2:
        colors = ["red", "green"]
    elif len(energy_types) == 4:
        colors = ["orange", "red", "blue", "green"]
    else:
        colors = ['red']
    from bokeh.core.properties import value


    tools = ["pan", "wheel_zoom,save,reset"]

    plot = figure(title=title, x_range=months, plot_height=height, plot_width=width, h_symmetry=False,
                  v_symmetry=False,
                  min_border=0, toolbar_location="above", tools=tools, sizing_mode='scale_width',
                  outline_line_color="#666666", active_scroll='wheel_zoom', active_drag='pan')

    if chart_type == 'Column':
        source = ColumnDataSource(data)
        renderers = plot.vbar_stack(energy_types, x='months', width=0.8, color=colors, source=source,
                                    legend=[value(x) for x in energy_types])
        for r in renderers:
            year = r.name
            hover = HoverTool(tooltips=[
                ("Building: ", "%s " % year),
                ("Zużycie: ", "@%s{0.00} kWh" % year),
                ("Miesiąc: ", "@months")
            ], renderers=[r])
            plot.add_tools(hover)


    elif chart_type == 'Line':

        r = plot.multi_line([[month for month in months] for item in energy_types],
                            [data[type_energy] for type_energy in energy_types], color=colors, line_width=4)

        # r = plot.multi_line(xs='months', ys='school', source=source, line_color='color', line_width=4)


        legend = Legend(
            items=[LegendItem(label=item, renderers=[r], index=index) for index, item in enumerate(energy_types)])
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