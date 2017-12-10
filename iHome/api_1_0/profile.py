# -*- coding:utf-8 -*-

from . import api
from flask import request, current_app, jsonify, session
from iHome import redis_store, db
from iHome.models import User
from iHome.utils.response_code import RET
from iHome.utils.storage_image import storage_image
from iHome.constants import QINIU_DOMIN_PREFIX


@api.route('/user/avatar', methods=['POST'])
def upload_avatar():
    """
    1. TODO 判断是否登录
    2.获取上传的文件内容
    3.上传到七牛
    4.返回上传成功的图片地址

    :return:
    """
    # 1.TODO 判断是否登录

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
