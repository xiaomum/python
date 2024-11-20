import oss2
import os
#from oss2.credentials import EnvironmentVariableCredentialsProvider
# 填写你的Access Key ID和Access Key Secret
auth = oss2.Auth('mh72SYfrjuPYhQCe','w38Ux9Z9mo8ninre2crVYD6GUf5m56')
# 填写bucket信息
bucket = oss2.Bucket(auth,'http://oss-cn-hangzhou-zjy-d01-a.ops.cloud.zhejianglab.com/','oss-zpy')

# 要上传的文件名和文件对象
#file_name ='ISO-image'
local_file = "D:\\技术栈学习\\Linux命令集\\Linux命令大全.pdf"

#上传文件
with open(local_file,'rb') as fileobj:
    fileobj.seek(0,os.SEEK_SET)
    current = fileobj.tell()
    bucket.put_object('ISO-image',fileobj)
    #bucket.put_object_from_file('ISO-image',fileobj)
print(f"{file_name} uploaded to OSS Successfully.")