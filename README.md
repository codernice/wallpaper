# Python壁纸下载与轮换
本人对于壁纸一直偏佛系，不爱特意去找一堆壁纸。因此用Python简单地搞了一个自动下载壁纸，定时随机轮换的功能来自娱自乐，顺便分享给大家。
# 准备
## 下载安装Python3
官网下载即可，选择合适的版本：[https://www.python.org/downloads/](https://www.python.org/downloads/)
安装一直下一步即可，记得勾选添加到环境变量。
## 安装pypiwin32
执行设置壁纸操作需要调用Windows系统的API，需要安装pypiwin32，控制台执行如下命令：
```
pip install pypiwin32
```
# 工作原理
两个线程，一个用来下载壁纸，一个用来轮换壁纸。每个线程内部均做定时处理，通过在配置文件中配置的等待时间来实现定时执行的功能。
## 壁纸下载线程
简易的爬虫工具，查询目标壁纸网站，过滤出有效连接，逐个遍历下载壁纸。
## 壁纸轮换线程
遍历存储壁纸的目录，随机选择一张壁纸路径，并使用pypiwin32库设置壁纸。
# 部分代码
## 线程创建与配置文件读取
```
def main():
    # 加载现有配置文件
    conf = configparser.ConfigParser()
    # 读取配置文件
    conf.read("conf.ini")
    # 读取配置项目
    search = conf.get('config', 'search')
    max_page = conf.getint('config','max_page')
    loop = conf.getint('config','loop')
    download = conf.getint('config','download')
    
    # 壁纸轮换线程
    t1 = Thread(target=loop_wallpaper,args=(loop,))
    t1.start()

    # 壁纸下载线程
    t2 = Thread(target=download_wallpaper,args=(max_page,search,download))
    t2.start()
```
## 遍历图片随机设置壁纸
```
def searchImage():
    # 获取壁纸路径
    imagePath = os.path.abspath(os.curdir) + '\images'
    if not os.path.exists(imagePath):
        os.makedirs(imagePath)
    # 获取路径下文件
    files = os.listdir(imagePath)
    # 随机生成壁纸索引
    if len(files) == 0:
        return
    index = random.randint(0,len(files)-1)
    for i in range(0,len(files)):
        path = os.path.join(imagePath,files[i])
        # if os.path.isfile(path):
        if i == index:
            if path.endswith(".jpg") or path.endswith(".bmp"):
                setWallPaper(path)
            else:
                print("不支持该类型文件")
```
## 设置壁纸
```
def setWallPaper(pic):
    # open register
    regKey = win32api.RegOpenKeyEx(win32con.HKEY_CURRENT_USER,"Control Panel\\Desktop",0,win32con.KEY_SET_VALUE)
    win32api.RegSetValueEx(regKey,"WallpaperStyle", 0, win32con.REG_SZ, "2")
    win32api.RegSetValueEx(regKey, "TileWallpaper", 0, win32con.REG_SZ, "0")
    # refresh screen
    win32gui.SystemParametersInfo(win32con.SPI_SETDESKWALLPAPER,pic, win32con.SPIF_SENDWININICHANGE)
```
## 壁纸查询链接过滤
```
def crawl(page,search):
    # 1\. 进入壁纸查询页面
    hub_url = 'https://wallhaven.cc/search?q=' + search + '&sorting=random&page=' + str(page)
    res = requests.get(hub_url)
    html = res.text

    # 2\. 获取链接
    ## 2.1 匹配 'href'
    links = re.findall(r'href=[\'"]?(.*?)[\'"\s]', html)
    print('find links:', len(links))
    news_links = []
    ## 2.2 过滤需要的链接
    for link in links:
        if not link.startswith('https://wallhaven.cc/w/'):
            continue
        news_links.append(link)
    print('find news links:', len(news_links))
    # 3\. 遍历有效链接进入详情
    for link in news_links:
        html = requests.get(link).text
        fing_pic_url(link, html)
    print('下载成功，当前页码:'+str(page));
```
## 图片下载
```
def urllib_download(url):
    #设置目录下载图片
    robot = './images/'
    file_name = url.split('/')[-1]
    path = robot + file_name
    if os.path.exists(path):
        print('文件已经存在')
    else:
        url=url.replace('\\','')
        print(url)
        r=requests.get(url,timeout=60)
        r.raise_for_status()
        r.encoding=r.apparent_encoding
        print('准备下载')
        if not os.path.exists(robot):
            os.makedirs(robot)
        with open(path,'wb') as f:
            f.write(r.content)
            f.close()
            print(path+' 文件保存成功')
```
## import部分
```
import re
import time
import requests
import os
import configparser
import random
import tldextract #pip install tldextract
import win32api, win32gui, win32con
from threading import Thread
```
完整代码请查看GitHub：[https://github.com/codernice/wallpaper](https://github.com/codernice/wallpaper)
# 知识点
threading：多线程，这里用来创建壁纸下载和壁纸轮换两个线程。
requests：这里用get获取页面，并获取最终的壁纸链接
pypiwin32：访问windows系统API的库，这里用来设置壁纸。
configparser：配置文件操作，用来读取线程等待时间和一些下载配置。
os：文件操作，这里用来存储文件，遍历文件，获取路径等。