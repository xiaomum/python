import ssl
#import pysphere
from pysphere.vi_property import VIProperty
from pysphere.vi_server import VIServer
from pyVim import connect
import pyVmomi
ssl._create_default_https_context = ssl._create_unverified_context
host_ip = '10.211.93.236'
username = 'dengyy@vsphere.local'
passwd = '*IK<0okm'
connect.Connect()
#s = VIServer()
s = connect(host_ip, username, passwd)
hosts = s.get_hosts()

for host in hosts:
    p = VIProperty(s, host)
    HostName = p.name
    HostCpuUsage = p.summary.quickStats.overallCpuUsage
    HostMemoryUsage = p.summary.quickStats.overallMemoryUsage
    HostNumCpuCores = p.summary.hardware.numCpuCores
    HostMhzPerCore = p.summary.hardware.cpuMhz
    HostCpuTotal = (HostNumCpuCores * HostMhzPerCore)
    HostTotalMemory = p.summary.hardware.memorySize / 1048576
    HostCpuUsagePercent = ((HostCpuUsage * 100) / HostCpuTotal)
    HostMemoryUsagePercent = ((HostMemoryUsage * 100) / HostTotalMemory)

    print("%s | CpuUsage=%s MemoryUsage=%s" % (HostName, str(HostCpuUsage), str(HostMemoryUsage)))
    print("%s | TotalCpu=%s TotalMemory=%s" % (HostName, str(HostCpuTotal), str(HostTotalMemory)))
    print("%s | CpuUsagePercent=%s MemoryUsagePercent=%s" % (HostName, str(HostCpuUsagePercent), str(HostMemoryUsagePercent)))

s.disconnect()
pyVmomi.QueryTypes.AddVersion()