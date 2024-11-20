# VMware操作类
# author: zpy
# 时间: 2021-08-16
from pyVmomi import ServerObjects
from pyVim.connect import SmartConnectNoSSL
from pyVmomi import vim
#from logging.handlers import info
import logging




class VMware:
    def __init__(self):
        self.log = logging.info()
        self.log.info("调用VMware操作类")
        self.log.info(self.__class__)
        self.ip = None
        self.port = 443
        self.username = None
        self.password = None

        self.client = None
        self.content = None
        self.result = None
        self.message = None

    def get_client(self):
        """
        创建连接
        """
        self.log.debug("创建连接")
        try:
            self.client = SmartConnectNoSSL(host=self.ip,
                                            user=self.username,
                                            pwd=self.password,
                                            port=self.port
                                            )
            self.content = self.client.RetrieveContent()
            self.result = True
        except Exception as e:
            self.result = False
            self.message = e

    def _get_all_objs(self, obj_type, folder=None):
        """
        根据对象类型获取这一类型的所有对象
        """
        if folder is None:
            container = self.content.viewManager.CreateContainerView(self.content.rootFolder, obj_type, True)
        else:
            container = self.content.viewManager.CreateContainerView(folder, obj_type, True)
        return container.view

    def _get_obj(self, obj_type, name):
        """
        根据对象类型和名称来获取具体对象
        """
        obj = None
        content = self.client.RetrieveContent()
        container = content.viewManager.CreateContainerView(content.rootFolder, obj_type, True)
        for c in container.view:
            if c.name == name:
                obj = c
                break
        return obj

    def get_datacenters(self):
        """
        返回所有的数据中心
        """
        return self._get_all_objs([vim.Datacenter])

    def get_ClusterComputeResource_by_name(self, name):
        """
        根据集群名称查询对象
        """
        return self._get_obj([vim.ClusterComputeResource], name)

    def get_HostSystem_by_name(self, name):
        """
        根据物理机名称查询对象
        """
        return self._get_obj([vim.HostSystem], name)

    def get_VirtualMachine_by_name(self, name):
        """
        根据虚拟机机名称查询对象
        """
        return self._get_obj([vim.VirtualMachine], name)

    def get_pm_summary(self, name):
        """
        查询物理机信息
        """
        hostSystem_obj = self.get_HostSystem_by_name(name=name)
        return hostSystem_obj.summary

    def get_vm_summary(self, name):
        """
        查询虚拟机信息
        """
        virtualMachine_obj = self.get_VirtualMachine_by_name(name=name)
        return virtualMachine_obj.summary

    def get_pm_obj(self, name):
        """
        根据物理机名称组装对象
        """
        self.log.debug("物理机名称:" + name)
        hostSystem_obj = self.get_HostSystem_by_name(name=name)

        pm_obj = {
            "name": name,
            "type": "pm",
            "uuid": hostSystem_obj.summary.hardware.uuid,
            "child": [],
        }

        # 物理机下的虚拟机
        vm_data = []
        for v in hostSystem_obj.vm:
            # 虚拟化对象
            vm_obj = {
                "name": v.name,
                "type": "vm",
                "uuid": str(v.summary.config.instanceUuid),
            }
            vm_data.append(vm_obj)
        pm_obj["child"] = vm_data
        return pm_obj

    def get_data(self):
        """
        集群对象类型：[vim.ClusterComputeResource]
        物理机对象类型：[vim.HostSystem]
        虚拟机对象：[vim.VirtualMachine]
        获取 Vcenter 下 数据中心，集群结构与 物理机 虚拟机的层级关系
        """
        datacenter_objs = self.get_datacenters()
        data = []
        # 获取数据中心
        for i in datacenter_objs:

            self.log.debug("数据中心名称:" + i.name)

            datacenter_obj = {
                "name": i.name,
                "type": "datacenter",
                "child": [],
            }

            # 根据数据中心的对象类型
            for j in i.hostFolder.childEntity:

                self.log.debug("类型:" + str(type(j)))

                # 集群
                if type(j) == vim.ClusterComputeResource:
                    self.log.debug("集群名称:" + j.name)
                    cluster_obj = {
                        "name": j.name,
                        "type": "cluster",
                        "child": [],
                    }
                    clusterComputeResource_obj = self.get_ClusterComputeResource_by_name(name=j.name)

                    # 集群下的物理机
                    pm_data = []
                    for h in clusterComputeResource_obj.host:
                        pm_obj = self.get_pm_obj(name=h.name)
                        pm_data.append(pm_obj)

                    cluster_obj["child"] = pm_data
                    datacenter_obj["child"].append(cluster_obj)

                # 物理机
                elif type(j) == vim.ComputeResource:
                    pm_obj = self.get_pm_obj(name=j.name)
                    datacenter_obj["child"].append(pm_obj)

            data.append(datacenter_obj)

        self.log.debug("data:")
        self.log.debug(data)
        return data


if __name__ == '__main__':
    vm = VMware()
    vm.ip = "10.211.93.236"
    vm.username = "dengyy"
    vm.password = "*IK<0okm"
    vm.get_client()
    # 得到结构数据
    #vm.get_data()
    # 打印此节点的虚拟机信息
    print(vm.get_vm_summary(name="ZJHZ-CMREAD-TEST343"))