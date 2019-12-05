from flask import jsonify

from app.api import api
from app.models import User


#返回一个用户
@api.route('/users/<int:id>',methods = ['GET'])
def get_user(id):
    user = User.query.get_or_404(id)
    return jsonify(user.to_json())

#返回一个用户发布的所有博客文章
@api.route('/users/<int:id>/posts/',methods = ['GET'])
def get_user_posts(id):
    user= User.query.get_or_404(id)
    return jsonify({'users':[i.to_json() for i in user.post]})

#返回一个用户所关注用户发布的所有文章
@api.route('/users/<int:id>/timeline/',methods = ['GET'])
def get_user_timeline(id):
    user= User.query.get_or_404(id)
    return jsonify({'users':[i.to_json() for i in user.follow_posts]})

#返回用户关注的人
@api.route('users/<int:id>/is_fans/',methods = ["GET"])
def get_is_fans(id):
    user = User.query.get_or_404(id).is_fans.all()
    return jsonify({'is_fans':[i.to_json() for i in user]})


#查出关注了自己的用户
@api.route('users/<int:id>/is_blogers/',methods = ["GET"])
def get_is_blogers(id):
    user = User.query.get_or_404(id).is_blogers.all()
    return jsonify({'is_bloger': [i.to_json() for i in user]})
