# -*- coding:utf-8 -*-
import codecs
import os
import sys
from xml.dom.minidom import parseString
import requests
from utils.setting import *
import shutil
from datetime import datetime

# under Python3
if sys.version_info.major < 3:
    reload(sys)
    sys.setdefaultencoding('utf8')


def handle_nhk():
    guid = set()
    dom = parseString(requests.get(RSS_URL).text)

    # load previous xml
    try:
        with codecs.open("rss.xml", "r", "utf-8") as fp:
            rss = parseString(fp.read())
    except:
        rss = parseString(requests.get(RSS_URL).text)

    # remove duplicate item
    for item in rss.getElementsByTagName('item'):
        guid.add(item.getElementsByTagName('guid')[0].childNodes[0].data)

    # proceed
    for item in dom.getElementsByTagName('item'):
        if item.getElementsByTagName('guid')[0].childNodes[0].data in guid:
            continue

        date = item.getElementsByTagName('pubDate')[0].childNodes[0].data
        filename = item.getElementsByTagName('title')[0].childNodes[0].data
        url = item.getElementsByTagName('enclosure')[0].getAttribute('url')
        try:
            date = datetime.strptime(date, '%a, %d %b %Y %H:%M:%S +0900')
            try:
                os.makedirs("{}{}".format(DOWNLOAD_DIR, date.strftime('%Y年/%m月%d日/')))
            except:
                pass

            try:
                response = requests.get(url)
                with open("{}{}{}.mp3".format(DOWNLOAD_DIR, date.strftime('%Y年/%m月%d日/'), filename), "wb") as f:
                    f.write(response.content)
                    print("%s 下载成功" % filename)
            except Exception:
                print("%s 下载失败" % filename)

            item.getElementsByTagName('enclosure')[0].\
                setAttribute('url', BASE_URL + "{}{}.mp3".format(date.strftime('%Y年/%m月%d日/'), filename))
            rss.getElementsByTagName('channel')[0].appendChild(item)
        except Exception as e:
            print(e)
            # pass
    # save
    with codecs.open("rss.xml", "w", "utf-8") as fp:
        fp.write('\n'.join([line for line in rss.toprettyxml(indent=' '*2).split('\n') if line.strip()]))


def additional_func():
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


handle_nhk()
additional_func()
