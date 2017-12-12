# -*- coding:utf-8 -*-

from werkzeug.routing import BaseConverter
from flask import session, jsonify, g
from iHome.utils.response_code import RET
import functools


# 定义正则的转换器
class RegexConverter(BaseConverter):
    def __init__(self, url_map, *args):
        super(RegexConverter, self).__init__(url_map)
        self.regex = args[0]


def login_required(f):
    """判断用户是否登录"""

    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        user_id = session.get('user_id')
        if not user_id:
            # 直接返回没有登录的 json
            return jsonify(errno=RET.SESSIONERR, errmsg='用户未登录')
        else:
            g.user_id = user_id
            return f(*args, **kwargs)

    return wrapper
