import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import re
import json
import base64
url1 = 'https://10.106.24.55/#login'
session = requests.Session()
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
passwd = 'YWRtaW4='
decode = base64.b64decode(passwd).decode("utf-8")
values = {
          'name': 'admin',
          'password': 'decode',
          'remeber': False,
          'commit': 'Login'
          }
header = { 'Accept': 'application/json, text/javascript, */*; q=0.01',
          'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:106.0) Gecko/20100101 Firefox/106.0'
           }
page_text = session.get(url1,headers=header,verify=False).text
page_text = session.post(url1,headers=header,data=values,verify=False).text
#print(page_text)
#print(page_text.content)

url2 = 'https://10.106.24.55/api/logs/eventlog?EVENTID=-3'
cookie = {'lang': 'zh-cn',
          'QSESSIONID': '09c40b90a80975d450qHhtOPwYQJPmJ4',
          'refresh_disable': '1'}
#def getdata(data,):
#if __name__== '__main__'：
data = session.post(url2,headers=header,cookies=cookie).text
data = json.loads(data)
print(data)
jsobj = json.dumps(data)
trdir = r'C:\Users\zpy\Desktop\1.json'
#with open(trdir,"w") as f:
    #f.write(jsobj)
    #f.close
json.dump(jsobj,open(trdir,"w"))


