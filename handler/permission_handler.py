# -*- coding: utf-8 -*-
# @Time    : 2018/8/12 下午10:47
# @Author  : Zhixin Piao 
# @Email   : piaozhx@shanghaitech.edu.cn

from handler.base_handler import BaseHandler
import datetime
import time
import json
import os
from multiprocessing import Pool
from utils import utils


class PermissionHandler(BaseHandler):
    def get(self):
        username = self.get_argument('username', default='')

        if username == '':
            user_info_list = self.db.get_all_user_info()
            self.render('../html/permission.html', user_info_list=user_info_list, cur_user=self.get_current_user())
        else:
            uid = self.db.get_uid_by_username(username)
            if not uid:
                self.write('None')
            else:
                user_info = self.db.get_user_detail_info_by_uid(uid)
                self.write(json.dumps(user_info))

    def post(self):
        """
        add permission for some user
        code 101 : blank input
        code 102 : invalid input longtime
        code 103 : invalid input nodes
        code 104 : user not exists
        code 105 : not long time but doesn't have start_date and end_date
        code 106 : not long time but doesn't have reason
        code 200 : success
        :return:
        """

        username = self.get_argument('cname')
        str_nodes = self.get_argument('nodes')
        longtime = self.get_argument('longtime')
        start_date = self.get_argument('start')
        end_date = self.get_argument('end')
        reason = self.get_argument('reason')

        ret = {'code': None}
        if username == '' or str_nodes == '':
            ret['code'] = 101
            self.write(ret)
            return

        if longtime not in ['yes', 'no']:
            ret['code'] = 102
            self.write(ret)
            return

        node_list = self.get_node_list_by_str_nodes(str_nodes)
        if node_list == None:
            ret['code'] = 103
            self.write(ret)
            return

        uid = self.db.get_uid_by_username(username)
        if not uid:
            ret['code'] = 104
            self.write(ret)
            return

        if longtime == 'no':
            if start_date == '' or end_date == '':
                ret['code'] = 105
                self.write(ret)
                return
            elif reason == '':
                ret['code'] = 106
                self.write(ret)
                return

            else:
                start_date = datetime.datetime.strptime(start_date, '%m/%d/%Y').strftime('%Y-%m-%d') + ' 00:00:00'
                end_date = datetime.datetime.strptime(end_date, '%m/%d/%Y').strftime('%Y-%m-%d') + ' 23:59:59'

        self.add_user_container(uid, node_list)
        self.run_user_container(uid, node_list)
        self.db.add_user_permission(uid, node_list, longtime, start_date, end_date, reason)

        ret['code'] = 200
        ret['log'] = self.log
        self.write(ret)

    def add_user_container(self, uid, node_list):
        self.log = ''
        uid, cname, container_port, open_port_range, advisor = self.db.get_user_info_by_uid(uid)

        rm_args_list = []
        add_args_list = []

        for node_id in node_list:
            docker_type = 'docker' if node_id == 0 else 'nvidia-docker'
            node_name = 'login' if node_id == 0 else 'g%02d' % node_id

            rm_args_list.append((node_name, cname))
            add_args_list.append((node_name, docker_type, cname, container_port, advisor))

        print(f'---- Stopping and removing old permission of "{cname}": {node_list} ----')
        p = Pool(len(node_list))
        r_list = p.starmap(self.rm_container_on_remote, rm_args_list)
        p.close()
        if all(r_list):
            self.log += f'Removed: {str([node_list[i] for i, e in enumerate(r_list) if e == True])}\n'
        else:
            self.log += f'Fail to remove: {str([node_list[i] for i, e in enumerate(r_list) if e != True])}\n'

        print(f'---- Adding permission of "{cname}": {node_list} ----')
        p = Pool(len(node_list))
        r_list = p.starmap(self.create_container_on_remote, add_args_list)
        p.close()
        if all(r_list):
            self.log += f'Created: {str([node_list[i] for i, e in enumerate(r_list) if e == True])}\n'
        else:
            self.log += f'Fail to create: {str([node_list[i] for i, e in enumerate(r_list) if e != True])}\n'
    
    def run_user_container(self, uid, node_list):
        uid, cname, container_port, open_port_range, advisor = self.db.get_user_info_by_uid(uid)

        print(f'---- Starting nodes {node_list} for user "{cname}"" ----')
        r_list = []
        for node_id in node_list:
            docker_type = 'docker' if node_id == 0 else 'nvidia-docker'
            node_name = 'login' if node_id == 0 else 'g%02d' % node_id

            r = self.start_container_on_remote(node_name, docker_type, cname, container_port, advisor)
            r_list.append(r)
        if all(r_list):
            self.log += f'Started: {str([node_list[i] for i, e in enumerate(r_list) if e == True])}\n'
        else:
            self.log += f'Fail to start: {str([node_list[i] for i, e in enumerate(r_list) if e != True])}\n'
