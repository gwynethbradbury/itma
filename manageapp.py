from it_monitor_app import app
from it_monitor_app.models import db

from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand

# ALEMBIC
migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command('db', MigrateCommand)
if __name__ == '__main__':
    manager.run()


# initialise:
# python manage.py db init

# migrate/update:
# python manage.py db migrate

# apply update:
# python manage.py db upgrade
