# -*- coding:utf-8 -*-
import codecs
import os
import sys
from xml.dom.minidom import parseString

import pytz
import requests
from utils.setting import *
import shutil
import logging
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(message)s"
)

# under Python3
if sys.version_info.major < 3:
    reload(sys)
    sys.setdefaultencoding('utf8')


def remove_node_once(dom, tag_name):
    try:
        tmp = dom.getElementsByTagName(tag_name)[0]
        tmp.parentNode.removeChild(tmp)
    except IndexError:
        logging.error(tag_name + " not exist.")


def handle_nhk():
    guid = set()
    dom = parseString(requests.get(RSS_URL).text)

    # load previous xml
    try:
        with codecs.open("rss.xml", "r", "utf-8") as fp:
            rss = parseString(fp.read())
    except:
        rss = parseString(requests.get(RSS_URL).text)
        remove_node_once(rss, 'itunes:new-feed-url')

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
                    logging.info("%s 下载成功" % filename)
            except Exception:
                logging.error("%s 下载失败" % filename)

            item.getElementsByTagName('enclosure')[0].\
                setAttribute('url', BASE_URL + "{}{}.mp3".format(date.strftime('%Y年/%m月%d日/'), filename))
            rss.getElementsByTagName('channel')[0].appendChild(item)
        except Exception as e:
            logging.error(e)
            # pass

    rss.getElementsByTagName('lastBuildDate')[0].childNodes[0].data =\
        datetime.now(tz=pytz.timezone('Asia/Tokyo')).strftime('%a, %d %b %Y %H:%M:%S +0900')
    # save
    with codecs.open("rss.xml", "w", "utf-8") as fp:
        fp.write('\n'.join([line for line in rss.toprettyxml(indent=' '*2).split('\n') if line.strip()]))


def additional_func():
    try:
        if MOVE_DIR:
            shutil.move("%s/*" % DOWNLOAD_DIR, MOVE_DIR)
            logging.info("移动成功")
        elif MOVE_COMMAND:
            os.system(MOVE_COMMAND.format(DOWNLOAD_DIR))
            logging.info("移动命令执行成功")

        # rss
        if COPY_COMMAND:
            os.system(COPY_COMMAND.format("rss.xml", "rss.xml"))
            logging.info("复制命令执行成功")
    except Exception as e:
        logging.error(e)


handle_nhk()
additional_func()
