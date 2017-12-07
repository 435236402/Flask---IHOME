# -*- coding:utf-8 -*-

from werkzeug.routing import BaseConverter


# 定义正则的转换器
class RegexConverter(BaseConverter):

    def __init__(self, url_map, *args):
        super(RegexConverter, self).__init__(url_map)
        self.regex = args[0]