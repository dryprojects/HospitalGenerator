# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from scrapy.exceptions import DropItem
from scrapy import signals
from scrapy.exporters import CsvItemExporter
from twisted.enterprise import adbapi
import re
import MySQLdb.cursors

class HospitalgeneratorPipeline(object):
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
        item['desc'] = re.sub(r"</?.*?>", "", item['desc'])
        p = re.compile(spider.rule.key_words)
        m = p.search(item['desc'])
        if m is None:
            raise DropItem(u'去掉不是招标的信息')

        p1 = re.compile(spider.rule.postTime_pattern)
        m = p1.search(item['postTime'])
        if m is not None:
            item['postTime'] = m.groups()[0]

        self.exporter.export_item(item)
        return item

class MySQLPipline(object):
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
        item['desc'] = re.sub(r"</?.*?>", "", item['desc'])
        p = re.compile(spider.rule.key_words)
        m = p.search(item['desc'])
        if m is None:
            raise DropItem(u'去掉不是招标的信息')
        p1 = re.compile(spider.rule.postTime_pattern)
        m = p1.search(item['postTime'])
        if m is not None:
            item['postTime'] = m.groups()[0]

        query = self.dbpool.runInteraction(self._conditional_insert, item)
        query.addErrback(self._handler_error, item, spider)
        return item

    def _conditional_insert(self, tx, item):
        sql = 'insert into info(postTime, msgLink, msgDesc, msgTitle) values(%s,%s,%s,%s)'
        params = (item['postTime'], item['link'], item['desc'], item['title'])
        tx.execute(sql, params)

    def _handler_error(self, failure, item, spider):
        print failure

if __name__ == '__main__':
    print 'DEBUG'
