# -*- coding: utf-8 -*-
# @Time    : 2018/8/22 下午9:05
# @Author  : Zhixin Piao 
# @Email   : piaozhx@shanghaitech.edu.cn

import os
import json
import multiprocessing
import math
import datetime


def get_user_name_and_run_time(pid):
    stdout = os.popen("ps -p %s -o user= -o etime=" % pid).read()
    if stdout == '':
        user_name, run_time = 'dead', 'dead'
    else:
        user_name, run_time = stdout.split()
        run_time = list(run_time)

        run_time[-3] = '分钟'

        if len(run_time) > 5:
            run_time[-6] = '小时'
        run_time = ''.join(run_time)
        run_time = run_time.replace('-', '天')
        run_time += '秒'

    if user_name == 'root':
        user_name = os.popen(''' docker inspect --format '{{.Name}}' "$(cat /proc/%d/cgroup |tail -n 1 |cut -d / -f 3)" | sed 's/^\///' ''' % pid).read()

    user_name = user_name.strip()
    run_time = run_time.strip()

    return user_name, run_time

def main():
    gpu_msg_list = os.popen("/p300/anaconda3/bin/gpustat -p -u --json").read()
    gpu_msg_list = json.loads(gpu_msg_list)

    for gpu_msg in gpu_msg_list['gpus']:
        for process in gpu_msg['processes']:
            user_name, run_time = get_user_name_and_run_time(process['pid'])
            process['username'] = user_name
            process['runtime'] = run_time

    cpu_info = os.popen("iostat -c | tail -n 2").read()
    user, nice, system, iowait, steal, idle = map(lambda x: float(x), cpu_info.split())

    cpu_utils = 100 - idle
    cpu_num = multiprocessing.cpu_count()
    cpu_msg = '%.2f%% [%d/%d]' % (cpu_utils, math.ceil(cpu_num * cpu_utils * 0.01), cpu_num)

    _, total, used, _, _, _, available = os.popen('''free -h | head -n 2 | tail -n 1''').read().split()
    memory_msg = '%s/%s' % (used, total)

    gpu_msg_list['cpu_msg'] = cpu_msg
    gpu_msg_list['memory_msg'] = memory_msg

    # convert query time format
    query_time = gpu_msg_list['query_time']
    query_time = query_time[:query_time.find('.')]
    query_time = datetime.datetime.strptime(query_time, "%Y-%m-%dT%H:%M:%S")
    query_time = query_time.strftime('%Y-%m-%d %H:%M:%S')
    gpu_msg_list['query_time'] = query_time

    print(json.dumps(gpu_msg_list, ensure_ascii=False))


if __name__ == '__main__':
    main()
