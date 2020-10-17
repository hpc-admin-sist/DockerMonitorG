from handler.base_handler import BaseHandler
import datetime
import time
import json
import os
from multiprocessing import Pool
from utils import utils


class RestartHandler(BaseHandler):
    def get(self):
        self.redirect(r"/permission")

    def post(self):
        """
        """
        if self.get_current_user() is not None:
            container_name = self.get_argument('container_name')
            print(f'---- Restarting "{container_name}" ----')
            self.restart_container_on_remote(container_name)

        self.redirect(r"/permission")
