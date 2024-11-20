#!/usr/bin/env python
import webbrowser
import os
import time

url = ['https://172.24.10.144/','https://172.24.10.145/','https://172.24.10.146']
counter =0
i = 0
while counter < 3:
    webbrowser.open_new_tab(url[i])
    time.sleep(1)
    counter +=1
    if not counter % 3:
        os.system('taskkill /IM 360se.exe ')
