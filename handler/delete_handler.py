# -*- coding: utf-8 -*-
# @Time    : 2018/8/11 下午10:00
# @Author  : Zhixin Piao 
# @Email   : piaozhx@shanghaitech.edu.cn

from handler.base_handler import BaseHandler, STANDARD_NODE_LIST
import os
from multiprocessing import Pool


def remove_container_on_remote(node_name, container_name):
    os.system('ssh %s "docker stop %s && docker rm %s"' % (node_name, container_name, container_name))
    print('close', container_name, 'done')


class DeleteHandler(BaseHandler):
    def post(self):
        '''
        code 101: blank input
        code 102: name not exists
        code 200: success
        :return:
        '''
        cname = self.get_argument('cname')

        ret = {'code': None}
        if cname == "":
            ret['code'] = 101
            self.write(ret)
            return

        uid = self.db.get_uid_by_username(cname)
        if uid == None:
            ret['code'] = 102
            self.write(ret)
            return

        self.close_all_container(cname, uid)

        print('rm -rf /p300/g_cluster/user_dir/%s...' % cname)
        os.system('rm -rf /p300/g_cluster/user_dir/%s' % cname)

        # print('rm -rf /p300/docker/%s' % cname)
        # os.system('rm -rf /p300/docker/%s' % cname)
        print('delete account successfully!!!')

        self.db.delete_user(uid)
        ret['code'] = 200
        self.write(ret)

    def close_all_container(self, cname, uid):
        p = Pool(len(STANDARD_NODE_LIST))
        args_list = []

        for node_id in STANDARD_NODE_LIST:
            node_name = 'login' if node_id == 0 else 'g%.2d' % node_id
            container_name = '%s-%s' % (cname, node_name)

            args_list.append((node_name, container_name))

        p.starmap(remove_container_on_remote, args_list)
        p.close()

        self.db.remove_user_permission(uid, STANDARD_NODE_LIST)
