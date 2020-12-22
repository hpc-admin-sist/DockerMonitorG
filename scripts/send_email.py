# -*- coding: utf-8 -*-
# @Time    : 2018/9/9 6:24 PM
# @Author  : Zhixin Piao 
# @Email   : piaozhx@shanghaitech.edu.cn

import smtplib
import time
from email.mime.text import MIMEText
from email.header import Header
from db.db_manager import DatabaseManager
from config import mail_host, mail_user, mail_pass


def send_broadcast_email(receiver, username, password, port, admin_open_port, node_name_list):
    sender = mail_user
    receivers = [receiver]  # 接收邮件，可设置为你的QQ邮箱或者其他邮箱

    mail_content = '''
    尊敬的集群用户：<br><br>

    你好！<br><br>

        在上一阶段的试运行中，用户普遍反映系统响应迟缓，因此我们计划于<strong>2020年11月25日晚19点</strong>对G-Cluster的存储策略进行调整，需要停机维护。<br>
    <strong>本次维护后，用户的系统环境将被重置，存储在<code>/home</code>目录以外的数据将不被保留。</strong>请用户及时将<code>/root</code>目录下的代码、数据文件迁移到<code>/home</code>目录。<br>
    注意：
    <ul>
        <li>用户只需备份有用的数据，无需手动删除文件。</li>
        <li>由于网络带宽有限，强烈建议用户仅迁移必需文件。不建议迁移Anaconda、Miniconda等环境目录。</li>
        <li>本次维护后，原<code>/home</code>文件夹改名为<code>/p300</code>， 继续与AI集群同名用户共享存储。另外，为了便于数据管理，我们始终建议用户将代码、数据等重要文件存储在<code>/p300</code>目录下。</li>
        <li>下列账户由于创建时间较晚，已自动采用新的存储策略，不需要迁移数据：jinlei,  kuanghf,  kuangjq,  liuzhch,  ouyangzhp, wentm, zengzy, zhangchg, zhiyh。</li>
        <li>关于本次迁移若有任何问题，请从导航栏进入<code>Issues</code>进行反馈。</li>
    </ul>
    <br>
    信息学院高性能集群运维管理团队 <br>
    2020年11月24日
    '''

    message = MIMEText(mail_content, 'html', 'utf-8')
    message['From'] = Header("信息学院高性能集群运维管理团队", 'utf-8')
    message['To'] = Header(receiver, 'utf-8')

    message['Subject'] = Header('G-Cluster数据迁移及停机维护通知', 'utf-8')

    try:
        smtpObj = smtplib.SMTP()
        smtpObj.connect(mail_host, 587)  # 25 为 SMTP 端口号

        smtpObj.ehlo()
        smtpObj.starttls()
        smtpObj.ehlo()

        smtpObj.login(sender, mail_pass)
        smtpObj.sendmail(sender, receivers, message.as_string())
        print("%s 邮件发送成功" % username)
        return True

    except smtplib.SMTPException as e:
        print("Error: %s 无法发送邮件" % receiver)
        print(e)
        return False


def main():
    db = DatabaseManager()
    user_info_list = db.get_all_user_info()

    for user_info in user_info_list:
        username = user_info['username']
        uid = user_info['uid']
        receiver = user_info['email']
        container_port = user_info['container_port']
        open_port_range = user_info['open_port_range']

        if '@' not in receiver:
            continue
        print(receiver)
        node_name_list = [p['name'] for p in user_info['permission']]
        success = False
        while not success:
            success = send_broadcast_email(receiver, username, 'sist', container_port, open_port_range, node_name_list)
            time.sleep(10)

if __name__ == '__main__':
    main()
