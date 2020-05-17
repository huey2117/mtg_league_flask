from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from app import app, db_session


manager = Manager(app)
migrate = Migrate(app, db_session)

manager.add_commander('db_session', MigrateCommand)

if __name__ == '__main__':
    manager.run()
