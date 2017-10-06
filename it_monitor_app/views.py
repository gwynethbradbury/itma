from flask import render_template, request, redirect, url_for, abort, jsonify, flash
from collections import defaultdict
from it_monitor_app import app, db
from it_monitor_app.models import Status, Color, Service
from it_monitor_app.signals import task_created, mission_created


@app.route('/')
def index():
    services = Service.query.order_by(Service.id.asc()).all()
    return render_template('home.html', services=services)

@app.route('/service_status')
def service_status():
    services = Service.query.order_by(Service.id.asc()).all()
    return render_template('service_status.html', services=services)

@app.route('/useage')
def useage():
    services = Service.query.order_by(Service.id.asc()).all()
    return render_template('useage.html', services=services)

