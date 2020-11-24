#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : python_h3c.py
# @Author: shijiu.Xu
# @Date  : 2020/11/24 
# @SoftWare  : PyCharm
# https://blog.csdn.net/q13554515812/article/details/89739517?utm_medium=distribute.pc_relevant.none-task-blog-BlogCommendFromBaidu-2.control&depth_1-utm_source=distribute.pc_relevant.none-task-blog-BlogCommendFromBaidu-2.control

import paramiko


class H3cToPython():

    def __init__(self, ip, port, user, pwd):
        self.ip = ip
        self.port = port
        self.user = user
        self.pwd = pwd
        self.conn = paramiko.Transport((self.ip, self.port))
        self.conn.connect(username=self.user, password=self.pwd)
        self.ssh = paramiko.SSHClient()
        self.ssh._transport = self.conn

    def get_all_port(self):
        stdin, stdout, stderr = self.ssh.exec_command('display interface brief', get_pty=True)
        out = str(stdout.read()).split('<H3C>')[1].split(r'\r\r\n')
        for o in out:
            print(o)

    def get_port_detail(self, port_name):
        stdin, stdout, stderr = self.ssh.exec_command('display interface %s' % port_name, get_pty=True)
        out = str(stdout.read()).split('<H3C>')[1].split(r'\r\r\n')
        for o in out:
            print(o)

    def get_port_ip(self):
        stdin, stdout, stderr = self.ssh.exec_command('dis arp', get_pty=True)
        out = str(stdout.read()).split('<H3C>')[1].split(r'\r\r\n')
        for o in out:
            print(o)


if __name__=="__main__":
    h3c = H3cToPython('171.106.48.55', 33801, 'admin', 'GXfy/2014!')
    print("********************************")
    print("输入 1： 获取所有的端口信息")
    print("输入 2： 获取指定端口的详细信息")
    print("输入 3： 获取端口占用的IP")
    print("********************************")
    want = input("请输入你需要的功能: ")
    if want == "1":
        h3c.get_all_port()
    if want == "2":
        port_name = input("请输入指定的端口号，比如：GE1/0/23")
        h3c.get_port_detail(port_name)
    if want == "3":
        h3c.get_port_ip()
