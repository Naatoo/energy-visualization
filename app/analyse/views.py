from flask import request, render_template

from app.analyse import analyse
from app.analyse.forms import ChartForm
from app.analyse.chart_tool import ChartTool
from bokeh.embed import components


@analyse.route('/analyse', methods=['GET', 'POST'])
def show():
    """
     Handle requests to the /show route
     Displays chart based on form
    """

    form = ChartForm()
    building = 'SCH'
    year = 2017
    energy_type = 'energy'
    chart_type = 'Column'
    if form.validate_on_submit():
        year = form.year.data
        building = form.building.data
        energy_type = form.energy_type.data
        chart_type = form.chart_type.data

    chart = ChartTool(building=building, interval=year, energy_type=energy_type, chart_type=chart_type)
    script, div = components(chart.plot)

    return render_template("analyse.html",
                           the_div=div, the_script=script,
                           form=form)
