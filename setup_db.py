import it_monitor_app
from it_monitor_app.database.seed import run_seed
from it_monitor_app.models import db
from it_monitor_app.models import Service, software, software_user, software_key, user_license, wol_computer

if __name__ == '__main__':
    db.drop_all()
    db.create_all()
    run_seed()

# SQL:
# create database taskmanagement;

# Python:
# python setup_db.py

# SQL:
# use taskmanagement
# insert into tag (name,color) values ('DBAS',3);
# insert into tag (name,color) values ('Online Learning',2);