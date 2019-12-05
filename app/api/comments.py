from flask import jsonify

from app.api import api
from app.models import Comment


#返回所有评论
@api.route('/comments/',methods =["GET"])
def get_comments():
    comment = Comment.query.all()
    return jsonify({'commens':[i.to_json() for i in comment]})


#返回一条评论
@api.route('/comments/<int:id>/',methods =["GET"])
def get_comment(id):
    comment = Comment.query.get_or_404(id)
    return jsonify(comment.to_json())