# -*- coding: utf-8 -*-
# @Time    : 2018/8/22 下午4:44
# @Author  : Zhixin Piao 
# @Email   : piaozhx@shanghaitech.edu.cn

import tornado.web
from handler.base_handler import BaseHandler
import json
import os
from collections import defaultdict


class GpuHandler(BaseHandler):
    def get(self):
        node_id = int(self.get_argument('id', default=-1))
        if node_id == -1:
            # node_gpu_msg_list = self.db.get_node_msg_list_with_chs_name()
            node_gpu_msg_list = self.db.get_node_msg_list()

            usr_consumpt_dict = defaultdict(int)
            for node_gpu_msg in node_gpu_msg_list:
                for gpu_msg in node_gpu_msg['gpus']:
                    users = []
                    for proc in gpu_msg['processes']:
                        usr = proc['username'].split('-')[0]
                        users.append(usr)
                    users = set(users)
                    for usr in users:
                        usr_consumpt_dict[usr] += 1

            self.render('../html/gpu.html', node_gpu_msg_list=node_gpu_msg_list,
                        usr_consumpt_dict=usr_consumpt_dict, cur_user=self.get_current_user())
        else:
            node_gpu_msg_list = self.db.get_node_msg_list()
            self.write(json.dumps(node_gpu_msg_list))

    def post(self):
        ret = {'code': 200}

        hostname = self.get_argument('hostname')
        card_id = self.get_argument('card_id')
        os.system("ssh %s fuser -k /dev/nvidia%s" % (hostname, card_id))

        self.write(ret)
