# -*- coding: utf-8 -*-
# @Time    : 2018/8/12 下午8:19
# @Author  : Zhixin Piao 
# @Email   : piaozhx@shanghaitech.edu.cn

from handler.base_handler import BaseHandler


class LoginHandler(BaseHandler):
    def get(self):
        self.render("../html/login.html", cur_user=self.get_current_user())

    def post(self):
        super_username = self.get_argument('name')
        pwd = self.get_argument('pwd')

        suid = self.db.get_suid_by_username(super_username)
        if suid is not None:
            superuser_info = self.db.get_superuser_info_by_suid(suid)
            if superuser_info['passwd'] == pwd:
                self.set_secure_cookie("user", super_username)
                self.write('yes')
                return

        self.write('no')
