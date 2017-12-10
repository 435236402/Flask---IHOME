# -*- coding:utf-8 -*-
# 验证码：图片验证码，短信验证码

import re, random
from . import api
from flask import request, abort, current_app, jsonify, make_response, json
from iHome.utils.captcha.captcha import captcha
from iHome import redis_store
from iHome import constants
from iHome.utils.response_code import RET
from iHome.utils.sms import CCP
from iHome.models import User


@api.route('/sms', methods=['POST'])
def send_sms():
    """
    1. 获取参数并判断是否为空
    2. 判断手机号是否合法
    3. 取到redis中缓存的图片验证码内容
    4. 对比图片验证码内容，如果对比成功
    5. 发送短信验证码
    6. 给前端响应结果
    :return:
    """
    # 1. 获取参数并判断是否为空
    # data = request.data
    # data_dict = json.loads(data)
    data_dict = request.get_json()
    mobile = data_dict.get("mobile")
    image_code = data_dict.get("image_code")
    image_code_id = data_dict.get("image_code_id")

    if not all([mobile, image_code, image_code_id]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不全")

    # 2. 判断手机号是否合法
    if not re.match("^1[34578][0-9]{9}$", mobile):
        return jsonify(errno=RET.PARAMERR, errmsg="手机号格式不正确")

    # 3. 取到redis中缓存的图片验证码内容
    try:
        real_image_code = redis_store.get("ImageCode_"+image_code_id)
        # 3.1 删除redis中的图片验证码内容
        redis_store.delete("ImageCode_"+image_code_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="获取验证码内容失败")

    # 如果取出来的验证码是 None,那么代表验证码过期
    if not real_image_code:
        return jsonify(errno=RET.NODATA, errmsg='验证码过期')

    # 4. 对比图片验证码内容，如果对比成功
    if real_image_code.lower() != image_code.lower():
        return jsonify(errno=RET.DATAERR, errmsg="验证码不正确")

    # 判断当前手机号是否注册过,如果注册过,直接返回错误
    try:
        user = User.query.filter_by(mobile=mobile).first()
    except Exception as e:
        # 一旦进入 except 里面,如果没有定义 user的话,代表会往下执行
        # 往下执行的过程中会去判断 user 是否存在,如果存在,如果 user 没有定义,会抛出未定义异常
        user = None
        current_app.logger.error(e)
    if user:
        return jsonify(errno=RET.DATAEXIST,errmsg='当前手机号码已经注册')

    # 5. 发送短信验证码
    # 5.1 生成短信验证码内容
    result = random.randint(0, 999999)
    sms_code = "%06d" % result
    current_app.logger.debug("短信验证码内容是：%s" % sms_code)
    # 5.2 发送
    # result = CCP().send_template_sms(mobile, [sms_code, constants.SMS_CODE_REDIS_EXPIRES/60], "1")
    # if result == 0:
    #     return jsonify(errno=RET.THIRDERR, errmsg="发送短信验证码失败")

    # 6. 存储验证码内容以便后续校验
    try:
        redis_store.set("SMS_"+mobile, sms_code, constants.SMS_CODE_REDIS_EXPIRES)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="保存验证码失败")

    # 7. 发送成功
    return jsonify(errno=RET.OK, errmsg="发送成功")


@api.route("/imagecode")
def get_image_code():
    """
    1. 取到图片编码
    2. 生成图片验证码
    3. 存储到redis中(key是图片编码，值是验证码的文字内容)
    4. 返回图片
    :return:
    """
    # 1. 取到图片编码
    args = request.args
    cur = args.get("cur")
    pre = args.get("pre")

    # 如果用户没有传图片id的话，直接抛错
    if not cur:
        abort(403)

    # 2. 生成图片验证码
    _, text, image = captcha.generate_captcha()
    # 为了测试输入到控制台中
    current_app.logger.debug(text)

    # 3. 存储到redis中(key是图片编码，值是验证码的文字内容)
    try:
        if pre:
            redis_store.delete("ImageCode_"+pre)
        redis_store.set("ImageCode_"+cur, text, constants.IMAGE_CODE_REDIS_EXPIRES)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="保存图片验证码失败")

    # 4. 返回验证码图片
    respnose = make_response(image)
    # 设置contentType
    respnose.headers["Content-Type"] = "image/jpg"
    return respnose



