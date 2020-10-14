# -*- coding: utf-8 -*-
# @Time    : 2018/9/9 6:24 PM
# @Author  : Zhixin Piao 
# @Email   : piaozhx@shanghaitech.edu.cn

import smtplib
import time
from email.mime.text import MIMEText
from email.header import Header
from db.db_manager import DatabaseManager

mail_host = "smtp.shanghaitech.edu.cn"  # 设置服务器
mail_user = "piaozhx@shanghaitech.edu.cn"  # 用户名
mail_pass = "yozN2JjhGMNVWDLDNYgGdGAo"  # 口令


def send_broadcast_email(receiver, username, password, port, admin_open_port, node_name_list):
    sender = 'piaozhx@shanghaitech.edu.cn'
    receivers = [receiver]  # 接收邮件，可设置为你的QQ邮箱或者其他邮箱

    mail_content = '''
    
    '''

    message = MIMEText(mail_content, 'plain', 'utf-8')
    message['From'] = Header("信息学院高性能集群运维管理团队", 'utf-8')
    message['To'] = Header("高性能集群", 'utf-8')

    message['Subject'] = Header('信息学院高性能集群', 'utf-8')

    try:
        smtpObj = smtplib.SMTP()
        smtpObj.connect(mail_host, 587)  # 25 为 SMTP 端口号

        smtpObj.ehlo()
        smtpObj.starttls()
        smtpObj.ehlo()

        smtpObj.login(mail_user, mail_pass)
        smtpObj.sendmail(sender, receivers, message.as_string())
        print("%s 邮件发送成功" % username)
        return True

    except smtplib.SMTPException:
        print("Error: %s 无法发送邮件" % receiver)
        return False


def main():
    db = DatabaseManager()
    user_info_list = db.get_all_user_info()

    for user_info in user_info_list:
        username = user_info['username']
        receiver = user_info['email']
        container_port = user_info['container_port']
        open_port_range = user_info['open_port_range']

        if '@' not in receiver:
            continue

        node_name_list = [p['name'] for p in user_info['permission']]
        success = False
        while not success:
            time.sleep(10)
            success = send_broadcast_email(receiver, username, 'sist', container_port, open_port_range, node_name_list)

if __name__ == '__main__':
    main()
