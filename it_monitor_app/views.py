from flask import render_template, request, redirect, url_for, abort, jsonify, flash
from collections import defaultdict
from . import app, db
from models import Status, Color, Service, software, software_user, user_license, wol_computer
from signals import task_created, mission_created
import time
from it_monitor_app.auth.iaasldap import LDAPUser as LDAPUser

current_user = LDAPUser()

import imp

import dbconfig
if dbconfig.is_server_version:
    p='/var/www/html/dbas/main/iaas/iaas.py'
else:
    p = '/Users/cenv0594/Repositories/dbas-dev/main/iaas/iaas.py'
import sys

# the mock-0.3.1 dir contains testcase.py, testutils.py & mock.py
sys.path.append(p)
import imp
from datetime import datetime

iaas = imp.load_source('iaas', p)






@app.context_processor
def inject_paths():
    return dict(LDAPUser=LDAPUser())


@app.route('/')
def index():
    services = Service.query.order_by(Service.id.asc()).all()
    nowevents, futureevents, pastevents = getEvents()
    return render_template('home.html', services=services, pastevents=pastevents, nowevents=nowevents, futureevents=futureevents)


@app.route('/service_status')
def service_status():
    services = Service.query.order_by(Service.id.asc()).all()
    return render_template('service_status.html', services=services)


@app.route('/usage')
def usage():
    services = Service.query.order_by(Service.id.asc()).all()
    return render_template('usage.html', services=services)


@app.route('/wakeonlan', methods=['POST', 'GET'])
def wakeonlan():
    wol_computers=wol_computer.query.filter_by(username=current_user.uid_trim()).all()


    if request.method == 'POST':
        w = wol_computer.query.filter_by(id=request.args.get('computer_id')).first()
        if request.form.get('wake')=="Wake":
            r, msg = w.wake_on_lan(uid=current_user.uid_trim())
            time.sleep(5)
            if r==1:
                flash(msg,category="error")
            elif r==3:
                flash(msg,category="info")
            else:
                flash(msg,category="warning")

        elif request.form.get('wake') == "Remote Desktop":
            flash("no rdp method entered", category="message")
        else:
            flash("something went wrong",category="error")



    return render_template('wakeonlan.html',wol_computers=wol_computers)


@app.route('/changepasswd', methods=["GET", "POST"])
def changepasswd():
    import auth.iaasldap as auth
    auth.change_password(user=request.form.get('username'),
                           current_pass=request.form.get('current_pass'),
                           new_pass=request.form.get('new_pass'),
                           repeat_password=request.form.get('rep_pass'))
    #     from auth.forms import ChangePWForm
    #     form = ChangePWForm()
    #     if form.validate_on_submit():
    #         user = current_user
    #         # user = User(username=form.username.data,
    #         #             email=form.username.data,
    #         #             password=form.password.data)
    #         success, ret = current_user.change_password(form.oldpw, form.password, form.password2)
    #         if success:
    #             flash(ret, category='message')
    #         else:
    #             flash(ret, category="error")
    #
    #             # return redirect(url_for('index'))
    #
    #     try:
    #         return render_template("account.html", groups=groups, instances=instances, form=form)
    #     except TemplateNotFound:
    #         abort(404)
    #

    return render_template('changepasswd.html')


@app.route('/software', methods=['POST', 'GET'])
def softwares():
    # if the user has never used the service, then add them to the database
    if software_user.query.filter_by(username=current_user.uid_trim()).count==0:
        su = software_user(current_user.uid_trim())
        db.session.add(su)
        db.session.commit()
        flash("First time user added to database.", category="message")


    this_software_user = software_user.query.filter_by(username=current_user.uid_trim()).first()
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


@app.route('/request_software')
def request_software():
    sid = request.args.get('sid')
    sw = software.query.get_or_404(sid)
    if sw.explicit_approval_required:
        flash('Request made to OUCE IT from user {}'.format(current_user.uid_trim()))
        make_support_request_for_software(sid)
    else:
        if request.args.get('personal')=='True':
            flash('Download started')
            return redirect(sw.downloadlink)
        else:
            flash('Request made to OUCE IT from user {}'.format(current_user.uid_trim()))
            make_support_request_for_software(sid)

    return redirect('/software')


def make_support_request_for_software(sid):
    sw = software.query.get_or_404(sid)
    emailheader="Software installation request"
    emailbody="Software installation requested by {} for software {}".format(current_user.uid_trim().capitalize(),sw.software_name)
    if sw.explicit_approval_required:
        emailbody=emailbody + " Explicit approval is required for this software.\n"
    emailbody=emailbody + sw.__str__()

    return
    #todo: send the request


@app.route('/help')
def help():
    return redirect("https://it.ouce.ox.ac.uk")




def getEvents():
    events = iaas.IaasEvent.query.order_by(iaas.IaasEvent.eventdate.asc()).all()
    pastevents = []
    futureevents = []
    nowevents = []
    for e in events:
        if e.eventdate < datetime.now().date():
            pastevents.append(e)
        elif e.eventdate > datetime.now().date():
            futureevents.append(e)
        else:
            nowevents.append(e)

    return [ nowevents, futureevents, pastevents]

