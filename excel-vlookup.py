#-*- condig:utf-8 -*-
#----------------------------------
#excel实现vlookup功能
#User:zhongpy
#Date:2021-10-21

import pandas as pd

table_a_name = input("请输入A表文件名：")
table_a_path = table_a_name + '.xlsx'
sheet_a_name = input("请输入A表中的sheet名称：")
table_a = pd.read_excel(table_a_path,sheet_name = sheet_a_name,converters={'DCN地址':str}).dropna(axis=1,how='all')
table_b_name = input("请输入B表文件名：")
table_b_path = table_b_name + ".xlsx"
sheet_b_name = input("请输入B表中的sheet名称：")
table_b = pd.read_excel(table_b_path,sheet_name=sheet_b_name,converters={'DCN地址':str})
table_b_2 = table_b.groupby("DCN地址").cpu利用率.sum().reset_index()
table_c = table_a.merge(right=table_b_2,how='left',left_on='DCN地址',right_on='DCN地址')
table_c.to_excel(r'D:\咪咕文档\虚拟化资源池使用统计\result.xlsx',index=False)
