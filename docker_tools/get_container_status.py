# -*- coding: utf-8 -*-
# @Time    : 2018/8/22 下午9:05
# @Author  : Zhixin Piao 
# @Email   : piaozhx@shanghaitech.edu.cn

import os
import json
import multiprocessing
import math
import datetime
import re


def main():
    container_stat_list = os.popen("docker ps -a").read().split('\n')
    # key_list = [key.lower() for key in container_stat_list[0].split()]
    status_list = []
    for row in container_stat_list[1:]:
        # print(row))
        row = re.sub('  +', ',', row).split(',')
        if len(row) != 6:
            continue
        container_name = row[-1].split('-')
        username = '-'.join(container_name[:-1])
        node_id = container_name[-1]
        status = row[-2]
        status_list.append({
            'username': username,
            'node_id': node_id,
            'status': status
        })

    print(str(status_list))


if __name__ == '__main__':
    main()
