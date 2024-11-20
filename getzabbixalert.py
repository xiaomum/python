#-*- condig:utf-8 -*-
#-------------------------------------------------------------------------
#获取zabbix中出现的系统重启，宕机，内核错误，空闲可用磁盘告警时，及时提醒
#Create:2021-10-18
#Mail:443601137@qq.com
#-------------------------------------------------------------------------
import json
import re
import requests
from bs4 import BeautifulSoup as Be
import time
import winsound
from lxml import etree
file = 'ls.json'
url1="https://zabbix.cmread.com/zabbix/index.php"
tabdatas={
    'name': 'guoxiaozong',
    'password' : 'Guo.zabbix',
    'autologin': '1',
    'enter': 'Sign in',
}
headers={
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36',
}

session = requests.Session()
page_text = session.get(url=url1,headers=headers).text
page_text = session.post(url1,headers=headers,data=tabdatas).text

url2 = 'https://zabbix.cmread.com/zabbix/zabbix.php?sid=8a37c080cb9c6c0f&action=widget.problems.view'


# with open(file,mode='r',encoding='utf-8') as f:
#     data = json.load(f)
# print(data)
ignorelist = []
def getData(data,ignorelist):
    soup = Be(data['body'],'lxml')
    sl = []
    host3 = []
    for m in soup.find_all('tbody')[0]:
        if len(m) == 11:
            s = ''
            for n in m:
                if m.index(n) == 0:
                    s = s + n.text
                else:
                    s = s + ',' + n.text
            sl.append(s)
    for  i in sl:
        sta = i.split(',')[4]
        host = i.split(',')[6]
        isue = i.split(',')[7]
        d = re.findall("本地时间服务|系统重启|宕机|kernel|空闲可用磁盘",str(isue))
        if (len(d)) != 0:
            if d[0] == '本地时间服务' or'系统重启' or d[0] == '宕机' or d[0] == 'kernel' or d[0] == '空闲可用磁盘':
                if sta == '问题':
                    if host not in ignorelist:
                        # print(igmorelist)
                        print(sta + ' ' + host + ' ' + isue)
                        winsound.Beep(600,5000)
                        host3.append(host)

        # for host in host3:
        #     url3 = "https://zabbix.cmread.com/zabbix/zabbix.php?action=search&search="+ host
        #     data3 = session.post(url3,headers).text
        #     tree = etree.HTML(data3)
        #     ip = tree.xpath('.//div[@class="body"]//td[2]/text()')[0]
        #     print(host + ' ' + ip)
#忽略列表，可以忽略报警的主机名加在这个列表里
ignorelist=['ZJHZ-CMREAD-MSMGW-VBUS-NJ-81','ZJHZ-PS-CMREAD-SV-CLIENTWAP31-INT-BJ','zjhz-dn120','umap_200.200.4.183']
n = 1
while True:
    print('第' + str(n) + '次开始\n')
    data = session.post(url2,headers).text
    data = json.loads(data)
    getData(data,ignorelist)
    print('第' + str(n) + '次结束\n')
    n = n + 1
    time.sleep(30)


