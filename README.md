`{% if LDAPUser.uid_trim()=="soge" %} ` determines which features are shown on the ipads (soge user)

## Running (esp locally)

Before running, you must create the database. Run the `setup_db.py` script to create an initial database and some sample data.
```
python setup_db.py
```

The development server can be started by running the `runserver.py` scrip.
```
python runserver.py
```

And finally browse to http://localhost:1445



# Pages

Most vews are documented in views.py

## Home page

This is set up to display different content on the ipad and desktop versions simply based on whether the user is signed in as 'soge' which is only true for the ipad. 
The ipad version has two differences: 
1. The change password button appears very visibly on the home page
2. This version of the web app automatically redirects to its home page every 30 seconds if there is no activity

The home page is set to show upcoming events before news stories is any are listed in the database. See the documentation in the code for details.

## Service status page

https://it.ouce.ox.ac.uk/service_status

The underlying python code simply pings the noted servers and displays whether they are online. For external networking, it pings google 8.8.8.8.

## Change password

Works without difficulty for external and internal users

## WOL

Does not seem to work although there is no notable change to the code. It is important to note that the database should be kept up to date on db.ouce.ox.ac.uk:

https://db.ouce.ox.ac.uk/projects/it_apps/databases/it_monitor_app/it_monitor_app_Wol%20Computer/