from it_monitor_app import db
from it_monitor_app.models import Service


def create_services():
    S1 = Service("Linux")
    S2 = Service("Gitlab")
    S3 = Service("SogE NextCloud",1)
    S4 = Service("DBAS",2)
    S5 = Service("OUCE Network")
    db.session.add(S1)
    db.session.add(S2)
    db.session.add(S3)
    db.session.add(S4)
    db.session.add(S5)
    db.session.commit()


def run_seed():

    print("Creating Services...")
    create_services()

