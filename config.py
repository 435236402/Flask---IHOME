# -*- coding:utf-8 -*-

import redis


class Config(object):
    '''项目的配置'''
    SECREK_KEY = "U1E69dSf+qPB7Rmr38uNVvI9S2gfEtbqeGnYT8UGo8N+CEy3x+0Olad0EJRpUaNt"

    # 数据库连接信息配置
    SQLALCHEMY_DATABASE_URI = 'mysql://root:mysql@172.16.160.130:3306/ihome'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # redis配置
    REDIS_HOST = '172.16.160.130'
    REDIS_PORT = 6379

    # Session 扩展的配置
    SESSION_TYPE = 'redis' # 存储类型
    SESSION_REDIS = redis.StrictRedis(host=REDIS_HOST,port=REDIS_PORT) # Redis 的连接
    SESSION_USE_SINGER = True # 是否签名
    PERMANENT_SESSION_LIFETIME = 86400 # 生命周期2


class DevelopementConfig(Config):
    """开发阶段所需要的配置"""
    # 开启调试模式
    DEBUG = True


class PruductionConfig(Config):
    """生产环境下所需要的配置"""
    pass

config = {
    'developement':DevelopementConfig,
    'production':PruductionConfig
}