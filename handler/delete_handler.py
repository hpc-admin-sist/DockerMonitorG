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
        username = self.get_argument('cname')

        print(f'---- Deleting user "{username}..." ----')
        
        ret = {'code': None}
        if username == "":
            ret['code'] = 101
            self.write(ret)
            return

        uid = self.db.get_uid_by_username(username)
        if uid == None:
            ret['code'] = 102
            self.write(ret)
            return

        self.close_all_container(username, uid)

        print(f'---- Removing user directory of "{username}" ----')
        offset = 1
        trash_path = '/p300/g_cluster/user_dir/trash_bin/trash-%d' % offset
        while os.path.exists(trash_path):
            offset += 1
            trash_path = '/p300/g_cluster/user_dir/trash_bin/trash-%d' % offset
        usr_dir = f'/p300/g_cluster/user_dir/{username}'
        print(f'mv {usr_dir} {trash_path}')
        os.system(f'mv {usr_dir} {trash_path}')

        print(f'rm -rf {trash_path} &')
        os.system(f'rm -rf {trash_path} &')

        # # print('rm -rf /p300/docker/%s' % username)
        # # os.system('rm -rf /p300/docker/%s' % username)
        print(f'User "{username}" deleted!')

        self.db.delete_user(uid)
        ret['code'] = 200
        self.write(ret)

    def close_all_container(self, username, uid):
        print(f'---- Stopping and removing all containers of "{username}" ----')
        args_list = []
        for node_id in STANDARD_NODE_LIST:
            node_name = 'login' if node_id == 0 else 'g%02d' % node_id
            args_list.append((node_name, username))

        p = Pool(len(STANDARD_NODE_LIST))
        p.starmap(self.rm_container_on_remote, args_list)
        print('Done')
        p.close()
        self.db.remove_user_permission(uid, STANDARD_NODE_LIST)
    