# -*- coding:utf-8 -*-

from flask import Blueprint, current_app

# 创建静态文件访问的蓝图
html = Blueprint('html', __name__)


# 定义静态文件访问的路由
@html.route('/<re(".*"):file_name>')
def get_html_file(file_name):

    if not file_name:
        file_name = 'index.html'

    # 当去加载网站的 logo 的时候,其文件是放在 static的目录下,直接子级
    if file_name != 'favicon.ico':
        # 拼接文件名
        file_name = 'html/' + file_name

    # 通过当前 app 去查找到静态文件夹的指定文件
    return current_app.send_static_file(file_name)