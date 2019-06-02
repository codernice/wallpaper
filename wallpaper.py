#!/usr/bin/env python3
# Author: veelion

import re
import time
import requests
import os
import configparser
import random
import tldextract #pip install tldextract
import win32api, win32gui, win32con #pip install pypiwin32
from threading import Thread

# 图片下载
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
            

# 获取图片链接
def fing_pic_url(url, html):
    print('%s : %s' % (url, len(html)))
    # 获取src中的链接，并根据如下规则过滤
    links = re.findall(r'src=[\'"]?(.*?)[\'"\s]', html)
    for link in links:
        if not link.startswith('https://w.wallhaven.cc/full/'):
            continue
        if not link.endswith('.jpg'):
            continue
        urllib_download(link)

# 爬虫入库
def crawl(page,search):
    # 1\. 进入壁纸查询页面
    hub_url = 'https://wallhaven.cc/search?q=' + search + '&page=' + str(page)
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

#设置壁纸
def setWallPaper(pic):
    # open register
    regKey = win32api.RegOpenKeyEx(win32con.HKEY_CURRENT_USER,"Control Panel\\Desktop",0,win32con.KEY_SET_VALUE)
    win32api.RegSetValueEx(regKey,"WallpaperStyle", 0, win32con.REG_SZ, "2")
    win32api.RegSetValueEx(regKey, "TileWallpaper", 0, win32con.REG_SZ, "0")
    # refresh screen
    win32gui.SystemParametersInfo(win32con.SPI_SETDESKWALLPAPER,pic, win32con.SPIF_SENDWININICHANGE)

# 遍历图片随机设置壁纸
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

# 壁纸轮换
def loop_wallpaper(loop):
    while loop:
        searchImage()
        print(str(loop) + "秒后更换壁纸")
        time.sleep(loop)

# 壁纸下载
def download_wallpaper(max_page, search, download):
    while download:
        page = 1
        while page <= max_page:
            crawl(page,search)
            page = page +1
        print(str(download) + "小时后再次下载");
        second = download * 3600
        time.sleep(second)

def main():
    # 加载现有配置文件
    conf = configparser.ConfigParser()
    # 读取配置文件，如果写文件的绝对路径，就可以不用os模块
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

if __name__ == '__main__':
    main()
