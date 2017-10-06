from it_monitor_app import db
from enum import Enum
from time import strftime


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



