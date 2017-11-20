from it_monitor_app import app
from it_monitor_app.views import socketio


socketio.run(app,port=4001)
# app.run(debug=True,port=4001)
