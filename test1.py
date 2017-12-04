# -*- coding:utf-8 -*-
import redis
from flask import Flask,session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_session import Session
from flask_script import Manager
from flask_migrate import Migrate,MigrateCommand


class Config(object):
    '''项目的配置'''
    SECREK_KEY = "U1E69dSf+qPB7Rmr38uNVvI9S2gfEtbqeGnYT8UGo8N+CEy3x+0Olad0EJRpUaNt"

    # 开启调试模式
    DEBUG = True

    # 数据库连接信息配置
    SQLALCHEMY_DATABASE_URI = 'mysql://root:mysql@172.16.160.128:3306/ihome'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # redis配置
    REDIS_HOST = '172.16.160.128'
    REDIS_PORT = 6379

    # Session 扩展的配置
    SESSION_TYPE = 'redis' # 存储类型
    SESSION_REDIS = redis.StrictRedis(host=REDIS_HOST,port=REDIS_PORT) # Redis 的连接
    SESSION_USE_SINGER = True # 是否签名
    PERMANENT_SESSION_LIFETIME = 86400 # 生命周期




app = Flask(__name__)
# 从对象中加载配置
app.config.from_object(Config)

# 初始化 SQLAlchemy
db = SQLAlchemy(app)

# 初始化 redis
redis_store = redis.StrictRedis(host=Config.REDIS_HOST,port=Config.REDIS_PORT)

# 集成 CSRF 保护:提供了校验 cookie 中的 csrf 和表单中提交过的 csrf 的是否一样
csrf = CSRFProtect(app)

# 集成session
Session(app)

manager = Manager(app)
# 集成数据库迁移
Migrate(app,db)
manager.add_command('db',MigrateCommand)


@app.route('/index',methods=['GET','POST'])
def index():
    session['name'] = 'xiaohua'
    redis_store.set('name','xiaofang')
    return 'index'


if __name__ == '__main__':
    app.run()