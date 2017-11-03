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

SQLALCHEMY_BINDS={}
SQLALCHEMY_BINDS['it_monitor_app']='mysql+pymysql://{}:{}@{}/{}'\
    .format(dbconfig.db_user,
            dbconfig.db_password,
            dbconfig.db_hostname,
            dbconfig.db_name)

SQLALCHEMY_BINDS['iaas']='mysql+pymysql://{}:{}@{}/{}'\
    .format(dbconfig.db_user,
            dbconfig.db_password,
            dbconfig.db_hostname,
            'iaas')
app.config['SQLALCHEMY_BINDS'] =SQLALCHEMY_BINDS

db = SQLAlchemy(app)


import views
import filters
import plugin_filters
import models
import logger


from it_monitor_app.plugins import load_plugins

load_plugins()


