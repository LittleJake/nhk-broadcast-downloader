# -*- coding:utf-8 -*-
import codecs
import os
import sys
from xml.dom.minidom import parseString
import requests
from utils.setting import *
import shutil

# under Python3
if sys.version_info.major < 3:
    reload(sys)
    sys.setdefaultencoding('utf8')

dom = parseString(requests.get(RSS_URL).text)
try:
    with open("rss.xml", "r") as fp:
        rss = parseString(fp.read())
except:
    rss = parseString(requests.get(RSS_URL).text)
    for node in rss.getElementsByTagName('item'):
        rss.getElementsByTagName('channel')[0].removeChild(node)

for node in dom.getElementsByTagName('item'):
    name = node.getElementsByTagName('title')[0].childNodes[0].data
    url = node.getElementsByTagName('enclosure')[0].getAttribute('url')
    try:
        date, filename = name.split(" ")
        try:
            os.mkdir(DOWNLOAD_DIR + date)
        except:
            pass

        try:
            response = requests.get(url)
            with open(DOWNLOAD_DIR + "%s/%s.mp3" % (date, filename), "wb") as f:
                f.write(response.content)
                print("%s 下载成功" % filename)
        except Exception:
            print("%s 下载失败" % filename)

        node.getElementsByTagName('enclosure')[0].setAttribute('url', BASE_URL + "%s/%s.mp3" % (date, filename))
        rss.getElementsByTagName('channel')[0].appendChild(node)
    except Exception as e:
        print(e)
        # pass


with codecs.open("rss.xml", "w", "utf-8") as fp:
    rss.writexml(fp)

try:
    if MOVE_DIR:
        shutil.move("%s/*" % DOWNLOAD_DIR, MOVE_DIR)
        print("移动成功")
    elif MOVE_COMMAND:
        os.system(MOVE_COMMAND.format(DOWNLOAD_DIR))
        print("移动命令执行成功")

    # rss
    if COPY_COMMAND:
        os.system(COPY_COMMAND.format("rss.xml", "rss.xml"))
        print("复制命令执行成功")
except Exception as e:
    print(e)
