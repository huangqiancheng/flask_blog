from flask import g, jsonify
from flask_httpauth import HTTPBasicAuth

from app.api import api
from app.api.errors import unauthorized, forbidden

from app.models import User

auth = HTTPBasicAuth()

@auth.verify_password
def verify_password(email_or_token,password):
    if email_or_token == '':
        return False
    if password == '':
        g.current_user = User.verify_auth_token(email_or_token)
        g.token_used = True
        return g.current_user is not None
    user = User.query.filter_by(email=email_or_token).first()
    if not user:
        return False
    g.current_user = user
    #密码验证通过返回true
    g.token_used = False
    return user.verify_password(password)

@auth.error_handler
def auth_error():
    return unauthorized("用户未认证！！")

@api.before_request
@auth.login_required
def before_request():
    if not g.current_user.is_anonymous and not g.current_user.confirmed:
        return forbidden('未认证或激活的账号')

#生成一个验证的token令牌的json数据
@api.route('/tokens/',methods = ["POST"])
def get_token():
    if g.current_user.is_anonymous or g.token_used:
        return unauthorized('无效的用户')
    #返回一个json类型的数据包含token和token过期时间
    return jsonify({'token': g.current_user.genrate_auth_token(expiration=3600), 'expiration': 3600})