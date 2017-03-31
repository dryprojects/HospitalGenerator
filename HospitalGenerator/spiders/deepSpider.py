#!/usr/bin/env python
# -*- coding:utf-8 -*-

from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from HospitalGenerator.items import HospitalgeneratorItem as HI
import logging

class DeepSpider(CrawlSpider):
    name='Deep'
    def __init__(self, rule):
        self.rule = rule

        self.name = rule.name
        self.allowed_domains = rule.allow_domains.split(',')
        self.start_urls = rule.start_urls.split(',')

        rule_list = []
        #如果是分页的网页，则采取分页处理
        if len(rule.next_page):
            rule_list.append(
                Rule(
                    LinkExtractor(restrict_xpaths=rule.next_page),
                    follow=True
                )
            )

            rule_list.append(
                Rule(
                    LinkExtractor(allow=(rule.allow_url, ), unique=True),
                    callback='parse_item',
                    follow=True
                )
            )
        else:
            # 不进行分页的一般处理
            rule_list.append(
                Rule(
                    LinkExtractor(allow=(rule.allow_url, ), unique=True),
                    callback='parse_item_normal',
                    follow=True
                )
            )

        self.rules = rule_list

        super(DeepSpider, self).__init__()

    def parse_item(self, response):
        """

        :param response:
        :return:
        """
        #如果不做循环处理
        if not len(self.rule.loop_css) :
            try:
                item = HI()
                item['title'] = response.css(self.rule.msgTitle_css)[0].extract().encode('gbk', 'ignore')
                item['desc'] = response.css(self.rule.msgDesc_css)[0].extract().encode('gbk', 'ignore')
                item['link'] = response.url.encode('gbk', 'ignore')
                item['postTime'] = response.css(self.rule.postTime_css)[0].extract().encode('gbk', 'ignore')
                item['msgFrom'] = self.rule.msgFrom.encode('gbk', 'ignore')
                yield item
            except IndexError:
                logging.error(u'内容不存在 %s' % response.url)
                yield HI()
        else:
            try:
                for sel in response.css(self.rule.loop_css):
                    item = HI()
                    item['title'] = response.css(self.rule.msgTitle_css)[0].extract().encode('gbk', 'ignore')
                    item['desc'] = sel.css(self.rule.msgDesc_css)[0].extract().encode('gbk', 'ignore')
                    item['link'] = response.url.encode('gbk', 'ignore')
                    item['postTime'] = sel.css(self.rule.postTime_css)[0].extract().encode('gbk', 'ignore')
                    item['msgFrom'] = self.rule.msgFrom.encode('gbk', 'ignore')
                    yield item
            except IndexError:
                logging.error(u'内容不存在 %s' % response.url)
                yield HI()

    def parse_item_normal(self, response):
        """

        :param response:
        :return:
        """
        #如果不做循环处理
        if not len(self.rule.loop_css) :
            try:
                item = HI()
                item['title'] = response.css(self.rule.msgTitle_css)[0].extract().encode('gbk', 'ignore')
                item['desc'] = response.css(self.rule.msgDesc_css)[0].extract().encode('gbk', 'ignore')
                item['link'] = response.url.encode('gbk', 'ignore')
                item['postTime'] = response.css(self.rule.postTime_css)[0].extract().encode('gbk', 'ignore')
                item['msgFrom'] = self.rule.msgFrom.encode('gbk', 'ignore')
                yield item
            except IndexError:
                logging.error(u'内容不存在 %s' % response.url)
                yield HI()
        else:
            try:
                for sel in response.css(self.rule.loop_css):
                    item = HI()
                    item['title'] = response.css(self.rule.msgTitle_css)[0].extract().encode('gbk', 'ignore')
                    item['desc'] = sel.css(self.rule.msgDesc_css)[0].extract().encode('gbk', 'ignore')
                    link = sel.css(self.rule.msgLink_css)[0].extract().encode('gbk', 'ignore')
                    item['link'] = self.rule.base_url + link.lstrip()
                    item['postTime'] = sel.css(self.rule.postTime_css)[0].extract().encode('gbk', 'ignore')
                    item['msgFrom'] = self.rule.msgFrom.encode('gbk', 'ignore')
                    yield item
            except IndexError, e:
                logging.error(u'内容不存在 %s' % (self.rule.base_url + response.url))
                yield HI()