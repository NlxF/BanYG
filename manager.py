#!/Users/ism/projects/bwg360/envmacos/bin/python
from flask_script import Manager
from bwg360 import create_app
from bwg360.commands import InitDbCommand, MyMigrateCommand

"""
    只用于命令行
"""

app = create_app(db_command=True)
manager = Manager(app)

manager.add_command('db', MyMigrateCommand)   # MigrateCommand)
manager.add_command('create_db', InitDbCommand)


if __name__ == '__main__':
    manager.run()
    print("server stop...")
