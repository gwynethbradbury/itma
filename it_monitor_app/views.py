from flask import render_template, request, redirect, url_for, abort, jsonify, flash, session, Response
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
from jinja2 import TemplateNotFound

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

socketio = SocketIO(app, async_mode='threading')
thread = None
thread_lock = Lock()



# region 'my code'
@app.context_processor
def inject_paths():
    if dbconfig.is_server_version:
        olp = '/online_learning/'
    else:
        olp = 'http://0.0.0.0:5000/'
    return dict(LDAPUser=LDAPUser(),debug=dbconfig.debug, online_learn_path=olp)


@app.route('/')
def index():
    services = Service.query.order_by(Service.id.asc()).all()
    nowevents, futureevents, pastevents = getEvents(5)
    news = getNews(5)
    return render_template('home.html', services=services, nowevents=nowevents, futureevents=futureevents,
                           news=news,
                           async_mode=socketio.async_mode)


@app.route('/<page>')
def show(page):
    try:
        return render_template("%s.html" % page)
    except TemplateNotFound:
        abort(404)


@app.route('/events')
def events():
    nowevents, futureevents, pastevents = getEvents()
    return render_template('events.html', pastevents=pastevents, nowevents=nowevents, futureevents=futureevents)

# @app.route('/events/<int:event_id>', methods=['POST', 'GET'])
# def event(event_id):
@app.route('/news/<int:news_id>', methods=['POST', 'GET'])
def news_item(news_id):
    news_item = iaas.News.query.get_or_404(news_id)

    if request.method == 'POST':
        try:
            pass
            # event.description = request.form.get('description')
            # event.venue_id = request.form.get('storyline_id')
            # event.date = request.form.get('nextdate')
            # event.startat = request.form.get('starttime')
            # event.endat = request.form.get('endtime')
            # if request.form.get('repeatsweekly') == "Yes":
            #     event.status = 2
            #     event.day = Day[request.form.get('day_id')].value
            # elif request.form.get('repeatreminder'):
            #     event.status = 3
            # else:
            #     event.status = 1
            #
            # for d in dances:
            #     if d.possibletags.count():
            #         for t in d.possibletags:
            #             x = (request.form.get(str(d.id) + '_' + str(t.id)) == str(t.id))
            #             y = (t in event.tags)
            #             if not x == y:
            #                 set_tag(event_id, t.id)
            #                 set_genre(event_id, t.dance.id)
            #     else:
            #         x = (request.form.get(str(d.id) + '_') == 'genre')
            #         y = (d in event.dances)
            #         if not x == y:
            #             set_genre(event_id, d.id)
            #
            # db.session.add(event)
            # db.session.commit()
        except KeyError:
            abort(400)

        flash("Saved", category='message')

    return render_template('news_item.html', news=news_item)

@app.route('/news')
def news():
    news = getNews()
    return render_template('news.html', news=news)


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
            time.sleep(15)
            if r==1:
                flash(msg,category="error")
            elif r==3:
                flash(msg,category="info")
            else:
                flash(msg,category="warning")

        elif request.form.get('wake') == "Remote Desktop (web)":
            id = get_guac_rdp_id(w.computer)
            return redirect(url('https://{}.ouce.ox.ac.uk/guacamole/#/client/c/{}'.format(dbconfig.hostpage,str(id))))

        elif request.form.get('wake') == "Remote Desktop (RDP app)":
            return create_download_rdp_file(w.computer)
        # else:
        #     flash("something went wrong",category="error")



    return render_template('wakeonlan.html',wol_computers=wol_computers)


def create_download_rdp_file(comp_address):
    content=("full address:s:{}.ouce.ox.ac.uk\n" 
                "username:s:ouce\{}\n" 
                "screen mode id:i:1\n" 
                "use multimon:i:0\n" 
                "desktopwidth:i:1368\n" 
                "desktopheight:i:768\n" 
                "session bpp:i:16\n" 
                "winposstr:s:0,3,932,283,2300,1011\n" 
                "compression:i:1\n" 
                "keyboardhook:i:2\n" 
                "audiocapturemode:i:0\n" 
                "videoplaybackmode:i:1\n" 
                "connection type:i:7\n" 
                "networkautodetect:i:1\n" 
                "bandwidthautodetect:i:1\n" 
                "displayconnectionbar:i:1\n" 
                "enableworkspacereconnect:i:0\n" 
                "disable wallpaper:i:0\n" 
                "allow font smoothing:i:0\n" 
                "allow desktop composition:i:0\n" 
                "disable full window drag:i:1\n" 
                "disable menu anims:i:1\n" 
                "disable themes:i:0\n" 
                "disable cursor setting:i:0\n" 
                "bitmapcachepersistenable:i:1\n" 
                "audiomode:i:0\n" 
                "redirectprinters:i:1\n" 
                "redirectcomports:i:0\n" 
                "redirectsmartcards:i:1\n" 
                "redirectclipboard:i:1\n" 
                "redirectposdevices:i:0\n" 
                "autoreconnection enabled:i:1\n" 
                "authentication level:i:2\n" 
                "prompt for credentials:i:0\n" 
                "negotiate security layer:i:1\n" 
                "remoteapplicationmode:i:0\n" 
                "alternate shell:s:\n" 
                "shell working directory:s:\n" 
                "gatewayhostname:s:\n" 
                "gatewayusagemethod:i:4\n" 
                "gatewaycredentialssource:i:4\n" 
                "gatewayprofileusagemethod:i:0\n" 
                "promptcredentialonce:i:0\n" 
                "gatewaybrokeringtype:i:0\n" 
                "use redirection server name:i:0\n" 
                "rdgiskdcproxy:i:0\n" 
                "kdcproxyname:s:\n" 
                "smart sizing:i:1".format(comp_address,current_user.uid_trim()))
    return Response(content,
                    mimetype="text/plain",
                    headers={"Content-Disposition":
                                 "attachment;filename={}.rdp".format(comp_address)})

@app.route('/changepasswd', methods=["GET", "POST"])
def changepasswd():
    if request.method=="POST":
        import auth.iaasldap as auth
        if current_user.uid_trim()=='soge':
            success, msg = auth.change_password(user=request.form.get('username'),
                                   current_pass=request.form.get('current_pass'),
                                   new_pass=request.form.get('new_pass'),
                                   repeat_password=request.form.get('rep_pass'),
                                 full=True)
        else:
            success, msg = auth.change_password(user=current_user.uid_trim(),
                                   current_pass=request.form.get('current_pass'),
                                   new_pass=request.form.get('new_pass'),
                                   repeat_password=request.form.get('rep_pass'),
                                 full=False)

        if success==1:
            flash(msg,'message')
        else:
            flash(msg,'error')

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

from datetime import datetime, timedelta, date
from json import dumps

def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError ("Type %s not serializable" % type(obj))

def background_thread():
    """Example of how to send server generated events to clients."""
    count = 0
    while True:
        socketio.sleep(5)
        count += 1
        t=datetime.utcnow()
        graph_data = []
        for j in range(60):
            i=j

            d=[int(time.mktime((t-timedelta(minutes=j)).timetuple())) * 1000]

            for n in range(10):
                d.append(math.sin(n*6+3*2*3.14159*(t-timedelta(minutes=j)).minute*6/360)+2)
            graph_data.append(d)
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


@socketio.on('join', namespace='/systemusage')
def join(message):
    join_room(message['room'])
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': 'In rooms: ' + ', '.join(rooms()),
          'count': session['receive_count']})


@socketio.on('leave', namespace='/systemusage')
def leave(message):
    leave_room(message['room'])
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': 'In rooms: ' + ', '.join(rooms()),
          'count': session['receive_count']})


@socketio.on('close_room', namespace='/systemusage')
def close(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response', {'data': 'Room ' + message['room'] + ' is closing.',
                         'count': session['receive_count']},
         room=message['room'])
    close_room(message['room'])


@socketio.on('my_room_event', namespace='/systemusage')
def send_room_message(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': message['data'], 'count': session['receive_count']},
         room=message['room'])


@socketio.on('disconnect_request', namespace='/systemusage')
def disconnect_request():
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': 'Disconnected!', 'count': session['receive_count']})
    disconnect()


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









def getEvents(lim=-1):
    if lim<0:
        events = iaas.IaasEvent.query.order_by(iaas.IaasEvent.eventdate.asc()).all()
    else:
        events = iaas.IaasEvent.query.order_by(iaas.IaasEvent.eventdate.asc()).limit(lim).all()

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


def getNews(lim=-1):
    if lim<0:
        news = iaas.News.query.order_by(iaas.News.updated_on.asc()).all()
    else:
        news = iaas.News.query.order_by(iaas.News.updated_on.asc()).limit(lim).all()
    return news

