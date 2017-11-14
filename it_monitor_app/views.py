from flask import render_template, request, redirect, url_for, abort, jsonify, flash, session
from collections import defaultdict
from . import app, db
from models import Status, Color, Service, software, software_user, user_license, wol_computer
from signals import task_created, mission_created
import time
from it_monitor_app.auth.iaasldap import LDAPUser as LDAPUser

from threading import Lock
from flask_socketio import SocketIO, emit, join_room, leave_room, \
    close_room, rooms, disconnect
async_mode = None
import math

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

socketio = SocketIO(app)
thread = None
thread_lock = Lock()



# region 'my code'
@app.context_processor
def inject_paths():
    return dict(LDAPUser=LDAPUser(),debug=dbconfig.debug)


@app.route('/')
def index():
    services = Service.query.order_by(Service.id.asc()).all()
    nowevents, futureevents, pastevents = getEvents()
    return render_template('home.html', services=services, nowevents=nowevents, futureevents=futureevents, async_mode=socketio.async_mode)

@app.route('/events')
def events():
    nowevents, futureevents, pastevents = getEvents()
    return render_template('events.html', pastevents=pastevents, nowevents=nowevents, futureevents=futureevents)


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

# endregion


def background_thread():
    """Example of how to send server generated events to clients."""
    count = 0
    while True:
        socketio.sleep(5)
        count += 1
        graph_data = []
        for j in range(360):
            i=2*3.14159*j/360
            graph_data.append([j,math.sin(i),math.cos(i),max(min(math.tan(i),2),-2)])
        socketio.emit('my_response',
                      {'data': 'Server generated event '+str(datetime.utcnow()),
                       'count': count,
                       'graph_data': graph_data},
                      namespace='/systemusage')


# @app.route('/')
# def index():
#     return render_template('index.html', async_mode=socketio.async_mode)


@socketio.on('my_event', namespace='/systemusage')
def test_message(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': message['data'], 'count': session['receive_count']})


@socketio.on('my_broadcast_event', namespace='/systemusage')
def test_broadcast_message(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': message['data'], 'count': session['receive_count']},
         broadcast=True)


# @socketio.on('join', namespace='/systemusage')
# def join(message):
#     join_room(message['room'])
#     session['receive_count'] = session.get('receive_count', 0) + 1
#     emit('my_response',
#          {'data': 'In rooms: ' + ', '.join(rooms()),
#           'count': session['receive_count']})
#
#
# @socketio.on('leave', namespace='/systemusage')
# def leave(message):
#     leave_room(message['room'])
#     session['receive_count'] = session.get('receive_count', 0) + 1
#     emit('my_response',
#          {'data': 'In rooms: ' + ', '.join(rooms()),
#           'count': session['receive_count']})
#
#
# @socketio.on('close_room', namespace='/systemusage')
# def close(message):
#     session['receive_count'] = session.get('receive_count', 0) + 1
#     emit('my_response', {'data': 'Room ' + message['room'] + ' is closing.',
#                          'count': session['receive_count']},
#          room=message['room'])
#     close_room(message['room'])
#
#
# @socketio.on('my_room_event', namespace='/systemusage')
# def send_room_message(message):
#     session['receive_count'] = session.get('receive_count', 0) + 1
#     emit('my_response',
#          {'data': message['data'], 'count': session['receive_count']},
#          room=message['room'])
#
#
# @socketio.on('disconnect_request', namespace='/systemusage')
# def disconnect_request():
#     session['receive_count'] = session.get('receive_count', 0) + 1
#     emit('my_response',
#          {'data': 'Disconnected!', 'count': session['receive_count']})
#     disconnect()


@socketio.on('my_ping', namespace='/systemusage')
def ping_pong():
    emit('my_pong')


@socketio.on('connect', namespace='/systemusage')
def test_connect():
    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(target=background_thread)
    emit('my_response', {'data': 'Connected', 'count': 0})


@socketio.on('disconnect', namespace='/systemusage')
def test_disconnect():
    print('Client disconnected', request.sid)









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

