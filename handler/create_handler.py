# -*- coding: utf-8 -*-
# @Time    : 2018/8/11 下午9:59
# @Author  : Zhixin Piao 
# @Email   : piaozhx@shanghaitech.edu.cn

from handler.base_handler import BaseHandler
import os
import json
import smtplib
import time
from email.mime.text import MIMEText
from email.header import Header
from datetime import datetime


class CreateHandler(BaseHandler):
    def post(self):
        """
        code 101: blank input!
        code 102: name exists
        code 200: everything is ok
        :return:
        """
        cname = self.get_argument('cname')
        print(f'==== Adding new account for "{cname} ====')

        chs_name = self.get_argument('chs_name')
        email = self.get_argument('email')
        advisor = self.get_argument('advisor')
        ret_data = {'code': '', 'log': ''}
        self.log = ''

        if cname == '' or chs_name == '' or email == '' or advisor == '':
            ret_data['code'] = 101
            self.write(ret_data)
            return

        uid = self.db.get_uid_by_username(cname)
        if uid != None:
            ret_data['code'] = 102
            self.write(ret_data)
            return

        uid = self.db.try_to_add_user(cname)

        container_port = uid + 21000
        each_user_port_num = 10
        port_range_str = '%d-%d' % (30000 + each_user_port_num * (uid - 1000), 30000 + each_user_port_num * (uid - 1000 + 1) - 1)
        if self.create_user_docker_dir(cname, container_port, port_range_str, advisor):
            self.db.add_user(cname, container_port, port_range_str, email, chs_name, advisor)
            self.db.add_user_permission(uid, [0], 'yes', '', '', '')
            
            self.send_email_to_new_account(cname, chs_name, email, container_port, port_range_str)
            self.log += 'E-mail sent.\n'
            
            ret_data['code'] = 200
            ret_data['log'] = self.log
            self.write(ret_data)

    def create_user_docker_dir(self, cname, container_port, port_range_str, advisor):
        

        user_dir = '/p300/g_cluster/user_dir/%s' % cname
        if os.path.exists(user_dir):
            print(f'!!!! User directory "{user_dir}" exists !!!!')
            self.log += "User directory exists, please use another user name.\n"
            return False
        else:
            print(f'---- Creating user directory for "{cname}"" ----')
            self.log += 'Creating user docker dir...\n'

            ## ubuntu18.04-cudnn8-cuda10.2
            baseline_root_path = '/p300/g_cluster/user_dir/baseline-ubuntu18.04-nvidia'  
            prepare_root_path = '/p300/g_cluster/user_dir/prepared_baseline-ubuntu18.04-nvidia'
            prepare_dirname_list = sorted(os.listdir(prepare_root_path))
            
            if len(prepare_dirname_list) == 0:
                os.system("cp -r %s %s" % (baseline_root_path, user_dir))
            else:
                prepare_dir = '%s/%s' % (prepare_root_path, prepare_dirname_list[0])
                print("mv %s %s" % (prepare_dir, user_dir))
                os.system("mv %s %s" % (prepare_dir, user_dir))

            # build ssh-key
            # os.system('''cat /dev/zero | ssh-keygen -q -N "" -f /p300/g_cluster/user_dir/%s/root/.ssh/id_rsa''' % cname)
            os.system(f'ssh-keygen -q -N "" -f /p300/g_cluster/user_dir/{cname}/root/.ssh/id_rsa')
            os.system("cat /p300/g_cluster/user_dir/%s/root/.ssh/id_rsa.pub >> /p300/g_cluster/user_dir/%s/root/.ssh/authorized_keys" % (cname, cname))
            os.system('sed -i "s/user_port/%d/g" /p300/g_cluster/user_dir/%s/root/.ssh/config' % (container_port, cname))
            # os.system('sed -i "s/user_port_range/%s/g" /public/docker/%s/etc/motd' % (port_range_str, cname))

            print('---- Creating user login container... ----')
            self.log += 'Creating user login container...'

            self.create_container_on_remote('login', 'docker', cname, container_port, advisor, run=True)

            self.log += 'Success!\n'
            self.log += 'Please login by "ssh root@%s -p %d"\ndefault passwd: sist\n' % (self.get_website_ip(), container_port)
            print('Please login by "ssh root@%s -p %d"\ndefault passwd: sist' % (self.get_website_ip(), container_port))
            
            return True

    def send_email_to_new_account(self, username, ch_username, receiver, login_port, assigned_port):
        mail_host = "smtp.shanghaitech.edu.cn"  # 设置服务器
        mail_user = "piaozhx@shanghaitech.edu.cn"  # 用户名
        mail_pass = "yozN2JjhGMNVWDLDNYgGdGAo"  # 口令

        sender = 'piaozhx@shanghaitech.edu.cn'
        receivers = [receiver]  # 接收邮件，可设置为你的QQ邮箱或者其他邮箱

        mail_content = f'''
{ch_username}:

    你好！

    你的G-Cluster新账户已开通：
        用户名： {username}
        默认密码：sist                （建议在初次登陆后使用passwd命令修改密码）
        登录端口号： {login_port}
        分配端口号： {assigned_port}  （为了减少端口冲突，在开启Tensorboard、Visdom、Jupyter Notebook等程序时，请使用分配给你的端口号。）

    你的账户登录命令为：
        ssh root@10.15.89.43 -p {login_port}

    G-Cluster集群与AI集群的架构基本相似，主要有以下几点区别：
    1. G-Cluster的校内IP地址为10.15.89.43
    2. 操作系统升级至Ubuntu 18.04LTS
    3. 预装NVIDIA CUDA 10.2和PyTorch1.6
    4. 由于不同节点之间的GPU驱动型号存在差异，当用户在不同型号的计算节点运行程序时，
       可能会出现检测不到显卡或库文件缺失的问题。此时，直接在命令行中运行ldconfig命令可以解决问题。
    5. 当用户在G-Cluster上的用户名和AI集群一致时，系统会自动将用户在AI集群/p300目录下的内容挂载到
       新账号的/home目录下。因此，我们仍然强烈建议用户将代码及数据存储在这一目录下。这样既可以实现
       两个集群的数据共享，也便于系统维护和数据迁移。
    6. 在初次登入账户及计算节点时，系统需要预加载，请耐心等待。计算节点的权限生成存在延迟。

    现阶段，G-Cluster尚没有专门的文档，使用方法请参考AI集群文档：http://10.15.89.41:8898
    GPU监控网页：http://10.15.89.43/gpu
    计算节点权限：http://10.15.89.43/permission

    特别注意：集群为公有资源，每个用户的正常使用量为1-2个节点，请勿长时间占用大量计算资源。
    禁止使用占卡、抢卡脚本，违者将被直接删除权限。

高性能集群管理员
{datetime.today().strftime("%b %d, %Y")}
'''

        message = MIMEText(mail_content, 'plain', 'utf-8')
        message['From'] = Header("高性能集群管理员", 'utf-8')
        message['To'] = Header(f"{ch_username}", 'utf-8')

        message['Subject'] = Header('您的G-Cluster新账户已开通', 'utf-8')

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
