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
        self.db.add_user_permission(uid, node_list, longtime, start_date, end_date, reason)

        ret['code'] = 200
        ret['log'] = self.log
        self.write(ret)

    def add_user_container(self, uid, node_list):
        self.log = ''
        uid, cname, container_port, open_port_range, advisor = self.db.get_user_info_by_uid(uid)

        for node_id in node_list:
            docker_type = 'docker' if node_id == 0 else 'nvidia-docker'
            node_name = 'login' if node_id == 0 else 'g%.2d' % node_id

            self.rm_container_on_remote(node_name, cname)
            self.create_container_on_remote(node_name, docker_type, cname, container_port, advisor)

        print('create', cname, 'done!', 'port: ', container_port)
        self.log += 'Create %s done! port: %d\n' % (cname, container_port)
        print('add nodes permission successfully')
        self.log += 'add nodes permission on %s successfully\n' % str(node_list)
        
