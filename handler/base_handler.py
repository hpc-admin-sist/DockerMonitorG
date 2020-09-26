# -*- coding: utf-8 -*-
# @Time    : 2018/8/12 下午8:36
# @Author  : Zhixin Piao 
# @Email   : piaozhx@shanghaitech.edu.cn

import tornado.web
import os
import subprocess
from utils import utils
import time

STANDARD_NODE_LIST = list(range(0, 30 + 1))

class BaseHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        return self.get_secure_cookie("user")

    @property
    def db(self):
        return self.application.db

    def get_node_list_by_str_nodes(self, nodes):
        try:
            node_list = eval('[%s]' % nodes)
        except:
            return None

        if not isinstance(node_list, list) or len(node_list) == 0:
            return None

        for node_id in node_list:
            if node_id not in STANDARD_NODE_LIST:
              return None
        return node_list

    @classmethod
    def get_website_ip(self):
        return '10.15.89.43'

    @classmethod
    def create_container_on_remote(self, node_name, docker_type, cname, container_port, advisor, run=False):
        container_name = '%s-%s' % (cname, node_name)
        addition_str = utils.ContainerAdditionStr(node_name, advisor, cname).get_additional_str()

        # memory_size = os.popen('''ssh %s  free -h | head -n 2 | tail -n 1 | awk -F' ' '{print $2}' ''' % node_name).read().strip()
        cmd = '''ssh %s  free -h | head -n 2 | tail -n 1 | awk -F' ' '{print $2}' ''' % node_name
        memory_size = self.cmd_with_timeout(cmd, timeout=10)
        if memory_size is not None:
            memory_size = memory_size.strip()
        else:
            return
        memory_unit = memory_size[-1]
        memory_size = int(memory_size[:-1])
        shm_size = memory_size // 2
        shm_size = str(shm_size) + memory_unit

        command = 'run' if run==True else 'create'
        detach = '-d' if run==True else ''
        cmd = (f"ssh {node_name} "
              f"{docker_type} {command} "
              f"--name {container_name} "
              "--network=host "
              f"-v /p300/docker/{cname}:/home "
              "-v /p300/datasets:/datasets:ro "
              f"-v /p300/g_cluster/user_dir/{cname}/bin:/bin "
              f"-v /p300/g_cluster/user_dir/{cname}/etc:/etc "
              f"-v /p300/g_cluster/user_dir/{cname}/lib:/lib "
              f"-v /p300/g_cluster/user_dir/{cname}/lib64:/lib64 "
              f"-v /p300/g_cluster/user_dir/{cname}/opt:/opt "
              f"-v /p300/g_cluster/user_dir/{cname}/root:/root "
              f"-v /p300/g_cluster/user_dir/{cname}/sbin:/sbin "
              f"-v /p300/g_cluster/user_dir/{cname}/usr:/usr "
              # "--privileged=true "
              # "--volume /run/dbus/system_bus_socket:/run/dbus/system_bus_socket:ro "
              # "--restart unless-stopped "
              f"--add-host {container_name}:127.0.0.1 "
              "--add-host g01:10.10.10.201 "
              "--add-host g02:10.10.10.202 "
              "--add-host g03:10.10.10.203 "
              "--add-host g04:10.10.10.204 "
              "--add-host g05:10.10.10.205 "
              "--add-host g06:10.10.10.206 "
              "--add-host g07:10.10.10.207 "
              "--add-host g08:10.10.10.208 "
              "--add-host g09:10.10.10.209 "
              "--add-host g10:10.10.10.210 "
              "--add-host g11:10.10.10.211 "
              "--add-host g12:10.10.10.212 "
              "--add-host g13:10.10.10.213 "
              "--add-host g14:10.10.10.214 "
              "--add-host g15:10.10.10.215 "
              "--add-host g16:10.10.10.216 "
              "--add-host g17:10.10.10.217 "
              "--add-host g18:10.10.10.218 "
              "--add-host g19:10.10.10.219 "
              "--add-host g20:10.10.10.220 "
              "--add-host g21:10.10.10.221 "
              "--add-host g22:10.10.10.222 "
              "--add-host g23:10.10.10.223 "
              "--add-host g24:10.10.10.224 "
              "--add-host g25:10.10.10.225 "
              "--add-host g26:10.10.10.226 "
              "--add-host g27:10.10.10.227 "
              "--add-host g28:10.10.10.228 "
              "--add-host g29:10.10.10.229 "
              "--add-host g30:10.10.10.230 "
              "--add-host login:10.10.10.231 "
              f"--shm-size={shm_size} "
              f"{addition_str} "
              f"-h {container_name} "
              f"{detach} "
              "ubuntu18.04 "
              f"/usr/sbin/sshd -p {container_port} -D")

        # os.system(cmd)
        r = self.cmd_with_timeout(cmd, timeout=10)
        if r is not None:
            print(f'{container_name} created.') 
            return True
        else:
            return False

    @classmethod
    def start_container_on_remote(self, node_name, docker_type, cname, container_port, advisor, run=False):
        container_name = '%s-%s' % (cname, node_name)

        memory_size = self.cmd_with_timeout('''ssh %s  free -h | head -n 2 | tail -n 1 | awk -F' ' '{print $2}' ''' % node_name)
        if memory_size is not None:
            memory_size = memory_size.strip()
        else:
            return

        cmd = f"ssh {node_name} docker start {container_name}"
        # os.system(cmd)

        tic = time.time()
        r = self.cmd_with_timeout(cmd, timeout=60)
        toc = time.time()
        if r is not None:
            print('%s started in %.2f s.' % (container_name, toc-tic))
            return True
        else:
            return False
        

        

    @classmethod
    def rm_container_on_remote(self, node_name, username):
        container_name = '%s-%s' % (username, node_name)
        cmd = 'ssh %s docker stop %s && docker rm %s' % (node_name, container_name, container_name)
        # os.system(cmd)
        r = self.cmd_with_timeout(cmd, timeout=10)
        if r is not None:
            print(f'{container_name} removed')
            return True
        else:
            return False

    
    @classmethod
    def cmd_with_timeout(self, cmd, timeout=10):
        p = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE)
        try:
            p.wait(timeout)
            text = p.communicate()[0].decode('utf-8')
            return text
        except subprocess.TimeoutExpired:
            p.kill()
            print(f'!!!! Timeout: {cmd} !!!!')
            return None
