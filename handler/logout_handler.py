# -*- coding: utf-8 -*-
# @Time    : 2018/8/12 下午8:19
# @Author  : Zhixin Piao 
# @Email   : piaozhx@shanghaitech.edu.cn

from handler.base_handler import BaseHandler
from config import WEBSITE_ACCOUNT_LIST


class LogoutHandler(BaseHandler):
    def get(self):
        self.clear_cookie("user")
        self.redirect(r"/")

    def post(self):
        pass