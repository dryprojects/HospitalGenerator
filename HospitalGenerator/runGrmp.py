#!/usr/bin/env python
# -*- coding:utf-8 -*-

#######################################
#   scrapy 启动脚本
#   日期: 2017/03/06
#   作者: jennei
#   邮箱: jennei@hotmail.com
#   说明: 根据不同页面抓取规则，在主进程中分别创建
#   多个线程级别爬虫，抓取页面。
#######################################

from spiders.deepSpider import DeepSpider
from models import HospitalModel
from models import Rules

#scrapy api
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

import logging
try:
    process = CrawlerProcess(get_project_settings())

    # 1.初始化数据库连接池
    hospital = HospitalModel()
    # 2.查询爬虫需要的爬取规则
    rules = hospital.session.query(Rules).filter(Rules.enable == 1)
    # 3.根据爬虫规则分别制定不同的爬虫线程
    for rule in rules:
        # 非阻塞 twisted defer
        process.crawl(DeepSpider, rule)
    # 4.主进程启动（阻塞）
    process.start()
except:
    import sys
    import traceback
    logging.error(u"\n%s[%s][%s]"%(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2]))
    logging.error(u"\n%s", traceback.print_exc())
