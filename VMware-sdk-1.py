import atexit
from pyVim import connect

#Connect to Server
def get_args():
if  args.disable_ssl_verification:        #no check SSL certification
          service_instance=connect.SmartConnectNoSSL(host=args.host,
                                                   user=args.user,
                                                   pwd=args.password,
                                                   port=int(args.port))

else:  #check SSL certification
    service_instance=connect.SmartConnect(host=args.host,
                                         user=args.user,
                                         pwd=args.password,
                                         port=int(args.port))

#Disconnect from Server
atexit.register(connect.Disconnect,service_instance)