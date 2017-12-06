# -*- coding:utf-8 -*-
import logging
from . import api
from flask import session,current_app
from iHome import redis_store


@api.route('/index', methods=['GET', 'POST'])
def index():
    session['name'] = 'xiaohua'
    redis_store.set('name', 'xiaofang')
    logging.debug('DEBUG LOGLOG')
    print '=============='
    current_app.logger.debug('DEBUG LOGLOG CURRENT')
    return 'index'
