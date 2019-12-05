from flask import jsonify

#成功
from wtforms import ValidationError

from app.api import api


def ok(message):
    response = jsonify({'error':'OK','message':message})
    response.status_code = 200
    return response

#已创建
def created(message):
    response = jsonify({'error':'Created','message':message})
    response.status_code = 201
    return response

#已接收
def accepted(message):
    response = jsonify({'error':'Accepted','message':message})
    response.status_code = 202
    return response

#没有内容，请求成功处理，但是返回的响应没有数据
def no_content(message):
    response = jsonify({'error':'No Content','message':message})
    response.status_code = 204
    return response

#坏请求，请求无效或不一致
def bad_request(message):
    response = jsonify({'error':'Bad Request','message':message})
    response.status_code = 400
    return response


#未授权，请求未包含身份验证信息，或者提供的凭据无效
def unauthorized(message):
    response = jsonify({'error':'Unauthorized','message':message})
    response.status_code = 401
    return response

#禁止，请求中发送的身份验证凭据无权访问目标
def forbidden(message):
    response = jsonify({'error':'forbidden','message':message})
    response.status_code = 403
    return response

#不允许使用的方法，指定资源不支持请求使用的方法
def method_not_allowed(message):
    response = jsonify({'error':'Method Not Allowed','message':message})
    response.status_code = 405
    return response

@api.errorhandler(ValidationError)
def validation_error(e):
    return bad_request(e.args[0])
