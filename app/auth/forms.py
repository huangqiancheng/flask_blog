from flask_pagedown.fields import PageDownField
from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired, FileAllowed
from wtforms import FileField, SubmitField, StringField, PasswordField, BooleanField, TextAreaField, SelectField, \
    HiddenField
from wtforms.validators import DataRequired, Length, Email, EqualTo, Regexp, ValidationError

from app.models import Role, User


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(1, 64), Email()])
    password = PasswordField('密码', validators=[DataRequired()])
    remember_me = BooleanField('保持登录')
    submit = SubmitField('登录')

class RegisterForm(FlaskForm):
    email = StringField(label='邮箱',validators=[DataRequired(), Length(1,64),Email()])
    username = StringField(label='用户名',validators=
        [DataRequired(), Length(1,64),Regexp('^[a-zA-Z][A-Za-z0-9_.]*$',0,message ='用户名必须以字母开头，并且由数字，字母，下滑线组成！')])
    password = PasswordField(label='密码',validators=[DataRequired()])
    password2 = PasswordField(label="确认密码",validators=[DataRequired(),EqualTo('password',message ="两次密码必须一致")])
    submit = SubmitField(label="提交")

class UploadForm(FlaskForm):
    img = FileField(label='图片',validators=[FileRequired(),FileAllowed(upload_set = ['jpg','jpeg','png','gif'],message="上传文件格式不允许！")])
    submit = SubmitField('提交')

class EditProfileForm(FlaskForm):
    name = StringField(label='昵称',validators=[DataRequired()])
    location = StringField(label='所在地',validators=[DataRequired()])
    about_me = TextAreaField(label='自我介绍',validators = [DataRequired()])
    img = FileField(label='头像',validators=[FileAllowed(upload_set = ['jpg','jpeg','png','gif'],message="上传文件格式不允许！")])
    submit = SubmitField('提交')
    # def validate_email(self,field):
    #     if User.query.filter_by(email= field.data.lower()).first():
    #         raise ValidationError('该邮箱已被使用')
    #
    # def validate_username(self,field):
    #     if User.query.filter_by(username = field.data).first():
    #         raise ValidationError("该用户名已被使用，请换一个继续修改！")

class EditProfilenameAdminForm(FlaskForm):
    email = StringField(label='邮箱', validators=[DataRequired(), Length(1, 64), Email()])
    username = StringField(label='用户名', validators=[DataRequired()])
    state =  BooleanField('激活状态')
    role = SelectField(label='用户角色',coerce=int)
    name = StringField(label='昵称', validators=[DataRequired()])
    location = StringField(label='所在地', validators=[DataRequired()])
    about_me = TextAreaField(label='自我介绍', validators=[DataRequired()])
    img = FileField(label='头像', validators=[FileAllowed(upload_set=['jpg', 'jpeg', 'png', 'gif'],message="上传文件格式不允许！")])
    submit = SubmitField('提交')

    # def validate_email(self, field):
    #     if User.query.filter_by(email=field.data.lower()).first():
    #         raise ValidationError('该邮箱已被使用')
    #
    # def validate_username(self, field):
    #     if User.query.filter_by(username=field.data).first():
    #         raise ValidationError("该用户名已被使用，请换一个继续修改！")

    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.role.choices = [(role.id,role.name) for role in Role.query.all()]

class  PostForm(FlaskForm):
    body = PageDownField("现在的想法？？",validators=[DataRequired()])
    submit = SubmitField("提交")

class CommentForm(FlaskForm):
    body = PageDownField("你的看法是？？",validators=[DataRequired()])
    submit = SubmitField("提交")

