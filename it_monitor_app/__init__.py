from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import dbconfig

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://{}:{}@{}/{}'\
    .format(dbconfig.db_user,
            dbconfig.db_password,
            dbconfig.db_hostname,
            dbconfig.db_name)

app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'

db = SQLAlchemy(app)


import it_monitor_app.views
import it_monitor_app.filters
import it_monitor_app.plugin_filters
import it_monitor_app.models
import it_monitor_app.logger


from it_monitor_app.plugins import load_plugins

load_plugins()
