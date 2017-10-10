from it_monitor_app import db
from enum import Enum
from time import strftime

from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property

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
            return 'Not Ok'
        return 'Status Unknown'

class wol_computer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(8))
    computer = db.Column(db.String(20))

    def __init__(self,username="unknown",computer="unknown"):
        self.username=username
        self.computer=computer

    def get_status(self):
        return 3

    def status_style(self):
        if self.get_status()==3:
            return 'btn-success'
        if self.get_status()==1:
            return 'btn-danger'
        return 'btn-warning'


    def wake_on_lan(self):
        pass

    def do_remotedesktop(self):
        pass

class user_license(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    software_user_id = db.Column(db.Integer, db.ForeignKey('software_user.id'))
    software_id = db.Column(db.Integer, db.ForeignKey('software.id'))

    def __init__(self,software_user_id,software_id):
        self.software_user_id = software_user_id
        self.software_id = software_id


class software(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    software_name = db.Column(db.String(70))
    link=db.Column(db.String(100))
    licenselink=db.Column(db.String(100))
    downloadlink=db.Column(db.String(100))
    license=db.Column(db.Text())

    users = relationship("software_user",
                    secondary=user_license.__table__,
                    backref="softwares")

    def __init__(self, sw_name,link="#",licenselink="#",downloadlink="#", license="no license text"):
        self.software_name=sw_name
        self.link=link
        self.licenselink=licenselink
        self.downloadlink=downloadlink
        self.license=license

    def accepted_by_user(self,user):
        if user in self.users:
            return True
        return False


class software_user(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(8),unique=True)

    def __init__(self,username="unknown"):
        self.username = username



