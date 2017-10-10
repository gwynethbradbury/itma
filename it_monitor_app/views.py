from flask import render_template, request, redirect, url_for, abort, jsonify, flash
from collections import defaultdict
from it_monitor_app import app, db
from it_monitor_app.models import Status, Color, Service, software, software_user, user_license, wol_computer
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






software_user_id="unknown"
@app.route('/wakeonlan', methods=['POST', 'GET'])
def wakeonlan():
    wol_computers=wol_computer.query.filter_by(username=software_user_id).all()
    if request.method == 'POST':
        if request.form.get('wake')=="Wake":
            flash("no wake method entered", category="message")
        elif request.form.get('wake')=="Remote Desktop":
            flash("no rdp method entered", category="message")
        else:
            flash("something went wrong",category="error")



    return render_template('wakeonlan.html',wol_computers=wol_computers)

@app.route('/changepasswd')
def changepasswd():
    return render_template('changepasswd.html')

@app.route('/software', methods=['POST', 'GET'])
def softwares():
    # if the user has never used the service, then add them to the database
    if software_user.query.filter_by(username=software_user_id).count==0:
        su = software_user(software_user_id)
        db.session.add(su)
        db.session.commit()
        flash("First time user added to database.", category="message")


    this_software_user = software_user.query.filter_by(username=software_user_id).first()
    softwares = software.query.order_by(software.software_name.asc()).all()

    if request.method == 'POST':
        sid = request.args.get("sid")

        if request.form.get('license_agreement')=="Accept Licence":
            this_license_count = user_license.query.filter_by(software_user_id=this_software_user.id, software_id=sid).count()

            if this_license_count>0:
                flash("License previously accepted",category='warning')
            else:
                ul = user_license(this_software_user.id,sid)
                db.session.add(ul)
                db.session.commit()

                flash("License accepted",category='message')
        else:
            flash("License not accepted",category='error')



    return render_template('software.html',all_software=softwares, this_software_user=this_software_user)



@app.route('/help')
def help():
    return redirect("https://it.ouce.ox.ac.uk")