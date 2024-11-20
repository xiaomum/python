import json
from json import load,dump,dumps,loads

js_file = r'C:\Users\zpy\Desktop\test.json'
jsobj = load(open(js_file)) #读取JSON文件内容
print(jsobj)

print(type(jsobj))

for key in jsobj.keys()
    print('key: %s' value: %s' % (key,jsobj.get(key)))
dict = {'name':'zhongpeiyao','age':'35','sex':'man'}
trdir = r'C:\Users\zpy\Desktop\test.json'
jsobj = dumps(dict)  #Python对象编码成JSON字符串
with open(trdir,"w") as f:
    f.write(jsobj)
    f.close()

dump(dict,open(trdir,"w")) #将Python对象编码成JSON文件