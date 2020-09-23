# -*- coding: utf-8 -*-
# @Time    : 2018/8/22 下午4:44
# @Author  : Zhixin Piao 
# @Email   : piaozhx@shanghaitech.edu.cn

import tornado.web
from handler.base_handler import BaseHandler
import json
import os


class GpuHandler(BaseHandler):
    def get(self):
        node_id = int(self.get_argument('id', default=-1))
        if node_id == -1:
            # node_gpu_msg_list = self.db.get_node_msg_list_with_chs_name()
            node_gpu_msg_list = self.db.get_node_msg_list()
            self.render('../html/gpu.html', node_gpu_msg_list=node_gpu_msg_list, cur_user=self.get_current_user())
        else:
            node_gpu_msg_list = self.db.get_node_msg_list()
            self.write(json.dumps(node_gpu_msg_list))

    def post(self):
        ret = {'code': 200}

        hostname = self.get_argument('hostname')
        card_id = self.get_argument('card_id')
        os.system("ssh %s fuser -k /dev/nvidia%s" % (hostname, card_id))

        self.write(ret)


class P40GpuHandler(BaseHandler):
    def get(self):
        node_gpu_msg_list = self.db.get_p40_node_msg_list()
        self.render('../html/p40_gpu.html', node_gpu_msg_list=node_gpu_msg_list, cur_user=self.get_current_user())
        # node_id = int(self.get_argument('id', default=-1))
        # node_gpu_msg_list = list(self.db.get_p40_node_msg_list())
        # if node_id == -1:
            # self.render('../html/p40_gpu.html', node_gpu_msg_list=node_gpu_msg_list, cur_user=self.get_current_user())
        # else:
            # self.write(json.dumps(node_gpu_msg_list))


class PPPPP40GpuHandler(BaseHandler):
    def get(self):
        node_id = int(self.get_argument('id', default=-1))
        node_gpu_msg_list = list(self.db.get_p40_node_msg_list())
        if node_id == -1:
            self.render('../html/p40_gpu.html', node_gpu_msg_list=node_gpu_msg_list, cur_user=self.get_current_user())
        else:
            self.write(json.dumps(node_gpu_msg_list))


class PLUSGpuHandler(BaseHandler):
    def get(self):
        node_gpu_msg_list = self.db.get_plus_node_msg_list()
        self.render('../html/plus_gpu.html', node_gpu_msg_list=node_gpu_msg_list, cur_user=self.get_current_user())


class PLUSPLUSGpuHandler(BaseHandler):
    def get(self):
        node_gpu_msg_list = self.db.get_plus_plus_node_msg_list()
        self.render('../html/plus_plus_gpu.html', node_gpu_msg_list=node_gpu_msg_list, cur_user=self.get_current_user())


class SVIPGpuHandler(BaseHandler):
    def get(self):
        node_gpu_msg_list = self.db.get_svip_node_msg_list()
        self.render('../html/svip_gpu.html', node_gpu_msg_list=node_gpu_msg_list, cur_user=self.get_current_user())

class SVIPSVIPGpuHandler(BaseHandler):
    def get(self):
        node_gpu_msg_list = self.db.get_svip_svip_node_msg_list()
        self.render('../html/svip_svip_gpu.html', node_gpu_msg_list=node_gpu_msg_list, cur_user=self.get_current_user())

class affpermissionHandler(BaseHandler):
    def get(self):
        node_gpu_msg_list = self.db.get_svip_svip_node_msg_list()
        self.render('../html/aff_per.html', node_gpu_msg_list=node_gpu_msg_list, cur_user=self.get_current_user())

class affstatusHandler(BaseHandler):
    def get(self):
        node_gpu_msg_list = self.db.get_aff_node_msg_list()
        self.render('../html/gpu.html', node_gpu_msg_list=node_gpu_msg_list, cur_user=self.get_current_user())