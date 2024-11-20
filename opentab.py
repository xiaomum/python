# -*- coding: utf-8 -*-
_auther_ = 'zpy'
_email_ = 'zhongpeiyao@139.com'
import os
import time
import webbrowser
from selenium import  webdriver
file = r'C:\Users\Administrator\Desktop\web.txt'
f = open(file,encoding="UTF_8")
url = f.readline().split('://')[-1].strip()
print(url)

url_list = f.readline().strip()
print(url_list)
for url in url_list:
    webbrowser.open(url)
f.close()


driver = webdriver.Chrome(r'C:\Users\Administrator\AppData\Local\Google\Chrome\Application\chrome.exe')
f = open(r'C:\Users\Administrator\Desktop\web.txt',encoding='UTF_8')
#file = r'C:\Users\Administrator\Desktop\web.txt'
url = f.readline().strip()
print(url)
driver.get(url)
url = f.readline().strip()
while url:
    print(url)
    js = "windows.open('" + url + "')"
    driver.execute_script(js)
    url = f.readline().strip()
f.close()
#url_li# st = ['https://www.hao123.com/','https://www.2345.com/','https://www.sina.com.cn/']

