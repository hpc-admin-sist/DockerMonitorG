# -*- coding: utf-8 -*-
# @Time    : 2018/9/9 11:22 PM
# @Author  : Zhixin Piao 
# @Email   : piaozhx@shanghaitech.edu.cn

import sys

sys.path.append('./')

import os
from db.db_manager import DatabaseManager
from handler.base_handler import BaseHandler
from tqdm import tqdm


def main():
    db = DatabaseManager()
    user_info_list = db.get_all_user_info()

    """
    start without admin
    """
    for user_info in tqdm(user_info_list):
        username = user_info['username']
        cname = username
        container_port = user_info['container_port']
        advisor = user_info['advisor']

        for permission_detail in user_info['permission']:
            node_name = permission_detail['name']
            docker_type = 'docker' if node_name == 'admin' else 'nvidia-docker'

            if node_name == 'admin':
                continue

            BaseHandler.rm_container_on_remote(node_name, cname)
            BaseHandler.create_container_on_remote(node_name, docker_type, cname, container_port, advisor)

            print("create %s-%s successfully." % (cname, node_name))

    """
    start with admin
    """
    for user_info in tqdm(user_info_list):
        username = user_info['username']
        cname = username
        container_port = user_info['container_port']
        advisor = user_info['advisor']

        for permission_detail in user_info['permission']:
            node_name = permission_detail['name']
            docker_type = 'docker' if node_name == 'admin' else 'nvidia-docker'

            if node_name != 'admin':
                continue

            BaseHandler.rm_container_on_remote(node_name, cname)
            BaseHandler.create_container_on_remote(node_name, docker_type, cname, container_port, advisor)

            print("create %s-%s successfully." % (cname, node_name))


if __name__ == '__main__':
    main()
