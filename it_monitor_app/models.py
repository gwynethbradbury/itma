# from . import db
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import dbconfig
import pymysql

import sqlalchemy as SqlAl


it_monitor_app_app = Flask(__name__)
it_monitor_app_app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://{}:{}@{}/{}'\
    .format(dbconfig.db_user,
            dbconfig.db_password,
            dbconfig.db_hostname,
            dbconfig.db_name)

it_monitor_app_app.secret_key = 'super secret key'
it_monitor_app_app.config['SESSION_TYPE'] = 'filesystem'

SQLALCHEMY_BINDS={'it_monitor_app':'mysql+pymysql://{}:{}@{}/{}'\
    .format(dbconfig.db_user,
            dbconfig.db_password,
            dbconfig.db_hostname,
            dbconfig.db_name)}
it_monitor_app_app.config['SQLALCHEMY_BINDS'] =SQLALCHEMY_BINDS

db = SQLAlchemy(it_monitor_app_app)






from enum import Enum
from time import strftime

from sqlalchemy.orm import relationship
import datetime
from subprocess import check_output, call
from dbconfig import debug as is_debug

class Status(Enum):
    DOWN = 1
    ISSUES = 2
    UP = 3

class Color(Enum):
    GREY = 1
    BLUE = 2
    GREEN = 3
    YELLOW = 4
    RED = 5





class Service(db.Model):
    __bind_key__ = 'it_monitor_app'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(70))
    status = db.Column(db.Integer,default=1) #1: down; 3: runnng; 2: running but some problem identified

    def __init__(self,name="no name",status=3):
        self.name=name
        self.status=status

    def status_style(self):
        if self.status==3:
            return 'btn-success'
        if self.status==1:
            return 'btn-danger'
        return 'btn-warning'

    def status_content(self):
        if self.status==3:
            return 'OK'
        if self.status==1:
            return 'Not OK'
        return 'Status Unknown'

class wol_computer(db.Model):
    __bind_key__ = 'it_monitor_app'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(8))
    computer = db.Column(db.String(20))

    def __init__(self,username="unknown",computer="unknown"):
        self.username=username
        self.computer=computer

    def get_status(self):
        return self.is_awake()

    def status_style(self):
        if self.get_status() == 3:
            return 'btn-success'
        if self.get_status() == 1:
            return 'btn-danger'
        return 'btn-warning'


    def wake_on_lan(self,uid):
        if uid == self.username:
            if is_debug:
                return 3,"debug version"

            call(["/usr/local/bin/wol_by_name", self.computer])

            r = self.is_awake()
            if r==1:
                return r, "{} is still asleep.".format(self.computer)
            elif r==3:
                return r, "{} is awake!".format(self.computer)
            else:
                return r, "Something went wrong.."



        return self.is_awake()


    def do_remotedesktop(self):
        pass

    def is_awake(self):
        if is_debug:
            return 3

        r = check_output(["/usr/local/bin/is_up", self.computer])
        rr = r.split('\n')
        if rr[0] == 'up':
            return 3
        elif rr[0] == 'down':
            return 1
        return 2

    def get_guac_id(self):
        if is_debug:
            return str(1)

        dbe = DBEngine(db='mysql+pymysql://{}:{}@{}/{}' \
                    .format(dbconfig.db_user,
                            dbconfig.db_password,
                            dbconfig.db_hostname,
                            'guac'))
        r = dbe.E.execute("SELECT connection_id from guacamole_connection where connection_name='{}';".format(self.computer))
        return str(r[0])

class DBEngine:
    E = SqlAl.null
    metadata = SqlAl.MetaData()
    db=""

    def __init__(self,db):
        self.metadata = SqlAl.MetaData()
        self.db=db
        self.E = SqlAl.create_engine(db)
        self.metadata.bind = self.E


class user_license(db.Model):
    __bind_key__ = 'it_monitor_app'
    id = db.Column(db.Integer, primary_key=True)
    software_user_id = db.Column(db.Integer, db.ForeignKey('software_user.id'))
    software_id = db.Column(db.Integer, db.ForeignKey('software.id'))

    def __init__(self,software_user_id,software_id):
        self.software_user_id = software_user_id
        self.software_id = software_id


class software(db.Model):
    __bind_key__ = 'it_monitor_app'
    id = db.Column(db.Integer, primary_key=True)
    software_name = db.Column(db.String(70))
    link=db.Column(db.String(100))
    downloadlink=db.Column(db.String(100))
    license=db.Column(db.Text())
    #admin
    license_expires=db.Column(db.Boolean,default=True)#is this a perpetual license
    license_expiry_date=db.Column(db.DateTime)# when does the software license expire
    license_renewal_date=db.Column(db.DateTime)# when does the software need to be renewed (sometimes before the exp date - this is for IT mgmt)
    owner=db.Column(db.String(100), default="IT")# who owns the license? group or school?
    count=db.Column(db.Integer,default=-1)#also determines type (site vs count)
    explicit_approval_required=db.Column(db.Boolean,default=True)#true - generate support request, false - generate download link on mirror.ouce


    users = relationship("software_user",
                    secondary=user_license.__table__,
                    backref="softwares")

    def __init__(self, sw_name,link="#",downloadlink="#", license="no license text",lexpires=True,
                 lexpiry=datetime.datetime.utcnow() + datetime.timedelta(days=(365)),
                 lrenew=datetime.datetime.utcnow() + datetime.timedelta(days=(365)),
                 owner="IT",count=-1,approve=False):
        self.software_name=sw_name
        self.link=link
        self.downloadlink=downloadlink
        self.license=license
        self.license_expires = lexpires
        self.license_expiry_date= lexpiry
        self.license_renewal_date = lrenew
        self.owner = owner
        self.count = count
        self.explicit_approval_required = approve

    def accepted_by_user(self,user):
        if user in self.users:
            return True
        return False

    def is_available(self):
        pass

    def licence_type(self):
        if self.count<0:
            return 'site license'
        else:
            return '{} licenses avilable for this software'.format(self.count)

    def __str__(self):
        return 'id: {},\n' \
               'software_name: {},\n' \
               'link: {},\n' \
               'downloadlink: {},\n' \
               'license: {},\n' \
               'ADMIN INFO:\n' \
               'license_expires: {},\n' \
               'license_expiry_date: {},\n' \
               'license_renewal_date: {},\n' \
               'owner: {},\n' \
               'count: {},\n' \
               'explicit_approval_required'.format(self.id ,self.software_name ,self.link,self.downloadlink,self.license,
                                                   self.license_expires,self.license_expiry_date,self.license_renewal_date,self.owner,self.count,self.explicit_approval_required)


class software_user(db.Model):
    __bind_key__ = 'it_monitor_app'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(8),unique=True)

    def __init__(self,username="unknown"):
        self.username = username



