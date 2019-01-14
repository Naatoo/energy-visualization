from math import pi

import pandas as pd
from bokeh.models import LinearColorMapper, ColorBar, BasicTicker
from bokeh.plotting import figure


def squares(quantity):
    data = pd.DataFrame(quantity)
    data['Year'] = data['Year'].astype(str)
    data = data.set_index('Year')
    data.columns.name = 'Month'

    years = list(data.index)
    months = list(data.columns)

    df = pd.DataFrame(data.stack(), columns=['rate']).reset_index()

    colors = ["#75968f", "#a5bab7", "#c9d9d3", "#e2e2e2", "#dfccce", "#ddb7b1", "#cc7878", "#933b41", "#550b1d"]
    mapper = LinearColorMapper(palette=colors, low=df.rate.min(), high=df.rate.max())

    TOOLS = "hover,save,pan,box_zoom,reset,wheel_zoom"

    p = figure(title="US Unemployment ({0} - {1})".format(years[0], years[-1]),
               y_range=years, x_range=list(reversed(months)),
               x_axis_location="above", plot_width=900, plot_height=400,
               tools=TOOLS, toolbar_location='below', tooltips=[('Miesiąc', '@Month @Year'), ('Koszt', '@rate{0.00} zł')])

    p.grid.grid_line_color = None
    p.axis.axis_line_color = None
    p.axis.major_tick_line_color = None
    # p.axis.major_label_text_font_size = "5pt"
    p.axis.major_label_standoff = 0
    p.xaxis.major_label_orientation = pi / 3

    p.rect(y="Year", x="Month", width=1, height=1,
           source=df,
           fill_color={'field': 'rate', 'transform': mapper},
           line_color=None)

    color_bar = ColorBar(color_mapper=mapper, title='Koszt [zł]',
                         # major_label_text_font_size="5pt",
                         ticker=BasicTicker(desired_num_ticks=len(colors)),
                         # formatter=PrintfTickFormatter(format="%d zł"),
                         label_standoff=12, border_line_color=None, location=(0, 0))
    p.add_layout(color_bar, 'right')

    return p