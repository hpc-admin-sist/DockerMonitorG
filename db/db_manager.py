# -*- coding: utf-8 -*-
# @Time    : 2018/8/13 下午9:35
# @Author  : Zhixin Piao 
# @Email   : piaozhx@shanghaitech.edu.cn

import pymysql
from config import DB_HOST, DB_NAME, DB_PASSWOED, DB_USERNAME
import json
import numpy as np
import datetime


class DatabaseManager:
    def __init__(self):
        self.connect()

    def connect(self):
        self.conn = pymysql.connect(DB_HOST, DB_USERNAME, DB_PASSWOED, DB_NAME)

    def get_cursor(self):
        self.conn.ping(reconnect=True)
        cursor = self.conn.cursor()

        return cursor
    
    def get_suid_by_username(self, username):
        '''
        superuser_id query
        '''
        cursor = self.get_cursor()
        cursor.execute("select suid from docker.superuser where username = '%s'" % username)
        suid = cursor.fetchone()
        suid = suid[0] if suid else None

        self.commit()
        return suid
    
    def get_superuser_info_by_suid(self, suid):
        cursor = self.get_cursor()
        cursor.execute("select suid, username, passwd from docker.superuser where suid=%s" % suid)
        superuser_info = cursor.fetchone()

        superuser_info = {
            'uid': superuser_info[0],
            'username': superuser_info[1],
            'passwd': superuser_info[2]
        }

        self.commit()
        return superuser_info

    def get_all_user_info(self):
        cursor = self.get_cursor()
        cursor.execute(
            "select uid, username,chinese_name,email, container_port, open_port_range,advisor from docker.user")
        user_base_list = cursor.fetchall()

        user_info_list = []
        for user_base in user_base_list:

            user_info = {'uid': user_base[0],
                            'username': user_base[1],
                            'chinese_name': user_base[2],
                            'email': user_base[3],
                            'container_port': user_base[4],
                            'open_port_range': user_base[5],
                            'advisor': user_base[6],
                            'permission': []
                            }

            # query user permission
            cursor.execute(
                "select node_id,longtime,start_date,end_date, reason, status from docker.permission where uid = %s" % user_info[
                    'uid'])
            user_permission_list = cursor.fetchall()

            for user_permission in user_permission_list:
                node_id, longtime, start_date, end_date, reason, status = user_permission
                if longtime == 0:
                    start_date = start_date.strftime('%Y-%m-%d %H:%M:%S')
                    end_date = end_date.strftime('%Y-%m-%d %H:%M:%S')

                node_info = {'name': 'login' if node_id == 0 else 'g%.2d' % node_id,
                                'longtime': longtime,
                                'start_date': start_date,
                                'end_date': end_date,
                                'reason': reason,
                                'status': status,
                                }
                user_info['permission'].append(node_info)

            user_info_list.append(user_info)

        self.commit()
        return user_info_list

    def get_user_detail_info_by_uid(self, uid):
        cursor = self.get_cursor()
        cursor.execute(
            "select uid,username,chinese_name,email, container_port, open_port_range,advisor from docker.user where uid = %s" % uid)
        user_base = cursor.fetchone()
        user_info = {'uid': user_base[0],
                     'username': user_base[1],
                     'chinese_name': user_base[2],
                     'email': user_base[3],
                     'container_port': user_base[4],
                     'open_port_range': user_base[5],
                     'advisor': user_base[6],
                     'permission': []
                     }
        # query user permission
        cursor.execute(
            "select node_id,longtime,start_date,end_date, reason from docker.permission where uid = %s" % user_info[
                'uid'])
        user_permission_list = cursor.fetchall()

        for user_permission in user_permission_list:
            node_id, longtime, start_date, end_date, reason = user_permission
            if longtime == 0:
                start_date = start_date.strftime('%Y-%m-%d %H:%M:%S')
                end_date = end_date.strftime('%Y-%m-%d %H:%M:%S')

            node_info = {'name': 'admin' if node_id == 0 else 'node%.2d' % node_id,
                         'longtime': longtime,
                         'start_date': start_date,
                         'end_date': end_date,
                         'reason': reason
                         }
            user_info['permission'].append(node_info)

        self.commit()
        return user_info

    def get_user_info_by_uid(self, uid):
        cursor = self.get_cursor()
        cursor.execute("select uid, username, container_port, open_port_range, advisor from docker.user where uid=%s" % uid)
        user_info = cursor.fetchone()

        self.commit()
        return user_info

    def get_user_chs_name_by_username(self, username):
        cursor = self.get_cursor()
        cursor.execute("select chinese_name from docker.user where username='%s' " % username)
        chinese_name = cursor.fetchone()
        chinese_name = chinese_name[0] if chinese_name else None

        self.commit()
        return chinese_name

    def try_to_add_user(self, username):
        '''
        before add user, we try to add user for uid
        '''
        cursor = self.get_cursor()
        cursor.execute("INSERT INTO docker.user(username) VALUES ('%s')" % username)
        cursor.execute("SELECT uid from docker.user where username = '%s'" % username)
        uid = cursor.fetchone()
        uid = uid[0] if uid else None

        self.commit()
        return uid

    def add_user(self, username, container_port, open_port_range, email, chinese_name, advisor):
        '''
        add_user actually is update operator
        '''
        cursor = self.get_cursor()
        cursor.execute(
            "UPDATE docker.user SET container_port = %s, open_port_range = '%s', email = '%s', chinese_name = '%s', advisor = '%s' WHERE username = '%s'"
            % (container_port, open_port_range, email, chinese_name, advisor, username))

        self.commit()

    def get_uid_by_username(self, username):
        cursor = self.get_cursor()
        cursor.execute("select uid from docker.user where username = '%s'" % username)
        uid = cursor.fetchone()
        uid = uid[0] if uid else None

        self.commit()
        return uid

    def delete_user(self, uid):
        cursor = self.get_cursor()
        cursor.execute("delete from docker.user where uid = %s" % uid)

        self.commit()

    def remove_user_permission(self, uid, node_list):
        cursor = self.get_cursor()
        node_list = tuple(node_list + [100])
        cursor.execute("delete from docker.permission where uid = %s and node_id in %s" % (uid, node_list))

        self.commit()

    def add_user_permission(self, uid, node_list, long_time, start_date, end_date, reason):
        """
        :param uid: int
        :param node_list: list
        :param long_time: 'yes' or 'no'
        :return:
        """
        cursor = self.get_cursor()

        cursor.execute("SELECT node_id from docker.permission where uid=%s" % uid)
        exist_node_list = cursor.fetchall()

        exist_node_list = list(map(lambda x: x[0], exist_node_list))
        node_list = filter(lambda x: x not in exist_node_list, node_list)

        if long_time == 'yes':
            for node_id in node_list:
                cursor.execute("INSERT INTO docker.permission(uid, node_id, reason) "
                               "VALUES (%s, %s, '%s')" % (uid, node_id, reason))
        else:
            for node_id in node_list:
                cursor.execute("INSERT INTO docker.permission(uid, node_id, longtime, start_date, end_date, reason) "
                               "VALUES (%s, %s, 0, '%s', '%s', '%s')" % (uid, node_id, start_date, end_date, reason))

        self.commit()
        return node_list

    def get_all_user_lifecycle(self):
        cursor = self.get_cursor()
        cursor.execute("select u.uid, u.username, l.long_time_user, l.start_date, l.end_date, l.reason "
                       "from docker.user u left join docker.lifecycle l on u.uid=l.uid ")
        user_lifecycle_list = cursor.fetchall()

        def format_user_info(user_info):
            long_time_user = True if user_info[2] == 1 else False
            using_date = '%s -- %s' % (user_info[3], user_info[4])

            user_info = {'uid': user_info[0],
                         'username': user_info[1],
                         'lifecycle': 'long time' if long_time_user else using_date,
                         'reason': user_info[5]
                         }

            return user_info

        user_lifecycle_list = list(map(format_user_info, user_lifecycle_list))

        self.commit()
        return user_lifecycle_list

    def get_node_msg_list(self):
        cursor = self.get_cursor()

        # cursor.execute('''select node_gpu_msg from docker.gpu where node_gpu_msg <> "" ''')

        cursor.execute("select node_gpu_msg from gpu,"
                       "(select node_id, max(query_time) as max_query_time from gpu where query_time <> '0000-00-00 00:00:00'  GROUP BY node_id)b "
                       "where gpu.node_id = b.node_id and gpu.query_time = max_query_time")

        node_msg_list = cursor.fetchall()

        node_msg_list = list(map(lambda x: json.loads(x[0]), node_msg_list))

        self.commit()
        return node_msg_list

    def get_node_msg_list_with_chs_name(self):
        cursor = self.get_cursor()

        # cursor.execute('''select node_gpu_msg from docker.gpu where node_gpu_msg <> "" ''')

        cursor.execute("select node_gpu_msg from gpu,"
                       "(select node_id, max(query_time) as max_query_time from gpu where query_time <> '0000-00-00 00:00:00' GROUP BY node_id)b "
                       "where gpu.node_id = b.node_id and gpu.query_time = max_query_time")

        node_msg_list = cursor.fetchall()
        node_msg_list = list(map(lambda x: json.loads(x[0]), node_msg_list))

        for node_msg in node_msg_list:
            for gpu_msg in node_msg['gpus']:
                for process in gpu_msg['processes']:
                    uname_with_node = process['username']
                    uname = uname_with_node[:uname_with_node.rfind('-')]
                    chs_name = self.get_user_chs_name_by_username(uname)
                    process['username'] = chs_name


        self.commit()
        return node_msg_list

    def commit(self):
        try:
            self.conn.commit()
        except:
            self.conn.rollback()

    def __del__(self):
        self.conn.close()


if __name__ == '__main__':
    db_manager = DatabaseManager()
    print(db_manager.check_user_exist_in_db('piaozx'))
