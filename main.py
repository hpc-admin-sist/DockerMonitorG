# -*- coding: utf-8 -*-
# @Time    : 2018/8/11 下午4:47
# @Author  : Zhixin Piao 
# @Email   : piaozhx@shanghaitech.edu.cn

from tornado.options import define, options
import tornado.ioloop
import tornado.web
import os
import subprocess

from handler.create_handler import CreateHandler
from handler.delete_handler import DeleteHandler
from handler.remove_handler import RemoveHandler
from handler.user_handler import UserHandler
from handler.system_handler import SystemHandler
from handler.login_handler import LoginHandler
from handler.logout_handler import LogoutHandler
from handler.index_handler import IndexHandler
from handler.permission_handler import PermissionHandler
from handler.restart_handler import RestartHandler
from handler.gpu_handler import GpuHandler

from db.db_manager import DatabaseManager

define('port', default=80, help='run on the port', type=int)


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", IndexHandler),
            (r"/login", LoginHandler),
            (r"/logout", LogoutHandler),
            (r"/system", SystemHandler),
            (r"/create", CreateHandler),
            (r"/remove", RemoveHandler),
            (r"/delete", DeleteHandler),
            (r"/permission", PermissionHandler),
            (r"/restart", RestartHandler),
            (r"/user", UserHandler),
            (r"/gpu", GpuHandler),
        ]

        settings = dict(
            cookie_secret="7CA71A57B571B5AEAC5E64C6042415DE",
            # TemplateData_path = os.path.join(os.path.dirname(__file__).decode('gbk'), u'TemplateData'),
            static_path='static',
            login_url="/login",
            debug=True
        )

        self.db = DatabaseManager()
        print('G-Cluster Monitor launched!')
        tornado.web.Application.__init__(self, handlers, **settings)


if __name__ == '__main__':
    tornado.options.parse_command_line()
    Application().listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
