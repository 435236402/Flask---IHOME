# -*- coding:utf-8 -*-

from flask import request,g,jsonify,current_app
from iHome.models import Area,Facility,User,House
from . import api
from iHome.utils.response_code import RET
from iHome import redis_store,db
from iHome.constants import AREA_INFO_REDIS_EXPIRES
from iHome.utils.common import login_required


@api.route('/house',methods=['POST'])
@login_required
def save_new_house():
    """
    1.获取上传的参数
    2.判断是否为空,校验参数
    3.初始化一个 House 的对象
    4.进行数据保存
    5.返回结果
    :return:

    前端发送过来的json数据
    {
        "title":"",
        "price":"",
        "area_id":"1",
        "address":"",
        "room_count":"",
        "acreage":"",
        "unit":"",
        "capacity":"",
        "beds":"3",
        "deposit":"",
        "min_days":"",
        "max_days":"",
        "facility":["7","8"]
    }"""

    #1. 获取上传的参数
    user_id = g.user_id
    json_dict = request.json
    title = json_dict.get('title')
    price = json_dict.get('price')
    area_id = json_dict.get('area_id')
    address = json_dict.get('address')
    room_count = json_dict.get('room_count')
    acreage = json_dict.get('acreage')
    unit = json_dict.get('unit')
    capacity = json_dict.get('capacity')
    beds = json_dict.get('beds')
    deposit = json_dict.get('deposit')
    min_days = json_dict.get('min_days')
    max_days = json_dict.get('max_days')

    # 2.判断是否为空.校验参数
    if not all(
            [title, price, address, area_id, room_count, acreage, unit, capacity, beds, deposit, min_days, max_days]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数缺失')

    try:
        price = int(float(price)*100)
        deposit = int(float(deposit)*100)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg='参数缺失')

    # 3.初始化 house 对象
    house = House()

    house.user_id = user_id
    house.area_id = area_id
    house.title = title
    house.price = price
    house.address = address
    house.room_count = room_count
    house.acreage = acreage
    house.unit = unit
    house.capacity = capacity
    house.beds = beds
    house.deposit = deposit
    house.min_days = min_days
    house.max_days = max_days

    # 设置房屋设施
    facilities = json_dict.get('facility')
    if facilities:
        # 查询指定列表中对应的模型并设置设施信息
        house.facilities = Facility.query.filter(Facility.id.in_(facilities)).all()

    # 4.进行数据保存
    try:
        db.session.add(house)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='添加数据失败')

    return jsonify(errno=RET.OK, errmsg='ok',data={'house_id':house.id})


@api.route('/areas')
def get_areas():
    """获取城区信息"""

    # 先从 Redis 中获取
    try:
        areas_array = redis_store.get('areas')
        if areas_array:
            return jsonify(errno=RET.OK,errmsg='OK',data={'areas':eval(areas_array)})
    except Exception as e:
        current_app.logger.error(e)

    # 1. 获取所有的城区信息
    areas = Area.query.all()

    # 2.因为 areas 是一个对象的列表,不能直接返回,需要将其转化成字典的列表
    areas_array = []
    for area in areas:
        areas_array.append(area.to_dict())

    # 3. 将数据缓存到 redis中
    try:
        redis_store.set('areas',areas_array,AREA_INFO_REDIS_EXPIRES)
    except Exception as e:
        current_app.logger.error(e)

    # 数据返回
    return jsonify(errno=RET.OK,errmsg='OK',data={'areas':areas_array})