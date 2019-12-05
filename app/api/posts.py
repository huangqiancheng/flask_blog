from flask import request, g, jsonify, url_for, current_app

from app import db
from app.api import api
from app.api.decorators import permission_required
from app.api.errors import forbidden
from app.models import Post, Permission, Comment


@api.route('/posts/',methods = ['POST'])
@permission_required(Permission.WRITE)
def new_post():
    post = Post.from_json(request.json)
    post.author_id = g.current_user.id
    db.session.add(post)
    db.session.commit()
    return jsonify(post.to_json()), 201,{'Location': url_for('api.get_post', id=post.id)}


#获取全部文章
@api.route('/posts/',methods = ["GET" ])
def get_posts():
    page = request.args.get('page',1,type = int)
    pagination = Post.query.paginate(page,per_page =current_app.config['FLASKY_POSTS_PER_PAGE'],error_out = False)
    posts = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_posts',page = page-1)
    next = None
    if pagination.has_next:
        next = url_for('api.get_posts',page = page + 1 )
    return jsonify({'posts': [post.to_json() for post in posts], 'prev_url': prev,
                    'next_url': next, 'count': pagination.total})
    # posts = Post.query.all()
    # return jsonify({ 'posts':[post.to_json() for post in posts]})

#返回一篇博客文章
@api.route('/posts/<int:id>',methods = ["GET" ])
def get_post(id):
    post = Post.query.get_or_404(id)
    return jsonify(post.to_json())

#返回一篇博客文章的评论
@api.route('/posts/<int:id>/comments/',methods = ["GET"])
def get_post_comments(id):
    comments = Post.query.get_or_404(id).comment
    return jsonify({'comment':[i.to_json() for i in comments]})


#在文章中添加一条新的评论
@api.route('/posts/<int:id>/comments/',methods = ["POST"])
@permission_required(Permission.WRITE)
def new_comment(id):
    comment = Comment.from_json(request.json)
    comment.post_id = id
    comment.author_id = g.current_user.id
    db.session.add(comment)
    db.session.commit()
    return jsonify(comment.to_json())



#修改一篇博客文章
@api.route('/posts/<int:id>/' , methods = ["PUT"])
@permission_required(Permission.WRITE)
def edit_post(id):
    post = Post.query.get_or_404(id)
    if g.current_user.id != post.author_id and not g.current_user.can(Permission.ADMIN):
        return forbidden("权限不足！！")
    post.body = request.json.get("body",post.body)
    db.session.add(post)
    db.session.commit()
    return jsonify(post.to_json())
