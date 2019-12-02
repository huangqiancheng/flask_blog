import os
import uuid

from datetime import datetime
from flask import flash, session, url_for, render_template, request, send_from_directory, current_app, make_response
from flask_login import login_required, current_user, logout_user, login_user
from werkzeug.utils import secure_filename, redirect

from app import db, config
from app.auth import auth
from app.auth.email import sender_email
from app.auth.forms import UploadForm, RegisterForm, LoginForm, EditProfileForm, EditProfilenameAdminForm, PostForm, \
    CommentForm
from app.decorators import permission_required
from app.models import User, Permission, Post, Comment


@auth.app_context_processor
def inject_permissions():
    return dict(Permission=Permission)


# 首页
@auth.route("/", methods=['GET', 'POST'])
def index():
    form = PostForm()
    user =  current_user._get_current_object()
    body = form.body.data
    show_followed=False
    if current_user.is_authenticated:
        show_followed =  bool(request.cookies.get('show_followed',''))
    if show_followed:
        query = user.follow_posts
    else:
        query=Post.query
    page = request.args.get('page', 1, type=int)
    pagination = query.order_by(Post.created.desc()).paginate(page,per_page=10,error_out = False)
    if form.validate_on_submit():
        a=Post(body = body,author_id=user.id)
        db.session.add(a)
        try:
            db.session.commit()
            flash("成功！")
            return redirect(url_for('auth.index'))
        except Exception :
            db.session.rollback()
            flash("失败！")
            return render_template('auth/index.html', form=form)
    return render_template('auth/index.html',form=form,user=current_user,pagination=pagination,show_followed=show_followed)


# 登录
@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            next = request.args.get('next')
            if next is None or not next.startswith('/'):
                next = url_for('auth.index')
            return redirect(next)
        flash("邮箱名或密码错误！！")
    return render_template('auth/login.html', form=form)


# 注销
@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('您已成功注销在本网站的登录。')
    return redirect(url_for('auth.index'))


# 注册
@auth.route("/register", methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        useranme = form.username.data
        email = form.email.data
        user = User(username=useranme, email=email, password=form.password.data)
        db.session.add(user)
        try:
            db.session.commit()
            token = user.generate_confirmation_token(expiration=3600)
            sender_email(email, '激活账号！', 'auth/email/confirm', user=useranme, token=token)
            flash("已发送一封邮件到你的邮箱")
        except:
            db.session.rollback()
            flash("注册失败！")
            return render_template("auth/register.html", form=form)
        return redirect(url_for("auth.index"))
    return render_template("auth/register.html", form=form)


@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for("auth.index"))
    if current_user.confirm(token):
        db.session.commit()
        flash("您已成功激活账户！")
    else:
        flash("激活连接无效或令牌过期")
    return redirect(url_for("auth.index"))

#生成随机文件名
def random_filename(filename):
    ext = os.path.splitext(filename)[1]
    new_filename = uuid.uuid4().hex + ext
    return new_filename

# 上传（测试）
@auth.route("/upload", methods=['GET', 'POST'])
@login_required
def upload():
    form = UploadForm()
    if form.validate_on_submit():
        f = form.img.data
        filename = random_filename(f.filename)
        #当前文件夹的上上层目录
        basepath = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        # 图片上传的绝对路径
        upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'],current_app.config['UPLOAD_HEAD'], secure_filename(filename))
        print(upload_path)
        current_user.avatar_url=current_app.config['UPLOAD_HEAD'] + '/' + filename
        db.session.add(current_user)
        db.session.commit()
        f.save(upload_path)
        flash('上传成功！')
        return redirect(url_for("auth.index"))
    return render_template("auth/upload.html", form=form)


#配合model中的get_upload_file（）获取完整链接
@auth.route('/upload_file_dir/<path:filename>',methods = ["GET" , 'POST'])
def upload_file(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'],filename)


#个人信息展示
@auth.route('/aboutme/<int:id>',methods = ["GET"])
def aboutme(id):
    user = User.query.filter_by(id=id).first_or_404()
    login_user = current_user._get_current_object()
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.order_by(Post.created.desc()).paginate(page, per_page=10, error_out=False)
    return render_template("auth/about_me.html" ,user=user,login_user = login_user,current_time=datetime.utcnow(),form=PostForm(),post=Post.query.all(),pagination=pagination)


# 用户修改资料
@auth.route('/edit-profile',methods = ["GET" , 'POST'])
@login_required
def edit_profile():
    user = current_user._get_current_object()
    form =  EditProfileForm(data=user.__dict__)
    if form.validate_on_submit():
        f = form.img.data
        filename = random_filename(f.filename)
        user.name = form.name.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], current_app.config['UPLOAD_HEAD'],
                                   secure_filename(filename))
        if not f:
            user.avatar_url = user.avatar_url
        else:
            user.avatar_url = current_app.config['UPLOAD_HEAD'] + '/' + filename
        f.save(upload_path)
        db.session.add(user)
        try:
            db.session.commit()
            flash("信息修改成功！")
            return redirect(url_for('auth.aboutme'))
        except Exception:
            db.session.rollback()
            flash("信息修改失败！")
            return render_template('auth/edit_profile.html',form=form)
    return render_template('auth/edit_profile.html', form=form)


#管理员修改资料
@auth.route('/edit-profile/<int:user_id>',methods = ["GET" , 'POST'])
@login_required
def edit_profile_admin(user_id):
    user = User.query.filter_by(id=user_id).first()
    form = EditProfilenameAdminForm(obj=user)
    if form.validate_on_submit():
        f = form.img.data
        filename = random_filename(f.filename)
        user.name = form.name.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        user.email = form.email.data
        user.confirmed = form.state.data
        user.role_id = form.role.data
        user.username = form.username.data
        upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], current_app.config['UPLOAD_HEAD'],
                                   secure_filename(filename))
        if not f:
            user.avatar_url = user.avatar_url
        else:
            user.avatar_url = current_app.config['UPLOAD_HEAD'] + '/' + filename
        f.save(upload_path)
        db.session.add(user)
        try:
            db.session.commit()
            flash("信息修改成功！")
            return redirect(url_for('auth.aboutme'))
        except Exception:
            db.session.rollback()
            flash("信息修改失败！")
            return render_template('auth/edit_profile_admin.html', form=form)
    return render_template('auth/edit_profile_admin.html', form=form,user=user)

@auth.route('/edit/<int:id>',methods = ['GET','POST'])
def edit(id):
    form_data = Post.query.filter_by(id=id).first()
    form =  PostForm(obj=form_data)
    body = form.body.data
    if form.validate_on_submit():
        form_data.body = body
        db.session.add(form_data)
        try:
            db.session.commit()
            flash("修改成功！")
            return redirect(url_for("auth.index"))
        except:
            db.session.rollback()
            flash("修改文章失败！")
            return redirect(url_for("auth.index"))
    return render_template('auth/edit_post.html',form = form)

#查看粉丝
@auth.route('/fans_amount/<int:id>',methods = ['GET'])
def fans_amount(id):
    user =  User.query.filter_by(id=id).first()
    a= user.is_blogers.all()
    return render_template("auth/fans_amount.html" ,user = a,username=user)


#查看关注数
@auth.route('/bloger/<int:id>',methods = ['GET'])
def bloger(id):
    user =  User.query.filter_by(id=id).first()
    a= user.is_fans.all()
    return render_template("auth/bloger_amount.html" ,user = a,username=user)

@auth.route('/followed')
@login_required
def show_followed():
    resp = make_response(redirect(url_for('auth.index')))
    resp.set_cookie('show_followed', '1', max_age=30 * 24 * 60 * 60)
    return resp

@auth.route('/all')
@login_required
def show_all():
    resp = make_response(redirect(url_for('auth.index')))
    resp.set_cookie('show_followed', '', max_age=30 * 24 * 60 * 60)
    return resp


@auth.route('/cancel_or_attention/<int:id>',methods = ["GET","POST"])
@login_required
def cancel_or_attention(id):
    user = User.query.filter_by(id=id).first()
    login_user = current_user._get_current_object()
    login_user.follow(user)
    return redirect(url_for('auth.aboutme',id=id))

@auth.route('/cancel_the_attention/<int:id>',methods = ["GET","POST"])
@login_required
def cancel_the_attention(id):
    user = User.query.filter_by(id=id).first()
    login_user = current_user._get_current_object()
    login_user.unfollow(user)
    return redirect(url_for('auth.aboutme',id=id))

@auth.route('/comment/<int:id>',methods = ["GET" , 'POST'])
def comment(id):
    post = Post.query.filter_by(id=id).first()
    user = User.query.filter_by(id=post.author_id).first()
    form =CommentForm()
    page = request.args.get('page', 1, type=int)
    pagination = Comment.query.filter_by(post_id=id).order_by(Comment.timestamp.desc()).paginate(page, per_page=10, error_out=False)
    if form.validate_on_submit():
        body = form.body.data
        comment = Comment(body=body,author_id=user.id,post_id=post.id)
        db.session.add(comment)
        try:
            db.session.commit()
            flash("评论成功！！")
            return redirect(url_for('auth.comment',id=id))
        except:
            db.session.rollback()
            flash("评论失败！！")
            return redirect(url_for('auth.comment', id=id))
    return render_template('auth/comment.html',user=user,post=post,form=form,pagination=pagination)

@auth.route('/banned/<int:id>',methods = ["GET" , 'POST'])
def banned(id):
    comment = Comment.query.filter_by(id=id).first()
    comment.ban = True
    db.session.add(comment)
    try:
        db.session.commit()
        flash("禁言成功！")
    except:
        db.session.rollback()
        flash("禁言失败！")
        return redirect(url_for('auth.comment', id=comment.post_id))
    return redirect(url_for('auth.comment',id=comment.post_id))

@auth.route('/cancel_banned/<int:id>',methods = ["GET" , 'POST'])
def cancel_banned(id):
    comment = Comment.query.filter_by(id=id).first()
    comment.ban = False
    db.session.add(comment)
    try:
        db.session.commit()
        flash("取消禁言成功！")
    except:
        db.session.rollback()
        flash("取消禁言失败！")
        return redirect(url_for('auth.comment',id=comment.post_id))
    return redirect(url_for('auth.comment', id=comment.post_id))