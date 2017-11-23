from it_monitor_app import app
from it_monitor_app.views import socketio
import dbconfig

socketio.run(app,port=dbconfig.port)
# app.run(debug=True,port=4001)
