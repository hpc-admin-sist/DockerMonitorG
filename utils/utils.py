import os
import pathlib


class ContainerAdditionStr:

    def __init__(self, node_name, advisor, cname):
        self.node_name = node_name
        self.advisor = advisor
        self.group_mapping = {
            '何旭明': 'plus_group',
            '高盛华': 'svip_group'
        }
        self.username = cname

    def get_node_addition_str(self):
        addition_str = ""
        banned_users = ['yanshp']
        '''
        set motd 
        '''
        if self.username not in banned_users:
            if self.node_name == 'login':
                addition_str = ' -v /p300/motd/login_motd:/etc/motd:ro '
            else:
                addition_str = ' -v /p300/motd/g_motd:/etc/motd:ro '

        '''
        restrict admin memory usage
        '''
        # if self.node_name == 'admin':
        #     addition_str += " -m 4G --memory-swap 8G --memory-reservation 2G "

        return addition_str

    def get_advisor_addition_str(self):
        addition_str = ""
        if self.advisor in self.group_mapping:
            group_dir = f'/p300/{self.group_mapping[self.advisor]}'
            readonly_dir = f'/p300/{self.group_mapping[self.advisor]}/readonly'
            pathlib.Path(group_dir).mkdir(parents=True, exist_ok=True)
            pathlib.Path(readonly_dir).mkdir(parents=True, exist_ok=True)
            addition_str += f' -v {group_dir}:/group ' \
                f' -v {readonly_dir}:/group/readonly:ro '
        return addition_str

    def get_user_addition_str(self):
        addition_str = ""
        if self.username == "zhangxy" and self.node_name == "admin":
            addition_str += " -v /public/docker/huangshy/root/huangshy/:/root/huangshy "
        elif self.username == "piaozx":
            addition_str += " -v /p300/docker/liuwen:/p300_liuwen "
            addition_str += " -v /p300/docker/xuyy:/p300_xuyy "
            addition_str += " -v /p300/docker/liuyf:/p300_liuyf "
        elif self.username == 'liuwen':
            addition_str += " -v /p300/docker/piaozx:/p300_piaozx"

        return addition_str

    def get_additional_str(self):

        str = self.get_node_addition_str() + self.get_advisor_addition_str() + self.get_user_addition_str()
        print(str)
        return str
