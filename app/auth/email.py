from flask import current_app, render_template
from flask_mail import Message
from threading import Thread
def send_async_email(app,msg):
     with app.app_context():
         mail.send(msg)
from app import mail


def sender_email(to,subject,template,**kwargs):
    msg = Message( subject ,sender="13476319128@163.com",recipients = [to])
    # msg.body = render_template(template + '.txt',**kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    thr = Thread(target=send_async_email, args=[current_app._get_current_object(),msg])
    thr.start()
    return thr