# -*- coding:utf-8 -*-

# 实现登录注册的功能
from . import api
from flask import request,  current_app, jsonify,session
from iHome.models import User
from iHome import redis_store,db

from iHome.utils.response_code import RET


@api.route('/session',methods=['POST'])
def login():
    # 1.获取参数
    data_dict = request.json
    mobile = data_dict.get('mobile')
    password = data_dict.get('password')

    if not all([mobile,password]):
        return jsonify(errno=RET.PARAMERR,errmsg='数据不完整')

    # 2.找到对应的手机号码的用户
    try:
        user = User.query.filter_by(mobile=mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg='查询数据错误')

    if not user:
        return jsonify(errno=RET.DATAEXIST,errmsg='用户未注册')

    # 3.校验密码
    if not user.check_password(password):
        return jsonify(errno=RET.PWDERR,errmsg='用户名或密码错误')

    # 4.保存登录状态并返回结果
    session['name'] = user.name
    session['mobile'] = user.mobile
    session['user_id'] = user.id

    # 5.返回结果
    return jsonify(errno=RET.OK,errmsg='登录成功')


@api.route('/users',methods=['POST'])
def register():
    """
    1.获取参数并判断是否为空
    2.取到本地的验证码
    3.将本地验证码和传入的短信进行对比
    4.创建用户模型,并设置数据,并添加到数据库
    5.返回结果
    :return:
    """
    # 1. 获取参数并判断是否有值
    data_dict = request.json
    mobile = data_dict.get('mobile')
    phonecode = data_dict.get('phonecode')
    password = data_dict.get('password')

    if not all([mobile,phonecode,password]):
        return jsonify(errno=RET.PARAMERR,errmsg='参数不全')

    # 2.取到本地的验证码
    try:
        sms_code = redis_store.get('SMS_'+mobile)
        redis_store.delete('SMS_'+mobile)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg='本地验证码获取失败')

    if not sms_code:
        return jsonify(errno=RET.NODATA,errmsg='验证码过期')

    # 3.将本地验证码传入的短信验证码进行对比
    if phonecode != sms_code:
        return jsonify(errno=RET.DATAERR,errmsg='验证码错误')

    # 4.创建用户模型,并设置数据,并添加到数据库中
    user = User()
    # 设置数据
    user.name = mobile
    user.mobile = mobile
    user.password = password
    # 保存用户数据
    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg='保存数据失败')

    # 保存登录状态
    session['name'] = mobile
    session['mobile'] = mobile
    session['password'] = password

    # 5.返回结果
    return jsonify(errno=RET.OK,errmsg='注册成功')
