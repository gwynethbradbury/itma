




import sys
import os
from flask import Flask
from flask import render_template, redirect, url_for
from flask import request
import json
path=__file__[0:-9]
sys.path.insert(0,path)

from threading import Lock
from werkzeug.wsgi import pop_path_info, extract_path_info, peek_path_info
from main.sqla.app import create_app, get_user_for_prefix, get_current_schema_id
import dbconfig

from it_monitor_app import app as application

