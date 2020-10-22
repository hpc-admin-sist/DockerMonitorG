# -*- coding: utf-8 -*-
# @Time    : 2018/8/22 下午10:03
# @Author  : Zhixin Piao 
# @Email   : piaozhx@shanghaitech.edu.cn

import sys
import os

sys.path.append(os.path.abspath('./'))

from multiprocessing import Pool
import json
import pymysql
import time

from handler.base_handler import STANDARD_NODE_LIST
from config import DB_HOST, DB_NAME, DB_PASSWOED, DB_USERNAME
import re

NODE_LIST = STANDARD_NODE_LIST

def get_node_container_status(node_id):
    conn = pymysql.connect(DB_HOST, DB_USERNAME, DB_PASSWOED, DB_NAME, )
    cursor = conn.cursor()

    while True:
        node_name = 'g%02d' % node_id if node_id !=0 else 'login'
        print(f'Inspecting containers in {node_name}...', end='')

        tic = time.time()
        if node_id == 0:
            msgs = os.popen('/p300/anaconda3/bin/python /p300/g_cluster/DockerMonitor/docker_tools/get_container_status.py').read()
        else:
            msgs = os.popen('''ssh g%02d '/p300/anaconda3/bin/python /p300/g_cluster/DockerMonitor/docker_tools/get_container_status.py' ''' % node_id).read()
        msgs = eval(msgs)

        for msg in msgs:
            cursor.execute("select uid from docker.user where username = '%s'" % msg['username'])
            uid = cursor.fetchone()
            uid = uid[0] if uid else None
            if uid is None:
                continue
            status = msg['status']

            cursor.execute("SELECT uid, node_id FROM docker.permission WHERE uid=%d AND node_id=%d " % (uid, node_id))
            ret = cursor.fetchall()
            if len(ret) != 0:
                cursor.execute('''UPDATE docker.permission SET status = '%s' WHERE uid=%d AND node_id=%d''' % (status, uid, node_id))
        try:
            conn.commit()
            toc = time.time() - tic
            print('OK    ', round(toc,3), 's')
        except:
            conn.rollback()
            print('rollback')
        min_interval = 5
        if toc < min_interval:
            time.sleep(min_interval - toc)
        
    
def main():
    p = Pool(len(NODE_LIST))
    args_list = [(i,) for i in NODE_LIST]
    p.starmap(get_node_container_status, args_list)
    p.close()

if __name__ == '__main__':
    main()
