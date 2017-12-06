# -*- coding:utf-8 -*-

from flask_script import Manager
from flask_migrate import Migrate,MigrateCommand
from iHome import create_app

# 通过传入不同的配置名字,去创建不同配置的 APP
app = create_app('developement')
from iHome import db
manager = Manager(app)
# 集成数据库迁移
Migrate(app, db)
manager.add_command('db', MigrateCommand)


if __name__ == '__main__':
    # app.run()
    manager.run()