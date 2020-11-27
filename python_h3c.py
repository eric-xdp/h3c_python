#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : python_h3c.py
# @Author: shijiu.Xu
# @Date  : 2020/11/24 
# @SoftWare  : PyCharm
# https://blog.csdn.net/q13554515812/article/details/89739517?utm_medium=distribute.pc_relevant.none-task-blog-BlogCommendFromBaidu-2.control&depth_1-utm_source=distribute.pc_relevant.none-task-blog-BlogCommendFromBaidu-2.control

import paramiko
import sqlsever as sqls
import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
import configparser
import time
import mythreading


class H3cToPython():

    def __init__(self, ip, port, user, pwd, switch_name):
        self.ip = ip
        self.port = port
        self.user = user
        self.pwd = pwd
        self.switch = switch_name
        self.conn = paramiko.Transport((self.ip, self.port))
        self.conn.connect(username=self.user, password=self.pwd)
        self.ssh = paramiko.SSHClient()
        self.ssh._transport = self.conn

    def get_all_port(self):
        stdin, stdout, stderr = self.ssh.exec_command('display interface brief', get_pty=True)
        out = str(stdout.read()).split('<H3C>')[1].replace(r'\t', '').split(r'\r\r\n')
        out_data = []
        out_list = []
        for o in out:
            if 'Vlan3' in o:
                for p in o.split(' '):
                    if '.' in p:
                        out_data.append(p)
            if 'GE1' in o:
                out_data.append(o.split(' ')[0])
                for s in o.split(' '):
                    if 'UP' in s or 'DOWN' in s:
                        out_data.append(s)
                        out_data.append(str(datetime.datetime.now()).split('.')[0])
                out_list.append(tuple(out_data))
                out_data = [out_data[0]]
        return out_list

    def get_port_detail(self, port_name):
        stdin, stdout, stderr = self.ssh.exec_command('display interface %s' % port_name, get_pty=True)
        out = str(stdout.read()).split('<H3C>')[1].replace(r'\t', '').split(r'\r\r\n')
        out_data = []
        in_data = ['Description', 'Current state:']
        for o in out:
            for s in in_data:
                if s in o:
                    out_data.append(o)
        print(out_data)

    def get_port_ip(self):
        stdin, stdout, stderr = self.ssh.exec_command('dis arp', get_pty=True)
        out = str(stdout.read()).split('<H3C>')[1].replace(r'\t', '').split(r'\r\r\n')
        ip_list = []
        detail = [self.switch]
        for i in range(3, len(out)):
            for d in out[i].split(' '):
                if '.' in d:
                    detail.append(d)
                if '-' in d:
                    detail.append(d)
                if 'GE1/' in d:
                    detail.append(d)
                    ip_list.append(tuple(detail))
            detail = [self.switch]
        return ip_list


def insert_sql(info, sql):
    data = []
    for i in info:
        data += i
    odb.ExecuteMany(sql, data)



def get_switch(switch_name):
    if switch_name == 'all':
        sql = "SELECT * FROM [db_switch]"
    else:
        sql = "SELECT * FROM [db_switch] WHERE switchName = '%s'" % switch_name
    info = odb.ExecQuery(sql)
    if info is not None: return info


def get_all_switch(section):
    h3c = H3cToPython(section[0], int(section[1]), section[2], section[3], section[4])
    return h3c.get_all_port()


def get_up_port_ip(section):
    h3c = H3cToPython(section[0], int(section[1]), section[2], section[3], section[4])
    return h3c.get_port_ip()


def run30min():
    # 当交换机多的时候，多线程执行交换机
    t_list = []
    sql = 'INSERT INTO [h3cPort] (h3cIp, portName, status, updateTime) VALUES (?, ?, ?, ?)'
    switchs = get_switch('all')
    start = time.time()
    for section in switchs:
        t = mythreading.MyThread(get_all_switch, (section,))
        t.start()
        t.join()
        t_list.append(t.get_result())

    print("当前时间：", datetime.datetime.now())
    insert_sql(t_list, sql)
    print(time.time() - start)


def process_all_port():
    # 定时执行
    sched = BlockingScheduler()
    sched.add_job(run30min, 'interval', seconds=int(conf.get('SQL', 'frequency')))
    sched.start()


# 获取指定交换机UP状态端口的所有IP
def process_get_ip(switch_name):
    info = get_switch(switch_name)
    detail_list = []
    sql = 'INSERT INTO [db_switch_ip] (bySwitch, ipAddress, macAddress, switchInterface) VALUES (?, ?, ?, ?)'
    start = time.time()
    for sw in info:
        t = mythreading.MyThread(get_up_port_ip, (sw,))
        t.start()
        t.join()
        detail_list.append(t.get_result())
    print("当前时间：", datetime.datetime.now())
    insert_sql(detail_list, sql)
    print(time.time() - start)


if __name__ == "__main__":

    conf = configparser.ConfigParser()
    conf.read_file(open('conf.cfg'))
    odb = sqls.ODBC(server=conf.get('SQL', 'server'), uid=conf.get('SQL', 'uid'),
                    pwd=conf.get('SQL', 'pwd'), db=conf.get('SQL', 'db'))

    # 定时执行
    # process_all_port()
    # 获取指定交换机所有UP状态端口的IP。
    process_get_ip('外网入口1')
    # run30min()

