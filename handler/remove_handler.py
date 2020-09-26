# -*- coding: utf-8 -*-
# @Time    : 2018/8/12 下午4:19
# @Author  : Zhixin Piao 
# @Email   : piaozhx@shanghaitech.edu.cn

from handler.base_handler import BaseHandler
import os
from multiprocessing import Pool


class RemoveHandler(BaseHandler):
    def post(self):
        """
        code 101: blank input
        code 102: invalid input nodes
        code 103: name not exists
        code 200: success
        :return:
        """
        username = self.get_argument('cname')
        str_nodes = self.get_argument('nodes')

        ret = {'code': None}
        if username == '' or str_nodes == '':
            ret['code'] = 101
            self.write(ret)
            return

        node_list = self.get_node_list_by_str_nodes(str_nodes)
        if node_list == None:
            ret['code'] = 102
            self.write(ret)
            return

        uid = self.db.get_uid_by_username(username)
        if not uid:
            ret['code'] = 103
            self.write(ret)
            return

        print(f'---- Stopping and removing permission of "{username}" on nodes: {node_list} ----')
        p = Pool(len(node_list))
        args_list = []

        for node_id in node_list:
            node_name = 'login' if node_id == 0 else 'g%.2d' % node_id
            args_list.append((node_name, username))
        p.starmap(self.rm_container_on_remote, args_list)
        p.close()

        self.db.remove_user_permission(uid, node_list)
        ret['code'] = 200
        self.write(ret)
