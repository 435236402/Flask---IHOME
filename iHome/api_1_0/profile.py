# -*- coding:utf-8 -*-

from . import api
from flask import request, current_app, jsonify, session,g
from iHome import redis_store, db
from iHome.models import User
from iHome.utils.response_code import RET
from iHome.utils.storage_image import storage_image
from iHome.constants import QINIU_DOMIN_PREFIX
from iHome.utils.common import login_required


@api.route('/user/auth', methods=['POST'])
@login_required
def set_user_auth():
    """保存用户的实名认证信息"""

    # 1.去除参数并判空
    data_dict = request.json
    real_name = data_dict.get('real_name')
    id_card = data_dict.get('id_card')

    if not all([real_name, id_card]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数错误')

    # 2.取到当前登录用户,并设置数据
    user_id = g.user_id
    try:
        user = User.query.get(user_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询用户失败')

    if not user:
        return jsonify(errno=RET.USERERR, errmsg='用户不存在')

    # 3.保存用户的认证信息
    user.real_name = real_name
    user.id_card = id_card
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg='保存数据失败')

    return jsonify(errno=RET.OK, errmsg='保存认证信息成功')


@api.route('/user/auth')
@login_required
def get_user_auth():
    """获取用户的实名认证信息"""
    user_id = g.user_id

    try:
        user = User.query.get(user_id)
    except Exception as e:
        current_app.logger.errno(e)
        return jsonify(errno=RET.DBERR, errmsg='查询用户失败')

    if not user:
        return jsonify(errno=RET.USERERR, errmsg='用户不存在')

    return jsonify(errno=RET.OK, errmsg='ok',data=user.to_auth_dict())


@api.route('/user')
@login_required
def get_user_info():
    """
    1. 判断是否登录并且获取达到当前登录用户的 id
    2. 查询数据
    3. 将用户模型指定的数据进行指定格式的返回
    :return:
    """

    user_id = g.user_id

    # 2.查询数据
    try:
        user = User.query.get(user_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询数据出错')

    if not user:
        return jsonify(errno=RET.USERERR,errmsg='用户不存在')

    # 返回数据
    return jsonify(errno=RET.OK, errmsg='OK', data=user.to_dict())


@api.route('/user/name',methods=['POST'])
@login_required
def set_user_name():
    """
    1.TODO 判断是否登录
    2.获取到传入的名字参数,并判空
    3.取到当前登录用户的 id 并查询出对应的模型
    4.更新模型
    5.返回结果
    :return:
    """

    # 1.判断是否登录

    # 2.获取到传入的名字参数,并判空
    data_dict = request.json

    name = data_dict.get('name')
    if not name:
        return jsonify(errno=RET.PARAMERR,errmsg='参数不全')

    # 3.取到当前登录用户的 id 并查询出对应的模型
    user_id = g.user_id
    try:
        user = User.query.get(user_id)
    except Exception as e:
        return jsonify(errno=RET.DBERR,errmsg='查询数据失败')

    if not user:
        return jsonify(errno=RET.USERERR, errmsg='用户不存在')

    # 4. 更新模型
    try:
        user.name = name
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='保存用户名失败')

    # 5.返回结果
    return jsonify(errno=RET.OK, errmsg='修改成功')


@api.route('/user/avatar', methods=['POST'])
@login_required
def upload_avatar():
    """
    1. TODO 判断是否登录
    2.获取上传的文件内容
    3.上传到七牛
    4.返回上传成功的图片地址

    :return:
    """
    # 1.判断是否登录

    # 2.获取上传的文件内容
    try:
        avatar_file = request.files.get('avatar').read()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg='请选择图片')

    # 3.上传到七牛云
    try:
        key = storage_image(avatar_file)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg='上传到七牛云失败')

    # 4.取到用户的 User模型,将上传成功的头像的地址保存到模型中并更新到数据库
    try:
        user = User.query.get(session['user_id'])
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询当前登录用户失败')

    if not user:
        return jsonify(errno=RET.USERERR, errmsg='用户不存在')

    user.avatar_url = key
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg='保存用户头像失败')

    # 5.返回上传成功的图片地址
    return jsonify(errno=RET.OK, errmsg='上传成功', data={'avatar_url': QINIU_DOMIN_PREFIX + key})
