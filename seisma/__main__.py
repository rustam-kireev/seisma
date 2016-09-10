# -*- coding: utf-8 -*-

from flask_script import Manager
from flask_migrate import Migrate
from flask_migrate import MigrateCommand

from seisma import wsgi
from seisma import constants
from seisma.database.alchemy import alchemy


manager = Manager(wsgi.app)
migrate = Migrate(wsgi.app, alchemy, directory=constants.MIGRATE_DIR)


manager.add_command('db', MigrateCommand)


if __name__ == '__main__':
    manager.run()
