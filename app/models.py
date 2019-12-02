from datetime import datetime
import bleach
from flask import current_app, url_for
from flask_login import UserMixin, AnonymousUserMixin
from markdown import markdown
from werkzeug.security import generate_password_hash,check_password_hash
from app import db, login_manager
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

class Permission:
    FOLLOW = 1
    COMMENT =2
    WRITE = 4
    MODERATE = 8
    ADMIN = 16
class Role(db.Model):
    __tablename__ = "roles"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean,default = False,index = True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role')
    created = db.Column(db.DateTime, default=datetime.now())
    update = db.Column(db.DateTime, default=datetime.now(), nullable=True)

    #SQLAlchemy默认会把permissions的值，所以使用构造函数给他设置初始值为0
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.permissions is None:
            self.permissions = 0

    def __repr__(self):
        return '<Role %s>' % self.name

    def __str__(self):
        return self.name

    #检查是否有某个权限，位于运算符
    def has_permission(self,perm):
        return self.permissions & perm == perm

    #添加权限
    def add_permission(self,perm):
        if not self.has_permission(perm):
            self.permissions += perm

    #移除权限
    def remove_permission(self,perm):
        if  self.has_permission(perm):
            self.permissions -= perm

    #重置权限
    def reset_permission(self):
        self.permissions = 0


    #新增角色，角色为roles字典中key的值，value值为对应角色的权限
    @staticmethod
    def insert_roles():
        roles = {
            'User':[Permission.FOLLOW,Permission.COMMENT,Permission.WRITE],
            'Moderator':[Permission.FOLLOW,Permission.COMMENT,Permission.WRITE,Permission.MODERATE],
            'Administrator':[Permission.FOLLOW,Permission.COMMENT,Permission.WRITE,Permission.MODERATE,Permission.ADMIN]
        }
        default_role = 'User'
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.reset_permission()
            for perm in roles[r]:
                role.add_permission(perm)
            role.default = (role.name  == default_role)
            db.session.add(role)
        db.session.commit()

class Follow(db.Model):
    __tablename__ = 'follows'
    fans_id = db.Column(db.Integer,db.ForeignKey('users.id'),primary_key = True)
    bloger_id = db.Column(db.Integer,db.ForeignKey("users.id"),primary_key = True)
    timestamp = db.Column(db.DateTime,default=datetime.now)

    def __repr__(self):
        return "<Follow {} follow {}>".format(self.fan.username,self.bloger.username)

class User(UserMixin,db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    email = db.Column(db.String(64),unique = True)
    name = db.Column(db.String(16))
    location = db.Column(db.String(64))
    about_me = db.Column(db.Text)
    member_since = db.Column(db.DateTime,default=datetime.now)
    last_seen = db.Column(db.DateTime,default = datetime.now)
    avatar_url = db.Column(db.String(128),default ='head_image/U105P28T3D2048907F326DT20080604225106.jpg')
    confirmed = db.Column(db.Boolean,default=False)
    role_id = db.Column(db.Integer, db.ForeignKey("roles.id"),nullable=True)
    post = db.relationship('Post',backref = 'author')
    created = db.Column(db.DateTime, default=datetime.now)
    update = db.Column(db.DateTime, default=datetime.now, nullable=True)
    password_hash = db.Column(db.String(100))
    is_fans = db.relationship('Follow',foreign_keys = [Follow.fans_id],backref =db.backref('fan',lazy ='joined'),lazy ='dynamic',cascade ='all,delete-orphan')
    is_blogers = db.relationship('Follow',foreign_keys = [Follow.bloger_id], backref = db.backref("bloger" , lazy = 'joined'),lazy = "dynamic" , cascade = 'all,delete-orphan')
    comment = db.relationship('Comment',backref = "user_comment")

    def get_upload_file(self):
        return url_for('auth.upload_file',filename=self.avatar_url)

    #激活
    def generate_confirmation_token(self,expiration):
        s = Serializer(current_app.config['SECRET_KEY'],expiration)
        return s.dumps({'confirm':self.id}).decode('utf-8')

    #验证
    def confirm(self,token):
        s = Serializer(current_app.config["SECRET_KEY" ])
        try:
            data =  s.loads(token.encode('utf-8'))
        except Exception as e:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True


    @property
    def password(self):
        raise AttributeError('password 不可读！！')

    @password.setter
    def password(self,password):
        self.password_hash = generate_password_hash(password)

    #验证密码
    def verify_password(self,password):
        return check_password_hash(self.password_hash,password)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    #判断一个用户是否具有某种权限
    def can(self,perm):
        return self.role_id is not None and self.role.has_permission(perm)

    #关注某个用户
    def follow(self,user):
        gz = Follow(fan=self,bloger=user)
        db.session.add(gz)
        db.session.commit()
    #取消对某个用户的关注
    def unfollow(self,user):
        ss = self.is_fans.filter_by(bloger_id=user.id).first()
        db.session.delete(ss)
        db.session.commit()

    #判断是否关注了某个用户
    def is_following(self,user):
        ss = self.is_fans.filter_by(bloger_id=user.id).first()
        return ss in user.is_blogers.all()
    #判断是否被某个人用户关注
    def is_followed_by(self,user):
        ss =  self.is_blogers.filter_by(fans_id = user.id).first()
        return ss in self.is_blogers

    #获取关注用户的文章
    @property
    def follow_posts(self):
        return Post.query.join(Follow,Follow.bloger_id == Post.author_id).filter(Follow.fans_id == self.id)



    def __init__(self,**kwargs):
        super(User,self).__init__(**kwargs)
        if self.role_id is None:
            self.role_id = Role.query.filter_by(default=True).first()

    def is_administrator(self):
        return self.can(Permission.ADMIN)
    def __repr__(self):
        return '<User %s>' % self.username

    def __str__(self):
        return self.username

# 判断一个用户是否具有管理员权限
class AnonymouUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False

login_manager.anonymous_user = AnonymouUser


class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    created = db.Column(db.DateTime, default=datetime.utcnow)
    update = db.Column(db.DateTime, default=datetime.now, nullable=True)
    author_id = db.Column(db.Integer,db.ForeignKey("users.id"))
    body_html = db.Column(db.Text)
    comment = db.relationship('Comment',backref ="post_comment")
    @staticmethod
    def on_changed_body(target,value,oldvalue,initiator):
        allowed_tags = ['a','abbr','acronym','b','blockquote','code','em','i','li','ol','pre','strong','ul','h1','h2','h3','h4','h5','p']
        target.body_html =bleach.linkify(bleach.clean(markdown(value,output_format ='html'),tags = allowed_tags,strip = True))
db.event.listen(Post.body,'set',Post.on_changed_body)


class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key = True)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    timestamp = db.Column(db.DateTime,default=datetime.now)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    ban = db.Column(db.Boolean,default=False)
    post_id = db.Column(db.Integer, db.ForeignKey("posts.id"))