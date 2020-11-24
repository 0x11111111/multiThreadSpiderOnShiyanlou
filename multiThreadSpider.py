# coding = 'utf-8'
"""A spider that extracts the course information on www.shiyanlou.com.

This script uses xml.etree.ElementTree to load the path and timeout configuration stored in file conf.xml.
Uses urllib.request to obtain the html raw content from each couuse.
Uses re to extract the detailed target information from the raw content by means of regular expression.
Uses datetime and time to obtain the date and time which will be used in log information and filename.
Uses threadpool, a easy to use thread pool framework, which even saves you the trouble to add lock while writing in data.
Uses xlwt to operate the xls file storage.
Uses socket to set the timeout on each attempts, which may save you some time at some circumanstances.
Uses html to load a Exception called 'http.client.RemoteDisconnected', which arises when your behavior is recognized as a spider and thus refused by the server. 

"""

import xml.etree.ElementTree as ET
import urllib.request
import re
import datetime
import time
import xlwt
import threadpool
import socket
import http

end = 1400  # 终止id（不含）
idList = [id for id in range(1, end)]  # 待爬取id列表
failureList = []  # 失败爬取id列表

# xml提取器，用于提取保存在./conf.xml中的path与timeout信息
def get_conf(key):
    conf = ET.parse('/home/Code/spiderFinal/conf.xml')  
    confRoot = conf.getroot()
    for val in confRoot:
        if key == val.tag:
            return val.text
   
path = get_conf('path')  # 保存爬取的xls的path
timeout = int(get_conf('timeout'))  # 每个连接尝试的timeout数，默认120秒
socket.setdefaulttimeout(timeout)  #设置每个连接尝试的timeout
startTime = time.time()  # 获取开始时间
headings = ['课程号', '名称', '免费', '学过', '关注', '评论', '实验数目', '作者']  # 表头
row = 1  # 写入行号
# user_agents，用于伪造访问头部，反反爬虫机制
USER_AGENTS = ["Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",
    "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",
    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6",
    "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5",
    "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
    "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
    "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/531.21.8 (KHTML, like Gecko) Version/4.0.4 Safari/531.21.10",
    "Mozilla/5.0 (Windows; U; Windows NT 5.2; en-US) AppleWebKit/533.17.8 (KHTML, like Gecko) Version/5.0.1 Safari/533.17.8",
    "Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/533.19.4 (KHTML, like Gecko) Version/5.0.2 Safari/533.18.5",
    "Mozilla/5.0 (Windows; U; Windows NT 6.1; en-GB; rv:1.9.1.17) Gecko/20110123 (like Firefox/3.x) SeaMonkey/2.0.12",
    "Mozilla/5.0 (Windows NT 5.2; rv:10.0.1) Gecko/20100101 Firefox/10.0.1 SeaMonkey/2.7.1",
    "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_5_8; en-US) AppleWebKit/532.8 (KHTML, like Gecko) Chrome/4.0.302.2 Safari/532.8",
    "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_4; en-US) AppleWebKit/534.3 (KHTML, like Gecko) Chrome/6.0.464.0 Safari/534.3",
    "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_5; en-US) AppleWebKit/534.13 (KHTML, like Gecko) Chrome/9.0.597.15 Safari/534.13",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_2) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/14.0.835.186 Safari/535.1",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_8) AppleWebKit/535.2 (KHTML, like Gecko) Chrome/15.0.874.54 Safari/535.2",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_8) AppleWebKit/535.7 (KHTML, like Gecko) Chrome/16.0.912.36 Safari/535.7",
    "Mozilla/5.0 (Macintosh; U; Mac OS X Mach-O; en-US; rv:2.0a) Gecko/20040614 Firefox/3.0.0 ",
    "Mozilla/5.0 (Macintosh; U; PPC Mac OS X 10.5; en-US; rv:1.9.0.3) Gecko/2008092414 Firefox/3.0.3",
    "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.5; en-US; rv:1.9.1) Gecko/20090624 Firefox/3.5",
    "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.6; en-US; rv:1.9.2.14) Gecko/20110218 AlexaToolbar/alxf-2.0 Firefox/3.6.14",
    "Mozilla/5.0 (Macintosh; U; PPC Mac OS X 10.5; en-US; rv:1.9.2.15) Gecko/20110303 Firefox/3.6.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:2.0.1) Gecko/20100101 Firefox/4.0.1"]

# 获取日期
def get_date():
    return str(datetime.date.today())  

#获取时间
def get_time():
    t = datetime.datetime.now()
    return t.strftime('%H:%M:%S')

def get_info(id, captured):
    result = re.search(r'<a href="/courses/' + str(id) + r'">\s\s\s\s\s\s\s\s\s(.*?)\s\s\s\s\s\s\s\s\s</a>', captured)  # 获取课程名称
    title = result.group(1)

    result = re.search(r'<span>([0-9]*) 人学过</span>', captured)  # 获取学过人数，使用条件判断以防未列出该项
    if result:
        learned = result.group(1)
    else:
        learned = 'N/A'
    result = re.search(r'<span>([0-9]*)人关注</span>', captured)  # 获取关注人数，使用条件判断以防未列出该项
    if result:
        subscribed = result.group(1)
    else:
        subscribed = 'N/A'
    result = re.search(r'<span>([0-9]*)人评论</span>', captured)  # 获取评论人数，使用条件判断以防未列出该项
    if result:
        commented = result.group(1)
    else:
        commented = 'N/A'
        
    result = re.search(r'<span class="course-infobox-type" data-course-type="\d">(.*?)</span>', captured)  # 课程类型信息
    classType = result.group(1)

    result = re.search(r'<div class="name"><strong>(.*?)</strong>', captured)  # 课程老师信息
    tearcher = result.group(1)

    result = re.findall(r'lab-item-index', captured)  # 通过检索lab-item-index字段获取实验数目
    labItemCount = len(result)

    return id, title, classType, learned, subscribed, commented, labItemCount, tearcher

def write_in(toWrite, row = 0):  # 将数据写入sheet1
    for col, text in enumerate(toWrite): 
        sheet1.write(row, col, text)

workbook = xlwt.Workbook()   # 注意Workbook的开头W要大写
sheet1 = workbook.add_sheet('sheet1', cell_overwrite_ok = True)  # 添加sheet1，覆盖写入设为真
write_in(headings)  # 将表头写入sheet1

def capture(id):
    global row
    global failureList
    try:
        print('[%s %s INFO]Attempting to get:%d' % (get_date(), get_time(), id))
        req = urllib.request.Request('https://www.shiyanlou.com/courses/' + str(id))
        req.add_header('User-Agent', USER_AGENTS[id % len(USER_AGENTS)])
        response = urllib.request.urlopen(req)   # 发起访问
        captured = response.read().decode('utf-8')  # 以utf-8解码
        write_in(get_info(id, captured), row)   # 如无异常，直接写入信息
        row += 1

    except urllib.error.HTTPError:  # 404 NOT FOUND 异常
        print('[%s %s ERROR]Not Found:%d!' % (get_date(), get_time(), id))
        failureList.append(id)
        time.sleep(0.5)
    except socket.timeout:  # 端口超时异常
        print('[%s %s ERROR]Timeout on:%d!' % (get_date(), get_time(), id))
        failureList.append(id)
    except http.client.RemoteDisconnected: #  被远程服务器关闭连接，可能被反爬虫
        print('[%s %s ERROR]Refused by server on:%d!' % (get_date(), get_time(), id))
        failureList.append(id)
    except Exception:  # 其他异常
        print('[%s %s ERROR]Encountering Error!' % (get_date(), get_time()))
        failureList.append(id)


# 初次尝试抓取
pool = threadpool.ThreadPool(2)
requests = threadpool.makeRequests(capture, idList)
[pool.putRequest(req) for req in requests]
pool.wait()

# 再次尝试获取失败抓取的课程，以防被反爬虫遗漏
print('[%s %s INFO]Try to retrive failure attempts %s' % (get_date(), get_time(), failureList))
pool = threadpool.ThreadPool(2)
requests = threadpool.makeRequests(capture, failureList)
[pool.putRequest(req) for req in requests]
pool.wait()

# 保存工作簿
try:
    workbook.save(path + get_date() + '.xls')
except FileNotFoundError:
    print('[%s %s ERROR]File not found! Please verify the path(%s)!' % (get_date(), get_time(), path))
except Exception:
    print('[%s %s ERROR]File write in failed! Please grant the permission!' % (get_date(), get_time()))

finishTime = time.time()  # 获取结束时间
print('[%s %s INFO]Crawl Finished!' % (get_date(), get_time()))
print('[%s %s INFO]Total time cost is %d seconds' % (get_date(), get_time(), finishTime - startTime))
