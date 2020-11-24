# 多线程爬虫（现已失效，爬取[实验楼](https://www.shiyanlou.com/)将被反爬虫）
multiThreadSpiderPE 简易版脚本介绍
- 详细可以参考多线程爬虫（简易版）脚本说明文档.docx

multiThreadSpider 详细版（部署版）脚本功能介绍
- 该版本是可以部署在Ubuntu服务器环境中的爬取脚本。
- 由如下几个部分组成
    1.multiThreadSpider.py 程序体
    2.configurer.py 程序参数配置器
    3.launcher.py 程序启动器
    4.conf.xml 程序参数配置文件
    5.threadpool.py 第三方多线程库
- 通过configurer.py可以配置Python目录、timeout时间、是否日常爬取、home路径、Python版本以及自动爬取时间。
- 通过launcher.py可以直接在shell中运行爬虫部署版
- 第156行为多线程数量，建议设置数量不宜过大，以免遭受反爬虫限制。
- USER_AGENTS是修改爬虫的头部信息，需要按需修改
- 程序运行完毕后会在home目录下新建一个当前日期的xls文件
- 输出xls文件格式可以参考2019-02-24.xls
- 其余信息可以参考多线程爬虫（简易版）脚本说明文档.docx


