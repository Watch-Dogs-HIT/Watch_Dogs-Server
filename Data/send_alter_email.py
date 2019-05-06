#!/usr/bin/env python
# encoding:utf8

"""
Watch_Dogs
邮件发送功能
"""

import smtplib
from email.header import Header
from email.mime.text import MIMEText

from conf.setting import Setting

setting = Setting()
email_log = setting.logger
mail_host = setting.EMAIL_HOST
mail_user = setting.EMAIL_USER
mail_pass = setting.EMAIL_PASS
mail_sender = setting.EMAIL_SENDER


def mail_html_generate(alter_object="", alter_condition="", alter_details=""):
    """邮件内容生成"""
    mail_logo = """<div style="width: 800px">
    <img src="https://upload-images.jianshu.io/upload_images/5617720-b0e063bdea12c505.jpg?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240"
         alt="Watch_Dogs-logo"/>
    <h1 style="color:black;text-align: center">Linux远程主机及进程状态监测系统 - 预警邮件</h1>
    <hr style="height: 5px;color: black;width: 90%;" color="black"/>
</div>"""

    mail_text = """<div style="width: 800px">
    <p style="color:red;font-size: 20px">告警对象 > {alter_object}</p>
    <p>告警触发条件 >>> {alter_condition}</p>
    <p>告警触发详情 >>> <br/>{alter_details}
    </p>
    <hr style="height: 2px;color: black;width: 95%;" color="black"/>
</div>""".format(
        alter_object=alter_object, alter_condition=alter_condition, alter_details=alter_details
    )

    mail_footer = """<p style="color: grey;font-style:italic">邮件由系统自动生成,若不想继续接收可以在系统中取消预警或者拉黑发件地址<br>邮件内容生成于{date}</p>
    <footer>
        <p>&copy; 2019 <a href="https://github.com/h-j-13" target="_blank" title="侯捷">h-j-13</a>
        </p>
    </footer>""".format(date=setting.get_local_time())

    return mail_logo + mail_text + mail_footer


def send_alter_email(receiver, receiver_user_name="user", alter_object="", alter_condition="", alter_details=""):
    """发送告警邮件"""
    message = MIMEText(mail_html_generate(alter_object, alter_condition, alter_details), 'html', 'utf-8')
    message['From'] = Header("Watch_Dogs-alert", 'utf-8')
    message['To'] = Header(receiver_user_name, 'utf-8')
    subject = 'Linux远程主机及进程状态监测系统 - 告警邮件'
    message['Subject'] = Header(subject, 'utf-8')
    try:
        smtpObj = smtplib.SMTP_SSL(mail_host, 465)
        smtpObj.login(mail_user, mail_pass)
        smtpObj.sendmail(mail_sender, [receiver], message.as_string())
        smtpObj.quit()
        email_log.info("向 " + receiver + "(" + receiver_user_name + ") 发送了告警邮件")
    except smtplib.SMTPException as err:
        email_log.error("邮件发送异常 : " + str(err))
        email_log.error(
            "详情:to" + str(receiver) + "内容:" + str(alter_object) + "/" + str(alter_condition) + "/" + str(alter_details))


if __name__ == '__main__':
    # Demo
    send_alter_email("450943084@qq.com", "houjie", "just 4 test", "test error", "test case")
