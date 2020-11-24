# coding = 'utf-8'
"""An interface which allows the user to edit the configuration of the spider.

This script uses xml.etree.ElementTree to load the path and timeout configuration stored in file conf.xml.
Uses xml.dom.minidom to writein the setup configuration into the conf.xml.
Uses os to run commands and obtain the working directory, in a gesture to make daily autorun available by setuping up the /etc/crontab 

This script is intended to edit the configuration stored in conf.xml, please run this script first.

"""
import xml.etree.ElementTree as ET
import xml.dom.minidom as md
import os

# 提取./conf.xml键值对信息
conf = ET.parse('./conf.xml')
confDic = {}
confRoot = conf.getroot()
for val in confRoot:
    confDic[val.tag] = val.text

# 检测是否开启过每日运行，以防重复写入
firstEdition = True
if confDic['dailyAutorunOn'] == 'y':
    firstEdition = False
        
# 循环修改信息直到确认
confirm = False
while not confirm:
    print('Data saving path is %s' % confDic['path'])
    if confDic['dailyAutorunOn'] == 'y':
        print('Daily Autorun Service is on, activated at %s' % confDic['time'])
    else:
        print('Daily Autorun Service is off')
    print('Python path is %s' % confDic['pythonPath'])
    print('Python version is %s' % confDic['pythonVersion'])
    print('Timeout on each attempt is %s' % confDic['timeout'])
    ans = input('Confirm and save?(y/n)')
    if ans[0:1] == 'n' or ans[0:1] == 'N':
        print('Enter a new path or a single ENTER to remain default')
        newPath = input()
        if newPath != '':
            confDic['path'] = newPath
        if confDic['dailyAutorunOn'] == 'n':
            print('Turn on Daily Autotun Service?(y/n)')
            ans = input()
            if ans[0:1] == 'y' or ans[0:1] == 'Y':
                confDic['dailyAutorunOn'] = 'y'
                print('Enter a new time(HH:MM) or a single ENTER to remain default(%s)' % confDic['time'])
                newTime = input()
                if newTime != '':
                    confDic['time'] = newTime
                    
        else:
            print('Daily Autorun Service is on, activated at %s.' % confDic['time'])
            confDic['dailyAutorunOn'] = 'y'
            print('Enter a new time(HH:MM) or a single ENTER to remain default(%s)' % confDic['time'])
            newTime = input()
            if newTime != '':
                confDic['time'] = newTime
        
        print('Enter a new python path or a single ENTER to remain default(%s)' % confDic['pythonPath'])
        newPath = input()
        if newPath != '':
            confDic['pythonPath'] = newPath
        
        print('Enter a new python version(3.x) or a single ENTER to remain default(%s)' % confDic['pythonVersion'])
        newVersion = input()
        if newVersion != '':
            confDic['pythonVersion'] = newVersion
        
        print('Enter a new timeout(sec) or a single ENTER to remain default(%s).Larger value is recommended.' % confDic['timeout'])
        newTimeout = input()
        if newTimeout != '':
            confDic['timeout'] = newTimeout
    else:
        confirm = True
        break

# 更新xml信息
rootName = ET.Element('conf')
for key, val in confDic.items():
    key = ET.SubElement(rootName, key)
    key.text = val

# 写入xml
rawXml = ET.tostring(rootName, 'utf-8')
outXml = md.parseString(rawXml)
with open('./conf.xml', 'w+') as fs:
    outXml.writexml(fs, addindent="    ", newl="\n", encoding="utf-8")

# 提取信息，用于写入crontab文件
dailyAutoRun = False
if confDic['dailyAutorunOn'] == 'y' and firstEdition == True:
    dailyAutoRun = True
    path = confDic['path']
    version = confDic['pythonVersion']
    hour = confDic['time'][:2]
    miniute = confDic['time'][3:]
    pythonPath = confDic['pythonPath']

# 写入crontab文件以开启每日爬取
if dailyAutoRun:
    cronExpr = miniute + ' ' + hour + ' * * * root ' + pythonPath + 'python' + version + ' ' + os.getcwd() + '/multiThreadSpider.py >> ' + os.getcwd() + '/spider.log 2>&1'
    os.system('sudo echo "' + cronExpr + '" >> /etc/crontab')
