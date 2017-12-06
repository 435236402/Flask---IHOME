# -*- coding:utf-8 -*-

import redis
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_session import Session
from config import config

#  redis
redis_store = None

# 初始化SQLAlchemy
db = SQLAlchemy()

# 集成 CSRF 保护:提供了校验 cookie 中的 csrf 和表单中提交过的 csrf 的是否一样
csrf = CSRFProtect()

# 设置日志的记录等级
logging.basicConfig(level=logging.DEBUG)  # 调试debug级
# 创建日志记录器，指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上限
file_log_handler = RotatingFileHandler("logs/log", maxBytes=1024*1024*100, backupCount=10)
# 创建日志记录的格式                 日志等级    输入日志信息的文件名 行数    日志信息
formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
# 为刚创建的日志记录器设置日志记录格式
file_log_handler.setFormatter(formatter)
# 为全局的日志工具对象（flask app使用的）添加日志记录器
logging.getLogger().addHandler(file_log_handler)


def create_app(config_name):
    """工厂方法:根据传入的内容,生产指定内容所对应的对象"""

    app = Flask(__name__)
    # 从对象中加载配置
    app.config.from_object(config[config_name])

    # 关联当前 app
    db.init_app(app)
    # redis初始化
    global redis_store
    redis_store = redis.StrictRedis(host=config[config_name].REDIS_HOST,port=config[config_name].REDIS_PORT)
    # 关联当前 app
    csrf.init_app(app)
    # 集成session
    Session(app)

    from iHome.api_1_0 import api
    # 注册蓝图
    app.register_blueprint(api)
    return app
