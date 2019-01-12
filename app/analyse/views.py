from flask import request, render_template

from app.analyse import analyse
from app.analyse.forms import ChartForm
from app.analyse.chart_tool import ChartTool


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
    if form.validate_on_submit():
        year = form.year.data
        building = form.building.data
        energy_type = form.energy_type.data

    chart = ChartTool(building=building, year=year, energy_type=energy_type)
    script, div = chart.generate_components()

    return render_template("analyse.html", year=year,
                           the_div=div, the_script=script,
                           building='szkoła' if building == 'SCH'
                           else 'warsztat', form=form)
