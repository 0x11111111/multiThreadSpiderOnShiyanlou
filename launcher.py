# coding = utf-8
"""The launcher for Multiple Thread Spider. 

This script serves as a launcher for Multiple Thread Spider with its running status saved in a log file. It enables the functioning of the main spider script with its running status directed to the standard output(screen) and the spider.log file as well.

This launcher extracts ths version of python installed from the conf.xml, then launch ths main spider with the linux command 'tee', which directs the log to the log file.

"""


import xml.etree.ElementTree as ET
import os


def get_conf(key):
    conf = ET.parse('./conf.xml')
    confRoot = conf.getroot()
    for val in confRoot:
        if key == val.tag:
            return val.text


version = get_conf('pythonVersion')

# 运行爬虫本体，tee命令将输出定向至标准输出与log文件
os.system('sudo python' + version + ' ./multiThreadSpider.py | tee -a spider.log')
