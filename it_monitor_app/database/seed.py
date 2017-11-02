from it_monitor_app import db
from it_monitor_app.models import Service, software, software_user, user_license, wol_computer


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

def create_software():
    s = software("test software","#","#")
    s1 = software("second software","#","#")
    db.session.add(s)
    db.session.add(s1)
    db.session.commit()
    return s.id

def create_software_user():
    su = software_user("unknown")
    db.session.add(su)
    db.session.commit()
    return su.id

def create_licence(sid,uid):
    ul = user_license(uid,sid)
    db.session.add(ul)
    db.session.commit()
    return

def create_wol_computer():
    w = wol_computer("cenv0594","OUCE38-13")
    db.session.add(w)
    db.session.commit()
    return




def run_seed():

    print("Creating Services...")
    create_services()

    print("Creating software...")
    sid = create_software()
    uid = create_software_user()
    create_licence(sid,uid)

    print("creating wol")
    create_wol_computer()
