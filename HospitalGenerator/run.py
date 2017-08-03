#!/usr/bin/env python
# -*- coding:utf-8 -*-

#######################################
#   scrapy 启动脚本
#   日期: 2017/04/14
#   作者: jennei
#   邮箱: jennei@hotmail.com
#   说明: 根据不同页面抓取规则，在主进程中分别创建
#   多个线程级别爬虫，抓取页面。
#######################################

from HospitalGenerator.spiders.deepSpider import DeepSpider
#from spiders.deepSpider import DeepSpider
from HospitalGenerator.models import HospitalModel
from HospitalGenerator.models import Rules

#scrapy api
from scrapy.crawler import CrawlerProcess
import ConfigParser
import logging
from HospitalGenerator.progressbar import ProgressBar
from scrapy.utils.log import configure_logging

# 创建一个命令行的进度条
# 35个爬虫
pb = ProgressBar(
    total=35
)

def spiderFinished(result):
    #执行完一个爬虫后，步长加一
    pb.move(1)
    pb.log()
    logging.info("spider finished! [%s]"%result)

def spiderErr(result, r2=None):
    logging.info("spider error \n%s\n%s"%(result, r2))

def main():
    try:
        cp = ConfigParser.SafeConfigParser()
        cp.read('./settings.conf')

        settings = {
            'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36',
            'BOT_NAME': 'HospitalGenerator',
            'SPIDER_MODULES': ['HospitalGenerator.spiders'],
            'NEWSPIDER_MODULE': 'HospitalGenerator.spiders',
            'ROBOTSTXT_OBEY': True,
            'ITEM_PIPELINES': {
                'HospitalGenerator.pipelines.HospitalgeneratorPipeline': 300,
                'HospitalGenerator.pipelines.MySQLPipline': 300,
            },
            'LOG_FILE': cp.get('LOG', 'LOG_FILE'),
            'LOG_LEVEL': cp.getint('LOG', 'LOG_LEVEL'),
            'LOG_ENABLE': True
        }

        process = CrawlerProcess(settings)
        # 1.初始化数据库连接池
        hospital = HospitalModel()
        # 2.查询爬虫需要的爬取规则
        rules = hospital.session.query(Rules).filter(Rules.enable == 1)
        # 3.根据爬虫规则分别制定不同的爬虫线程
        for rule in rules:
            # 非阻塞 twisted defer
            d = process.crawl(DeepSpider, rule)
            d.addCallbacks(spiderFinished, spiderErr)
        # 4.主进程启动（阻塞）
        process.start()
    except:
        import sys
        import traceback
        logging.error(u"\n%s[%s][%s]" % (sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2]))
        logging.error(u"\n%s", traceback.print_exc())


if __name__ == "__main__":
    pb.log()
    main()