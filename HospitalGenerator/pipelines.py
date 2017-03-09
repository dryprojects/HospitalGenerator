# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from scrapy.exceptions import DropItem
from scrapy import signals
from scrapy.exporters import CsvItemExporter
from twisted.enterprise import adbapi
from datetime import datetime
import re
import MySQLdb.cursors

class CleanedData(object):
    def clean_data(self, item, spider):
        """
        做一些数据清理工作
        :param item:
        :return:
        """
        if not self.__valid(item):
            raise DropItem(u'去掉不符合的信息')

        #去掉包含在数据中的标签
        item['desc'] = re.sub(r"</?.*?>", "", item['desc'])
        item['postTime'] = re.sub(r"</?.*?>", "", item['postTime'])

        #去掉包含在数据中的空格
        item['desc'] = re.sub(r"\s", "", item['desc'])

        #匹配规则关键字，初步过滤数据
        p = re.compile(spider.rule.key_words)
        p1 = re.compile(spider.rule.postTime_pattern)

        #如果不包含想要的关键字，扔掉数据
        m = p.search(item['desc'])
        if m is None:
            raise DropItem(u'去掉不符合信息')

        #从一堆杂乱的数据中提取出时间
        m = p1.search(item['postTime'])
        if m is not None:
            item['postTime'] = m.groups()[0]
        item['postTime'] = self.__clean_time(item['postTime'])

        return item

    def __clean_time(self, time):
        """
        将time中的时间日期，过滤成统一的格式
        :param time: 初步过滤出的时间字符串
        :return: 统一格式化的时间字符串
        """
        #如果有汉字 年， 月 或者'/'则把汉字首先转换成 '-'
        time, n = re.subn(r'\xc4\xea|\xd4\xc2|/', '-', time)
        time = re.sub(r'\xc8\xd5', '', time)

        #去掉时间，只留日期
        time = time.split(' ')[0]

        #转换日期的顺序 如果年份在后 月日年, 则统一转换为 年月日
        #普通转换为年月日
        try:
            t1 = datetime.strptime(time, '%Y-%m-%d')
            t1 = t1.strftime('%Y/%m/%d')
        except ValueError:
            t1 = datetime.strptime(time, '%m-%d-%Y')
            t1 = t1.strftime('%Y/%m/%d')
        time = t1

        return time

    def __valid(self, item):
        """
        验证数据是否有效
        :param item:
        :return:
        """

        try:
            test = item['postTime']
            if test is None or test == '':
                return False
            test = item['title']
            if test is None or test == '':
                return False
            test = item['link']
            if test is None or test == '':
                return False
            test = item['desc']
            if test is None or test == '':
                return False
        except KeyError:
            return False

        return True

class HospitalgeneratorPipeline(CleanedData):
    def __init__(self):
        self.files = {}

    @classmethod
    def from_crawler(cls, crawler):
        pipline = cls()
        crawler.signals.connect(pipline.spider_opened, signals.spider_opened)
        crawler.signals.connect(pipline.spider_closed, signals.spider_closed)
        return pipline

    def spider_opened(self, spider):
        filename = spider.name + '.csv'
        file = open(filename, 'w+b')
        self.files[spider] = file
        self.exporter = CsvItemExporter(file)
        self.exporter.start_exporting()

    def spider_closed(self, spider):
        self.exporter.finish_exporting()
        file = self.files.pop(spider)
        file.close()

    def process_item(self, item, spider):
        item = self.clean_data(item, spider)
        self.exporter.export_item(item)
        return item

class MySQLPipline(CleanedData):
    def __init__(self, dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_crawler(cls, crawler):
        dbparams = dict(
            host = crawler.settings['MYSQL_HOST'],
            db = crawler.settings['MYSQL_DBNAME'],
            user = crawler.settings['MYSQL_USER'],
            passwd = crawler.settings['MYSQL_PASSWORD'],
            charset = 'gbk',
            cursorclass = MySQLdb.cursors.DictCursor,
            use_unicode = False
        )
        dbpool = adbapi.ConnectionPool('MySQLdb', **dbparams)
        return cls(dbpool)

    def process_item(self, item, spider):
        item = self.clean_data(item, spider)
        query = self.dbpool.runInteraction(self._conditional_insert, item)
        query.addErrback(self._handler_error, item, spider)
        return item

    def _conditional_insert(self, tx, item):
        sql = 'insert into info(postTime, msgLink, msgDesc, msgTitle, msgFrom) values(%s,%s,%s,%s,%s)'
        params = (item['postTime'], item['link'], item['desc'], item['title'], item['msgFrom'])
        tx.execute(sql, params)

    def _handler_error(self, failure, item, spider):
        import logging
        logging.error(failure)

if __name__ == '__main__':
    print 'DEBUG'
