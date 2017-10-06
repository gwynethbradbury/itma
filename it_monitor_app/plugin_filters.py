from flask import Markup
from it_monitor_app import app
from it_monitor_app.plugins import dispatch


@app.template_filter('html_dispatch')
def html_dispatch(mission, function):
    values = dispatch(function, mission)
    return Markup(''.join(values))
