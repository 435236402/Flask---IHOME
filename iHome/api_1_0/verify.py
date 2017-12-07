# -*- coding:utf-8 -*-

# 验证码:图片验证码,短信验证码

from . import api
from flask import request, abort, current_app, jsonify, make_response
from iHome.utils.captcha.captcha import captcha
from iHome import redis_store
from iHome import constants
from iHome.utils.response_code import RET


@api.route("/imagecode")
def get_image_code():
    # 1.取图片编码
    args = request.args
    cur = args.get('cur')
    pre = args.get('pre')

    # 如果用户没有传图片 id 的话,直接抛错
    if not cur:
        abort(403)

    # 2.生成图片验证码
    _, text, image = captcha.generate_captcha()

    # 为了测试输出到控制台中
    current_app.logger.debug(text)

    # 3.存储到 redis 中( key 是图片编码,值是验证码)
    try:
        if pre:
            redis_store.delete('ImageCode' + cur)
        redis_store.set('ImageCode' + cur, text, constants.IMAGE_CODE_REDIS_EXPIRES)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg='保存图片验证码失败')

    # 4.返回图片
    response = make_response(image)
    # 设置 contentType
    response.headers['Content-Type'] = 'image/jpg'
    return response
