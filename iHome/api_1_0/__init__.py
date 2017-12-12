# -*- coding:utf-8 -*-

from flask import Blueprint

# 初始蓝图
api = Blueprint('api_1_0', __name__)

from . import verify, passport, profile, house
