import pandas as pd
test1 = pd.read_excel(r'D:\之江\资产管理\CMDB数据-bak.xlsx',sheet_name='10月份')
test2 = pd.read_excel(r'D:\咪咕文档\虚拟化资源池使用统计\资源池运行情况统计\资源利用率低效虚拟机.xlsx',sheet_name='9月份')

result = pd.merge(test1,test2.loc[:,['业务模块','业务维护接口人','DCN地址','业务地址','CPU','内存(G)','CPU利用率(%)','内存利用率(%)']],how='left',on='DCN地址')
print(result.head(20))
writer = pd.ExcelWriter(r'D:\咪咕文档\虚拟化资源池使用统计\资源池运行情况统计\result.xlsx')
result.to_excel(writer,index=False,sheet_name='重叠')
writer.save()




