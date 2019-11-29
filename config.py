import os

from datetime import timedelta



basedir = os.path.abspath(os.path.dirname(__file__))
class Config:
    SECRET_KEY =os.environ.get('SECRET_KEY') or 's23434asdV#FB?DFBHD/sdfb\dfbaw15656564'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    #上传配置
    UPLOAD_FOLDER = os.path.join(basedir,'upload_file_dir')
    UPLOAD_HEAD = 'head_image'
    ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
    # MAX_CONTENT_LENGTH = 16 * 1024 * 1024 )


    #邮件配置
    MAIL_SERVER = 'smtp.163.com'
    EMAIL_PORT = 25
    MAIL_USE_TLS = False
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or '13476319128@163.com'
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or  'QWER123456'
    @staticmethod
    def init_app(app):
        pass

#开发环境配置
class DevelopmentConfig(Config):
    DEBUG = True
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or 'sqlite:///' + \
                              os.path.join(basedir,'data.sqlite3') + '?check_same_thread=False'


#测试环境配置
class TestinsConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or 'sqlite:///' + \
                              os.path.join(basedir, 'data.sqlite3') + '?check_same_thread=False'

#生产环境配置
class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or 'sqlite:///' + \
                              os.path.join(basedir,'data.sqlite3') + '?check_same_thread=False'

config = {
    'development':DevelopmentConfig,
    'testing':TestinsConfig,
    'production':ProductionConfig,
    'default':DevelopmentConfig
}