from email import message
import smtplib
import base64

msg = message.EmailMessage()
msg["From"] = 'zhongpeiyao@139.com'
msg["To"] = 'zhongpy@zhejianglab.com'
msg ['subject'] = '测试邮件'
msg.set_content("民工兄弟，今天该你值班了，请关注当天的告警哦")
#tolist = sys.args[1]

def sender_msg(username,passwd):
    server = smtplib.SMTP_SSL('smtp.139.com',465)
    server.login(username,passwd)
    server.send_message(msg)
    server.close()
if __name__== '__main__':
   #pass = base64.b64decode('WnB5MTk4NDAzMDkx').decode("utf-8")
   username = 'zhongpeiyao'
   passwd = 'WnB5MTk4NDAzMDkxQA=='
   decode = base64.b64decode(passwd).decode("utf-8")
   #print("pass is :",decode)
   sender_msg(username,decode)