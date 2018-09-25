`{% if LDAPUser.uid_trim()=="soge" %} ` determines which features are shown on the ipads (soge user)

## Running

Before running, you must create the database. Run the `setup_db.py` script to create an initial database and some sample data.
```
python setup_db.py
```

The development server can be started by running the `runserver.py` scrip.
```
python runserver.py
```

And finally browse to http://localhost:1445
