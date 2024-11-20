# -*- coding: utf-8 -*-
from pyVim.connect import SmartConnectNoSSL,SmartConnect,Disconnect
from pyVmomi import vim,vmodl
import pyVmomi
import time
import json
import ssl
from openpyxl import Workbook

class connect(object):
    #收集Vcenter中数据中心，主机集群，主机，网络，虚拟机，的信息
    def __init__(self,host,user,pwd,port):
        context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        context.verify_mode = ssl.CERT_NONE
        self.si = SmartConnect(host=host,user=user,pwd=pwd,port=port,sslContext=context)
        self.content = self.si.RetrieveContent()
        datacenter = self.content.rootFolder.childEntity[0]
        self.datacentername = datacenter.name
        print(self.datacentername)

    def get_cluster_list(self):
        """
        获取所有机器资源使用情况
        1。CPU
        2。内存
        3。磁盘
        :return:
        """
        # 获取集群视图
        objview = self.content.viewManager.CreateContainerView(self.content.rootFolder, [vim.ComputeResource], True)
        # 获取集群对象
        clusters = objview.view
        # 销毁视图
        objview.Destroy()

        redata = []
        for cluster in clusters:
            summary = cluster.summary
            cpuusage = 0
            memusage = 0
            vmcount = 0
            for host in cluster.host:
                # print "主机已使用cpu", host.summary.quickStats.overallCpuUsage
                # print "主机已使用内存", host.summary.quickStats.overallMemoryUsage
                cpuusage += host.summary.quickStats.overallCpuUsage #CPU总使用率
                memusage += host.summary.quickStats.overallMemoryUsage #内存总使用率
                vmcount += len(host.vm) #虚拟机总数
                return cpuusage,memusage,vmcount


            totaldatastore = 0
            datastorefree = 0
            for datastore in cluster.datastore:
                totaldatastore += datastore.summary.capacity #可用存储总量
                datastorefree += datastore.summary.freeSpace #剩余可置备存储
            # print("---------------------------------")
            # print "集群名称：", cluster.name
            # print "集群状态：", summary.overallStatus
            # print "总主机数：", summary.numHosts
            # print "vm数量：", vmcount
            # print "cpu颗数：", summary.numCpuCores
            # print "总cpu：%.2f GHz" % (summary.totalCpu / 1000.0)
            # print "已使用cpu: %.2f GHz" % (cpuusage / 1000.0)
            # print "总内存：%.2f GB" % (summary.totalMemory / 1024 / 1024 / 1024.0)
            # print "已使用mem: %.2f GB" % (memusage / 1024.0)
            # print "总存储: %.2f T" % (totaldatastore / 1024 / 1024 / 1024 / 1024.0)
            # print "可用存储: %.2f T" % (datastorefree / 1024 / 1024 / 1024 / 1024.0)
            clusterdata = {
                "clustername": cluster.name,  #集群名称
                "overallstatus": summary.overallStatus, #集群状态
                "numhosts": summary.numHosts, #总物理主机数
                "numcpucores": summary.numCpuCores, #CPU颗数
                "cputotal": "%.2f GHz" % (summary.totalCpu / 1000.0),
                "cpuusage": "%.2f GHz" % (cpuusage / 1000.0),
                "memtotal": "%.2f GB" % (summary.totalMemory / 1024 / 1024 / 1024.0),
                "memusage": "%.2f GB" % (memusage / 1024.0),
                "totaldatastore": "%.2f T" % (totaldatastore / 1024 / 1024 / 1024 / 1024.0),
                "datastorefree": "%.2f T" % (datastorefree / 1024 / 1024 / 1024 / 1024.0),
                "vmcount": vmcount,
                "datacentername": datacentername,
            }
            redata.append(clusterdata)
        return redata

    def print_vm_info(self, virtual_machine):
        """
        Print information for a particular virtual machine or recurse into a
        folder with depth protection
        """
        summary = virtual_machine.summary
        if summary.guest.ipAddress:
            return
        count += 1
        print("Name: ", summary.config.name)
        print("Template: ", summary.config.template)
        print("Path: ", summary.config.vmPathName)
        print("Guest: ", summary.config.guestFullName)
        print("Instance UUID: ", summary.config.instanceUuid)
        print("Bios UUID: ", summary.config.uuid)
        annotation = summary.config.annotation
        if annotation:
            print("Annotation : ", annotation)
        print("State      : ", summary.runtime.powerState)
        if summary.guest is not None:
            ip_address = summary.guest.ipAddress
            tools_version = summary.guest.toolsStatus
            if tools_version is not None:
                print("VMware-tools: ", tools_version)
            else:
                print("Vmware-tools: None")
            if ip_address:
                print("IP: ", ip_address)
            else:
                print("IP: None")
        if summary.runtime.question is not None:
            print("Question  : ", summary.runtime.question.text)
        print("")

    def get_all_vm(self):
        count = 0
        container = self.content.rootFolder
        viewType = [vim.VirtualMachine]
        recursive = True
        containerView = self.content.viewManager.CreateContainerView(
            container, viewType, recursive)
        children = containerView.view

        for child in children:
            print_vm_info(child)
        print(count)
        print(len(children))

    def get_vm_count(self):

        container = self.content.rootFolder
        viewType = [vim.VirtualMachine]
        recursive = True
        containerView = self.content.viewManager.CreateContainerView(
            container, viewType, recursive)
        children = containerView.view
        return len(children)

    def get_datacenter_list(self):
        """
        数据中心信息
        :return:
        """

        objview = self.content.viewManager.CreateContainerView(self.content.rootFolder, [vim.ComputeResource], True)
        # 获取集群对象
        clusters = objview.view
        # 销毁视图
        objview.Destroy()

        # cpu总大小
        cputotal = 0
        # 使用cpu
        cpuusage = 0
        memtotal = 0
        memusage = 0
        totaldatastore = 0
        datastorefree = 0
        numHosts = 0
        numCpuCores = 0
        datastore_list = []

        for cluster in clusters:
            summary = cluster.summary
            for host in cluster.host:
                cpuusage += host.summary.quickStats.overallCpuUsage
                memusage += host.summary.quickStats.overallMemoryUsage

            for datastore in cluster.datastore:
                datastore_list.append(datastore)
            cputotal += summary.totalCpu
            memtotal += summary.totalMemory
            numHosts += summary.numHosts
            numCpuCores += summary.numCpuCores

            # print("---------------------------------")
            # print "集群名称：", cluster.name
            # print "集群状态：", summary.overallStatus
            # print "总主机数：", summary.numHosts
            # print "cpu颗数：", summary.numCpuCores
            # print "总cpu：%.2f GHz" % (summary.totalCpu / 1000.0)
            # print "已使用cpu: %.2f GHz" % (cpuusage / 1000.0)
            # print "总内存：%.2f GB" % (summary.totalMemory / 1024 / 1024 / 1024.0)
            # print "已使用mem: %.2f GB" % (memusage / 1024.0)
            # print "总存储: %.2f T" % (totaldatastore / 1024 / 1024 / 1024 / 1024.0)
            # print "可用存储: %.2f T" % (datastoreusage / 1024 / 1024 / 1024 / 1024.0)
            # clusterdata = {"clustername": cluster.name,
            #                "overallStatus": summary.overallStatus,
            #                "numHosts": summary.numHosts,
            #                "numCpuCores": summary.numCpuCores,
            #                "totalCpu": "%.2f GHz" % (summary.totalCpu / 1000.0),
            #                "cpuusage": "%.2f GHz" % (cpuusage / 1000.0),
            #                "totalMemory": "%.2f GB" % (summary.totalMemory / 1024 / 1024 / 1024.0),
            #                "memusage": "%.2f GB" % (memusage / 1024.0),
            #                "totaldatastore": "%.2f T" % (totaldatastore / 1024 / 1024 / 1024 / 1024.0),
            #                "datastoreusage": "%.2f T" % (datastoreusage / 1024 / 1024 / 1024 / 1024.0),
            #                }
            # redata.append(clusterdata)

        for datastore in set(datastore_list):
            totaldatastore += datastore.summary.capacity
            datastorefree += datastore.summary.freeSpace

        return {
            "cputotal": "%.2f GHz" % (cputotal / 1000.0),
            "cpuusage": "%.2f GHz" % (cpuusage / 1000.0),
            "memtotal": "%.2f GB" % (memtotal / 1024 / 1024 / 1024.0),
            "memusage": "%.2f GB" % (memusage / 1024.0),
            "totaldatastore": "%.2f T" % (totaldatastore / 1024 / 1024 / 1024 / 1024.0),
            "datastorefree": "%.2f T" % (datastorefree / 1024 / 1024 / 1024 / 1024.0),
            "numhosts": numHosts,
            "numcpucores": numCpuCores,
            "vmcount": get_vm_count(),
            "datacentername": datacentername,
        }

    def get_datastore_list(self):
        objview = self.content.viewManager.CreateContainerView(self.content.rootFolder, [vim.Datastore], True)
        objs = objview.view
        objview.Destroy()
        # 存储部分
        # 存储集群环境-通过单个存储汇总得到存储集群得容量情况
        cluster_store_dict = {}
        datastore_list = []
        for i in objs:
            capacity = "%.2f G" % (i.summary.capacity / 1024 / 1024 / 1024.0)
            freespace = "%.2f G" % (i.summary.freeSpace / 1024 / 1024 / 1024.0)
            datastore_summary = {
                "cluster_store_name": "默认集群目录" if i.parent.name == "datastore" else i.parent.name,
                "datacentername": self.datacentername,
                "datastore": str(i.summary.datastore),
                "name": i.summary.name,
                "url": i.summary.url,  # 唯一定位器
                "capacity": capacity,
                "freespace": freespace,
                "type": i.summary.type,
                "accessible": i.summary.accessible,  # 连接状态
                "multiplehostaccess": i.summary.multipleHostAccess,  # 多台主机连接
                "maintenancemode": i.summary.maintenanceMode  # 当前维护模式状态
            }
            datastore_list.append(datastore_summary)
        return datastore_list

    def get_host_list(self):
        """
        vcenter下物理主机信息
        :return:
        """
        objview = self.content.viewManager.CreateContainerView(self.content.rootFolder, [vim.HostSystem], True)
        objs = objview.view
        objview.Destroy()
        host_list = []
        for host in objs:
            """物理信息"""
            # 厂商
            vendor = host.summary.hardware.vendor
            # 型号
            model = host.summary.hardware.model
            uuid = host.summary.hardware.uuid
            # cpu信号
            cpumodel = host.summary.hardware.cpuModel
            # cpu插槽
            numcpupkgs = host.summary.hardware.numCpuPkgs
            # cpu核心
            numcpucores = host.summary.hardware.numCpuCores
            # 逻辑处理器
            numcputhreads = host.summary.hardware.numCpuThreads
            # cpuMhz
            cpumhz = host.summary.hardware.cpuMhz
            # cpu总Ghz
            cpusize = "%.2f GHz" % (host.summary.hardware.cpuMhz * host.summary.hardware.numCpuCores / 1000.0)
            # 使用cpu
            cpuusage = "%.2f GHz" % (host.summary.quickStats.overallCpuUsage / 1000.0)
            # 内存大小 G
            memorysize = "%.2f G" % (host.summary.hardware.memorySize / 1024 / 1024 / 1024.0)
            memusage = "%.2f G" % (host.summary.quickStats.overallMemoryUsage / 1024.0)
            # 运行时间
            uptime = host.summary.quickStats.uptime

            """运行状态"""
            # 主机连接状态
            connectionstate = host.runtime.connectionState
            # 主机电源状态
            powerstate = host.runtime.powerState
            # 主机是否处于维护模式
            inmaintenancemode = host.runtime.inMaintenanceMode
            """基础信息"""
            name = host.name
            # EXSI版本
            fullname = host.summary.config.product.fullName
            """关联信息"""
            clustername = host.parent.name
            datacentername = datacentername
            # 多对多
            network = [network.name for network in host.network]
            datastore = [datastore.name for datastore in host.datastore]
            data = {
                "name": name,
                "clustername": clustername,
                "datacentername": datacentername,
                "network": network,
                "datastore": datastore,
                "connectionstate": connectionstate,
                "powerstate": powerstate,
                "inmaintenancemode": inmaintenancemode,
                "vendor": vendor,
                "model": model,
                "uuid": uuid,
                "cpumodel": cpumodel,
                "numcpupkgs": numcpupkgs,
                "numcpucores": numcpucores,
                "numcputhreads": numcputhreads,
                "cpumhz": cpumhz,
                "cpusize": cpusize,
                "cpuusage": cpuusage,
                "memorysize": memorysize,
                "memusage": memusage,
                "uptime": uptime,
            }

            host_list.append(data)
        return host_list

    def get_networkport_group_list(self):
        objview = self.content.viewManager.CreateContainerView(self.content.rootFolder, [vim.Network], True)
        objs = objview.view
        objview.Destroy()
        network_list = []
        for networkobj in objs:
            name = networkobj.name
            # network = networkobj.summary.network
            accessible = networkobj.summary.accessible
            # 分布式交换机名称
            try:
                distributedvirtualswitchname = networkobj.config.distributedVirtualSwitch.name
                key = networkobj.config.key
                vlanid = networkobj.config.defaultPortConfig.vlan.vlanId
                type = "上行链路端口组"
                if not isinstance(vlanid, int):
                    vlanid = "0-4094"
                    type = "分布式端口组"
            except AttributeError:
                continue

            data = {
                "name": name,
                "datacentername": datacentername,
                "key": key,
                "accessible": accessible,
                "distributedvirtualswitchname": distributedvirtualswitchname,
                "vlanid": vlanid,
                "type": type,
            }
            network_list.append(data)
        return network_list

    def get_vm_list(self):
        objview = self.content.viewManager.CreateContainerView(self.content.rootFolder, [vim.VirtualMachine], True)
        objs = objview.view
        objview.Destroy()
        vm_list = []
        allstime = time.time()
        count = 0
        for vm_machine in objs:
            count += 1
            starttime = time.time()
            # print(count)
            # 虚拟机名称
            name = vm_machine.name
            # EXSI主机
            host = vm_machine.summary.runtime.host.name
            """运行状态"""
            # 连接状态
            connectionstate = vm_machine.summary.runtime.connectionState
            # 电源状态
            powerstate = vm_machine.summary.runtime.powerState
            """guest模版-"""
            # vmwareTools 安装情况
            toolsstatus = vm_machine.summary.guest.toolsStatus
            # 系统内hostname
            hostname = vm_machine.summary.guest.hostName

            """config"""
            uuid = vm_machine.summary.config.uuid
            # 是否模版
            template = vm_machine.summary.config.template
            # vm文件路径
            vmpathname = vm_machine.summary.config.vmPathName
            # cpu 颗数
            numcpu = vm_machine.summary.config.numCpu
            # 内存总大小
            memtotal = vm_machine.summary.config.memorySizeMB
            # 网卡数
            numethernetcards = vm_machine.summary.config.numEthernetCards
            # 虚拟磁盘数量
            numvirtualdisks = vm_machine.summary.config.numVirtualDisks
            # 已使用存储容量
            storage_usage = "%.2fG" % (vm_machine.summary.storage.committed / 1024 / 1024 / 1024.0)
            # cpu使用Mhz
            cpuusage = vm_machine.summary.quickStats.overallCpuUsage
            # MB
            memusage = vm_machine.summary.quickStats.guestMemoryUsage
            # 开机时间
            uptime = vm_machine.summary.quickStats.uptimeSeconds
            # 运行状态
            overallstatus = vm_machine.summary.overallStatus
            # 网络
            network = [i.name for i in vm_machine.network]
            # 虚拟磁盘信息
            virtualdisk = []
            try:
                for disk in vm_machine.config.hardware.device:
                    try:
                        if hasattr(disk, "diskObjectId"):
                            label = disk.deviceInfo.label
                            capacityinkb = disk.capacityInKB
                            virtualdisk.append({"label": label, "capacityinkb": capacityinkb})
                    except AttributeError:
                        pass
            except AttributeError:
                # print("----------什么都没有的------------")
                continue
            # print virtualdisk
            virtualdiskinfo = json.dumps(virtualdisk)

            # IP信息
            ipaddress = vm_machine.guest.ipAddress
            other_ip = set()
            for vmnet in vm_machine.guest.net:
                for ip in vmnet.ipAddress:
                    other_ip.add(ip)

            data = {
                "name": name,
                "host": host,
                "datacentername": datacentername,
                "ipaddress": ipaddress,
                "other_ip": json.dumps(list(other_ip)),
                "connectionstate": connectionstate,
                "powerstate": powerstate,
                "toolsstatus": toolsstatus,
                "hostname": hostname,
                "uuid": uuid,
                "template": template,
                "vmpathname": vmpathname,
                "numcpu": numcpu,
                "memtotal": memtotal,
                "numethernetcards": numethernetcards,
                "numvirtualdisks": numvirtualdisks,
                "storage_usage": storage_usage,
                "cpuusage": cpuusage,
                "memusage": memusage,
                "uptime": uptime,
                "overallstatus": overallstatus,
                "network": network,
                "virtualdiskinfo": virtualdiskinfo,
            }

            vm_list.append(data)
            # print time.time()-starttime

        print ("allover---", time.time() - allstime)
        return vm_list

    def print_vc_event(self):
        objview =self.content.viewManager.CreateContainerView(self.content.rootFolder,[pyVmomi.CoreTypes])

        objs = objview.view
        objview.Destroy()


if __name__ == '__main__':
    obj = connect(host='10.211.93.236',user='test',pwd='*IK<0okm',port=443)
    print(obj.get_cluster_list())

    """ 
    list = obj.get_cluster_list()
    wb = Workbook()
    sheet = wb.active
    sheet.title ='存储'
    for i in list:
        sheet.append(i)
    wb.save(r'D:\咪咕文档\虚拟化资源池使用统计\1.xlsx')
    """
